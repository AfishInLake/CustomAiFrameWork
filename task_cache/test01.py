import asyncio
from agents.mcp import MCPServerStreamableHttp
from agents.run_context import RunContextWrapper
from agents import Agent

async def main():
    server = MCPServerStreamableHttp(
        params={
            "url": "http://localhost:8931/mcp",
        },
        cache_tools_list=False
    )
    print("MCP HTTP server client prepared.")

    run_context = RunContextWrapper(context=None)
    # 模拟一个 Agent 接入 MCP 工具
    agent = Agent(name="test-agent", instructions="Use available tools to respond")

    async with server:
        tools = await server.list_tools(run_context, agent)
        print("Available tools:", tools)

        # 如果存在工具，可以调用第一个工具（假设是 “do_something”）
        if tools:
            tool = tools[0]
            result = await server.call_tool(
                run_context,
                agent,
                tool_name=tool.name,
                arguments={}  # 根据工具定义传入合适参数
            )
            print("Tool call result:", result)

if __name__ == "__main__":
    asyncio.run(main())
