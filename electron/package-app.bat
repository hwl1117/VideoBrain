@echo off
echo ========================================
echo    VideoBrain 手动打包脚本
echo ========================================
echo.

cd /d "%~dp0.."

set OUTPUT_DIR=release
set APP_DIR=%OUTPUT_DIR%\VideoBrain

echo [1/5] 清理旧文件...
if exist %OUTPUT_DIR% rmdir /s /q %OUTPUT_DIR%
mkdir %APP_DIR%

echo [2/5] 复制 Electron 运行时...
xcopy /e /i /q electron\bin %APP_DIR%\electron >nul

echo [3/5] 复制应用代码...
copy /y electron\main.js %APP_DIR%\ >nul
copy /y electron\preload.js %APP_DIR%\ >nul
copy /y videobrain.ico %APP_DIR%\ >nul

echo [4/5] 复制前端构建...
xcopy /e /i /q frontend\.next %APP_DIR%\frontend\.next >nul
xcopy /e /i /q frontend\public %APP_DIR%\frontend\public >nul
copy /y frontend\package.json %APP_DIR%\frontend\ >nul
copy /y frontend\next.config.js %APP_DIR%\frontend\ >nul
xcopy /e /i /q frontend\src %APP_DIR%\frontend\src >nul
xcopy /e /i /q frontend\styles %APP_DIR%\frontend\styles >nul

echo [5/5] 复制后端代码...
xcopy /e /i /q backend\api %APP_DIR%\backend\api >nul
xcopy /e /i /q backend\services %APP_DIR%\backend\services >nul
xcopy /e /i /q backend\models %APP_DIR%\backend\models >nul
copy /y backend\config.py %APP_DIR%\backend\ >nul
copy /y backend\requirements.txt %APP_DIR%\backend\ >nul
copy /y backend\.env %APP_DIR%\backend\ >nul

echo.
echo ========================================
echo    打包完成！
echo    文件位置: %APP_DIR%
echo ========================================
echo.
pause
