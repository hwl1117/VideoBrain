@echo off
echo ========================================
echo    VideoBrain 打包脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 清理旧的构建文件...
if exist dist rmdir /s /q dist

echo [2/3] 打包应用...
npx electron-builder --win --config electron-builder.yml

echo [3/3] 完成!
echo.
echo 构建文件在 dist 目录中
pause
