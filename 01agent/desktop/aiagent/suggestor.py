import os
import platform
import requests
import ui_extraction
import mss
from io import BytesIO
from PIL import Image
import base64
import json
import logging
from datetime import datetime


# === Setup logging for better debugging ===
logging.basicConfig(
    filename="suggestion.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def take_screenshot_b64(resize_to=(1280, 720)):
    """
    Takes a screenshot of the primary monitor, resizes, and returns as Base64.
    """
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            shot = sct.grab(monitor)
            img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")

            if resize_to:
                img = img.resize(resize_to)

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            screenshot_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            logger.debug("Screenshot captured and converted to Base64 successfully.")
            return screenshot_b64

    except Exception as e:
        logger.error(f"Screenshot capture failed: {e}")
        return None


def get_suggestions():
    """
    Gathers current UI/OS context and requests AI agent suggestions.
    """
    try:
        api_url = os.getenv("01AGENT_API_URL")
        token = os.getenv("01AGENT_USER_ACCESS_TOKEN")

        if not api_url or not token:
            logger.error("API URL or User Access Token missing in environment variables.")
            return {"suggestions": [], "error": "Missing API credentials"}

        full_url = api_url.rstrip("/") + "/aiagent/suggestor"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "current_os": "MacOS" if platform.system().lower() == "darwin" else platform.system(),
            "current_interactive_elements": ui_extraction.extract_interactive_elements(),
            "current_running_apps": ui_extraction.get_running_apps(),
            "screenshot_b64": take_screenshot_b64(),
        }

        logger.debug(f"Sending payload to {full_url}: {json.dumps(payload)[:500]}...")

        response = requests.post(full_url, json=payload, headers=headers, timeout=15)

        if response.ok:
            logger.info("Suggestions retrieved successfully.")
            return response.json()

        logger.warning(f"Suggestion request failed: HTTP {response.status_code}")
        return {"suggestions": [], "error": f"HTTP {response.status_code}", "details": response.text}

    except Exception as e:
        logger.error(f"Exception in get_suggestions: {e}")
        return {"suggestions": [], "error": str(e)}


def generate_response(user_input, fun_mode=False):
    """
    Example post-processing of suggestions or user responses.
    """
    # Placeholder logic for now — could integrate suggestions here
    original_response = f"You said: {user_input}"

    if fun_mode:
        original_response += " 🎲✨"
        if "hi" in user_input.lower():
            original_response += " Hey there! Let's play a game? 😄"

    return original_response


if __name__ == "__main__":
    suggestions = get_suggestions()
    print(json.dumps(suggestions, indent=2))
