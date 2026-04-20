import os
import platform
import subprocess
import logging
import time

logger = logging.getLogger(__name__)

class AppDiscovery:
    def __init__(self):
        self.system = platform.system().lower()
        self._cached_apps = []
        self._last_refresh = 0
        self._refresh_interval = 3600 # Refresh once per hour

    def get_installed_apps(self):
        """Returns a list of common application names found on the system (cached)."""
        now = time.time()
        if not self._cached_apps or (now - self._last_refresh) > self._refresh_interval:
            try:
                if self.system == "windows":
                    self._cached_apps = self._get_windows_apps()
                elif self.system == "darwin":
                    self._cached_apps = self._get_mac_apps()
                elif self.system == "linux":
                    self._cached_apps = self._get_linux_apps()
                self._cached_apps = sorted(list(set(self._cached_apps)))
                self._last_refresh = now
            except Exception as e:
                logger.error(f"App discovery error: {e}")
        return self._cached_apps

    def _get_windows_apps(self):
        apps = []
        dirs = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
            os.path.join(os.environ.get("AppData", ""), "Microsoft\\Windows\\Start Menu\\Programs"),
            os.path.join(os.environ.get("ProgramData", ""), "Microsoft\\Windows\\Start Menu\\Programs")
        ]
        for d in dirs:
            if os.path.exists(d):
                # Only look at top levels for speed
                try:
                    for item in os.listdir(d):
                        if item.endswith(".lnk") or item.endswith(".exe"):
                            apps.append(item.rsplit(".", 1)[0])
                        elif os.path.isdir(os.path.join(d, item)):
                            # One level deeper for common app folders
                            for sub in os.listdir(os.path.join(d, item)):
                                if sub.endswith(".lnk") or sub.endswith(".exe"):
                                    apps.append(sub.rsplit(".", 1)[0])
                except Exception: continue
        return apps

    def _get_mac_apps(self):
        apps = []
        dirs = ["/Applications", "/System/Applications", os.path.expanduser("~/Applications")]
        for d in dirs:
            if os.path.exists(d):
                try:
                    for item in os.listdir(d):
                        if item.endswith(".app"):
                            apps.append(item.rsplit(".app", 1)[0])
                except Exception: continue
        return apps

    def _get_linux_apps(self):
        apps = []
        dirs = ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]
        for d in dirs:
            if os.path.exists(d):
                try:
                    for f in os.listdir(d):
                        if f.endswith(".desktop"):
                            apps.append(f.rsplit(".desktop", 1)[0])
                except Exception: continue
        return apps

app_discovery = AppDiscovery()
