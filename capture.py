import os
import cv2
import time
from picamera2 import Picamera2

class WebcamCapture:
    def __init__(self,voice_assistant, camera_index=0):
        self.voice_assistant = voice_assistant
        self.camera_index = camera_index
        self.camera = None

    def start_capture(self):
       self.picam2 = Picamera2()
       self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
       self.picam2.start()

    def capture_frame(self, save_path=None):
        frame = self.picam2.capture_array()
           
        if save_path:
            cv2.imwrite(save_path, frame)
        if cv2.waitKey(1):
            return False
        return True

    def stop_capture(self):
        cv2.destroyAllWindows()

    def capture_photo(self, save_path="./captured_image.jpg"):
        self.start_capture()
        time.sleep(2)
        while True:
            if not self.capture_frame(save_path):
                break
        self.stop_capture()
        return os.path.abspath(save_path)

