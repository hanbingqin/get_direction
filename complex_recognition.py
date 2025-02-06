import time
import threading
import logging
import os
from datetime import datetime
from picamera2 import Picamera2
from zhipuai import ZhipuAI
import base64
import numpy as np
import cv2

class ComplexRecognition:
    def __init__(self,voicer, api_key, request_prompt=None, save_location='static', save_base_path='tmp'):
        # 初始化配置
        self.client = ZhipuAI(api_key=api_key)  # 初始化 ZhipuAI 客户端
        self.requestPrompt = request_prompt or '''
        你需要对图片中的场景进行客观真实的描述，目的是帮助盲人用户了解周围的环境信息。首先，你需要判断图像是室内还是室外场景。

        如果是室内场景，请描述场所，并根据左前方、右前方、正前方等方位来描述拍摄到的信息。你需要注意提供障碍物、危险物体或需要注意的地方，比如提醒用户前方有障碍物需要避开。

        如果是室外场景，重点提醒用户周围的安全，特别是行人和车辆密集的地方。你需要描述环境的动态元素，如光线、天气、以及可能的噪音或危险源。

        1. 请如实描述图片中的环境信息，确保为盲人用户提供最真实可靠的场景描述。
        2. 描述时不需要提到图片的来源或构成，例如“这是一张由多张图片拼接得到的图片”之类的内容。专注于场景内容。
        3. 请使用第二人称来描述，例如：“你的正前方”、“在你的左前方”、“在你的右前方”。
        4. 只描述图片中出现的事物，不需要加入任何额外的推测或解释。
        '''
        
        # 保存路径
        self.save_location = save_location
        self.save_base_path = save_base_path
        self.save_dir = os.path.join(save_base_path, save_location)
        self.voice_assistant = voicer
        
        # 创建文件夹路径
        os.makedirs(self.save_dir, exist_ok=True)
        time.sleep(2)

        # 设置日志
        logging.basicConfig(level=logging.INFO)

    def encode_image(self, image_path):
        while True:
            try:
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode("utf-8")
            except IOError as e:
                if e.errno != errno.EACCES:
                    raise
                time.sleep(0.1)

    def run_inference(self, text, img_path):
        with open(img_path, 'rb') as img_file:
            img_base = base64.b64encode(img_file.read()).decode('utf-8')
        
        # 创建推理请求
        response = self.client.chat.completions.create(
            model="glm-4v",  # 使用 GLM-4V 模型
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.requestPrompt},
                        {"type": "image_url", "image_url": {"url": img_base}}
                    ]
                }
            ]
        )

        result = response.choices[0].message.content
        logging.info("智谱推理结果: %s", result)
        return result

    def describe_image(self, collageFilePath):
        result = self.run_inference("", collageFilePath)
        self.voice_assistant.speak(result)
        return result

    def is_interesting(self, image, filePath):
        return True  # 简化逻辑，实际可以根据模型判断是否为“有趣”场景

    def save_image_collage(self, base64_images):
        montage = None
        for base64_frame in base64_images:
            jpg_original = base64.b64decode(base64_frame)
            jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
            frame = cv2.imdecode(jpg_as_np, flags=1)
            
            if montage is None:
                montage = frame
            else:
                montage = np.hstack((montage, frame))

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(self.save_dir, f"montage_{timestamp}.jpg")
        cv2.imwrite(file_path, montage)
        logging.info(f"Montage saved successfully. Path: {file_path}")
        return file_path

    def take_photo(self, picam2):
        try:
            timestamp = int(datetime.timestamp(datetime.now()))
            image_name = f'{timestamp}.jpg'
            current_dir = os.path.dirname(__file__)
            static_dir = os.path.join(current_dir, self.save_dir)
            filepath = os.path.join(static_dir, image_name)
            request = picam2.capture_request()
            image = request.make_image("main")
            image.save(filepath)
            request.release()
            logging.info(f"Image captured successfully. Path: {filepath}")
            return filepath, image
        except Exception as e:
            logging.error(f"Error capturing image: {e}")

    def periodic_capture(self, picam2):
        base64Frames = []
        numOfFrames = 5
        captureMode = False

        while True:
            # 拍照
            filePath, image = self.take_photo(picam2)

            # 判断图片是否有趣
            if not captureMode:
                interestingBool = self.is_interesting(image, filePath)
                if interestingBool:
                    captureMode = True
                    logging.info(f"Interesting scene detected. Processing the image at {filePath}.")
                else:
                    logging.info(f"Not an interesting scene at {filePath}.")
                    continue

            # 对有趣的图片进行处理
            base64_image = self.encode_image(filePath)
            if len(base64Frames) < numOfFrames:
                base64Frames.append(base64_image)
            else:
                captureMode = False
                collageFilePath = self.save_image_collage(base64Frames)
                
                # 使用智谱 GLM 进行图像描述
                aiResponse = self.describe_image(collageFilePath)
                descriptionText = aiResponse

                # 处理结果，生成语音或其他输出

                base64Frames = []

            time.sleep(2)
