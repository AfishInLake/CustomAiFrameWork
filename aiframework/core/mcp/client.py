import asyncio
import json
import threading
from contextlib import AsyncExitStack
from typing import Dict, Any, Optional, Callable, Union

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from aiframework.conf.PackageSettingsLoader import FrozenJSON
from aiframework.logger import logger


class MCPClient:
    """
    MCP客户端
    """

    def __init__(self, mcp_name: str, server_url: str):
        self.name = mcp_name
        self._server_url = server_url
        self._streams = None
        self.read_stream = None
        self.write_stream = None
        self.session_id = None
        self.session: Optional[ClientSession] = None
        self._tools = None
        self._connected = False
        self._exit_stack: Optional[AsyncExitStack] = None
        self._lock = asyncio.Lock()  # 保证 connect/initialize/disconnect 不被并发调用
        self._loop = asyncio.new_event_loop()  # 为每个客户端创建独立的事件循环
        self._thread = None  # 用于运行事件循环的线程

    def start_event_loop(self):
        """启动事件循环线程"""
        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()

    def _run_event_loop(self):
        """在新线程中运行事件循环"""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def stop_event_loop(self):
        """停止事件循环"""
        if self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def run_async(self, coro: Callable, *args, **kwargs):
        """在新线程中运行异步函数并返回结果"""
        if not self._loop.is_running():
            self.start_event_loop()

        future = asyncio.run_coroutine_threadsafe(coro(*args, **kwargs), self._loop)
        return future.result()

    async def connect(self):
        async with self._lock:
            if self._connected:
                return

            # 创建AsyncExitStack但不立即进入
            self._exit_stack = AsyncExitStack()

            try:
                # 进入AsyncExitStack上下文
                await self._exit_stack.__aenter__()

                # 添加streamablehttp_client到exit stack
                self._streams = await self._exit_stack.enter_async_context(
                    streamablehttp_client(self._server_url)
                )
                self.read_stream, self.write_stream, self.session_id = self._streams

                # 添加ClientSession到exit stack
                self.session = await self._exit_stack.enter_async_context(
                    ClientSession(self.read_stream, self.write_stream)
                )
            except Exception as e:
                logger.error(f"{self.name} connect 失败: {e}")
                await self._cleanup()
                raise

    async def initialize(self):
        async with self._lock:
            if not self.session:
                raise RuntimeError("请先调用 connect()")
            await self.session.initialize()
            self._connected = True
            self._tools = await self.session.list_tools()
            logger.info(f"{self.name} 已初始化，工具数量: {len(self._tools.tools)}")

    def list_tools(self) -> Dict[str, Any]:
        if not self._tools:
            return {}
        return {tool.name: tool for tool in self._tools.tools}

    def to_tool_list(self):
        result = []
        for tool in self._tools.tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,  # 自动提取名称
                    "description": tool.description,  # 自动提取描述
                    "parameters": tool.inputSchema.get("properties", {})
                }
            }
            result.append(openai_tool)
        return result

    async def call_tool(self, tool_name, **kwargs):
        return await self.session.call_tool(tool_name, kwargs)

    async def disconnect(self):
        async with self._lock:
            if not self._exit_stack:
                return
            try:
                # 正确退出AsyncExitStack上下文
                await self._exit_stack.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"{self.name} disconnect 异常（忽略）: {e}")
            finally:
                await self._cleanup()

    async def _cleanup(self):
        # 清理所有内部状态
        self._streams = None
        self.read_stream = None
        self.write_stream = None
        self.session_id = None
        self.session = None
        self._tools = None
        self._exit_stack = None
        self._connected = False
        logger.info(f"{self.name} 已断开连接并清理资源")


# MCPClientManager 和配置加载
def get_mcp_config(config):
    if not config:
        raise ValueError("请指定MCP配置文件路径")
    if isinstance(config, str):
        with open(config, "r") as f:
            config = json.load(f)
        return config['mcpServers']
    elif isinstance(config, FrozenJSON):
        config = config
        return config['mcpServers'].to_dict()
    else:
        raise ValueError("MCP配置文件格式错误")


class MCPClientManager:
    def __init__(self, config: Union[str, Dict]):
        self.tools = {}
        self.clients: Dict[str, MCPClient] = {}
        self.config: Dict = get_mcp_config(config)
        self.tool_server_mapping = {}
        self._loop = asyncio.new_event_loop()  # 主事件循环
        self._thread = None  # 用于运行主事件循环的线程
        self.connect_all()

    def start(self):
        """启动管理器的事件循环"""
        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()

    def _run_event_loop(self):
        """在新线程中运行事件循环"""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def stop(self):
        """停止管理器的事件循环"""
        if self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def run_async(self, coro: Callable, *args, **kwargs):
        """在主事件循环中运行异步函数并返回结果"""
        if not self._loop.is_running():
            self.start()

        future = asyncio.run_coroutine_threadsafe(coro(*args, **kwargs), self._loop)
        return future.result()

    def connect_all(self):
        """同步方法连接所有客户端"""
        self.run_async(self._connect_all_async)

    async def _connect_all_async(self):
        for server_name, server_config in self.config.items():
            client = MCPClient(server_name, server_config['url'])
            await client.connect()
            await client.initialize()
            self.clients[server_name] = client
        self.initialize()

    def initialize(self):
        """注册工具名称和服务名称映射表"""
        for server_name, client in self.clients.items():
            tools = client.list_tools()
            for tool_name, tool in tools.items():
                self.tool_server_mapping[tool_name] = server_name

    def disconnect_all(self):
        """同步方法断开所有客户端连接"""
        self.run_async(self._disconnect_all_async)

    async def _disconnect_all_async(self):
        # 按照后进先出顺序断开连接
        for server_name in reversed(list(self.clients.keys())):
            try:
                await self.clients[server_name].disconnect()
            except Exception as e:
                logger.error(f"断开 {server_name} 失败: {e}")
            finally:
                # 从客户端字典中移除
                if server_name in self.clients:
                    del self.clients[server_name]

    def call_tool(self, tool_name, **kwargs):
        """同步方法调用工具"""
        logger.info(f"正在调用工具 {tool_name}...")
        return self.run_async(self._call_tool_async, tool_name, **kwargs)

    async def _call_tool_async(self, tool_name, **kwargs):
        if tool_name not in self.tool_server_mapping:
            raise ValueError(f"工具 {tool_name} 未找到")
        client = self.clients[self.tool_server_mapping[tool_name]]
        result = await client.call_tool(tool_name=tool_name, **kwargs)
        return result

    def tool_list(self) -> Dict[str, str]:
        """获取所有工具列表"""
        if self.tools:
            return self.tools

        self.tools = {}
        for server_name, client in self.clients.items():
            tools = client.list_tools()
            self.tools.update({name: tool.description for name, tool in tools.items()})
        return self.tools

    def to_json(self):
        """将工具列表转换为JSON格式"""
        result = []
        for server_name, client in self.clients.items():
            tools = client.to_tool_list()
            result.extend(tools)
        return result


def main():
    manager = MCPClientManager('mcp_config.json')
    print(manager.to_json())
    result = manager.call_tool("browser_navigate", url="https://www.baidu.com/")
    result = manager.call_tool('browser_take_screenshot')
    print( result)
    # print(f"Result: {result.content}")
    manager.disconnect_all()
    manager.stop()


if __name__ == '__main__':
    main()
