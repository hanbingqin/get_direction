import speech_recognition as sr
import numpy as np
import whisper
import torch
from queue import Queue
import time

class VoiceRecognition:
    def __init__(self, model_size="tiny", language="zh", record_timeout=3, phrase_timeout=1):
        """
        初始化语音识别类

        :param model_size: Whisper模型的大小（默认是 "tiny"）
        :param language: 识别语言（默认是中文 "zh"）
        :param record_timeout: 录音超时（默认是3秒）
        :param phrase_timeout: 识别之间的超时时间（默认是1秒）
        """
        # 参数初始化
        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout
        self.phrase_time = None
        self.data_queue = Queue()
        self.transcription = ['']
        self.text_lengths = []  # 用于保存每次转录文字的长度
        self.transcription_times = []  # 用于保存每次转录的耗时

        # 语音识别相关设置
        self.recorder = sr.Recognizer()
        self.recorder.dynamic_energy_threshold = False
        self.source = sr.Microphone(sample_rate=16000)

        # 加载Whisper模型
        self.model = whisper.load_model(model_size, device="cpu")

        # 初始化音频捕获
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)

       
        print("Init ASR successfully!")

    def record_callback(self, _, audio: sr.AudioData) -> None:
        """
        语音识别回调函数，用于将录音数据放入队列
        """
        data = audio.get_raw_data()
        self.data_queue.put(data)

    def process_audio(self, transcription_queue):
        """
        处理音频数据并进行转录
        """
         # 启动后台监听
        self.recorder.listen_in_background(self.source, self.record_callback, phrase_time_limit=self.record_timeout)

        while True:
            try:
                now = time.time()
                if not self.data_queue.empty():
                    phrase_complete = False

                    if self.phrase_time and now - self.phrase_time > self.phrase_timeout:
                        phrase_complete = True

                    self.phrase_time = now

                    audio_data = b''.join(self.data_queue.queue)
                    self.data_queue.queue.clear()

                    # 将音频数据转换为浮点型数组
                    audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                    # 使用 Whisper 模型进行转录
                    print("开始转录")
                    start_time = time.time()  # 记录开始转录的时间
                    result = self.model.transcribe(audio_np, language="zh", fp16=torch.cuda.is_available(), initial_prompt="以下是普通话的句子")
                    text = result['text'].strip()
                    end_time = time.time()  # 记录转录结束的时间

                    # 计算转录的耗时
                    transcription_time = end_time - start_time
                    self.transcription_times.append(transcription_time)

                    # 打印转录结果和耗时
                    print(f"识别结果：{text}")
                    if len(text) > 0:
                        # 根据是否有暂停，决定是更新现有文字还是开始新的一行
                        transcription_queue.put(text)
                        if phrase_complete:
                            self.transcription.append(text)
                        else:
                            self.transcription[-1] = self.transcription[-1] + " " + text

                        # 统计转录文本的长度并保存在列表中
                        text_length = len(text)
                        self.text_lengths.append(text_length)

                # else:
                #     time.sleep(0.5)
            except KeyboardInterrupt:
                self.data_queue.queue.clear()
                break

        print("\n语音识别完成，最终转录结果：\n")
        print(self.transcription)

        # 输出每次转录的文字长度和耗时
        print("\n每次转录的文字长度：")
        print(self.text_lengths)
        print("\n每次转录的耗时（秒）：")
        print(self.transcription_times)

        return self.transcription

    def get_transcription(self):
        """
        获取当前转录结果
        """
        return self.transcription


# 示例代码

# 创建一个语音识别实例
# voice_recognition = VoiceRecognition()
# transcription_queue = Queue()
# voice_recognition.process_audio(transcription_queue)
