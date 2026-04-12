import logging
import time
import os
import subprocess
import pyautogui
import pyperclip
import platform
import webbrowser
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Configure pyautogui
pyautogui.FAILSAFE = True # Standard safety: move mouse to corner to abort

class Executor:
    """
    A high-performance, fully compliant executor for OS-level actions.
    Supports all actions defined in the AI Agent system prompts.
    """

    def __init__(self):
        self.system = platform.system().lower()
        logger.info(f"Executor initialized for {self.system}")

    def execute_actions(self, actions: List[Dict[str, Any]]):
        """Executes a list of actions sequentially."""
        for action_obj in actions:
            action = action_obj.get("action")
            params = action_obj.get("params", {})

            logger.info(f"Executing action: {action} with params: {params}")

            try:
                if action == "mouse_move":
                    pyautogui.moveTo(params.get("x"), params.get("y"))

                elif action == "left_click":
                    pyautogui.click(params.get("x"), params.get("y"), button='left')

                elif action == "double_click":
                    pyautogui.doubleClick(params.get("x"), params.get("y"))

                elif action == "triple_click":
                    pyautogui.tripleClick(params.get("x"), params.get("y"))

                elif action == "right_click":
                    pyautogui.click(params.get("x"), params.get("y"), button='right')

                elif action == "left_click_drag":
                    from_pos = params.get("from", {})
                    to_pos = params.get("to", {})
                    pyautogui.moveTo(from_pos.get("x"), from_pos.get("y"))
                    pyautogui.dragTo(to_pos.get("x"), to_pos.get("y"), button='left')

                elif action == "left_mouse_down":
                    pyautogui.mouseDown(button='left')

                elif action == "left_mouse_up":
                    pyautogui.mouseUp(button='left')

                elif action == "type":
                    text = params.get("text", "")
                    replace = params.get("replace", False)
                    if replace:
                        cmd_key = 'command' if self.system == 'darwin' else 'ctrl'
                        pyautogui.hotkey(cmd_key, 'a')
                        pyautogui.press('backspace')
                    pyautogui.write(text, interval=0.01)

                elif action == "key":
                    pyautogui.press(params.get("text"))

                elif action == "key_combo":
                    pyautogui.hotkey(*params.get("keys", []))

                elif action == "hold_key":
                    key = params.get("text")
                    duration = params.get("duration", 1.0)
                    pyautogui.keyDown(key)
                    time.sleep(duration)
                    pyautogui.keyUp(key)

                elif action == "scroll":
                    direction = params.get("scroll_direction")
                    amount = params.get("scroll_amount", 3)
                    # Note: amount/direction interpretation varies by OS in pyautogui
                    clicks = amount * 100
                    if direction == "down":
                        pyautogui.scroll(-clicks)
                    else:
                        pyautogui.scroll(clicks)

                elif action == "wait":
                    time.sleep(params.get("duration", 1.0))

                elif action == "launch_app":
                    app_name = params.get("app_name")
                    if self.system == "windows":
                        subprocess.Popen(f"start {app_name}", shell=True)
                    elif self.system == "darwin":
                        subprocess.Popen(["open", "-a", app_name])
                    else:
                        subprocess.Popen([app_name])

                elif action == "focus_app":
                    app_name = params.get("app_name")
                    logger.info(f"Focusing app: {app_name}")
                    # Basic platform-specific focus logic could go here

                elif action == "launch_browser":
                    url = params.get("url", "https://www.google.com")
                    webbrowser.open(url)

                elif action == "request_screenshot":
                    # main loop will take another screenshot anyway
                    pass

                elif action in ["subtask_completed", "subtask_failed", "tool_use"]:
                    # These are primarily handled by the backend or main loop logic
                    logger.info(f"Action {action} acknowledged.")

                else:
                    logger.warning(f"Unsupported action: {action}")

            except Exception as e:
                logger.error(f"Failed to execute action {action}: {e}")

executor = Executor()
