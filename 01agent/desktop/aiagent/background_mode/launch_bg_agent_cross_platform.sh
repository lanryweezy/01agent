#!/bin/bash

# This script launches a background browser automation environment
# for 01Agent on Linux and macOS.

# --- Configuration ---
# Path to your Chrome/Chromium executable.
# On Linux, it might be 'google-chrome' or 'chromium-browser'.
# On macOS, it's typically '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'.
# You might need to adjust this based on your system.
CHROME_EXECUTABLE="google-chrome-stable"

# Path to the 01Agent AI agent (main.py or compiled executable)
# Adjust this path based on your installation.
AGENT_EXECUTABLE="/agent/agent" # Assuming a compiled agent, or use python /path/to/main.py

# Display settings for Xvfb
DISPLAY_NUM=":99"
SCREEN_RESOLUTION="1280x720x24"

# Remote debugging port for Chrome
CHROME_DEBUGGING_PORT="13783"

# User data directory for Chrome profile
CHROME_USER_DATA_DIR="/tmp/01agent_chrome_profile"

# VNC server port
VNC_PORT="31583"

# noVNC listen port
NOVNC_PORT="39742"

# Path to noVNC directory
NOVNC_DIR="/agent/noVNC" # Adjust if noVNC is installed elsewhere

# --- Functions ---
cleanup() {
  echo "[*] Cleaning up background processes..."
  kill $(jobs -p) 2>/dev/null
  rm -f /tmp/bg_xvfb.pid /tmp/bg_chrome.pid /tmp/bg_vnc.pid /tmp/bg_novnc.pid
  echo "[*] Cleanup complete."
}

# Trap signals for graceful exit
trap cleanup EXIT INT TERM

# --- Main Script ---

mkdir -p "$CHROME_USER_DATA_DIR"

echo "[*] Starting Xvfb..."
# Check if Xvfb is already running on the display
if pgrep -f "Xvfb ${DISPLAY_NUM}" > /dev/null; then
  echo "[!] Xvfb already running on ${DISPLAY_NUM}. Skipping start."
else
  Xvfb "${DISPLAY_NUM}" -screen 0 "${SCREEN_RESOLUTION}" -nolisten tcp &
  echo $! > /tmp/bg_xvfb.pid
  # Wait until Xvfb is ready
  tries=0
  while ! xdpyinfo -display "${DISPLAY_NUM}" >/dev/null 2>&1; do
    sleep 0.5
    tries=$((tries + 1))
    if [ "$tries" -gt 20 ]; then
      echo "❌ Xvfb failed to start."
      cleanup
      exit 1
    fi
  done
fi

export DISPLAY="${DISPLAY_NUM}"
unset WAYLAND_DISPLAY # Ensure Wayland doesn't interfere on Linux

echo "[*] Clearing previous Chrome session files..."
rm -f "${CHROME_USER_DATA_DIR}/Default/Last"* "${CHROME_USER_DATA_DIR}/Default/Sessions"/*

echo "[*] Launching Chrome with persistent profile and remote debugging..."
"${CHROME_EXECUTABLE}" \
  --no-sandbox \
  --test-type \
  --disable-gpu \
  --disable-accelerated-2d-canvas \
  --force-device-scale-factor=1 \
  --remote-debugging-port="${CHROME_DEBUGGING_PORT}" \
  --user-data-dir="${CHROME_USER_DATA_DIR}" \
  --no-first-run \
  --restore-last-session=false \
  --disable-session-crashed-bubble \
  --disable-features=TranslateUI \
  --disable-default-apps \
  --disable-notifications \
  --window-size=1280,720 \
  https://www.google.com & # Start with a default page
echo $! > /tmp/bg_chrome.pid
export BROWSER_CDP_URL="http://127.0.0.1:${CHROME_DEBUGGING_PORT}"
sleep 2 # Give Chrome some time to start

echo "[*] Starting VNC server..."
# Check if x11vnc is already running
if pgrep -f "x11vnc -display ${DISPLAY_NUM}" > /dev/null; then
  echo "[!] x11vnc already running. Skipping start."
else
  x11vnc -display "${DISPLAY_NUM}" -rfbport "${VNC_PORT}" -xkb -noxrecord -noxdamage -noxfixes -repeat -modtweak -capslock -forever -listen localhost &
  echo $! > /tmp/bg_vnc.pid
fi
sleep 2

echo "[*] Starting noVNC..."
# Check if noVNC is already running
if pgrep -f "novnc_proxy --vnc localhost:${VNC_PORT}" > /dev/null; then
  echo "[!] noVNC already running. Skipping start."
else
  "${NOVNC_DIR}/utils/novnc_proxy" --vnc "localhost:${VNC_PORT}" --listen "${NOVNC_PORT}" &
  echo $! > /tmp/bg_novnc.pid
fi
sleep 2

echo "[*] Launching 01Agent AI agent..."
# This command will keep the script running until the agent exits
"${AGENT_EXECUTABLE}"

echo "[*] 01Agent AI agent exited. Cleaning up..."
cleanup
