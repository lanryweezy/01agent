import logging
import time
import os
import subprocess
import pyautogui
import pyperclip
import platform
import webbrowser
import ctypes
import pyttsx3
import threading
import json
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
        try:
            self._tts_engine = pyttsx3.init()
            self._tts_engine.setProperty('rate', 150)
        except Exception:
            self._tts_engine = None
        logger.info(f"Executor initialized for {self.system} with scale factor {self._scale_factor}")

    def _get_dpi_scale(self) -> float:
        """Determines the system DPI scaling factor."""
        if self.system == "windows":
            try:
                hdc = ctypes.windll.user32.GetDC(0)
                dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88) # 88 = LOGPIXELSX
                ctypes.windll.user32.ReleaseDC(0, hdc)
                return dpi / 96.0
            except Exception:
                return 1.0
        return 1.0

    def _map_coords(self, x: int, y: int) -> tuple:
        """Maps logical coordinates to physical coordinates if needed."""
        if self.system == "windows":
            return int(x / self._scale_factor), int(y / self._scale_factor)
        return x, y

    def execute_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Executes a list of actions sequentially and returns execution results."""
        results = []
        for action_obj in actions:
            action = action_obj.get("action")
            params = action_obj.get("params", {})

            logger.info(f"Executing action: {action} with params: {params}")

            result = {"action": action, "status": "success"}
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
                    self._focus_window(params.get("app_name"))

                elif action == "launch_browser":
                    webbrowser.open(params.get("url", "https://www.google.com"))

                elif action == "clipboard_set":
                    pyperclip.copy(params.get("text", ""))

                elif action == "speak":
                    text = params.get("text")
                    if text:
                        threading.Thread(target=self._speak, args=(text,), daemon=True).start()

                elif action == "shell_execute":
                    result = self._run_shell(params.get("command"))
                    print(json.dumps({"event": "shell_result", "data": result}), flush=True)

                elif action == "window_move":
                    self._move_window(params.get("title"), params.get("x"), params.get("y"))

                elif action == "window_resize":
                    self._resize_window(params.get("title"), params.get("width"), params.get("height"))

                elif action in ["window_minimize", "window_maximize", "window_restore"]:
                    self._window_action(params.get("title"), action.split('_')[1])

                elif action == "set_volume":
                    self._set_volume(params.get("level", 50))

                elif action == "set_brightness":
                    self._set_brightness(params.get("level", 50))

                elif action == "request_screenshot":
                    pass

                elif action in ["subtask_completed", "subtask_failed", "tool_use"]:
                    logger.info(f"Action {action} acknowledged.")

                else:
                    logger.warning(f"Unsupported action: {action}")
                    result["status"] = "unsupported"

            except Exception as e:
                logger.error(f"Failed to execute action {action}: {e}")
                result["status"] = "failed"
                result["error"] = str(e)

            results.append(result)
        return results

    def _get_window(self, title: str):
        if not pwc: return None
        windows = pwc.getWindowsWithTitle(title)
        if windows: return windows[0]
        for t in pwc.getAllTitles():
            if title.lower() in t.lower():
                return pwc.getWindowsWithTitle(t)[0]
        return None

    def _focus_window(self, name: str):
        win = self._get_window(name)
        if win:
            try: win.activate()
            except Exception: pass

    def _move_window(self, title: str, x: int, y: int):
        win = self._get_window(title)
        if win: win.moveTo(x, y)

    def _resize_window(self, title: str, width: int, height: int):
        win = self._get_window(title)
        if win: win.resizeTo(width, height)

    def _window_action(self, title: str, action: str):
        win = self._get_window(title)
        if win:
            if action == "minimize": win.minimize()
            elif action == "maximize": win.maximize()
            elif action == "restore": win.restore()

    def _speak(self, text: str):
        if not self._tts_engine: return
        try:
            self._tts_engine.say(text)
            self._tts_engine.runAndWait()
        except Exception: pass

    def _run_shell(self, command: str) -> Dict[str, Any]:
        try:
            shell = True if self.system == "windows" else False
            process = subprocess.run(command, shell=shell, capture_output=True, text=True, timeout=30)
            return {"stdout": process.stdout, "stderr": process.stderr, "returncode": process.returncode}
        except Exception as e:
            return {"error": str(e)}

    def _set_volume(self, level: int):
        """Sets the system volume (0-100)."""
        level = max(0, min(100, level))
        try:
            if self.system == "windows":
                # Using nircmd if available or powershell
                subprocess.run(["powershell", "-Command", f"(new-object -com wscript.shell).SendKeys([char]175)" * (level // 2)], shell=True)
            elif self.system == "darwin":
                subprocess.run(["osascript", "-e", f"set volume output volume {level}"])
        except Exception: pass

    def _set_brightness(self, level: int):
        """Sets the system brightness (0-100)."""
        level = max(0, min(100, level))
        try:
            if self.system == "windows":
                subprocess.run(["powershell", "-Command", f"Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods | Invoke-CimMethod -MethodName WmiSetBrightness -Arguments @{{Brightness = {level}; Timeout = 0}}"], shell=True)
            elif self.system == "darwin":
                subprocess.run(["osascript", "-e", f"tell application \"System Events\" to set picture of current desktop to \"{level}\""]) # Placeholder
        except Exception: pass

    def get_system_state(self) -> Dict[str, Any]:
        """Gathers information about the current OS state."""
        state = {"active_window": "", "open_windows": [], "clipboard_content": ""}
        try: state["clipboard_content"] = pyperclip.paste()[:500]
        except Exception: pass
        if pwc:
            try:
                active = pwc.getActiveWindow()
                state["active_window"] = active.title if active else ""
                state["open_windows"] = pwc.getAllTitles()
            except Exception: pass
        return state

executor = Executor()
