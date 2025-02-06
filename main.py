from voice_helper import VoiceHelper
from piApi import piAPI
from my_navigator import NavigateUser
from capture import WebcamCapture
from complex_recognition import ComplexRecognition
import time
import threading
import logging
import os
voice_assistant = VoiceHelper()
pi = piAPI(voice_assistant)
navigate = NavigateUser(voice_assistant)
my_capture = WebcamCapture(voice_assistant)
voice_assistant.speak("很高兴认识你，请问有什么可以帮助你的？")
picam2 = pi.picam2
file_path = my_capture.capture_photo(picam2)
complex_recog = ComplexRecognition(voice_assistant, "b7e88901786f46cca64c3629b37caee9.azmT0tAvhVrOzSNe")
print("save_path: ", file_path)

def process1():
    complex_recog.periodic_capture(picam2)


def main():
    t1 = threading.Thread(target=process1)
    t1.start()
     # 主线程等待一段时间以便捕获和处理图片
    try:
        # 模拟运行 1 分钟，捕获并描述多个场景
        logging.info("Starting periodic capture and scene description for 1 minute...")
        time.sleep(60)  # 测试程序运行 60 秒
    except KeyboardInterrupt:
        logging.info("Test interrupted by user.")
    finally:
        # 停止摄像头
        picam2.stop()

if __name__ == "__main__":
    main()
