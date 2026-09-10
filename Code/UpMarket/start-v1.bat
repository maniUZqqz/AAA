@echo off
chcp 65001 >nul
setlocal

title UpMarket Launcher

REM ============================================================
REM
REM  UpMarket - one-click launcher with pre-flight checks
REM  Does everything itself: creates .env, installs packages,
REM  runs migrations, creates the admin user, starts all parts,
REM  then health-checks each service and reports [OK]/[WARN]/[FAIL].
REM
REM  *>>>* Only thing to configure: COMFYUI_DIR below *<<<*
REM
REM ============================================================

REM ---------------- CONFIG ----------------

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"

REM Path to ComfyUI installation (folder containing main.py):
set "COMFYUI_DIR=E:\Ai\ComfyUI_windows_portable"
set "COMFYUI_CMD=run_nvidia_gpu.bat"

REM --- If you use ComfyUI PORTABLE instead, comment the 2 lines above
REM --- and un-comment these 2 (fix the path):
REM set "COMFYUI_DIR=C:\ComfyUI_windows_portable"
REM set "COMFYUI_CMD=run_nvidia_gpu.bat"

REM ----------------------------------------

echo.
echo  ============================================
echo    UpMarket Launcher - pre-flight checks
echo  ============================================
echo.

REM ---------- [1/9] Python ----------

where python >nul 2>nul
if errorlevel 1 goto fail_python

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set "PYVER=%%v"

echo [OK]   %PYVER%

REM ---------- [2/9] Node.js ----------

where npm >nul 2>nul
if errorlevel 1 goto fail_node

echo [OK]   Node.js / npm found

REM ---------- [3/9] ffmpeg ----------

where ffmpeg >nul 2>nul

if errorlevel 1 (
    echo [WARN] ffmpeg NOT found - video and voice steps WILL fail.
    echo        Install ffmpeg and add it to PATH, then re-run start.bat
) else (
    echo [OK]   ffmpeg found
)

REM ---------- [4/9] backend .env ----------

if not exist "%BACKEND%\.env" (
    copy "%BACKEND%\.env.example" "%BACKEND%\.env" >nul
    echo [setup] backend\.env created from .env.example
    echo         If Ollama runs on ANOTHER machine, edit OLLAMA_BASE_URL in backend\.env
)

echo [OK]   backend\.env present

REM ---------- [5/9] Python packages - auto-install ----------

python -c "import django,rest_framework,rest_framework_simplejwt,corsheaders,drf_spectacular,celery,dotenv,requests,PIL,gtts,edge_tts" >nul 2>nul

if errorlevel 1 (
    echo [setup] Installing backend packages - first run only, please wait...
    pushd "%BACKEND%"
    pip install -r requirements.txt
    popd
)

python -c "import django,rest_framework,celery" >nul 2>nul

if errorlevel 1 goto fail_pip

echo [OK]   Python packages

REM ---------- [6/9] Django check + migrate + admin user ----------

pushd "%BACKEND%"

python manage.py check >nul 2>"%TEMP%\upmarket_check.err"

if errorlevel 1 (
    popd
    goto fail_django_check
)

python manage.py migrate --noinput >nul 2>"%TEMP%\upmarket_migrate.err"

if errorlevel 1 (
    popd
    goto fail_migrate
)

python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin','','admin1234')" >nul 2>nul

popd

echo [OK]   Django config + database migrations
echo [OK]   Admin panel user ready: admin / admin1234

REM ---------- [7/9] Frontend packages - auto-install ----------

if not exist "%FRONTEND%\node_modules" (
    echo [setup] Installing frontend packages - first run only, please wait...
    pushd "%FRONTEND%"
    call npm install --no-audit --no-fund
    popd
)

if not exist "%FRONTEND%\node_modules" goto fail_npm

echo [OK]   Frontend packages

REM ---------- [8/9] Optional services ----------

set "HAS_OLLAMA=0"

where ollama >nul 2>nul && set "HAS_OLLAMA=1"

if "%HAS_OLLAMA%"=="0" (
    echo [WARN] ollama NOT found in PATH - AI features fail unless OLLAMA_BASE_URL
    echo        in backend\.env points to another machine that runs Ollama.
)

set "HAS_REDIS=0"
set "REDIS_CMD=redis-server"

