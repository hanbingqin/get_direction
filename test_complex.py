import time
import threading
import logging
import os
from picamera2 import Picamera2
from zhipuai import ZhipuAI
from complex_recognition import ComplexRecognition
from voice_helper import VoiceHelper

# 假设 ComplexRecognition 已经在另一个文件中定义并导入
# from your_module import ComplexRecognition

def test_periodic_capture(api_key):
    # 初始化摄像头和识别系统
    picam2 = Picamera2()  # 使用 PiCamera2 作为摄像头
    picam2.start()
    voice_assistant = VoiceHelper()

    complex_recognition = ComplexRecognition(voice_assistant, api_key=api_key)


    # 创建并启动周期性识别线程
    capture_thread = threading.Thread(target=complex_recognition.periodic_capture, args=(picam2,))
    capture_thread.daemon = True  # 设置为守护线程，主线程退出时自动退出
    capture_thread.start()

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
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    
    # 使用你自己的 API 密钥进行测试
    api_key = "b7e88901786f46cca64c3629b37caee9.azmT0tAvhVrOzSNe"  # 请替换为实际的 API Key

    # 运行测试
    test_periodic_capture(api_key)
