#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/6 16:51
# @Author  : afish
# @File    : AudioInput.py
from aiframework.core.listen.dashcope.listen import RealTimeSpeechRecognition
from aiframework.infrastructure.Input.InputHandler import InputHandlerBase

import time
from aiframework.core.listen.dashcope.listen import RealTimeSpeechRecognition
from aiframework.infrastructure.Input.InputHandler import InputHandlerBase


class AudioInputHandler(InputHandlerBase):
    def __init__(self, api_key: str, model: str = 'paraformer-realtime-v2'):
        self.recognizer = RealTimeSpeechRecognition(api_key=api_key, model=model)
        self.text = ""
        self.is_listening = False
        # 初始化识别器但不启动
        self.recognizer.on_result(self._on_result)
        self.recognizer.start_recognition()

    def _on_result(self, text: str):
        """识别结果回调"""
        self.text = text

    def read_input(self) -> None:
        """读取音频输入，等待语音识别结果"""
        self.text = ""
        timeout = 5  # 5秒超时
        start_time = time.time()

        # 等待识别到文本或超时
        while not self.text and (time.time() - start_time) < timeout:
            time.sleep(0.1)  # 避免过度占用CPU

    def process(self) -> str:
        """处理输入并返回识别结果"""
        self.read_input()
        return self.text

    def __del__(self):
        """析构时停止识别器"""
        if self.recognizer:
            self.recognizer.stop_recognition()
