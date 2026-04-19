import sys
import os
import json
import base64
import time
import requests
import pyautogui
import mss
import asyncio
from io import BytesIO
from PIL import Image

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_engine import ocr_engine
from executor import executor

class SuggestorLoop:
    def __init__(self):
        self.api_url = os.getenv('01AGENT_API_URL', 'http://localhost:8001')
        self.access_token = os.getenv('01AGENT_USER_ACCESS_TOKEN')
        self.is_running = True

    def capture_screen(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

            # Resize for faster upload and processing
            img.thumbnail((1280, 720))

            buffered = BytesIO()
            img.save(buffered, format="JPEG", quality=75)
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

    async def get_suggestions(self):
        if not self.access_token:
            return None

        try:
            screenshot_b64 = self.capture_screen()
            system_state = await asyncio.to_thread(executor.get_system_state)

            # OCR context using the Base64 directly
            ocr_results = await asyncio.to_thread(ocr_engine.get_ocr_results, screenshot_b64)

            payload = {
                "screenshot_b64": screenshot_b64,
                "current_os": sys.platform,
                "current_interactive_elements": ocr_results[:50],
                "current_running_apps": system_state.get("open_windows", [])[:20]
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            # Using a thread for the blocking requests call
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None,
                lambda: requests.post(f"{self.api_url}/aiagent/suggestor", json=payload, headers=headers, timeout=30)
            )

            if response.status_code == 200:
                return response.json()
        except Exception as e:
            # Silence loop errors
            pass
        return None

    async def run(self):
        # Initial status to signal Electron it started
        print(json.dumps({"event": "status", "message": "Suggestor loop started"}), flush=True)
        while self.is_running:
            suggestions = await self.get_suggestions()
            if suggestions:
                print(json.dumps({"event": "suggestions", "data": suggestions}), flush=True)

            # Wait 30 seconds between suggestions to avoid spamming the LLM
            await asyncio.sleep(30)

if __name__ == "__main__":
    loop = SuggestorLoop()
    asyncio.run(loop.run())
