@echo off
setlocal
chcp 65001 >nul 2>nul
cd /d "%~dp0backend"
if not exist "%~dp0logs" mkdir "%~dp0logs"
echo Backend working directory: %cd%
echo Backend log: %~dp0logs\backend-start.log
echo.

if not exist "venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  python -m venv venv
  if errorlevel 1 (
    echo Failed to create Python virtual environment.
    pause
    exit /b 1
  )
)

call venv\Scripts\activate.bat
python -m pip show fastapi >nul 2>nul
if errorlevel 1 (
  echo Installing backend dependencies...
  python -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Backend dependency install failed.
    pause
    exit /b 1
  )
)

python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 1>>"%~dp0logs\backend-start.log" 2>>&1
echo.
echo Backend service stopped. Close this window to exit.
pause >nul
