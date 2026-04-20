import mss
import numpy as np
import cv2
import base64
from typing import Tuple, Optional, List, Dict
import time

class FastCapture:
    def __init__(self):
        self.sct = mss.mss()
        self._last_img = None

    def get_monitors(self) -> List[Dict]:
        return self.sct.monitors

    def capture_fast(self, monitor_index: int = 1, quality: int = 75, target_size: Tuple[int, int] = (1280, 720), draw_grid: bool = True) -> Tuple[np.ndarray, str, str, bool]:
        """High-speed capture with delta-check and perceptual hashing."""
        if monitor_index >= len(self.sct.monitors): monitor_index = 0
        monitor = self.sct.monitors[monitor_index]
        sct_img = self.sct.grab(monitor)
        img = np.array(sct_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # Delta Check (Static background optimization)
        is_delta = True
        if self._last_img is not None and img.shape == self._last_img.shape:
            # Quick structural similarity check
            diff = cv2.absdiff(img, self._last_img)
            if np.mean(diff) < 0.5: # Virtually identical
                is_delta = False

        self._last_img = img.copy()
        img_resized = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)

        if draw_grid: self._draw_grounding_grid(img_resized)

        # WebP encoding (if available, fallback to JPEG)
        try:
            encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), quality]
            _, encimg = cv2.imencode('.webp', img_resized, encode_param)
        except Exception:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            _, encimg = cv2.imencode('.jpg', img_resized, encode_param)

        b64_str = base64.b64encode(encimg).decode('utf-8')
        v_hash = self._get_perceptual_hash(img_resized)

        return img_resized, b64_str, v_hash, is_delta

    def _get_perceptual_hash(self, img: np.ndarray) -> str:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        small = cv2.resize(gray, (9, 8), interpolation=cv2.INTER_AREA)
        diff = small[:, 1:] > small[:, :-1]
        return str(sum([2**i for (i, v) in enumerate(diff.flatten()) if v]))

    def _draw_grounding_grid(self, img: np.ndarray):
        h, w = img.shape[:2]
        step = 100; color = (0, 255, 0); alpha = 0.2
        overlay = img.copy()
        for x in range(0, w, step):
            cv2.line(overlay, (x, 0), (x, h), color, 1)
            if x % 200 == 0: cv2.putText(overlay, str(x), (x + 5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        for y in range(0, h, step):
            cv2.line(overlay, (0, y), (w, y), color, 1)
            if y % 200 == 0: cv2.putText(overlay, str(y), (5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

fast_capture = FastCapture()
