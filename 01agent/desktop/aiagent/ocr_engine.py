import easyocr
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class OCREngine:
    def __init__(self):
        try:
            self.reader = easyocr.Reader(['en'], gpu=True)
            logger.info("EasyOCR initialized with GPU.")
        except Exception as e:
            logger.warning(f"EasyOCR GPU init failed, falling back to CPU: {e}")
            self.reader = easyocr.Reader(['en'], gpu=False)

    def get_text_coordinates(self, image: Image):
        """Returns a list of detected text with bounding boxes."""
        try:
            # Convert PIL to numpy
            img_np = np.array(image.convert('RGB'))
            results = self.reader.readtext(img_np)

            grounding_data = []
            for (bbox, text, prob) in results:
                if prob > 0.4: # Confidence threshold
                    # bbox is [[tl_x, tl_y], [tr_x, tr_y], [br_x, br_y], [bl_x, bl_y]]
                    tl, tr, br, bl = bbox
                    grounding_data.append({
                        "text": text,
                        "center": [(tl[0] + br[0]) / 2, (tl[1] + br[1]) / 2],
                        "bbox": [tl, br]
                    })
            return grounding_data
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return []

ocr_engine = OCREngine()
