@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

title UpMarket Launcher

REM ============================================================
REM  UpMarket - one-click launcher (resilient version)
REM  - Self-check failures DO NOT block startup
REM  - Missing optional services (Ollama/ComfyUI/ffmpeg/Redis) just warn
REM  - Frontend/backend always try to start if at all possible
REM ============================================================

REM ---------------- CONFIG ----------------

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"

REM Path to ComfyUI installation (folder containing main.py):
REM اگه ComfyUI نداری یا مسیرش فرق می‌کنه، اینجا درستش کن یا خالی بذار
set "COMFYUI_DIR="
set "COMFYUI_CMD=run_nvidia_gpu.bat"

REM اگه می‌خوای Ollama رو خودت جدا اجرا کنی، اینو 0 کن
set "START_OLLAMA=1"

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
    echo [WARN] ffmpeg NOT found - video/voice steps will fail.
    echo        Install: winget install ffmpeg   ^(then reopen terminal^)
) else (
    echo [OK]   ffmpeg found
)

REM ---------- [4/9] backend .env ----------
if not exist "%BACKEND%\.env" (
    if exist "%BACKEND%\.env.example" (
        copy "%BACKEND%\.env.example" "%BACKEND%\.env" >nul
        echo [setup] backend\.env created from .env.example
    ) else (
        echo [WARN] backend\.env.example missing - skipping .env creation
    )
)
echo [OK]   backend\.env present

REM ---------- [5/9] Python packages (per-package, no all-or-nothing) ----------
echo [setup] Checking Python packages ...

REM هر پکیج رو جدا چک کن که اگه یکی نبود، فقط همون رو نصب کنه
set "NEED_PIP=0"

python -c "import django"           >nul 2>nul || set "NEED_PIP=1"
python -c "import rest_framework"   >nul 2>nul || set "NEED_PIP=1"
python -c "import celery"           >nul 2>nul || set "NEED_PIP=1"
python -c "import dotenv"           >nul 2>nul || set "NEED_PIP=1"
python -c "import PIL"              >nul 2>nul || set "NEED_PIP=1"
python -c "import requests"         >nul 2>nul || set "NEED_PIP=1"

if "%NEED_PIP%"=="1" (
    echo [setup] Installing backend packages - first run only, please wait...
    pushd "%BACKEND%"
    pip install -r requirements.txt
    popd
)

