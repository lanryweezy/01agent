import easyocr
import numpy as np
from PIL import Image
import logging
import base64
import io
import cv2

logger = logging.getLogger(__name__)

class OCREngine:
    def __init__(self):
        try:
            self.reader = easyocr.Reader(['en'], gpu=True)
            logger.info("EasyOCR initialized with GPU.")
        except Exception as e:
            logger.warning(f"EasyOCR GPU init failed, falling back to CPU: {e}")
            try:
                self.reader = easyocr.Reader(['en'], gpu=False)
            except Exception:
                logger.error("EasyOCR initialization failed completely.")
                self.reader = None

    def get_text_coordinates(self, image_input, limit=50, crop_box=None):
        """Returns a list of detected text with bounding boxes. Supports PIL, Base64, or Numpy."""
        if not self.reader: return []
        try:
            if isinstance(image_input, str):
                if "," in image_input: image_input = image_input.split(",")[1]
                image_bytes = base64.b64decode(image_input)
                image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
                img_np = np.array(image)
            elif isinstance(image_input, np.ndarray):
                if len(image_input.shape) == 3 and image_input.shape[2] == 3:
                    img_np = cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB)
                else:
                    img_np = image_input
            elif isinstance(image_input, Image.Image):
                img_np = np.array(image_input.convert('RGB'))
            else:
                return []

            # Focused OCR: Crop to active window if provided
            offset_x, offset_y = 0, 0
            if crop_box:
                x, y, w, h = crop_box
                img_np = img_np[y:y+h, x:x+w]
                offset_x, offset_y = x, y

            results = self.reader.readtext(img_np)
            grounding_data = []
            for (bbox, text, prob) in results:
                if prob > 0.4:
                    tl, tr, br, bl = bbox
                    grounding_data.append({
                        "text": text,
                        "center": [(tl[0] + br[0]) / 2 + offset_x, (tl[1] + br[1]) / 2 + offset_y],
                        "bbox": [[tl[0] + offset_x, tl[1] + offset_y], [br[0] + offset_x, br[1] + offset_y]]
                    })

            grounding_data.sort(key=lambda x: x.get('prob', 1.0), reverse=True)
            return grounding_data[:limit]
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return []

    def get_ocr_results(self, image_input):
        return self.get_text_coordinates(image_input)

ocr_engine = OCREngine()
