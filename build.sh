#!/bin/bash

echo "========================================"
echo "开始打包 mini-open2anth 为单文件 EXE"
echo "========================================"
echo ""

# 检查是否安装了 pyinstaller
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "[提示] 未检测到 PyInstaller，正在安装..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo "[错误] PyInstaller 安装失败！"
        exit 1
    fi
    echo "[成功] PyInstaller 安装完成"
    echo ""
fi

# 清理之前的构建文件
if [ -d "build" ]; then
    echo "[清理] 删除旧的 build 目录..."
    rm -rf build
fi

if [ -d "dist" ]; then
    echo "[清理] 删除旧的 dist 目录..."
    rm -rf dist
fi

if [ -f "mini-open2anth.spec" ]; then
    echo "[清理] 删除旧的 spec 文件..."
    rm -f mini-open2anth.spec
fi

echo ""
echo "========================================"
echo "开始使用 PyInstaller 打包..."
echo "========================================"
echo ""

# 使用 build.spec 配置文件打包
pyinstaller build.spec --clean

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 打包失败！"
    exit 1
fi

echo ""
echo "========================================"
echo "打包成功！"
echo "========================================"
echo ""
echo "生成的文件位于: dist/mini-open2anth"
echo ""
echo "[提示] 运行前请确保在同目录下有 .env 配置文件"
echo "       或复制 .env.example 为 .env 并修改配置"
echo ""

# 复制 .env.example 到 dist 目录
if [ -f ".env.example" ]; then
    cp .env.example dist/.env.example
    echo "[完成] 已复制 .env.example 到 dist 目录"
fi

# 如果存在 .env 文件，也复制到 dist 目录
if [ -f ".env" ]; then
    cp .env dist/.env
    echo "[完成] 已复制 .env 到 dist 目录"
fi

echo ""