REM چک‌های نرم - اگه نبود فقط warning بده، متوقف نشو
python -c "import django,rest_framework,celery" >nul 2>nul
if errorlevel 1 (
    echo [FAIL] Core Python packages missing. Run manually:
    echo        cd backend ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

python -c "import gtts" >nul 2>nul
if errorlevel 1 echo [WARN] gTTS missing - Google TTS voice won't work

python -c "import edge_tts" >nul 2>nul
if errorlevel 1 (
    echo [WARN] edge-tts missing - Microsoft Edge TTS voice won't work.
    echo        Likely network/firewall blocks it. To fix later:
    echo          pip install edge-tts
)
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

REM ---------- [7/9] Frontend packages (ROBUST check) ----------
REM درست چک کن که vite واقعاً نصبه، نه فقط پوشه node_modules وجود داره
if not exist "%FRONTEND%\node_modules\.bin\vite.cmd" (
    echo [setup] Installing/repairing frontend packages, please wait...
    pushd "%FRONTEND%"
    if exist "node_modules" (
        echo        Removing broken node_modules ...
        rmdir /s /q node_modules
    )
    call npm install --no-audit --no-fund
    popd
)

if not exist "%FRONTEND%\node_modules\.bin\vite.cmd" (
    echo [FAIL] Frontend dependencies are still broken after reinstall.
    echo        Try manually:
    echo          cd frontend
    echo          rmdir /s /q node_modules
    echo          npm cache clean --force
    echo          npm install
    pause
    exit /b 1
)
echo [OK]   Frontend packages (vite present)

REM ---------- [8/9] Optional services ----------
set "HAS_OLLAMA=0"
where ollama >nul 2>nul && set "HAS_OLLAMA=1"
if "%HAS_OLLAMA%"=="0" (
    echo [WARN] ollama NOT found in PATH - AI features will fail unless
    echo        OLLAMA_BASE_URL in backend\.env points to another machine.
)

set "HAS_REDIS=0"
set "REDIS_CMD=redis-server"
if exist "%ROOT%redis\redis-server.exe" (
    set "HAS_REDIS=1"
    set "REDIS_CMD=%ROOT%redis\redis-server.exe"
)
if "%HAS_REDIS%"=="0" where redis-server >nul 2>nul && set "HAS_REDIS=1"

if "%HAS_REDIS%"=="1" (
    echo [OK]   Redis found - queue mode, video generation available.
) else (
    echo [WARN] Redis NOT found - video generation will be OFF. Everything else works.
    echo        You can run install-redis.bat later.
)

if not "%COMFYUI_DIR%"=="" (
    if not exist "%COMFYUI_DIR%" (
        echo [WARN] ComfyUI folder NOT found: %COMFYUI_DIR%
        echo        Image/video generation will fail until fixed.
    )
) else (
    echo [INFO] COMFYUI_DIR is empty - ComfyUI will not be started by this script.
)

netstat -ano 2>nul | findstr /r /c:":8000 .*LISTENING" >nul && echo [WARN] Port 8000 already in use - backend may already be running
netstat -ano 2>nul | findstr /r /c:":5173 .*LISTENING" >nul && echo [WARN] Port 5173 already in use - frontend may already be running

REM ---------- [9/9] Self-check (NON-BLOCKING) ----------
if /i "%~1"=="/notest" (
    echo [skip] Self-check skipped ^(/notest^).
    goto selfcheck_done
)

echo.
echo  --------------------------------------------------------
echo    Self-check - running the app against simulated models.
echo    Skip: start.bat /notest
echo  --------------------------------------------------------

set "SELFTEST_LOG=%TEMP%\upmarket_selftest.log"
set "E2E_LOG=%TEMP%\upmarket_e2e.log"

pushd "%BACKEND%"

python manage.py selftest --quick >"%SELFTEST_LOG%" 2>&1
if errorlevel 1 (
    set "SELFCHECK_FAILED=1"
    echo [WARN] AI pipeline self-check failed - see %SELFTEST_LOG%
) else (
    echo [OK]   AI pipelines self-check passed
)

if exist "%ROOT%redis\redis-server.exe" (
    python tools\e2e_api_test.py --queue >"%E2E_LOG%" 2>&1
) else (
    python tools\e2e_api_test.py >"%E2E_LOG%" 2>&1
)

if errorlevel 1 (
    set "SELFCHECK_FAILED=1"
    echo [WARN] API end-to-end self-check failed - see %E2E_LOG%
) else (
    echo [OK]   API end-to-end self-check passed
)

popd

if defined SELFCHECK_FAILED (
    echo.
    echo  ---- last lines of the failing check ----
    if defined SELFTEST_LOG powershell -NoProfile -Command "Get-Content -LiteralPath $env:SELFTEST_LOG -Tail 8 -Encoding UTF8" 2>nul
    powershell -NoProfile -Command "Get-Content -LiteralPath $env:E2E_LOG -Tail 8 -Encoding UTF8" 2>nul
    echo  -----------------------------------------
    echo [WARN] Some checks failed. Continuing anyway - Backend and Frontend
    echo        will still start. Fix the warnings above when you can.
    echo        Full logs: %SELFTEST_LOG%
    echo                   %E2E_LOG%
)

:selfcheck_done

ver >nul

echo.
echo  ============================================
echo    Pre-flight done - launching services
echo  ============================================
echo.

REM ============================================================
REM 1) Ollama (optional)
REM ============================================================
if "%START_OLLAMA%"=="1" if "%HAS_OLLAMA%"=="1" (
    echo [run] Ollama on :11434 ...
    set "OLLAMA_FLASH_ATTENTION=1"
    set "OLLAMA_NUM_PARALLEL=1"
    set "OLLAMA_CONTEXT_LENGTH=8192"
    set "OLLAMA_KV_CACHE_TYPE=q8_0"
    set "OLLAMA_MAX_LOADED_MODELS=1"
    set "OLLAMA_KEEP_ALIVE=30s"
    set "OLLAMA_GPU_OVERHEAD=500000000"
    start "UpMarket - Ollama" cmd /k "ollama serve"
)

