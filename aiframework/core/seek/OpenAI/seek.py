#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/16 16:16
# @Author  : afish
# @File    : seek.py
import json
from typing import Optional

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessage

from aiframework.core.mcp.client import MCPClientManager
from aiframework.core.seek.seek import LLMClientBase
from aiframework.logger import logger
from aiframework.message.MessageABC import MessageManagerBase


class OpenAIClient(LLMClientBase):

    def __init__(self, system_prompt: str, MessageManager: MessageManagerBase):
        self.system_info = None
        self.completion = None
        self.mcp: Optional[MCPClientManager] = None
        self.client = None
        self.model = "qwen-plus-2025-09-11"
        self.message_manager = MessageManager
        self.system_prompt = system_prompt

    def set(self, api_key: str, baseurl: str, mcp: MCPClientManager, *args, **kwargs):
        # 设置默认的DashScope API URL
        if not baseurl:
            baseurl = "https://dashscope.aliyuncs.com/compatible-mode/v1"

        # 确保baseurl是有效的URL格式
        if baseurl and not baseurl.startswith(('http://', 'https://')):
            baseurl = f"https://{baseurl}"

        self.client = OpenAI(
            api_key=api_key,
            base_url=baseurl,
            **kwargs
        )
        self.mcp = mcp
        self.set_system_message()

    def set_system_message(self):
        system_message = f"""
        你可以使用的工具有：{self.mcp.tool_list() if self.mcp.tool_list() else "无可用工具"}
        当前系统信息:{self.system_info}
        """
        self.message_manager.add_system_message(system_message)

    def get_response(self) -> ChatCompletion:
        """获取返回结果"""
        # 获取工具列表
        tool_list = self.mcp.to_json()

        # 准备API调用参数
        api_params = {
            "model": self.model,
            "messages": self.message_manager.messages,
            "parallel_tool_calls": True,
        }

        # 只有当有工具时才添加tools参数
        if tool_list:
            api_params["tools"] = tool_list

        logger.info(f"调用API参数: {api_params}")

        try:
            completion = self.client.chat.completions.create(**api_params)
            self.completion = completion
            logger.info(f"API调用成功，响应: {completion}")
            return completion
        except Exception as e:
            logger.error(f"API调用失败: {e}")
            raise

    def get_function(self) -> dict or None:
        """获取函数"""
        self.get_response()
        return self.completion.choices[0].message.tool_calls

    def get_function_name(self, function) -> str or None:
        """获取函数名称"""
        return function.function.name if function else None

    def get_arguments(self, function) -> json or None:
        """获取参数"""
        return json.loads(function.function.arguments) if function else None

    def get_message(self) -> ChatCompletionMessage:
        """获取消息"""
        self.get_response()
        return self.completion.choices[0].message

    def response(self, user_prompt: str):
        """处理用户输入并确保消息流完整"""
        # 1. 添加用户消息
        self.message_manager.add_user_message(user_prompt)
        # logger.info(f"用户输入后的消息历史: {self.message_manager.messages}")

        # 2. 获取AI初始响应
        msg = self.get_message()
        if not msg:
            return

        # 3. 处理工具调用（如果有）
        while hasattr(msg, 'tool_calls') and msg.tool_calls:
            # 记录工具请求（不重复添加）
            if not any(m.get('tool_call_id') == msg.tool_calls[0].id
                       for m in self.message_manager.messages):
                self.message_manager.add_assistant_message(msg)

            # 执行所有工具调用
            for tool_call in msg.tool_calls:
                function_name = tool_call.function.name
                logger.info(str(tool_call.function.arguments))
                arguments = json.loads(tool_call.function.arguments)

                # 执行工具
                try:
                    result = self.mcp.call_tool(function_name, **arguments)
                except Exception as e:
                    result = f"执行工具时出错: {str(e)}"
                    logger.error(result)
                # 添加工具执行结果到消息历史
                self.message_manager.add_tool_message(
                    content=str(result),
                    tool_call_id=tool_call.id
                )


            # 获取下一个响应（基于工具执行结果）
            msg = self.get_message()

        # 4. 添加最终响应到消息历史
        if msg and (not hasattr(msg, 'tool_calls') or not msg.tool_calls):
            self.message_manager.add_assistant_message(msg)
            logger.info(f"AI响应: {msg.content}")
