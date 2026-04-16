import mss
import numpy as np
import cv2
import base64
from typing import Tuple, Optional
import time

class FastCapture:
    def __init__(self):
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]

    def capture_fast(self, quality: int = 75) -> Tuple[np.ndarray, str]:
        """High-speed capture and JPEG encoding using OpenCV."""
        start = time.time()
        # Grab screen data directly into numpy array
        sct_img = self.sct.grab(self.monitor)
        img = np.array(sct_img)

        # Drop Alpha channel and convert BGRA to RGB (OpenCV uses BGR)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # Resize using INTER_AREA for best quality/speed balance
        img_resized = cv2.resize(img, (1280, 720), interpolation=cv2.INTER_AREA)

        # Turbo-charge encoding
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        result, encimg = cv2.imencode('.jpg', img_resized, encode_param)

        b64_str = base64.b64encode(encimg).decode('utf-8')

        # print(f"Fast Capture Latency: {(time.time() - start)*1000:.2f}ms")
        return img_resized, b64_str

fast_capture = FastCapture()
