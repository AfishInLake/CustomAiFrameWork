#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/16 10:54
# @Author  : afish
# @File    : ListenABC.py
from abc import ABC, abstractmethod
from typing import Any, Optional


class SpeechRecognition(ABC):
    """
    语音识别抽象基类，定义语音识别模块的标准接口。
    所有具体的语音识别实现都应继承此类，并实现抽象方法。
    """

    def __init__(self, api_key: Optional[str] = None, model: str = 'default',
                 sample_rate: int = 16000, language: str = 'zh-CN'):
        """
        初始化语音识别器

        :param api_key: 服务API密钥（可选）
        :param model: 识别模型（可选）
        :param sample_rate: 音频采样率（默认16000Hz）
        :param language: 识别语言（默认中文）
        """
        self.api_key = api_key
        self.model = model
        self.sample_rate = sample_rate
        self.language = language
        self.is_active = False
        self.is_paused = False

    @abstractmethod
    def start_recognition(self):
        """启动语音识别服务"""
        self.is_active = True
        self.is_paused = False

    @abstractmethod
    def stop_recognition(self):
        """停止语音识别服务"""
        self.is_active = False
        self.is_paused = False

    def pause_recognition(self):
        """暂停语音识别"""
        self.is_paused = True

    def resume_recognition(self):
        """恢复语音识别"""
        self.is_paused = False

    @abstractmethod
    def send_audio_frame(self, data: bytes):
        """发送音频帧进行识别"""
        pass

    @abstractmethod
    def get_text(self) -> str:
        """获取当前识别到的文本"""
        pass

    @abstractmethod
    def on_result(self, callback: callable):
        """设置识别结果回调函数"""
        pass

    @abstractmethod
    def on_error(self, callback: callable):
        """设置错误处理回调函数"""
        pass

    @abstractmethod
    def cleanup(self):
        """清理资源"""
        pass

    @property
    def is_running(self) -> bool:
        """检查识别服务是否正在运行"""
        return self.is_active and not self.is_paused