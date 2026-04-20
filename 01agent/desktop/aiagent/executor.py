import logging, time, os, subprocess, pyautogui, pyperclip, platform, webbrowser, ctypes, pyttsx3, threading, json, psutil, mss
try: import pywinctl as pwc
except ImportError: pwc = None

logger = logging.getLogger(__name__)

# Performance Toggles
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.005 # Near-zero delay

class NativeExecutor:
    """High-performance native input injection."""
    def __init__(self):
        self.system = platform.system().lower()
        self._monitors = mss.mss().monitors
        self._setup_native_bindings()
        try:
            self._tts_engine = pyttsx3.init()
            self._tts_engine.setProperty('rate', 160)
        except Exception:
            self._tts_engine = None

    def _setup_native_bindings(self):
        if self.system == "windows":
            self.user32 = ctypes.windll.user32
            # Structures for SendInput (Direct bypass of high-level libs)
            self.MOUSEEVENTF_MOVE = 0x0001
            self.MOUSEEVENTF_ABSOLUTE = 0x8000
            self.MOUSEEVENTF_LEFTDOWN = 0x0002
            self.MOUSEEVENTF_LEFTUP = 0x0004

    def _map_coords(self, x, y):
        # We assume monitor 1 (index 1 in mss) is the target display
        monitor = self._monitors[1] if len(self._monitors) > 1 else self._monitors[0]
        mx = int((x / 1280.0) * monitor['width']) + monitor['left']
        my = int((y / 720.0) * monitor['height']) + monitor['top']
        return mx, my

    def warp_mouse(self, x, y):
        """Move cursor without clicking (speculative warping)."""
        mx, my = self._map_coords(x, y)
        if self.system == "windows":
            nx = int(mx * 65535 / self.user32.GetSystemMetrics(0))
            ny = int(my * 65535 / self.user32.GetSystemMetrics(1))
            self.user32.mouse_event(self.MOUSEEVENTF_MOVE | self.MOUSEEVENTF_ABSOLUTE, nx, ny, 0, 0)
        else:
            pyautogui.moveTo(mx, my, duration=0)

    def execute_actions(self, actions):
        results = []
        for action_obj in actions:
            act = action_obj.get("action")
            params = action_obj.get("params", {})
            res = {"action": act, "status": "success"}
            try:
                if act == "mouse_move":
                    mx, my = self._map_coords(params.get("x"), params.get("y"))
                    if self.system == "windows":
                        # Turbo Move: 65535 is the internal coordinate system for MOUSEEVENTF_ABSOLUTE
                        nx = int(mx * 65535 / self.user32.GetSystemMetrics(0))
                        ny = int(my * 65535 / self.user32.GetSystemMetrics(1))
                        self.user32.mouse_event(self.MOUSEEVENTF_MOVE | self.MOUSEEVENTF_ABSOLUTE, nx, ny, 0, 0)
                    else:
                        pyautogui.moveTo(mx, my, duration=0)
                elif act == "left_click":
                    mx, my = self._map_coords(params.get("x"), params.get("y"))
                    if self.system == "windows":
                        # Turbo Click
                        nx = int(mx * 65535 / self.user32.GetSystemMetrics(0))
                        ny = int(my * 65535 / self.user32.GetSystemMetrics(1))
                        self.user32.mouse_event(self.MOUSEEVENTF_MOVE | self.MOUSEEVENTF_ABSOLUTE, nx, ny, 0, 0)
                        self.user32.mouse_event(self.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                        time.sleep(0.01)
                        self.user32.mouse_event(self.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    else:
                        pyautogui.click(mx, my, button='left')
                elif act == "type":
                    if params.get("replace"):
                        mod = 'command' if self.system == "darwin" else 'ctrl'
                        pyautogui.hotkey(mod, 'a'); pyautogui.press('backspace')
                    pyautogui.write(params.get("text", ""), interval=0.001)
                elif act == "key_combo":
                    pyautogui.hotkey(*(params.get("keys", [])))
                elif act == "scroll":
                    amt = params.get("scroll_amount", 3)
                    pyautogui.scroll(-amt * 100 if params.get("scroll_direction") == "down" else amt * 100)
                elif act == "shell_execute":
                    p = subprocess.run(params.get("command"), shell=True, capture_output=True, text=True, timeout=30)
                    res["data"] = {"stdout": p.stdout, "stderr": p.stderr, "returncode": p.returncode}
                elif act == "focus_app":
                    self._focus_window(params.get("app_name"))
                elif act == "speak":
                    text = params.get("text")
                    if text and self._tts_engine: threading.Thread(target=self._speak, args=(text,), daemon=True).start()
            except Exception as e:
                res["status"] = "failed"; res["error"] = str(e)
            results.append(res)
        return results

    def _speak(self, text):
        try: self._tts_engine.say(text); self._tts_engine.runAndWait()
        except Exception: pass

    def _focus_window(self, name):
        if not pwc: return
        win = None
        for w in pwc.getAllWindows():
            if name.lower() in w.title.lower(): win = w; break
        if win:
            try:
                if self.system == "darwin": subprocess.run(['osascript', '-e', f'tell application "{name}" to activate'])
                else: win.activate()
            except Exception: pass

    def get_system_state(self):
        state = {"active_window": "", "open_windows": [], "clipboard": "", "monitors": [], "os": self.system}
        try: state["clipboard"] = pyperclip.paste()[:500]
        except Exception: pass
        for i, m in enumerate(self._monitors):
            state["monitors"].append({"id": i, "w": m["width"], "h": m["height"], "l": m["left"], "t": m["top"]})
        if pwc:
            try:
                active = pwc.getActiveWindow()
                state["active_window"] = active.title if active else ""
                state["open_windows"] = [w.title for w in pwc.getAllWindows() if w.title]
            except Exception: pass
        return state

executor = NativeExecutor()
