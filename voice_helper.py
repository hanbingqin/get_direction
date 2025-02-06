# voice_helper.py

from baidu_tts import BaiduTTS
from voice_asrv2 import VoiceRecognition
from pydub import AudioSegment
from pydub.playback import play
import time
import threading
from time import sleep
import threading

class VoiceHelper:
    def __init__(self, model_size="tiny"):
        """
        初始化 VoiceHelper 类，集成语音识别和语音合成功能
        :param app_id: 百度 TTS API 的 App ID
        :param api_key: 百度 TTS API 的 API Key
        :param secret_key: 百度 TTS API 的 Secret Key
        :param model_size: Whisper 模型的大小（默认 "tiny"）
        """
        # 初始化 TTS 和语音识别
        self.tts = BaiduTTS(
            app_id="117214641", 
            api_key="IMI61WO3ZJkWbNDxEmA8trnP", 
            secret_key="LKsRieJPGKcrDYErYvrguHeDwZ7iMf7r"
        )
        self.lock = threading.Lock()  # 创建一个锁
        self.voice_recognition = VoiceRecognition(model_size=model_size)
        
    # # def recognize_and_respond(self):
    #     """
    #     语音识别并响应
    #     """
    #     transcription_queue = Queue()

    #     # 启动语音识别线程
    #     recognition_thread = threading.Thread(target=self.voice_recognition.process_audio, args=(transcription_queue,))
    #     recognition_thread.daemon = True
    #     recognition_thread.start()

    #     while True:
    #         try:
    #             # 获取识别到的文本
    #             if not transcription_queue.empty():
    #                 text = transcription_queue.get()
    #                 print(f"识别到的文本: {text}")

    #                 # 根据识别到的文本生成语音
    #                 response_audio = self.tts.text_to_speech(text)

    #                 # 播放语音
    #                 if response_audio:
    #                     self.play_audio(response_audio)

    #         except KeyboardInterrupt:
    #             break
    def speak(self, str):
        file_path = self.tts.text_to_speech(str)
        audio = AudioSegment.from_file(file_path)
        play(audio)
        
    def play_audio(self, file_path):
        """
        播放音频文件
        """
        with self.lock:  # 确保只有一个线程可以执行这部分代码
            audio = AudioSegment.from_file(file_path)
            play(audio)



# test  =  VoiceHelper()
# file_path = test.tts.text_to_speech("很高兴可以帮助到你")
# sleep(0.5)
# test.play_audio(file_path)