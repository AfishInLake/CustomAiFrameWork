# 监听模块说明

## 语音识别

### SpeechRecognition 类

`SpeechRecognition` 是一个抽象基类，定义了语音识别的基本接口。具体定义如下：

- **`__init__(self, api_key=None, model='paraformer-realtime-v2', format_pcm='pcm', sample_rate=16000)`**: 初始化语音识别类，设置 API 密钥、模型、音频格式和采样率。
- **`start(self)`**: 启动语音识别服务。该方法在子类中实现。
- **`pause(self)`**: 暂停语音识别。
- **`resume(self)`**: 恢复语音识别。
- **`stop(self)`**: 完全停止语音识别。
- **`send_audio_frame(self, data)`**: 发送音频帧进行识别。
- **`cleanup(self)`**: 清理资源，关闭音频流和麦克风。

### RealTimeSpeechRecognition 类

`RealTimeSpeechRecognition` 是 `SpeechRecognition` 的子类，实现了实时语音识别功能。具体定义如下：

- **`__init__(self, api_key=None, model='paraformer-realtime-v2', format_pcm='pcm', sample_rate=16000)`**: 初始化实时语音识别类，设置 API 密钥、模型、音频格式和采样率。
- **`start(self)`**: 启动实时语音识别服务。
- **`signal_handler(self, sig, frame)`**: 信号处理函数，用于处理停止信号。
- **`get_text(self)`**: 获取识别到的文本。
- **`process_text_and_resume(self, fun, *args, **kwargs)`**: 处理识别到的文本并恢复语音识别。

#### RecognitionCallback 类

`RecognitionCallback` 是 `RealTimeSpeechRecognition` 的内部类，用于处理语音识别的回调事件。具体定义如下：

- **`on_open(self)`**: 打开麦克风和音频流。
- **`on_close(self)`**: 关闭回调。
- **`on_error(self, message)`**: 处理错误事件。
- **`on_event(self, result: RecognitionResult)`**: 处理识别结果事件。