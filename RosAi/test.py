import asyncio

from aiframework.core.mcp.client import MCPClient
async def main():
    client = MCPClient("test-client", "http://localhost:8931")
    await client.connect()
    await client.initialize()
    print("工具列表：", client.list_tools())
    await client.disconnect()

asyncio.run(main())
