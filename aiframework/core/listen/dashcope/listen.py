from __future__ import annotations

import signal
import threading
import queue
from typing import Any, Callable, Optional

import dashscope
import pyaudio
from dashscope.audio.asr import Recognition, RecognitionResult
from dashscope.common.error import InvalidParameter

from aiframework.core.listen.ListenABC import SpeechRecognition
from aiframework.logger import logger


class RealTimeSpeechRecognition(SpeechRecognition):
    """
    DashScope 实时语音识别实现
    """

    def __init__(self, api_key: str, model: str = 'paraformer-realtime-v2',
                 sample_rate: int = 16000, language: str = 'zh-CN'):
        """
        初始化实时语音识别器

        :param api_key: DashScope API密钥
        :param model: 识别模型 (默认: 'paraformer-realtime-v2')
        :param sample_rate: 音频采样率 (默认: 16000Hz)
        :param language: 识别语言 (默认: 'zh-CN')
        """
        super().__init__(api_key, model, sample_rate, language)

        # 设置API密钥
        dashscope.api_key = api_key

        # 识别组件
        self.recognition: Optional[Recognition] = None
        self.mic: Optional[pyaudio.PyAudio] = None
        self.stream: Optional[pyaudio.Stream] = None

        # 回调函数
        self._result_callback: Optional[Callable[[str], None]] = None
        self._error_callback: Optional[Callable[[str], None]] = None

        # 音频采集线程
        self._audio_thread: Optional[threading.Thread] = None
        self._audio_queue = queue.Queue()

        # 信号处理
        signal.signal(signal.SIGINT, self._signal_handler)

    def start_recognition(self):
        """启动语音识别服务"""
        if self.is_active:
            logger.warning("语音识别已启动")
            return

        logger.info('初始化语音识别服务...')

        # 创建DashScope识别器
        self.recognition = Recognition(
            model=self.model,
            format='pcm',  # DashScope实时识别只支持PCM格式
            sample_rate=self.sample_rate,
            semantic_punctuation_enabled=True,
            callback=self._create_callback()
        )

        # 启动识别服务
        try:
            self.recognition.start()
            self.is_active = True
            logger.info("DashScope语音识别已启动")

            # 启动音频采集线程
            self._audio_thread = threading.Thread(
                target=self._audio_capture_loop,
                daemon=True
            )
            self._audio_thread.start()

        except Exception as e:
            logger.error(f"启动语音识别失败: {str(e)}")
            self._handle_error(str(e))

    def stop_recognition(self):
        """停止语音识别服务"""
        if not self.is_active:
            return

        logger.info("停止语音识别服务...")

        # 停止音频采集
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                logger.error(f"关闭音频流失败: {str(e)}")

        # 停止DashScope识别
        if self.recognition:
            try:
                self.recognition.stop()
            except InvalidParameter as e:
                logger.warning(f"语音识别已停止: {str(e)}")
            except Exception as e:
                logger.error(f"停止识别失败: {str(e)}")

        # 清理资源
        if self.mic:
            try:
                self.mic.terminate()
            except Exception as e:
                logger.error(f"终止PyAudio失败: {str(e)}")

        # 重置状态
        self.is_active = False
        self.is_paused = False
        logger.info("语音识别服务已停止")

    def send_audio_frame(self, data: bytes):
        """发送音频帧进行识别"""
        if not self.is_active or self.is_paused:
            return

        if self.recognition:
            try:
                self.recognition.send_audio_frame(data)
            except Exception as e:
                logger.error(f"发送音频帧失败: {str(e)}")
                self._handle_error(str(e))

    def get_text(self) -> str:
        """获取当前识别到的文本"""
        # DashScope实时识别是异步的，无法直接获取文本
        # 应通过回调函数获取识别结果
        return ""

    def on_result(self, callback: Callable[[str], None]):
        """设置识别结果回调函数"""
        self._result_callback = callback

    def on_error(self, callback: Callable[[str], None]):
        """设置错误处理回调函数"""
        self._error_callback = callback

    def cleanup(self):
        """清理资源"""
        self.stop_recognition()

        # 确保所有资源释放
        self.recognition = None
        self.mic = None
        self.stream = None
        self._result_callback = None
        self._error_callback = None
        logger.info("语音识别资源已清理")

    def _create_callback(self) -> Any:
        """创建DashScope回调对象"""

        class RecognitionCallback:
            def __init__(self, parent: RealTimeSpeechRecognition):
                self.parent = parent

            def on_open(self):
                """识别服务打开时的回调"""
                logger.info("DashScope识别服务已连接")

                # 初始化音频输入设备
                self.parent.mic = pyaudio.PyAudio()
                self.parent.stream = self.parent.mic.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=self.parent.sample_rate,
                    input=True,
                    frames_per_buffer=3200
                )
                logger.info("麦克风已就绪")

            def on_close(self):
                """识别服务关闭时的回调"""
                logger.info("DashScope识别连接已关闭")

            def on_event(self, result: RecognitionResult):
                """识别事件回调"""
                self.parent._handle_recognition_result(result)

            def on_error(self, message):
                """错误回调"""
                self.parent._handle_error(message)

        return RecognitionCallback(self)

    def _handle_recognition_result(self, result: RecognitionResult):
        """处理识别结果"""
        if not self.is_active:
            return

        sentence = result.get_sentence()
        if 'text' in sentence and sentence['text'].strip():
            text = sentence['text']

            # 如果是句子结束，触发完整结果回调
            if RecognitionResult.is_sentence_end(sentence):
                if self._result_callback:
                    self._result_callback(text)

                # 自动暂停识别
                self.pause_recognition()
                logger.info(f"识别到完整句子: {text} (已暂停)")
            else:
                # 部分结果可用于实时显示
                logger.debug(f"部分识别结果: {text}")

    def _handle_error(self, message: str):
        """处理错误"""
        logger.error(f"语音识别错误: {message}")

        if self._error_callback:
            self._error_callback(message)

        # 错误发生时自动停止服务
        self.stop_recognition()

    def _audio_capture_loop(self):
        """音频采集循环"""
        logger.info("开始音频采集...")

        while self.is_active:
            if self.is_paused:
                # 暂停状态时休眠等待
                threading.Event().wait(0.1)
                continue

            if not self.stream:
                logger.error("音频流未初始化")
                self._handle_error("音频流未初始化")
                break

            try:
                # 从麦克风读取音频数据
                data = self.stream.read(3200, exception_on_overflow=False)
                self.send_audio_frame(data)

            except Exception as e:
                logger.error(f"音频采集错误: {str(e)}")
                self._handle_error(str(e))
                break

        logger.info("音频采集已停止")

    def _signal_handler(self, sig, frame):
        """处理中断信号"""
        logger.info('收到中断信号，准备停止语音识别...')
        self.stop_recognition()