#!/usr/bin/env python3
"""
Anthropic to OpenAI API Proxy Service
将Anthropic API请求转换为OpenAI API请求的代理服务
支持流式输出和思考功能
"""

import os
import json
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 从环境变量获取OpenAI配置
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

app = FastAPI(title="Anthropic to OpenAI Proxy")


class AnthropicToOpenAIConverter:
    """Anthropic到OpenAI请求转换器"""

    @staticmethod
    def convert_messages(anthropic_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将Anthropic消息格式转换为OpenAI格式"""
        openai_messages = []

        for msg in anthropic_messages:
            if msg["role"] == "user":
                # 处理Anthropic的用户消息（可能包含content blocks）
                content = msg.get("content", [])
                if isinstance(content, list):
                    # Anthropic的content是blocks
                    text_parts = []
                    for block in content:
                        if block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                    openai_messages.append({
                        "role": "user",
                        "content": "\n".join(text_parts) if text_parts else ""
                    })
                else:
                    openai_messages.append({
                        "role": "user",
                        "content": str(content)
                    })
            elif msg["role"] == "assistant":
                # 处理Anthropic的assistant消息
                content = msg.get("content", [])
                if isinstance(content, list):
                    text_parts = []
                    for block in content:
                        if block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                        elif block.get("type") == "thinking":
                            # 思考内容在OpenAI中作为元数据处理
                            pass
                    openai_messages.append({
                        "role": "assistant",
                        "content": "\n".join(text_parts) if text_parts else ""
                    })
                else:
                    openai_messages.append({
                        "role": "assistant",
                        "content": str(content)
                    })
            elif msg["role"] == "system":
                openai_messages.append({
                    "role": "system",
                    "content": msg.get("content", "")
                })

        return openai_messages

    @staticmethod
    def convert_request(anthropic_request: Dict[str, Any]) -> Dict[str, Any]:
        """将完整的Anthropic请求转换为OpenAI请求"""
        # 固定模型映射：所有Anthropic模型都映射到 qwen-max-latest
        FIXED_MODEL = "qwen-max-latest"
        model = FIXED_MODEL

        # 转换消息
        messages = AnthropicToOpenAIConverter.convert_messages(
            anthropic_request.get("messages", [])
        )

        # 创建OpenAI请求
        openai_request = {
            "model": model,
            "messages": messages,
            "stream": anthropic_request.get("stream", False)
        }

        # 复制可选参数
        if "temperature" in anthropic_request:
            openai_request["temperature"] = anthropic_request["temperature"]
        if "max_tokens" in anthropic_request:
            openai_request["max_tokens"] = anthropic_request["max_tokens"]
        if "top_p" in anthropic_request:
            openai_request["top_p"] = anthropic_request["top_p"]
        if "stop" in anthropic_request:
            openai_request["stop"] = anthropic_request["stop"]

        return openai_request


class OpenAIToAnthropicConverter:
    """OpenAI到Anthropic响应转换器"""

    @staticmethod
    def convert_delta(delta: Dict[str, Any]) -> Dict[str, Any]:
        """转换OpenAI delta为Anthropic格式"""
        anthropic_delta = {
            "type": "content_block_delta",
            "index": delta.get("index", 0),
            "content_block": {
                "type": "text",
                "text": delta.get("content", "")
            }
        }

        # 处理思考内容（如果存在）
        if "thinking" in delta:
            anthropic_delta["content_block"]["thinking"] = delta["thinking"]

        return anthropic_delta

    @staticmethod
    def convert_chunk(chunk: Dict[str, Any]) -> Dict[str, Any]:
        """转换OpenAI流式块为Anthropic格式"""
        anthropic_chunk = {
            "type": "message_start",
            "message": {
                "id": chunk.get("id", "msg_xxx"),
                "type": "message",
                "role": "assistant",
                "content": [],
                "model": chunk.get("model", "unknown"),
                "stop_reason": None,
                "stop_sequence": None
            }
        }

        # 如果有choices，处理流式数据
        if "choices" in chunk:
            for choice in chunk["choices"]:
                if choice.get("finish_reason"):
                    anthropic_chunk["message"]["stop_reason"] = choice["finish_reason"]

        return anthropic_chunk

    @staticmethod
    def convert_response(openai_response: Dict[str, Any]) -> Dict[str, Any]:
        """转换完整的OpenAI响应为Anthropic格式"""
        anthropic_response = {
            "id": openai_response.get("id", "msg_xxx"),
            "type": "message",
            "role": "assistant",
            "content": [],
            "model": openai_response.get("model", "unknown"),
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {
                "input_tokens": openai_response.get("usage", {}).get("prompt_tokens", 0),
                "output_tokens": openai_response.get("usage", {}).get("completion_tokens", 0)
            }
        }

        # 转换内容
        if "choices" in openai_response and openai_response["choices"]:
            choice = openai_response["choices"][0]
            message = choice.get("message", {})
            
            # 处理思考内容（如果存在）
            reasoning_content = message.get("reasoning_content", "")
            if reasoning_content:
                anthropic_response["content"].append({
                    "type": "thinking",
                    "thinking": reasoning_content
                })
            
            # 处理普通内容
            content = message.get("content", "")
            if content:
                anthropic_response["content"].append({
                    "type": "text",
                    "text": content
                })

            if choice.get("finish_reason"):
                anthropic_response["stop_reason"] = choice["finish_reason"]

        return anthropic_response


async def stream_openai_response(
    openai_request: Dict[str, Any]
) -> AsyncGenerator[str, None]:
    """流式传输OpenAI响应并转换为Anthropic格式"""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                "POST",
                f"{OPENAI_API_URL}/chat/completions",
                json=openai_request,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json; charset=utf-8"
                }
            ) as openai_stream:
                # 发送消息开始事件
                message_start = {
                    "type": "message_start",
                    "message": {
                        "id": "msg_stream_xxx",
                        "type": "message",
                        "role": "assistant",
                        "content": [],
                        "model": openai_request.get("model", "unknown"),
                        "stop_reason": None,
                        "stop_sequence": None,
                        "usage": {
                            "input_tokens": 0,
                            "output_tokens": 0
                        }
                    }
                }
                yield f"data: {json.dumps(message_start)}\n\n"

                thinking_index = 0
                content_index = 1
                thinking_started = False
                content_started = False

                async for line_bytes in openai_stream.aiter_lines():
                    # 确保正确解码UTF-8
                    try:
                        if isinstance(line_bytes, bytes):
                            line = line_bytes.decode('utf-8', errors='replace')
                        else:
                            line = line_bytes
                    except Exception as e:
                        print(f"Decode error: {e}")
                        continue
                        
                    if not line or not line.startswith("data: "):
                        continue

                    data_str = line[6:]  # 移除 "data: " 前缀

                    if data_str == "[DONE]":
                        # 发送消息结束事件
                        message_delta = {
                            "type": "message_delta",
                            "delta": {"stop_reason": "end_turn"},
                            "message": {
                                "stop_reason": "end_turn",
                                "stop_sequence": None
                            }
                        }
                        yield f"data: {json.dumps(message_delta)}\n\n"

                        # 发送完成事件
                        yield "data: [DONE]\n\n"
                        break

                    try:
                        chunk = json.loads(data_str)

                        if "choices" in chunk:
                            for choice in chunk["choices"]:
                                delta = choice.get("delta", {})

                                # 处理思考内容（thinking）- 必须在content之前
                                if "reasoning_content" in delta and delta["reasoning_content"]:
                                    if not thinking_started:
                                        # 发送思考块开始
                                        thinking_start = {
                                            "type": "content_block_start",
                                            "index": thinking_index,
                                            "content_block": {
                                                "type": "thinking",
                                                "thinking": ""
                                            }
                                        }
                                        yield f"data: {json.dumps(thinking_start)}\n\n"
                                        thinking_started = True
                                    
                                    # 发送思考内容增量
                                    thinking_delta = {
                                        "type": "content_block_delta",
                                        "index": thinking_index,
                                        "delta": {
                                            "type": "thinking_delta",
                                            "thinking": delta["reasoning_content"]
                                        }
                                    }
                                    yield f"data: {json.dumps(thinking_delta)}\n\n"

                                # 处理content
                                if "content" in delta and delta["content"]:
                                    # 如果thinking已完成但未关闭，先关闭thinking块
                                    if thinking_started and not content_started:
                                        thinking_end = {
                                            "type": "content_block_stop",
                                            "index": thinking_index
                                        }
                                        yield f"data: {json.dumps(thinking_end)}\n\n"
                                    
                                    if not content_started:
                                        # 发送内容块开始
                                        content_start = {
                                            "type": "content_block_start",
                                            "index": content_index,
                                            "content_block": {
                                                "type": "text",
                                                "text": ""
                                            }
                                        }
                                        yield f"data: {json.dumps(content_start)}\n\n"
                                        content_started = True
                                    
                                    # 发送内容增量
                                    content_delta = {
                                        "type": "content_block_delta",
                                        "index": content_index,
                                        "delta": {
                                            "type": "text_delta",
                                            "text": delta["content"]
                                        }
                                    }
                                    yield f"data: {json.dumps(content_delta)}\n\n"

                                # 处理完成原因
                                if choice.get("finish_reason"):
                                    # 发送思考块结束（如果还未关闭）
                                    if thinking_started and not content_started:
                                        thinking_end = {
                                            "type": "content_block_stop",
                                            "index": thinking_index
                                        }
                                        yield f"data: {json.dumps(thinking_end)}\n\n"
                                    
                                    # 发送内容块结束
                                    if content_started:
                                        content_end = {
                                            "type": "content_block_stop",
                                            "index": content_index
                                        }
                                        yield f"data: {json.dumps(content_end)}\n\n"

                                    # 发送消息增量
                                    message_delta = {
                                        "type": "message_delta",
                                        "delta": {
                                            "stop_reason": choice["finish_reason"]
                                        },
                                        "message": {
                                            "stop_reason": choice["finish_reason"]
                                        }
                                    }
                                    yield f"data: {json.dumps(message_delta)}\n\n"

                    except json.JSONDecodeError:
                        continue

    except Exception as e:
        error_response = {
            "type": "error",
            "error": {
                "type": "internal_server_error",
                "message": str(e)
            }
        }
        yield f"data: {json.dumps(error_response)}\n\n"


@app.post("/v1/messages")
async def anthropic_messages_endpoint(request: Request):
    """处理Anthropic /v1/messages 端点的请求"""
    try:
        # 解析请求体
        anthropic_request = await request.json()

        # 检查API key
        if not OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured"
            )

        # 转换为OpenAI格式
        openai_request = AnthropicToOpenAIConverter.convert_request(anthropic_request)

        # 检查是否为流式请求
        if anthropic_request.get("stream", False):
            # 流式响应
            return StreamingResponse(
                stream_openai_response(openai_request),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"
                }
            )
        else:
            # 非流式响应
            async with httpx.AsyncClient(timeout=300.0) as client:
                openai_response = await client.post(
                    f"{OPENAI_API_URL}/chat/completions",
                    json=openai_request,
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json; charset=utf-8"
                    }
                )

                if openai_response.status_code != 200:
                    raise HTTPException(
                        status_code=openai_response.status_code,
                        detail=openai_response.text
                    )

                # 确保正确解码响应
                try:
                    # 显式设置UTF-8编码
                    openai_response.encoding = 'utf-8'
                    openai_data = openai_response.json()
                except Exception as e:
                    # 如果JSON解析失败，尝试手动处理
                    try:
                        text = openai_response.content.decode('utf-8', errors='replace')
                        openai_data = json.loads(text)
                    except Exception as e2:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Failed to decode OpenAI response: {str(e2)}"
                        )
                
                anthropic_data = OpenAIToAnthropicConverter.convert_response(openai_data)

                return JSONResponse(anthropic_data, media_type="application/json; charset=utf-8")

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Request timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "anthropic-to-openai-proxy",
        "openai_url": OPENAI_API_URL,
        "openai_configured": bool(OPENAI_API_KEY)
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print("Starting Anthropic to OpenAI Proxy Server...")
    print(f"OpenAI API URL: {OPENAI_API_URL}")
    print(f"OpenAI API Key configured: {bool(OPENAI_API_KEY)}")
    print(f"Fixed Model Mapping: ALL -> qwen-max-latest")
    print(f"Service Port: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
