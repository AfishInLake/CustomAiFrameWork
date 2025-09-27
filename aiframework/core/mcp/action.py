#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/8/21 20:10
# @Author  : afish
# @File    : action.py
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Any


class ComponentType(Enum):
    """组件类型枚举"""
    CLIENT = "client"
    SERVER = "server"
    BOTH = "both"


class ToolType(Enum):
    """工具类型枚举"""
    LOCAL_TOOL = "local_tool"
    MCP_TOOL = "mcp_tool"
    EXTERNAL_TOOL = "external_tool"

@dataclass
class ToolInfo:
    """工具信息数据类"""
    name: str
    tool_type: ToolType
    definition: Dict[str, Any]
    description: Optional[str] = None
    server_name: Optional[str] = None
    executor: Optional[Any] = None
    input_schema: Optional[Dict[str, Any]] = None