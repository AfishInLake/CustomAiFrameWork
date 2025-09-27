#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/6 16:54
# @Author  : afish
# @File    : TextInput.py
from aiframework.infrastructure.Input.InputHandler import InputHandlerBase


class TextInputHandler(InputHandlerBase):
    def __init__(self, *args, **kwargs):
        pass

    def read_input(self) -> str:
        try:
            return input("请输入指令: ").strip()
        except EOFError:
            import logging
            logging.getLogger(__name__).warning("输入流意外终止")
            return ""

    def process(self) -> str:
        return self.read_input()
