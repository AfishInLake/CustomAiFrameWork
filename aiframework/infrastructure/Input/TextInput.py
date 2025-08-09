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
        return input("请输入指令: ").strip()

    def process(self) -> str:
        return self.read_input()
