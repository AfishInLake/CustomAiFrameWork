#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/3/18 15:21
# @Author  : afish
# @File    : seek.py
import json
from abc import ABC, abstractmethod
from typing import Any

from openai.types.chat import ChatCompletionMessage, ChatCompletion


class LLMClientBase(ABC):
    completion = None

    @abstractmethod
    def set(self, api_key: str, baseurl: str, mcp: Any, *args, **kwargs):
        raise ValueError("未提供大模型接口")

    @abstractmethod
    def set_system_message(self):
        pass

    @abstractmethod
    def get_response(self) -> ChatCompletion:
        pass

    @abstractmethod
    def get_function_name(self, function_name) -> str or None:
        pass

    @abstractmethod
    def get_arguments(self, function) -> json or None:
        pass

    @abstractmethod
    def get_message(self) -> ChatCompletionMessage:
        pass

    @abstractmethod
    def response(self, user_prompt: str):
        pass
