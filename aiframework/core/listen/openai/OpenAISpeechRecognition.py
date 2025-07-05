#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/6/16 11:13
# @Author  : afish
# @File    : OpenAISpeechRecognition.py
import os
import tempfile
import wave
from pathlib import Path
from typing import Any

import openai
import pyaudio

from aiframework.core.listen.ListenABC import SpeechRecognition
from aiframework.logger import logger


class OpenAISpeechRecognition(SpeechRecognition):
    """
    使用 OpenAI Whisper 模型进行语音识别
    """

    def __init__(self, api_key=None, model='whisper-1', format_pcm='pcm', sample_rate=16000):
        super().__init__(api_key, model, format_pcm, sample_rate)
        self.client = openai.OpenAI(api_key=self.api_key)
        self.mic = None
        self.stream = None
        self.text = ''
        self.func = None
        self.audio_frames = []

    def _set_api_key(self, api_key: str):
        """设置 OpenAI API 密钥"""
        os.environ["OPENAI_API_KEY"] = api_key

    def start(self):
        """启动录音并发送音频到 OpenAI Whisper 进行识别"""
        logger.info('OpenAI 语音初始化中 ...')
        self._init_audio_stream()
        logger.info("开始聆听... (按 Ctrl+C 停止)")
        try:
            while self.running:
                if not self.pause_flag:
                    self._record_audio()
                elif self.audio_frames:
                    self._process_audio()
                    self.process_text_and_resume(self.func)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """停止录音并清理资源"""
        logger.info("完全停止 OpenAI 语音识别...")
        self.running = False
        self.cleanup()

    def pause(self):
        """暂停录音"""
        self.pause_flag = True
        logger.info("录音已暂停")

    def resume(self):
        """恢复录音"""
        self.pause_flag = False
        self.audio_frames.clear()
        logger.info("录音已恢复")

    def send_audio_frame(self, data: bytes):
        """添加音频帧到缓冲区"""
        self.audio_frames.append(data)

    def get_text(self) -> str:
        """获取当前识别文本"""
        return self.text

    def cleanup(self):
        """清理音频流和资源"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.mic:
            self.mic.terminate()
        self.audio_frames.clear()

    def on_result(self, result: Any):
        """处理识别结果"""
        if result and hasattr(result, 'text'):
            self.text = result.text
            logger.info(f"识别结果: {self.text}")

    def on_error(self, error: Any):
        """处理错误"""
        logger.error(f"识别出错: {error}")

    def _init_audio_stream(self):
        """初始化麦克风输入流"""
        self.mic = pyaudio.PyAudio()
        self.stream = self.mic.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=1024
        )

    def _record_audio(self):
        """持续录制音频"""
        data = self.stream.read(1024, exception_on_overflow=False)
        self.send_audio_frame(data)

    def _process_audio(self):
        """将音频保存为临时文件并调用 OpenAI Whisper"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            wf = wave.open(tmpfile.name, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.mic.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.audio_frames))
            wf.close()

            try:
                with open(tmpfile.name, "rb") as audio_file:
                    result = self.client.audio.transcriptions.create(
                        model=self.model,
                        file=audio_file
                    )
                self.on_result(result)
            except Exception as e:
                self.on_error(e)
            finally:
                Path(tmpfile.name).unlink(missing_ok=True)

    def process_text_and_resume(self, fun, *args, **kwargs):
        """处理识别到的文本并恢复监听"""
        if self.text.strip():
            logger.info(f"处理指令: {self.text}")
            fun(*args, **kwargs)
        self.resume()


if __name__ == '__main__':
    recognizer = OpenAISpeechRecognition(api_key="your_openai_api_key")


    def handle_command(command):
        print(f"执行命令: {command}")


    recognizer.func = handle_command

    try:
        recognizer.start()
    except Exception as e:
        logger.error(f"程序异常: {e}")
    finally:
        logger.info("OpenAI 语音识别已退出。")
