import sys
import os
import json
import base64
import time
import requests
import pyautogui
import mss
from io import BytesIO
from PIL import Image

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_engine import ocr_engine
from executor import executor

def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        # Resize for faster upload and processing
        img.thumbnail((1280, 720))

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

def get_suggestions():
    api_url = os.getenv('01AGENT_API_URL', 'http://localhost:8001')
    access_token = os.getenv('01AGENT_USER_ACCESS_TOKEN')

    if not access_token:
        return None

    try:
        screenshot_b64 = capture_screen()
        system_state = executor.get_system_state()

        # Rough OCR for better context
        ocr_results = ocr_engine.get_ocr_results(screenshot_b64)

        payload = {
            "screenshot_b64": screenshot_b64,
            "current_os": sys.platform,
            "current_interactive_elements": ocr_results[:50], # Limit to avoid huge payload
            "current_running_apps": system_state.get("open_windows", [])[:20]
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(f"{api_url}/aiagent/suggestor", json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        # Don't crash the background suggestor loop
        pass

    return None

if __name__ == "__main__":
    # If run directly, output one set of suggestions
    suggestions = get_suggestions()
    if suggestions:
        print(json.dumps({"event": "suggestions", "data": suggestions}))
    else:
        print(json.dumps({"event": "error", "message": "Could not get suggestions"}))