REM portable Redis: install-redis.bat drops redis-server.exe into <project>\redis\
if exist "%ROOT%redis\redis-server.exe" (
    set "HAS_REDIS=1"
    set "REDIS_CMD=%ROOT%redis\redis-server.exe"
)

if "%HAS_REDIS%"=="0" where redis-server >nul 2>nul && set "HAS_REDIS=1"

REM ------------------------------------------------------------
REM The backend picks its own mode at startup
REM (CELERY_TASK_ALWAYS_EAGER=auto in backend\.env):
REM   Redis up      -^> queue mode + workers -^> VIDEO GENERATION WORKS
REM   Redis missing -^> synchronous mode, everything except video
REM Nothing has to be edited by hand here - we only offer to
REM install Redis when it is missing.
REM ------------------------------------------------------------

if "%HAS_REDIS%"=="1" (
    echo [OK]   Redis found - queue mode, video generation available.
    goto redis_done
)

echo [WARN] Redis NOT found. Everything works EXCEPT video generation,
echo        which needs a background queue.
echo        install-redis.bat downloads a portable Redis into %ROOT%redis\

choice /c YN /m "Install Redis now - recommended"

if errorlevel 2 (
    echo [WARN] Skipped. Synchronous mode will be used; video stays off.
    echo        You can run install-redis.bat at any time later.
    goto redis_done
)

call "%ROOT%install-redis.bat"

if exist "%ROOT%redis\redis-server.exe" (
    set "HAS_REDIS=1"
    set "REDIS_CMD=%ROOT%redis\redis-server.exe"
    echo [OK]   Redis installed - video generation will be available.
) else (
    echo [WARN] Redis still missing - continuing in synchronous mode.
    echo        Read the instructions install-redis.bat printed above.
)

:redis_done

if not exist "%COMFYUI_DIR%" (
    echo [WARN] ComfyUI folder NOT found: %COMFYUI_DIR%
    echo        Image/video generation will fail. Edit COMFYUI_DIR in start.bat CONFIG.
)

netstat -ano 2>nul | findstr /r /c:":8000 .*LISTENING" >nul && echo [WARN] Port 8000 already in use - is the backend already running?

netstat -ano 2>nul | findstr /r /c:":5173 .*LISTENING" >nul && echo [WARN] Port 5173 already in use - is the frontend already running?

REM ---------- [9/9] Self-check - does the whole chain really work? ----------
REM
REM Runs the REAL code (tasks, prompts, JSON repair, database rows, Pillow
REM poster text, ffmpeg concat, the whole HTTP API) against SIMULATED models,
REM so it needs no GPU, no Ollama and no ComfyUI. About a minute.
REM
REM The point: if this fails, the application itself is broken and testing with
REM real models would only hide that behind "maybe the model is slow".
REM Skip it with:   start.bat /notest

if /i "%~1"=="/notest" (
    echo [skip] Self-check skipped ^(/notest^).
    goto selfcheck_done
)

echo.
echo  --------------------------------------------------------
echo    Self-check - running the whole app against simulated
echo    models. ~1 minute, no GPU needed.  Skip: start.bat /notest
echo  --------------------------------------------------------

set "SELFTEST_LOG=%TEMP%\upmarket_selftest.log"
set "E2E_LOG=%TEMP%\upmarket_e2e.log"

pushd "%BACKEND%"

python manage.py selftest --quick >"%SELFTEST_LOG%" 2>&1

if errorlevel 1 (
    set "SELFCHECK_FAILED=1"
    echo [FAIL] AI pipelines - analysis, market, captions, poster, script, video, chat
) else (
    echo [OK]   AI pipelines - analysis, market, captions, poster, script, video, chat
)

if exist "%ROOT%redis\redis-server.exe" (
    python tools\e2e_api_test.py --queue >"%E2E_LOG%" 2>&1
) else (
    python tools\e2e_api_test.py >"%E2E_LOG%" 2>&1
)

if errorlevel 1 (
    set "SELFCHECK_FAILED=1"
    echo [FAIL] API end-to-end - login, catalog, content, chat, orders, campaigns, publish
) else (
    echo [OK]   API end-to-end - login, catalog, content, chat, orders, campaigns, publish
)

