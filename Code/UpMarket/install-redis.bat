@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title UpMarket - Redis installer

REM ============================================================
REM  Installs a PORTABLE Redis into <project>\redis\
REM
REM  Why it matters: with Redis running, UpMarket switches itself
REM  to queue mode and VIDEO GENERATION becomes available.
REM  Without Redis everything else still works (synchronous mode)
REM  but video cannot run inside a web request.
REM
REM  Nothing is installed system-wide, nothing is added to PATH,
REM  and nothing outside this project folder is touched.
REM ============================================================

set "ROOT=%~dp0"
set "TARGET=%ROOT%redis"
set "ZIPURL=https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.zip"
set "ZIPFILE=%TEMP%\upmarket-redis.zip"

echo.
echo  ============================================
echo    UpMarket - Redis installer
echo  ============================================
echo.

if exist "%TARGET%\redis-server.exe" (
    echo [OK]   Redis is already installed here:
    echo        %TARGET%\redis-server.exe
    echo        Just run start.bat - it starts Redis automatically.
    echo.
    pause
    exit /b 0
)

where redis-server >nul 2>nul
if not errorlevel 1 (
    echo [OK]   redis-server is already available in PATH.
    echo        Just run start.bat - it starts Redis automatically.
    echo.
    pause
    exit /b 0
)

where curl >nul 2>nul
if errorlevel 1 goto no_curl

echo [1/3] Downloading Redis for Windows ^(about 6 MB^)...
echo       %ZIPURL%
curl -L --fail --max-time 300 -o "%ZIPFILE%" "%ZIPURL%"
if errorlevel 1 goto download_failed
if not exist "%ZIPFILE%" goto download_failed

echo [2/3] Extracting to %TARGET% ...
if not exist "%TARGET%" mkdir "%TARGET%"

set "EXTRACTED=0"
where tar >nul 2>nul
if not errorlevel 1 (
    tar -xf "%ZIPFILE%" -C "%TARGET%" >nul 2>nul
    if exist "%TARGET%\redis-server.exe" set "EXTRACTED=1"
)

if "!EXTRACTED!"=="0" (
    powershell -NoProfile -Command "Expand-Archive -LiteralPath '%ZIPFILE%' -DestinationPath '%TARGET%' -Force" >nul 2>nul
    if exist "%TARGET%\redis-server.exe" set "EXTRACTED=1"
)

del "%ZIPFILE%" >nul 2>nul

if "!EXTRACTED!"=="0" goto extract_failed

echo [3/3] Verifying...
if not exist "%TARGET%\redis-server.exe" goto extract_failed

echo.
echo  ============================================
echo    [OK] Redis installed
echo  ============================================
echo    %TARGET%\redis-server.exe
echo.
echo    Now run start.bat. It will:
echo      - start Redis on port 6379
echo      - start both Celery workers
echo      - switch the backend to queue mode automatically
echo        ^(CELERY_TASK_ALWAYS_EAGER=auto detects Redis by itself^)
echo.
echo    Video generation is available from then on.
echo.
pause
exit /b 0


:no_curl
echo [FAIL] curl.exe was not found, so the download cannot start.
goto manual


:download_failed
echo [FAIL] The download failed ^(no internet, or GitHub is blocked here^).
goto manual


:extract_failed
echo [FAIL] The archive could not be extracted.
goto manual


:manual
echo.
echo  ============================================
echo    Install Redis by hand - 3 steps
echo  ============================================
echo.
echo   1. On any machine with internet, download this file:
echo.
echo        %ZIPURL%
echo.
echo      ^(GitHub blocked? Search for "Redis-x64-5.0.14.1.zip" on any
echo       mirror, or use Memurai: https://www.memurai.com/get-memurai^)
echo.
echo   2. Extract the ZIP and copy redis-server.exe into EXACTLY this folder:
echo.
echo        %TARGET%\
echo.
echo      The result must be:  %TARGET%\redis-server.exe
echo.
echo   3. Run start.bat again. Redis is detected automatically and video
echo      generation turns on - no file needs to be edited.
echo.
echo   Without Redis everything else keeps working; only video generation
echo   stays off.
echo.
pause
exit /b 1
