import threading, time, queue
from fast_capture import fast_capture
from executor import executor
from ocr_engine import ocr_engine

class VisionProducer:
    """Decoupled background thread for zero-latency visual context."""
    def __init__(self):
        self.latest_ctx = None
        self.is_running = False
        self.change_event = threading.Event()
        self.lock = threading.Lock()

    def start(self):
        self.is_running = True
        threading.Thread(target=self._produce_loop, daemon=True).start()

    def _produce_loop(self):
        while self.is_running:
            try:
                # Capture frame
                img, b64, v_hash, is_delta = fast_capture.capture_fast()
                sys_info = executor.get_system_state()

                # Dynamic OCR only on visual change
                ocr_data = []
                if is_delta:
                    ocr_data = ocr_engine.get_ocr_results(img)

                with self.lock:
                    self.latest_ctx = {
                        "b64": b64,
                        "v_hash": v_hash,
                        "sys_info": sys_info,
                        "ocr": ocr_data,
                        "timestamp": time.time()
                    }

                if is_delta:
                    self.change_event.set()
                    self.change_event.clear()

                time.sleep(0.05) # ~20 FPS limit for agent vision
            except Exception:
                time.sleep(1)

    def get_latest(self):
        with self.lock: return self.latest_ctx

    def wait_for_change(self, timeout=1.0):
        return self.change_event.wait(timeout)

vision_producer = VisionProducer()
