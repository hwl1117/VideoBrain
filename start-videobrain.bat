@echo off
setlocal
chcp 65001 >nul 2>nul
title AgencySuperpowersProduct / VideoBrain Launcher

set "ROOT=%~dp0"
set "FRONTEND=%ROOT%frontend"
set "LOGDIR=%ROOT%logs"

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

echo.
echo ================================================
echo   AgencySuperpowersProduct / VideoBrain Launcher
echo ================================================
echo.

echo [1/5] Clearing ports 3000 / 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>nul
timeout /t 2 /nobreak >nul

echo [2/5] Checking Node.js / npm...
where node >nul 2>nul
if errorlevel 1 (
  echo Node.js was not found. Please install Node.js first.
  pause
  exit /b 1
)
where npm >nul 2>nul
if errorlevel 1 (
  echo npm was not found. Please install Node.js first.
  pause
  exit /b 1
)

echo [3/5] Checking frontend dependencies...
if not exist "%FRONTEND%\node_modules" (
  echo Installing frontend dependencies...
  pushd "%FRONTEND%"
  call npm install
  if errorlevel 1 (
    echo Frontend dependency install failed.
    popd
    pause
    exit /b 1
  )
  popd
)

echo [4/5] Starting backend API: http://localhost:8000
start "AgencySuperpowers Backend" cmd /k call "%ROOT%run-backend.bat"
timeout /t 3 /nobreak >nul

echo [5/5] Starting frontend: http://localhost:3000
start "AgencySuperpowers Frontend" cmd /k call "%ROOT%run-frontend.bat"

echo.
echo Waiting for frontend...
timeout /t 10 /nobreak >nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:3000' -TimeoutSec 8; if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500) { exit 0 } else { exit 1 } } catch { exit 1 }"
if errorlevel 1 (
  echo.
  echo Frontend did not respond yet. Wait 10-20 seconds and refresh.
  echo Frontend log: %LOGDIR%\frontend-start.log
  echo Backend log : %LOGDIR%\backend-start.log
) else (
  echo Frontend responded.
)

start "" http://localhost:3000

echo.
echo ================================================
echo   Keep Backend / Frontend service windows open.
echo   Frontend: http://localhost:3000
echo   API     : http://localhost:8000
echo ================================================
echo.
pause
