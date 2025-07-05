#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/16 16:16
# @Author  : afish
# @File    : seek.py
import json

from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessage

from aiframework.core.seek.seek import LLMClientBase
from aiframework.logger import logger
from aiframework.message.MessageABC import MessageManagerBase
from aiframework.utils.SystemInfo import *


class DashScope(LLMClientBase):
    model_map = {
        'qwen-plus': 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    }

    def __init__(self, system_prompt: str, MessageManager: MessageManagerBase):
        self.completion = None
        self.tools = None
        self.client = None
        self.model = None
        self.message_manager = MessageManager
        self.system_prompt = system_prompt


    def _verify(self, model: str) -> str:
        if model not in self.model_map:
            raise ValueError("暂不支持此模型")
        self.model = model
        return self.model_map[model]

    def set(self, api_key: str, model: str, tool: list):
        baseurl = self._verify(model)
        self.client = OpenAI(
            api_key=api_key,
            base_url=baseurl,
        )
        self.tools = tool
        self.set_system_message()

    def set_system_message(self):
        message = self.system_prompt
        if not message:
            raise ValueError("请 在 setting 设置系统提示信息 SYSTEM_PROMPT")
        message += f"""
        你可以使用的工具有：
        {",".join([f"{tool['function']['name']}: {tool['function']['description']}" for tool in self.tools.tools])}
        当前系统信息:
        {detect_and_get_system_info()}
        """
        logger.info(f"系统提示信息: {message}")
        self.message_manager.add_system_message(message)

    def get_response(self) -> ChatCompletion:
        """获取返回结果"""
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=self.message_manager.messages,
            tools=self.tools.get_tools(),
            parallel_tool_calls=True,
        )
        self.completion = completion
        return completion

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
        logger.info(f"用户输入后的消息历史: {self.message_manager.messages}")

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
                function = self.tools.actions_map.get(function_name)
                if not function:
                    logger.error(f"未知工具: {function_name}")
                    continue

                try:
                    if arguments:
                        logger.info(f"工具参数: {arguments}")
                        function_output = function.perform(**arguments)
                    else:
                        function_output = function.perform()
                    logger.info(f"工具调用结果: {function_output}")

                    # 添加工具结果到历史
                    self.message_manager.add_tool_message(
                        str(function_output),
                        tool_call.id
                    )
                except Exception as e:
                    logger.error(f"工具执行失败: {e}")
                    self.message_manager.add_tool_message(
                        f"工具执行错误: {str(e)}",
                        tool_call.id
                    )

            # 获取AI对工具结果的汇总回复
            msg = self.get_message()

        # 4. 添加最终AI回复
        if msg.content:
            logger.info(f"AI回复: {msg.content}")
            print(f"AI回复: {msg.content}")
            self.message_manager.add_assistant_message(msg)
