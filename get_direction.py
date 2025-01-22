import threading
import time
from voice_asrv2 import VoiceRecognition  # 假设封装了语音识别的类
from capture import WebcamCapture  # 假设封装了图像捕获的类
from vlm_inference import run_inference  # 假设封装了VLM推理的函数
from baidu_tts import BaiduTTS  # 假设封装了TTS的类

class VoiceAssistant:
    def __init__(self):
        self.voice_recognition = VoiceRecognition()  # 语音识别实例
        self.webcam_capture = WebcamCapture(self)  # 图像捕捉实例
        self.tts = BaiduTTS(
            app_id="39014101",
            api_key="Lba7nCPGulvBRPi9rhIlSo6b",
            secret_key="PDktguZiKvI5LdrM9xNx7rP5Ck2HGXBp"
        )
        self.running = True
        self.transcription = ""  # 当前识别的文本
        self.transcription_queue = Queue()  # 用于存放语音识别结果的队列

    def start_voice_recognition(self):
        """启动语音识别并实时处理语音指令"""
        self.voice_recognition.process_audio(self.transcription_queue)

    def process_recognition(self):
        """处理语音识别后的文本，启动图像捕获并进行推理"""
        while self.running:
            # 如果有识别的文本
              if not self.transcription_queue.empty():
                self.transcription = self.transcription_queue.get()
                print(f"识别到的指令：{self.transcription}")
                # 如果有指令，开始进行图片捕获和推理
                self.capture_and_infer(self.transcription)

    def capture_and_infer(self, text):
        """捕获图片并进行VLM推理"""
        print("开始捕获图片...")
        image_path = self.webcam_capture.capture_photo()  # 捕获一张图片
        print(f"图片已捕获，路径：{image_path}")
        result = run_inference(text, image_path)  # 执行VLM推理
        print(f"推理结果：{result}")
        self.tts.text_to_speech(result)  # 使用TTS播报推理结果

    def stop(self):
        """停止语音识别和程序运行"""
        self.running = False
        self.voice_recognition.stop()  # 停止语音识别

def main():
    # 创建语音助手实例
    assistant = VoiceAssistant()

    voice_thread = threading.Thread(target=assistant.start_voice_recognition, daemon=True)
    voice_thread.start()

    # 启动图像捕获和推理线程
    recognition_thread = threading.Thread(target=assistant.process_recognition, daemon=True)
    recognition_thread.start()
    # 持续运行，等待任务完成
    # 持续运行，等待任务完成
    try:
        while assistant.running:
            time.sleep(1)  # 等待线程执行
    except KeyboardInterrupt:
        assistant.stop()
        voice_thread.join()
        recognition_thread.join()
        print("程序已终止。")

if __name__ == "__main__":
    main()
