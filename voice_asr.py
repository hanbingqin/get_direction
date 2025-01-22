import whisper
import speech_recognition as sr
import numpy as np
import torch
from queue import Queue
import time

class VoiceRecognition:
    def __init__(self, model_type="tiny", device="cpu", record_timeout=3, phrase_timeout=1):
        """
        初始化语音识别系统。
        
        :param model_type: Whisper 模型类型，默认为 "tiny"
        :param device: 使用的设备，默认为 "cpu"
        :param record_timeout: 录音超时，默认为 3 秒
        :param phrase_timeout: 语音识别超时，默认为 1 秒
        """
        self.model = whisper.load_model(model_type, device=device)
        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout
        self.phrase_time = None
        self.data_queue = Queue()
        
        # 初始化语音识别器
        self.recorder = sr.Recognizer()
        self.recorder.dynamic_energy_threshold = False
        self.source = sr.Microphone(sample_rate=16000)

    def record_callback(self, _, audio: sr.AudioData) -> None:
        """回调函数，用于接收音频数据"""
        data = audio.get_raw_data()
        self.data_queue.put(data)

    def start_recognition(self):
        """启动语音识别"""
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)
            self.recorder.listen_in_background(self.source, self.record_callback, phrase_time_limit=self.record_timeout)
        print("语音识别系统已启动，请开始讲话...")

    def process_audio(self):
        """处理音频数据并返回识别结果"""
        transcription = ['']
        while True:
            try:
                if not self.data_queue.empty():
                    now = time.time()
                    phrase_complete = False
                    if self.phrase_time and now - self.phrase_time > self.phrase_timeout:  # 1秒内没有语音输入
                        phrase_complete = True
                    self.phrase_time = now

                    audio_data = b''.join(self.data_queue.queue)
                    self.data_queue.queue.clear()
                    audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                    # 使用 Whisper 模型进行语音转文字
                    result = self.model.transcribe(audio_np, language="zh", fp16=torch.cuda.is_available(), initial_prompt="以下是普通话的句子")
                    text = result['text'].strip()

                    if phrase_complete:
                        transcription.append(text)
                    else:
                        transcription[-1] = transcription[-1] + " " + text

                    print("当前识别结果:", transcription[-1])
            except KeyboardInterrupt:
                break
            time.sleep(0.5)
        return transcription
