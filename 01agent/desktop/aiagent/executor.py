import logging
import time
import os
import subprocess
import pyautogui
import pyperclip
import platform
import webbrowser
import ctypes
from typing import Dict, List, Any

# Cross-platform window management
try:
    import pywinctl as pwc
except ImportError:
    pwc = None

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
        self._scale_factor = self._get_dpi_scale()
        logger.info(f"Executor initialized for {self.system} with scale factor {self._scale_factor}")

    def _get_dpi_scale(self) -> float:
        """Determines the system DPI scaling factor."""
        if self.system == "windows":
            try:
                # Get DPI of the primary monitor
                hdc = ctypes.windll.user32.GetDC(0)
                dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88) # 88 = LOGPIXELSX
                ctypes.windll.user32.ReleaseDC(0, hdc)
                return dpi / 96.0
            except Exception:
                return 1.0
        return 1.0

    def _map_coords(self, x: int, y: int) -> tuple:
        """Maps logical coordinates to physical coordinates if needed."""
        # pyautogui usually handles scaling on macOS/Linux, but Windows often needs explicit mapping
        if self.system == "windows":
            return int(x / self._scale_factor), int(y / self._scale_factor)
        return x, y

    def execute_actions(self, actions: List[Dict[str, Any]]):
        """Executes a list of actions sequentially."""
        for action_obj in actions:
            action = action_obj.get("action")
            params = action_obj.get("params", {})

            logger.info(f"Executing action: {action} with params: {params}")

            try:
                if action == "mouse_move":
                    x, y = self._map_coords(params.get("x"), params.get("y"))
                    pyautogui.moveTo(x, y)

                elif action == "left_click":
                    x, y = self._map_coords(params.get("x"), params.get("y"))
                    pyautogui.click(x, y, button='left')

                elif action == "double_click":
                    x, y = self._map_coords(params.get("x"), params.get("y"))
                    pyautogui.doubleClick(x, y)

                elif action == "triple_click":
                    x, y = self._map_coords(params.get("x"), params.get("y"))
                    pyautogui.tripleClick(x, y)

                elif action == "right_click":
                    x, y = self._map_coords(params.get("x"), params.get("y"))
                    pyautogui.click(x, y, button='right')

                elif action == "left_click_drag":
                    from_pos = params.get("from", {})
                    to_pos = params.get("to", {})
                    fx, fy = self._map_coords(from_pos.get("x"), from_pos.get("y"))
                    tx, ty = self._map_coords(to_pos.get("x"), to_pos.get("y"))
                    pyautogui.moveTo(fx, fy)
                    pyautogui.dragTo(tx, ty, button='left')

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
                    self._focus_window(app_name)

                elif action == "launch_browser":
                    url = params.get("url", "https://www.google.com")
                    webbrowser.open(url)

                elif action == "clipboard_set":
                    pyperclip.copy(params.get("text", ""))

                elif action == "request_screenshot":
                    pass

                elif action in ["subtask_completed", "subtask_failed", "tool_use"]:
                    logger.info(f"Action {action} acknowledged.")

                else:
                    logger.warning(f"Unsupported action: {action}")

            except Exception as e:
                logger.error(f"Failed to execute action {action}: {e}")

    def _focus_window(self, name: str):
        """Attempts to focus a window by its name."""
        if not pwc:
            logger.warning("pywinctl not installed, cannot focus window.")
            return

        try:
            windows = pwc.getWindowsWithTitle(name)
            if windows:
                windows[0].activate()
                logger.info(f"Focused window: {name}")
            else:
                # Try fuzzy match
                all_titles = pwc.getAllTitles()
                for title in all_titles:
                    if name.lower() in title.lower():
                        pwc.getWindowsWithTitle(title)[0].activate()
                        logger.info(f"Focused window (fuzzy): {title}")
                        return
                logger.warning(f"No window found matching: {name}")
        except Exception as e:
            logger.error(f"Error focusing window {name}: {e}")

    def get_system_state(self) -> Dict[str, Any]:
        """Gathers information about the current OS state."""
        state = {
            "active_window": "",
            "open_windows": [],
            "clipboard_content": ""
        }
        try:
            state["clipboard_content"] = pyperclip.paste()[:1000]
        except Exception:
            pass

        if pwc:
            try:
                active = pwc.getActiveWindow()
                state["active_window"] = active.title if active else ""
                state["open_windows"] = pwc.getAllTitles()
            except Exception:
                pass
        return state

executor = Executor()
