# Anthropic to OpenAI API Proxy Service

一个将Anthropic API请求转换为OpenAI API的代理服务。支持流式输出和思考功能。

## 功能特性

- ✅ 将Anthropic API格式转换为OpenAI API格式
- ✅ 支持流式响应（SSE格式）
- ✅ 支持思考（thinking）功能转换
- ✅ 自动处理消息格式转换
- ✅ 支持所有常用参数（temperature、max_tokens等）
- ✅ 健康检查端点

## 环境要求

- Python 3.8.20
- uv包管理器

## 安装步骤

### 1. 创建虚拟环境

```bash
uv venv --python 3.8.20 .venv
```

### 2. 安装依赖

```bash
uv pip install fastapi uvicorn httpx pydantic
```

### 3. 配置API

复制`.env.example`为`.env`并填入你的配置：

```bash
cp .env.example .env
```

编辑`.env`文件：

```env
OPENAI_API_URL=https://your-openai-api-url.com/v1
OPENAI_API_KEY=your-openai-api-key-here
```

### 4. 启动服务

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

**手动启动:**
```bash
source .venv/Scripts/activate
python main.py
```

## API使用

### 基本端点

```
POST /v1/messages
```

### 请求示例（Anthropic格式）

```json
{
  "model": "gpt-3.5-turbo",
  "max_tokens": 1024,
  "stream": false,
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "你好，请介绍一下自己"
        }
      ]
    }
  ]
}
```

### 流式请求示例

```json
{
  "model": "gpt-3.5-turbo",
  "max_tokens": 1024,
  "stream": true,
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "请讲一个长故事"
        }
      ]
    }
  ]
}
```

### 响应示例（Anthropic格式）

```json
{
  "id": "msg_xxx",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "你好！我是AI助手..."
    }
  ],
  "model": "gpt-3.5-turbo",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 20
  }
}
```

### 流式响应格式

服务返回SSE格式的流式数据，每个事件都以`data: `开头：

```
data: {"type": "message_start", "message": {...}}

data: {"type": "content_block_start", "index": 0, "content_block": {...}}

data: {"type": "content_block_delta", "index": 0, "delta": {...}}

data: {"type": "content_block_stop", "index": 0}

data: {"type": "message_delta", "delta": {...}}

data: [DONE]
```

## 服务地址

- 服务地址: http://localhost:8000
- 健康检查: http://localhost:8000/health
- API文档: http://localhost:8000/docs

## 测试

使用curl测试：

```bash
curl -X POST http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "你好"
          }
        ]
      }
    ]
  }'
```

流式测试：

```bash
curl -X POST http://localhost:8000/v1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "stream": true,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "讲一个故事"
          }
        ]
      }
    ]
  }'
```

## 注意事项

1. 确保`.env`文件中的API URL和密钥配置正确
2. 服务默认运行在8000端口，可通过环境变量`PORT`修改
3. 流式请求使用Server-Sent Events (SSE)格式
4. 思考（thinking）功能会转换为文本块处理
5. 消息格式会自动在Anthropic和OpenAI之间转换

## 许可证

MIT
