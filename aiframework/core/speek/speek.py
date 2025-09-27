import os
import wave
from abc import ABC, abstractmethod

import dashscope
from dashscope.audio.tts import SpeechSynthesizer, ResultCallback, SpeechSynthesisResult
from pydub import AudioSegment
from pydub.playback import play

from aiframework.logger import logger


class SpeechSynthesis(ABC):
    """
    Abstract interface for text-to-speech synthesis.
    """

    def __init__(self, api_key=None, model='sambert-zhichu-v1', sample_rate=48000, voice='zhitian'):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        self.model = model
        self.sample_rate = sample_rate
        self.voice = voice

        # Initialize OpenAI API key
        if self.api_key:
            dashscope.api_key = self.api_key
        else:
            raise ValueError("API Key is required. Set DASHSCOPE_API_KEY in environment variables or pass it manually.")

    @abstractmethod
    def synthesize(self, text, output_file="output.wav"):
        """
        Synthesize text to audio.
        """
        pass

    def play_audio(self, file_path):
        """
        Play the generated audio file.
        """

        try:
            audio = AudioSegment.from_wav(str(file_path) + r"\speek.wav")
            play(audio)
        except Exception as e:
            logger.error(f"播放音频失败: {e}")


class RealTimeSpeechSynthesis(SpeechSynthesis):
    """
    Implementation of real-time speech synthesis using OpenAI TTS.
    """

    def __init__(self, api_key=None, model='sambert-zhichu-v1', sample_rate=48000, voice='zhitian'):
        super().__init__(api_key, model, sample_rate, voice)

    class Callback(ResultCallback):
        """
        Callback class for handling synthesis events.
        """

        def __init__(self, output_file):
            self.output_file = output_file
            self.audio_frames = []  # Store audio frames

        def on_open(self):
            # print('语音合成已启动.')
            pass

        def on_complete(self):
            with wave.open(str(self.output_file) + r"\speek.wav", 'wb') as wf:
                wf.setnchannels(1)  # Mono channel
                wf.setsampwidth(2)  # 16-bit PCM
                wf.setframerate(48000)  # Sample rate
                wf.writeframes(b''.join(self.audio_frames))

        def on_error(self, response):
            logger.error(f"语音合成失败: {response}")

        def on_close(self):
            logger.info('语音合成已关闭.')

        def on_event(self, result: SpeechSynthesisResult):
            if result.get_audio_frame() is not None:
                self.audio_frames.append(result.get_audio_frame())  # Save audio frame

    def synthesize(self, text, output_file="output.wav"):
        """
        Synthesize text to audio and save it to a file.
        """
        callback = self.Callback(output_file)
        SpeechSynthesizer.call(
            model=self.model,
            text=text,
            sample_rate=self.sample_rate,
            callback=callback,
            voice=self.voice,  # Specify the voice (e.g., 'zhitian', 'zhixia')
            word_timestamp_enabled=True,
            phoneme_timestamp_enabled=True
        )


# synthesizer = RealTimeSpeechSynthesis(api_key=Config().api_key, voice="zhitian")
# Main function
if __name__ == '__main__':
    # Initialize speech synthesis with a specific voice
    synthesizer = RealTimeSpeechSynthesis(api_key="sk-a587535f4171437295dcd8fa6f3ebe6f", voice="zhitian")

    # Text to synthesize
    text_to_synthesize = "今天天气怎么样？"
    output_file = "output.wav"
    # Synthesize text to audio
    synthesizer.synthesize(text_to_synthesize, output_file)
    # Play the generated audio
    synthesizer.play_audio(output_file)
