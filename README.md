# Anthropic to OpenAI API Proxy Service

一个将Anthropic API请求转换为OpenAI API的代理服务。支持流式输出和思考功能。

## 功能特性

- ✅ 将Anthropic API格式转换为OpenAI API格式
- ✅ 支持流式响应（SSE格式）
- ✅ 支持思考（thinking）功能转换（reasoning_content字段）
- ✅ 自动处理消息格式转换
- ✅ 支持所有常用参数（temperature、max_tokens等）
- ✅ 固定模型映射：所有Anthropic模型统一映射到 qwen-max-latest
- ✅ 完善的UTF-8编码支持
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
uv pip install fastapi uvicorn httpx python-dotenv
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
  "model": "claude-3-5-sonnet-20241022",
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

**注意**：无论请求中使用什么模型名称（如 `claude-3-5-sonnet-20241022`、`gpt-3.5-turbo` 等），服务都会自动映射到 `qwen-max-latest` 模型。
```

### 流式请求示例（支持思考功能）

```json
{
  "model": "claude-3-5-sonnet-20241022",
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

**普通响应：**
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
  "model": "qwen-max-latest",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 20
  }
}
```

**带思考内容的响应：**
```json
{
  "id": "msg_xxx",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "thinking",
      "thinking": "让我思考一下如何回答..."
    },
    {
      "type": "text",
      "text": "根据思考，我的回答是..."
    }
  ],
  "model": "qwen-max-latest",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 25
  }
}
```

### 流式响应格式

服务返回SSE格式的流式数据，每个事件都以`data: `开头。支持思考内容（thinking）和普通内容（text）的流式输出：

**带思考内容的流式响应：**
```
data: {"type": "message_start", "message": {...}}

data: {"type": "content_block_start", "index": 0, "content_block": {"type": "thinking", "thinking": ""}}

data: {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "思考内容..."}}

data: {"type": "content_block_stop", "index": 0}

data: {"type": "content_block_start", "index": 1, "content_block": {"type": "text", "text": ""}}

data: {"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": "回答内容..."}}

data: {"type": "content_block_stop", "index": 1}

data: {"type": "message_delta", "delta": {"stop_reason": "end_turn"}}

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
    "model": "claude-3-5-sonnet-20241022",
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
    "model": "claude-3-5-sonnet-20241022",
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

使用Python测试客户端：

```bash
python test_client.py
```

## 注意事项

1. 确保`.env`文件中的API URL和密钥配置正确
2. 服务默认运行在8000端口，可通过环境变量`PORT`修改
3. 流式请求使用Server-Sent Events (SSE)格式
4. **模型映射**：所有Anthropic模型名称（如 `claude-3-5-sonnet-20241022`）都会自动映射到 `qwen-max-latest`
5. **思考功能**：支持OpenAI的 `reasoning_content` 字段，会转换为Anthropic格式的 `thinking` 类型内容块
6. 消息格式会自动在Anthropic和OpenAI之间转换
7. 所有响应都使用UTF-8编码，支持中文等多语言字符

## 许可证

MIT
