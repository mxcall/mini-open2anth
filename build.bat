@echo off
chcp 65001 > nul
echo ========================================
echo 开始打包 mini-open2anth 为单文件 EXE
echo ========================================
echo.

rem 获取脚本所在目录并切换到项目根目录
cd /d %~dp0

echo [1/4] 激活虚拟环境...
if not exist .venv\Scripts\activate.bat (
    echo [错误] 未找到 .venv 虚拟环境，请先创建虚拟环境
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [错误] 虚拟环境激活失败
    pause
    exit /b 1
)

REM 检查是否安装了 pyinstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [提示] 未检测到 PyInstaller，正在安装...
    pip install pyinstaller
    if errorlevel 1 (
        echo [错误] PyInstaller 安装失败！
        pause
        exit /b 1
    )
    echo [成功] PyInstaller 安装完成
    echo.
)

REM 清理之前的构建文件
if exist "build" (
    echo [清理] 删除旧的 build 目录...
    rmdir /s /q build
)
if exist "dist" (
    echo [清理] 删除旧的 dist 目录...
    rmdir /s /q dist
)
if exist "mini-open2anth.spec" (
    echo [清理] 删除旧的 spec 文件...
    del /q mini-open2anth.spec
)

echo.
echo ========================================
echo 开始使用 PyInstaller 打包...
echo ========================================
echo.

REM 使用 build.spec 配置文件打包
pyinstaller build.spec --clean

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包成功！
echo ========================================
echo.
echo 生成的文件位于: dist\mini-open2anth.exe
echo.
echo [提示] 运行前请确保在同目录下有 .env 配置文件
echo        或复制 .env.example 为 .env 并修改配置
echo.

REM 复制 .env.example 到 dist 目录
if exist ".env.example" (
    copy /y .env.example dist\.env.example > nul
    echo [完成] 已复制 .env.example 到 dist 目录
)

REM 如果存在 .env 文件，也复制到 dist 目录
if exist ".env" (
    copy /y .env dist\.env > nul
    echo [完成] 已复制 .env 到 dist 目录
)

echo.
pause