REM ============================================================
REM 2) ComfyUI (optional - only if folder configured AND exists)
REM ============================================================
if not "%COMFYUI_DIR%"=="" if exist "%COMFYUI_DIR%" (
    echo [run] ComfyUI on :8188 ...
    start "UpMarket - ComfyUI" /d "%COMFYUI_DIR%" cmd /k "%COMFYUI_CMD%"
)

REM ============================================================
REM 3) Redis (optional)
REM ============================================================
if "%HAS_REDIS%"=="1" (
    echo [run] Redis on :6379 ...
    start "UpMarket - Redis" cmd /k ""%REDIS_CMD%""
    call :wait_for_redis
)

REM ============================================================
REM 4) Backend (ESSENTIAL)
REM ============================================================
echo [run] Django backend on :8000 ...
start "UpMarket - Backend" /d "%BACKEND%" cmd /k "python manage.py runserver 0.0.0.0:8000"

REM ============================================================
REM 5) Celery workers (only when Redis exists)
REM    Both queues in ONE window to keep desktop clean.
REM ============================================================
if "%HAS_REDIS%"=="1" (
    echo [run] Celery workers ^(AI + GPU^) ...
    start "UpMarket - Celery" /d "%BACKEND%" cmd /k "timeout /t 5 >nul && start /b celery -A config worker -l info -Q celery,ai --pool=solo -n ai@%%h && celery -A config worker -l info -Q gpu --pool=solo -n gpu@%%h"
)

REM ============================================================
REM 6) Frontend (ESSENTIAL)
REM ============================================================
echo [run] Frontend on :5173 ...
start "UpMarket - Frontend" /d "%FRONTEND%" cmd /k "npm run dev"

echo.
echo  Waiting 15 seconds, then health-checking services...
timeout /t 15 /nobreak >nul

echo.
echo  ============================================
echo    Health check
echo  ============================================

set "HAS_CURL=0"
where curl >nul 2>nul && set "HAS_CURL=1"

if "%HAS_CURL%"=="0" (
    echo [WARN] curl not available - skip health checks
    goto summary
)

call :healthcheck "Backend API      " "http://localhost:8000/api/docs/"
call :healthcheck "Frontend         " "http://localhost:5173/"

if "%HAS_OLLAMA%"=="1" call :healthcheck "Ollama           " "http://localhost:11434/"
if not "%COMFYUI_DIR%"=="" if exist "%COMFYUI_DIR%" call :healthcheck "ComfyUI          " "http://127.0.0.1:8188/"

echo.
pushd "%BACKEND%"
python manage.py checkmodels 2>nul
popd

:summary
echo.
echo  ============================================
echo    UpMarket is starting
echo  ============================================
echo  Dashboard : http://localhost:5173
echo  API docs  : http://localhost:8000/api/docs/
echo  Admin     : http://localhost:8000/admin/  user: admin  pass: admin1234
echo.
echo  If a service shows WARN/FAIL, read ITS window for the exact error.
echo.
start http://localhost:5173
pause
exit /b 0


REM ============================================================
:wait_for_redis
echo        waiting for Redis to accept connections ...
for /l %%i in (1,1,15) do (
    netstat -ano 2>nul | findstr /r /c:":6379 .*LISTENING" >nul && exit /b 0
    "%SystemRoot%\System32\ping.exe" -n 2 127.0.0.1 >nul 2>nul
)
echo [WARN] Redis did not open port 6379 in time.
exit /b 0

REM ============================================================
:healthcheck
set "HC=000"
for /f %%h in ('curl -s -o nul -w "%%{http_code}" --max-time 6 %~2 2^>nul') do set "HC=%%h"
if "%HC%"=="200" (
    echo [OK]   %~1 is up             %~2
) else (
    echo [WARN] %~1 HTTP %HC% - not ready or failed. %~2
)
exit /b 0

REM ============================================================
:fail_python
echo.
echo [FAIL] Python not installed or not in PATH.
echo        Install Python 3.10+ from python.org and CHECK "Add to PATH".
pause
exit /b 1

:fail_node
echo.
echo [FAIL] Node.js / npm not installed or not in PATH.
echo        Install Node.js LTS from nodejs.org.
pause
exit /b 1

:fail_django_check
echo.
echo [FAIL] Django check failed:
type "%TEMP%\upmarket_check.err" 2>nul
pause
exit /b 1

:fail_migrate
echo.
echo [FAIL] Migration failed:
type "%TEMP%\upmarket_migrate.err" 2>nul
pause
exit /b 1