@echo off
:: 启动Anthropic到OpenAI代理服务

echo =========================================
echo Anthropic to OpenAI API Proxy Service
echo =========================================
echo.

:: 检查.venv目录
if not exist ".venv" (
    echo 错误: 未找到虚拟环境目录 .venv
    echo 请先运行: uv venv --python 3.8.20 .venv
    pause
    exit /b 1
)

:: 激活虚拟环境
call .venv\Scripts\activate.bat

:: 检查.env文件
if not exist ".env" (
    echo 警告: 未找到 .env 配置文件
    echo 请复制 .env.example 为 .env 并填入你的API配置
    echo.
)

:: 显示配置信息
echo 配置信息:
echo OpenAI API URL: %OPENAI_API_URL%
if defined OPENAI_API_KEY (
    echo OpenAI API Key: 已配置
) else (
    echo OpenAI API Key: 未配置
)
echo.
echo Python版本:
python --version
echo.

:: 启动服务
echo 启动服务...
echo 服务地址: http://localhost:8000
echo 健康检查: http://localhost:8000/health
echo API文档: http://localhost:8000/docs
echo API端点: http://localhost:8000/v1/messages
echo.
echo 模型映射: 所有模型统一映射到 qwen-max-latest
echo 支持功能: 流式响应、思考内容(thinking)、UTF-8编码
echo.
echo 按 Ctrl+C 停止服务
echo.

python main.py
