#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/6 16:57
# @Author  : afish
# @File    : Factory.py
from aiframework.infrastructure.Input import InputHandler
from aiframework.infrastructure.Input.AudioInput import AudioInputHandler
from aiframework.infrastructure.Input.ImageInput import ImageInputHandler
from aiframework.infrastructure.Input.TextInput import TextInputHandler


class InputFactory:
    @staticmethod
    def get_handler(input_type: str, **kwargs) -> InputHandler:
        if input_type == "audio":
            return AudioInputHandler(**kwargs)
        elif input_type == "image":
            return ImageInputHandler(**kwargs)
        elif input_type == "text":
            return TextInputHandler(**kwargs)
        else:
            raise ValueError(f"不支持的输入类型: {input_type}")
