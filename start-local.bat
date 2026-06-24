@echo off
echo ========================================
echo    VideoBrain 本地启动脚本
echo ========================================
echo.

echo [1/2] 启动后端服务...
cd /d "%~dp0backend"
start "VideoBrain Backend" cmd /k "venv\Scripts\activate && uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] 启动前端服务...
cd /d "%~dp0frontend"
start "VideoBrain Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo    启动完成！
echo ========================================
echo.
echo    前端: http://localhost:3000
echo    后端: http://localhost:8000
echo.
echo    按任意键关闭此窗口...
pause > nul
