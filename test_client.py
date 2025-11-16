#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Anthropic到OpenAI代理服务的客户端
"""

import asyncio
import json
import aiohttp
import sys
import io

# 设置标准输出为UTF-8编码（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


async def test_normal_request():
    """测试普通请求"""
    print("\n=== 测试普通请求 ===")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/v1/messages",
            json={
                "model": "gpt-3.5-turbo",
                "max_tokens": 100,
                "stream": False,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "你好，请简单介绍一下自己"
                            }
                        ]
                    }
                ]
            }
        ) as response:
            result = await response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return response.status == 200


async def test_stream_request():
    """测试流式请求"""
    print("\n=== 测试流式请求 ===")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/v1/messages",
            json={
                "model": "gpt-3.5-turbo",
                "max_tokens": 200,
                "stream": True,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请讲一个关于猫的短故事，要求逐步输出"
                            }
                        ]
                    }
                ]
            }
        ) as response:
            print("流式响应:")
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        print("\n=== 流式响应完成 ===")
                        break
                    try:
                        parsed = json.loads(data)
                        if parsed.get('type') == 'content_block_delta':
                            delta = parsed.get('delta', {})
                            if 'text' in delta:
                                print(delta['text'], end='', flush=True)
                    except json.JSONDecodeError:
                        pass
            return True


async def test_health():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/health") as response:
            result = await response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return response.status == 200


async def main():
    """主测试函数"""
    print("=" * 50)
    print("Anthropic to OpenAI 代理服务测试")
    print("=" * 50)

    # 测试健康检查
    if not await test_health():
        print("\n❌ 健康检查失败，请确保服务正在运行")
        sys.exit(1)

    # 测试普通请求
    success = await test_normal_request()
    if not success:
        print("\n❌ 普通请求测试失败")

    # 测试流式请求
    success = await test_stream_request()
    if not success:
        print("\n❌ 流式请求测试失败")

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试出错: {e}")
        sys.exit(1)
