@echo off
chcp 65001 >nul
setlocal
title UpMarket Launcher
REM ============================================================
REM  UpMarket - one-click launcher with pre-flight checks
REM  Does everything itself: creates .env, installs packages,
REM  runs migrations, creates the admin user, starts all parts,
REM  then health-checks each service and reports [OK]/[WARN]/[FAIL].
REM  >>> Only thing to configure: COMFYUI_DIR below <<<
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

set "OLLAMA_CTX=8192"
REM ----------------------------------------

echo.
echo  ============================================
echo    UpMarket Launcher - pre-flight checks
echo  ============================================
echo.

REM ---------- [1/8] Python ----------
where python >nul 2>nul
if errorlevel 1 goto fail_python
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
echo [OK]   %PYVER%

REM ---------- [2/8] Node.js ----------
where npm >nul 2>nul
if errorlevel 1 goto fail_node
echo [OK]   Node.js / npm found

REM ---------- [3/8] ffmpeg ----------
where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo [WARN] ffmpeg NOT found - video and voice steps WILL fail.
  echo        Install ffmpeg and add it to PATH, then re-run start.bat
) else (
  echo [OK]   ffmpeg found
)

REM ---------- [4/8] backend .env ----------
if not exist "%BACKEND%\.env" (
  copy "%BACKEND%\.env.example" "%BACKEND%\.env" >nul
  echo [setup] backend\.env created from .env.example
  echo         If Ollama runs on ANOTHER machine, edit OLLAMA_BASE_URL in backend\.env
)
echo [OK]   backend\.env present

REM ---------- [5/8] Python packages - auto-install ----------
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

REM ---------- [6/8] Django check + migrate + admin user ----------
pushd "%BACKEND%"
python manage.py check >nul 2>"%TEMP%\upmarket_check.err"
if errorlevel 1 ( popd & goto fail_django_check )
python manage.py migrate --noinput >nul 2>"%TEMP%\upmarket_migrate.err"
if errorlevel 1 ( popd & goto fail_migrate )
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin','','admin1234')" >nul 2>nul
popd
echo [OK]   Django config + database migrations
echo [OK]   Admin panel user ready:  admin / admin1234

REM ---------- [7/8] Frontend packages - auto-install ----------
if not exist "%FRONTEND%\node_modules" (
  echo [setup] Installing frontend packages - first run only, please wait...
  pushd "%FRONTEND%"
  call npm install --no-audit --no-fund
  popd
)
if not exist "%FRONTEND%\node_modules" goto fail_npm
echo [OK]   Frontend packages

REM ---------- [8/8] Optional services ----------
set "HAS_OLLAMA=0"
where ollama >nul 2>nul && set "HAS_OLLAMA=1"
if "%HAS_OLLAMA%"=="0" (
  echo [WARN] ollama NOT found in PATH - AI features fail unless OLLAMA_BASE_URL
  echo        in backend\.env points to another machine that runs Ollama.
)

set "HAS_REDIS=0"
set "REDIS_CMD=redis-server"
if exist "%ROOT%redis\redis-server.exe" (
  set "HAS_REDIS=1"
  set "REDIS_CMD=%ROOT%redis\redis-server.exe"
)
if "%HAS_REDIS%"=="0" where redis-server >nul 2>nul && set "HAS_REDIS=1"

REM The backend chooses its own mode (CELERY_TASK_ALWAYS_EAGER=auto):
REM Redis up -^> queue mode + video generation; Redis down -^> synchronous.
REM Nothing in backend\.env has to be edited by hand.
if "%HAS_REDIS%"=="1" (
  echo [OK]   Redis found - queue mode, video generation available.
  goto redis_done
)
echo [WARN] Redis NOT found. Everything works EXCEPT video generation.
choice /c YN /m "Install a portable Redis now - recommended"
if errorlevel 2 (
  echo [WARN] Skipped - synchronous mode will be used; video stays off.
) else (
  call "%ROOT%install-redis.bat"
  if exist "%ROOT%redis\redis-server.exe" (
    set "HAS_REDIS=1"
    set "REDIS_CMD=%ROOT%redis\redis-server.exe"
  )
)
:redis_done

if not exist "%COMFYUI_DIR%" (
  echo [WARN] ComfyUI folder NOT found: %COMFYUI_DIR%
  echo        Image/video generation will fail. Edit COMFYUI_DIR in start.bat CONFIG.
)

netstat -ano 2>nul | findstr /r /c:":8000 .*LISTENING" >nul && echo [WARN] Port 8000 already in use - is the backend already running?
netstat -ano 2>nul | findstr /r /c:":5173 .*LISTENING" >nul && echo [WARN] Port 5173 already in use - is the frontend already running?

echo.
echo  ============================================
echo    Pre-flight done - launching services
echo  ============================================
echo.

REM 1) Ollama
if "%HAS_OLLAMA%"=="1" (
  echo [run] Ollama on :11434 ...
  start "UpMarket - Ollama" cmd /k "set OLLAMA_FLASH_ATTENTION=1&& set OLLAMA_NUM_PARALLEL=2&& set OLLAMA_CONTEXT_LENGTH=%OLLAMA_CTX%&& ollama serve"
)

REM 2) ComfyUI
if exist "%COMFYUI_DIR%" (
  echo [run] ComfyUI on :8188 ...
  start "UpMarket - ComfyUI" /d "%COMFYUI_DIR%" cmd /k "%COMFYUI_CMD%"
)

REM 3) Redis
if "%HAS_REDIS%"=="1" (
  echo [run] Redis on :6379 ...
  start "UpMarket - Redis" cmd /k ""%REDIS_CMD%""
  REM the backend probes Redis while booting - give it time to bind :6379
  "%SystemRoot%\System32\ping.exe" -n 5 127.0.0.1 >nul 2>nul
)

REM 4) Backend
echo [run] Django backend on :8000 ...
start "UpMarket - Backend" /d "%BACKEND%" cmd /k "python manage.py runserver 0.0.0.0:8000"

REM 5) Celery workers - only useful when Redis exists.
REM    Two separate workers so a long video generation (gpu queue) never
REM    blocks captions/analysis/chat jobs (ai queue).
if "%HAS_REDIS%"=="1" (
  echo [run] Celery worker - AI queue ...
  start "UpMarket - Celery AI" /d "%BACKEND%" cmd /k "timeout /t 5 >nul && celery -A config worker -l info -Q celery,ai --pool=solo -n ai@%%h"
  echo [run] Celery worker - GPU queue ...
  start "UpMarket - Celery GPU" /d "%BACKEND%" cmd /k "timeout /t 5 >nul && celery -A config worker -l info -Q gpu --pool=solo -n gpu@%%h"
)

REM 6) Frontend
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

:summary
echo.
echo  ============================================
echo    UpMarket is starting
echo  ============================================
echo   Dashboard : http://localhost:5173
echo   API docs  : http://localhost:8000/api/docs/
echo   Admin     : http://localhost:8000/admin/   user: admin  pass: admin1234
echo.
echo   If a service shows WARN/FAIL above, read ITS window for the exact error,
echo   then check the troubleshooting table in test.md
echo.
start http://localhost:5173
pause
exit /b 0

REM ================= health check helper =================
:healthcheck
set "HC=000"
for /f %%h in ('curl -s -o nul -w "%%{http_code}" --max-time 6 %~2 2^>nul') do set "HC=%%h"
if "%HC%"=="200" (
  echo [OK]   %~1 is up            %~2
) else (
  echo [WARN] %~1 HTTP %HC%  - not ready yet or failed; check its window. %~2
)
exit /b 0

REM ================= failure handlers =================
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
