#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/8/18 22:52
# @Author  : afish
# @File    : test02.py
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import StreamableHTTPClient  # 如果服务为 HTTP 形式

async def main():
    client = StreamableHTTPClient("http://localhost:8931/mcp")
    print("→ 客户端准备已启动")

    async with ClientSession(client=client) as session:
        print("→ 与 MCP 服务建立链接...")
        try:
            await session.initialize()
            print("√ initialize() 成功")
        except Exception as e:
            print("❌ 初始化失败:", e)
            return

        try:
            tools = await session.list_tools()
            print("√ list_tools 成功，获取工具列表：", tools)
        except Exception as e:
            print("❌ list_tools 异常:", e)
            return

        tool_name = tools[0].name if tools else None
        if not tool_name:
            print("没有获取到可调用的工具")
            return

        print(f"→ 调用工具: {tool_name}")
        try:
            result = await session.call_tool(tool_name, arguments={})
            print("√ 调用成功，结果:", result)
        except Exception as e:
            print("❌ 调用工具失败:", e)

if __name__ == "__main__":
    asyncio.run(main())
