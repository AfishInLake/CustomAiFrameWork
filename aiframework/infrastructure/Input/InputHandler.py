#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/6 16:50
# @Author  : afish
# @File    : InputHandler.py
from abc import ABC, abstractmethod
from typing import Any


class InputHandlerBase(ABC):
    @abstractmethod
    def read_input(self) -> Any:
        """
        读取输入并返回原始数据。
        子类需根据输入类型实现具体逻辑。
        """
        pass

    @abstractmethod
    def process(self) -> str:
        """
        处理输入并返回文本形式的输出，供下游使用。
        """
        pass