popd

if defined SELFCHECK_FAILED (
    echo.
    echo  ---- last lines of the failing check ----
    if defined SELFTEST_LOG powershell -NoProfile -Command "Get-Content -LiteralPath $env:SELFTEST_LOG -Tail 12 -Encoding UTF8" 2>nul
    powershell -NoProfile -Command "Get-Content -LiteralPath $env:E2E_LOG -Tail 12 -Encoding UTF8" 2>nul
    echo  -----------------------------------------
    echo  Full logs: %SELFTEST_LOG%
    echo             %E2E_LOG%
    echo.
    echo [WARN] The APPLICATION itself is failing - not the models, not the GPU.
    echo        Fix this first, or you will spend the night blaming Ollama.
    choice /c YN /m "Start the services anyway"
    if errorlevel 2 (
        echo Stopped. Nothing was launched.
        pause
        exit /b 1
    )
) else (
    echo [OK]   Self-check passed - the whole chain works. Anything that breaks
    echo        from here on is the models or the hardware, not the code.
)

:selfcheck_done

REM clear the errorlevel left behind by CHOICE so nothing downstream sees it
ver >nul

echo.

echo  ============================================
echo    Pre-flight done - launching services
echo  ============================================
echo.

REM ============================================================
REM 1) Ollama
REM ============================================================
REM
REM IMPORTANT:
REM Do NOT put "set ... && set ... && ollama serve"
REM inside the START command.
REM
REM The environment variables are defined here in the main
REM SETLOCAL scope. The Ollama child process inherits them.
REM They disappear automatically when this launcher exits.
REM ============================================================

if "%HAS_OLLAMA%"=="1" (

    echo [run] Ollama on :11434 ...

    REM Strict VRAM / RAM management for 30B / 32B models on RTX 3060 12GB
    set "OLLAMA_FLASH_ATTENTION=1"
    set "OLLAMA_NUM_PARALLEL=1"
    REM 2048 was truncating long JSON answers (captions/scripts died mid-JSON,
    REM beter.md #5). ROADMAP SS2.4 recommends 8192; q8_0 KV cache halves the
    REM extra VRAM that costs.
    set "OLLAMA_CONTEXT_LENGTH=8192"
    set "OLLAMA_KV_CACHE_TYPE=q8_0"
    set "OLLAMA_MAX_LOADED_MODELS=1"
    set "OLLAMA_KEEP_ALIVE=30s"
    set "OLLAMA_GPU_OVERHEAD=500000000"

    REM Start Ollama WITHOUT any chained SET commands.
    start "UpMarket - Ollama" cmd /k "ollama serve"
)

REM ============================================================
REM 2) ComfyUI
REM ============================================================

if exist "%COMFYUI_DIR%" (
    echo [run] ComfyUI on :8188 ...
    start "UpMarket - ComfyUI" /d "%COMFYUI_DIR%" cmd /k "%COMFYUI_CMD%"
)

REM ============================================================
REM 3) Redis
REM ============================================================

if "%HAS_REDIS%"=="1" (
    echo [run] Redis on :6379 ...
    start "UpMarket - Redis" cmd /k ""%REDIS_CMD%""
    REM The backend decides queue-vs-synchronous by probing Redis as it boots,
    REM so it must not start before Redis is accepting connections.
    call :wait_for_redis
)

REM ============================================================
REM 4) Backend
REM ============================================================

echo [run] Django backend on :8000 ...

start "UpMarket - Backend" /d "%BACKEND%" cmd /k "python manage.py runserver 0.0.0.0:8000"

REM ============================================================
REM 5) Celery workers - only useful when Redis exists.
REM
REM Two separate workers so a long video generation (gpu queue)
REM never blocks captions/analysis/chat jobs (ai queue).
REM ============================================================

if "%HAS_REDIS%"=="1" (

    echo [run] Celery worker - AI queue ...

    start "UpMarket - Celery AI" /d "%BACKEND%" cmd /k "timeout /t 5 >nul && celery -A config worker -l info -Q celery,ai --pool=solo -n ai@%%h"

    echo [run] Celery worker - GPU queue ...

    start "UpMarket - Celery GPU" /d "%BACKEND%" cmd /k "timeout /t 5 >nul && celery -A config worker -l info -Q gpu --pool=solo -n gpu@%%h"
)

