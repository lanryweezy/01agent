import logging, time, os, subprocess, pyautogui, pyperclip, platform, webbrowser, ctypes, pyttsx3, threading, json, psutil, mss
try: import pywinctl as pwc
except ImportError: pwc = None
logger = logging.getLogger(__name__)
pyautogui.FAILSAFE = True

class Executor:
    def __init__(self):
        self.system = platform.system().lower(); self._scale_factor = self._get_dpi_scale()
        self._monitors = mss.mss().monitors
        try: self._tts_engine = pyttsx3.init(); self._tts_engine.setProperty('rate', 150)
        except Exception: self._tts_engine = None

    def _get_dpi_scale(self):
        if self.system == "windows":
            try:
                hdc = ctypes.windll.user32.GetDC(0)
                dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
                ctypes.windll.user32.ReleaseDC(0, hdc); return dpi / 96.0
            except Exception: return 1.0
        return 1.0

    def _map_coords(self, x, y):
        if self.system == "windows": return int(x / self._scale_factor), int(y / self._scale_factor)
        return x, y

    def execute_actions(self, actions):
        results = []
        for action_obj in actions:
            action = action_obj.get("action"); params = action_obj.get("params", {}); res = {"action": action, "status": "success"}
            try:
                if action == "mouse_move": x, y = self._map_coords(params.get("x"), params.get("y")); pyautogui.moveTo(x, y)
                elif action == "left_click": x, y = self._map_coords(params.get("x"), params.get("y")); pyautogui.click(x, y, button='left')
                elif action == "right_click": x, y = self._map_coords(params.get("x"), params.get("y")); pyautogui.click(x, y, button='right')
                elif action == "double_click": x, y = self._map_coords(params.get("x"), params.get("y")); pyautogui.doubleClick(x, y)
                elif action == "triple_click": x, y = self._map_coords(params.get("x"), params.get("y")); pyautogui.tripleClick(x, y)
                elif action == "left_click_drag":
                    from_x, from_y = self._map_coords(params.get("from", {}).get("x"), params.get("from", {}).get("y"))
                    to_x, to_y = self._map_coords(params.get("to", {}).get("x"), params.get("to", {}).get("y"))
                    pyautogui.moveTo(from_x, from_y)
                    pyautogui.dragTo(to_x, to_y, button='left', duration=0.5)
                elif action == "left_mouse_down": pyautogui.mouseDown(button='left')
                elif action == "left_mouse_up": pyautogui.mouseUp(button='left')
                elif action == "scroll":
                    direction = params.get("scroll_direction", "down")
                    amount = params.get("scroll_amount", 1)
                    # Amount is usually clicks in pyautogui
                    clicks = amount * 100 if direction == "up" else -amount * 100
                    x, y = params.get("x"), params.get("y")
                    if x is not None and y is not None:
                        mx, my = self._map_coords(x, y)
                        pyautogui.scroll(clicks, x=mx, y=my)
                    else:
                        pyautogui.scroll(clicks)
                elif action == "type":
                    if params.get("replace"):
                        pyautogui.hotkey('ctrl', 'a')
                        pyautogui.press('backspace')
                    pyautogui.write(params.get("text", ""), interval=0.01)
                elif action == "key": pyautogui.press(params.get("text", ""))
                elif action == "key_combo": pyautogui.hotkey(*params.get("keys", []))
                elif action == "hold_key":
                    key = params.get("text", "")
                    duration = params.get("duration", 1.0)
                    pyautogui.keyDown(key)
                    time.sleep(duration)
                    pyautogui.keyUp(key)
                elif action == "clipboard_set": pyperclip.copy(params.get("text", ""))
                elif action == "launch_browser": webbrowser.open(params.get("url", "https://www.google.com"))
                elif action == "launch_app":
                    app_name = params.get("app_name", "")
                    if self.system == "windows":
                        subprocess.Popen(f'start "" "{app_name}"', shell=True)
                    elif self.system == "darwin":
                        subprocess.Popen(f'open -a "{app_name}"', shell=True)
                    else:
                        subprocess.Popen(app_name, shell=True)
                elif action == "wait": time.sleep(params.get("duration", 1.0))
                elif action == "shell_execute":
                    cmd = params.get("command")
                    # Use shell=True for string commands on all platforms
                    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                    res["data"] = {"stdout": p.stdout, "stderr": p.stderr, "returncode": p.returncode}
                elif action == "speak":
                    text = params.get("text")
                    if text: threading.Thread(target=self._speak, args=(text,), daemon=True).start()
                elif action == "window_move": self._move_window(params.get("title"), params.get("x"), params.get("y"))
                elif action == "focus_app": self._focus_window(params.get("app_name"))
            except Exception as e: res["status"] = "failed"; res["error"] = str(e)
            results.append(res)
        return results

    def _speak(self, text):
        if self._tts_engine:
            try: self._tts_engine.say(text); self._tts_engine.runAndWait()
            except Exception: pass

    def _get_window(self, title):
        if not pwc: return None
        windows = pwc.getWindowsWithTitle(title)
        if windows: return windows[0]
        for t in pwc.getAllTitles():
            if title.lower() in t.lower(): return pwc.getWindowsWithTitle(t)[0]
        return None

    def _focus_window(self, name):
        win = self._get_window(name)
        if win:
            try: win.activate()
            except Exception: pass

    def _move_window(self, title, x, y):
        win = self._get_window(title)
        if win: win.moveTo(x, y)

    def get_system_state(self):
        state = {"active_window": "", "open_windows": [], "clipboard_content": "", "monitors": []}
        try: state["clipboard_content"] = pyperclip.paste()[:500]
        except Exception: pass

        # Monitor info
        for i, m in enumerate(self._monitors):
            state["monitors"].append({"id": i, "width": m["width"], "height": m["height"], "left": m["left"], "top": m["top"]})

        if pwc:
            try:
                active = pwc.getActiveWindow()
                state["active_window"] = active.title if active else ""
                state["open_windows"] = [w.title for w in pwc.getAllWindows() if w.title]
            except Exception: pass
        return state

executor = Executor()
