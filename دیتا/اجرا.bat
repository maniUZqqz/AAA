@echo off
chcp 65001 >nul
title UpMarket — دیتا
cd /d "%~dp0"

echo.
echo   ============================================
echo    UpMarket — منبع داده و ارائه
echo   ============================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo   [FAIL] پایتون پیدا نشد. از python.org نصب کن.
  echo.
  pause
  exit /b 1
)

python -c "import flask" >nul 2>&1
if errorlevel 1 (
  echo   [..] نصب Flask ...
  python -m pip install --quiet flask
  if errorlevel 1 (
    echo   [FAIL] نصب Flask نشد.
    pause
    exit /b 1
  )
)

cd "0-منبع"
echo   [..] تطبیق داده با کد ...
python check.py
if errorlevel 1 (
  echo   [WARN] داده و کد از هم جدا افتاده‌اند — بالا را بخوان.
  echo.
)

echo   [..] بازتولید مستندات از data.json ...
python build_docs.py
python stitch.py
if errorlevel 1 (
  echo.
  echo   [FAIL] مدل مالی خطا داد — data.json را بررسی کن.
  cd ..
  pause
  exit /b 1
)
echo.
python model.py
cd ..

echo.
echo   ============================================
echo    ارائه روی http://127.0.0.1:5100
echo    برای بستن: Ctrl+C
echo   ============================================
echo.

start "" http://127.0.0.1:5100
cd "2-ارائه"
python app.py