REM ============================================================
REM 6) Frontend
REM ============================================================

echo [run] Frontend on :5173 ...

start "UpMarket - Frontend" /d "%FRONTEND%" cmd /k "npm run dev"

echo.

echo  Waiting 15 seconds, then health-checking every service...

timeout /t 15 /nobreak >nul

echo.

echo  ============================================
echo    Health check
echo  ============================================

set "HAS_CURL=0"

where curl >nul 2>nul && set "HAS_CURL=1"

if "%HAS_CURL%"=="0" (
    echo [WARN] curl not available - skip health checks, verify windows manually.
    goto summary
)

call :healthcheck "Backend API      " "http://localhost:8000/api/docs/"
call :healthcheck "Frontend         " "http://localhost:5173/"

if "%HAS_OLLAMA%"=="1" call :healthcheck "Ollama           " "http://localhost:11434/"

if exist "%COMFYUI_DIR%" call :healthcheck "ComfyUI          " "http://127.0.0.1:8188/"

REM ---- Are the models really there, under exactly these names? ----
REM The self-check above uses simulated models, so it can never notice that a
REM .safetensors on this machine is spelled differently from what the workflow
REM asks for. Only the running services can answer that, so we ask them here.

echo.

pushd "%BACKEND%"
python manage.py checkmodels
popd

:summary

echo.

echo  ============================================
echo    UpMarket is starting
echo  ============================================

echo  Dashboard : http://localhost:5173
echo  API docs  : http://localhost:8000/api/docs/
echo  Admin     : http://localhost:8000/admin/ user: admin pass: admin1234

echo.

echo  If a service shows WARN/FAIL above, read ITS window for the exact error,
echo  then check the troubleshooting table in test.md

echo.

start http://localhost:5173

pause

exit /b 0


REM ============================================================
REM WAIT FOR REDIS - the backend picks its mode at startup
REM ============================================================

:wait_for_redis

echo        waiting for Redis to accept connections ...

for /l %%i in (1,1,15) do (
    netstat -ano 2>nul | findstr /r /c:":6379 .*LISTENING" >nul && exit /b 0
    REM ping is the sleep that also works when stdin is redirected
    "%SystemRoot%\System32\ping.exe" -n 2 127.0.0.1 >nul 2>nul
)

echo [WARN] Redis did not open port 6379 in time - the backend may come up in
echo        synchronous mode and video generation would stay off. Read the
echo        Redis window, then re-run start.bat.

exit /b 0


REM ============================================================
REM HEALTH CHECK HELPER
REM ============================================================

:healthcheck

set "HC=000"

for /f %%h in ('curl -s -o nul -w "%%{http_code}" --max-time 6 %~2 2^>nul') do set "HC=%%h"

if "%HC%"=="200" (
    echo [OK]   %~1 is up             %~2
) else (
    echo [WARN] %~1 HTTP %HC% - not ready yet or failed; check its window. %~2
)

exit /b 0


REM ============================================================
REM FAILURE HANDLERS
REM ============================================================

:fail_python

echo.

echo [FAIL] Python is NOT installed or not in PATH.
echo        Install Python 3.10+ from python.org and CHECK "Add to PATH".

pause

exit /b 1


:fail_node

echo.

echo [FAIL] Node.js / npm is NOT installed or not in PATH.
echo        Install Node.js LTS from nodejs.org, then re-run start.bat

pause

exit /b 1


:fail_pip

echo.

echo [FAIL] Python package installation failed.
echo        Run manually to see the error:
echo          cd backend ^&^& pip install -r requirements.txt

pause

exit /b 1


:fail_django_check

echo.

echo [FAIL] Django configuration check failed. Error:

type "%TEMP%\upmarket_check.err" 2>nul

echo        Send this error text for debugging.

pause

exit /b 1


:fail_migrate

echo.

echo [FAIL] Database migration failed. Error:

type "%TEMP%\upmarket_migrate.err" 2>nul

echo        Send this error text for debugging.

pause

exit /b 1


:fail_npm

echo.

echo [FAIL] Frontend package installation failed.
echo        Run manually to see the error:
echo          cd frontend ^&^& npm install

pause

exit /b 1
