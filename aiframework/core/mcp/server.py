#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/9/4 20:30
# @Author  : afish
# @File    : server.py
from typing import Dict, Any, List, Optional

from aiframework.logger import logger

from aiframework.core.mcp.action import ToolType, ToolInfo
from aiframework.utils.decorate import singleton


# 服务端工具实现
class MCPServer:
    """MCP 服务器实现示例"""

    def __init__(self):
        self.tools = {}

    async def start(self):
        """启动服务器"""
        logger.info("MCP 服务器启动中...")
        # 这里实现服务器启动逻辑
        # 可以是 Stdio、SSE 或 HTTP 服务器

    async def stop(self):
        """停止服务器"""
        logger.info("MCP 服务器停止中...")
        # 这里实现服务器停止逻辑

    def register_tool(self, name: str, func: callable, description: str = None):
        """注册工具"""
        self.tools[name] = {
            "func": func,
            "description": description or f"Tool: {name}"
        }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求"""
        tool_name = request.get("tool")
        arguments = request.get("arguments", {})

        if tool_name not in self.tools:
            return {"error": f"Tool not found: {tool_name}"}

        try:
            result = await self.tools[tool_name]["func"](arguments)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


@singleton
class MCPServerManager:
    """MCP 服务端管理器，负责管理本地工具"""

    def __init__(self):
        self.local_tools: Dict[str, ToolInfo] = {}
        self.tool_definitions: List[Dict[str, Any]] = []
        self.initialized = False

    async def initialize(self):
        """初始化服务端管理器"""
        if self.initialized:
            return

        try:
            # 自动发现并注册本地工具
            await self.auto_discover_tools()
            self.initialized = True
            logger.info("MCP 服务端管理器初始化完成")
        except Exception as e:
            logger.error(f"MCP 服务端管理器初始化失败: {e}")
            raise

    async def auto_discover_tools(self):
        """自动发现并注册本地工具"""
        # 这里可以扫描特定的包或模块来发现工具
        # 例如，扫描所有带有 @mcp_tool 装饰器的函数

        # 示例：手动注册一些工具
        await self.register_tool("echo", self._echo_tool, "Echo tool", {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Message to echo"
                }
            },
            "required": ["message"]
        })

        logger.info("本地工具自动发现完成")

    async def register_tool(self, name: str, executor: Any, description: str = None,
                            input_schema: Dict[str, Any] = None):
        """注册本地工具"""
        # 构建工具定义
        tool_def = {
            "type": "function",
            "function": {
                "name": name,
                "description": description or f"Local tool: {name}",
                "parameters": input_schema or {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "Input for the function"
                        }
                    },
                    "required": ["input"]
                }
            }
        }

        # 创建工具信息
        tool_info = ToolInfo(
            name=name,
            tool_type=ToolType.LOCAL_TOOL,
            definition=tool_def,
            description=description,
            executor=executor,
            input_schema=input_schema
        )

        # 存储工具信息
        self.local_tools[name] = tool_info
        self.tool_definitions.append(tool_def)

        logger.info(f"已注册本地工具: {name}")

    def get_tool(self, name: str) -> Optional[ToolInfo]:
        """获取本地工具"""
        return self.local_tools.get(name)

    def get_all_tools(self) -> Dict[str, ToolInfo]:
        """获取所有本地工具"""
        return self.local_tools

    def get_all_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取所有本地工具的定义"""
        return self.tool_definitions

    def get_all_tool_names(self) -> List[str]:
        """获取所有本地工具名称"""
        return list(self.local_tools.keys())

    async def _echo_tool(self, arguments: Dict[str, Any]) -> Any:
        """示例工具：回声工具"""
        return f"Echo: {arguments.get('message', 'No message provided')}"
