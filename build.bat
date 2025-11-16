@echo off
chcp 65001 > nul

:: Enable strict error handling for CI
if defined CI (
    set ERROR_ON_ERROR=1
)

echo ========================================
echo 开始打包 mini-open2anth 为单文件 EXE
echo ========================================

rem 获取脚本所在目录并切换到项目根目录
cd /d %~dp0

echo.
echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python 未安装或不在PATH中
    exit /b 1
)

REM 清理之前的构建文件
echo [2/4] 清理之前的构建文件...
if exist "build" (
    echo 正在删除旧的 build 目录...
    rmdir /s /q build 2>nul
)
if exist "dist" (
    echo 正在删除旧的 dist 目录...
    rmdir /s /q dist 2>nul
)

echo.
echo [3/4] 开始使用 PyInstaller 打包...
echo 请稍候，这可能需要几分钟时间...

REM 使用 build.spec 配置文件打包
pyinstaller build.spec --clean

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    exit /b 1
)

echo.
echo [4/4] 准备发布文件...

REM 创建发布目录
if not exist "release" mkdir release

REM 复制exe文件
copy /y "dist\mini-open2anth.exe" "release\mini-open2anth.exe" >nul
if errorlevel 1 (
    echo [错误] 复制exe文件失败！
    exit /b 1
)

REM 复制 .env.example 到 release 目录
if exist ".env.example" (
    copy /y .env.example "release\.env.example" >nul
    echo 已复制 .env.example
)

REM 复制 .env（如果存在）
if exist ".env" (
    copy /y .env "release\.env" >nul
    echo 已复制 .env
)

echo.
echo ========================================
echo 打包成功！
echo ========================================
echo.
echo 生成的文件位于: release\mini-open2anth.exe
echo.

REM 在CI环境下不显示暂停提示
if not defined CI pause

