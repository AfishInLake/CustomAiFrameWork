#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/18 12:26
# @Author  : afish
# @File    : MessageABC.py
from abc import ABC, abstractmethod

from openai.types.chat import ChatCompletionMessage

from aiframework.utils.decorate import SingletonABCMeta


class MessageManagerBase(ABC, metaclass=SingletonABCMeta):
    """消息管理机制"""

    @abstractmethod
    def add_system_message(self, content: str):
        """
        添加模型初始角色设置
        """

    @abstractmethod
    def add_user_message(self, content: str):
        """
        添加用户指令
        """

    @abstractmethod
    def add_assistant_message(self, message: ChatCompletionMessage):
        """
        添加模型message回复
        """

    @abstractmethod
    def add_tool_message(self, content: str, tool_call_id: str):
        """
        添加工具调用结果
        """

    @property
    def messages(self) -> list:
        """
        返回信息调用结果
        """
        return []
