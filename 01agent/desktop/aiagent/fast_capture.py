import mss
import numpy as np
import cv2
import base64
from typing import Tuple, Optional, List, Dict
import time

class FastCapture:
    def __init__(self):
        self.sct = mss.mss()

    def get_monitors(self) -> List[Dict]:
        """Returns metadata for all available monitors."""
        return self.sct.monitors

    def capture_fast(self, monitor_index: int = 1, quality: int = 75, target_size: Tuple[int, int] = (1280, 720)) -> Tuple[np.ndarray, str]:
        """High-speed capture of a specific monitor and JPEG encoding."""
        if monitor_index >= len(self.sct.monitors):
            monitor_index = 0 # Fallback to all-monitor capture

        monitor = self.sct.monitors[monitor_index]
        sct_img = self.sct.grab(monitor)
        img = np.array(sct_img)

        # Drop Alpha channel and convert BGRA to BGR
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # Resize using INTER_AREA for best quality/speed balance
        img_resized = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)

        # Encode
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        result, encimg = cv2.imencode('.jpg', img_resized, encode_param)

        b64_str = base64.b64encode(encimg).decode('utf-8')
        return img_resized, b64_str

fast_capture = FastCapture()
