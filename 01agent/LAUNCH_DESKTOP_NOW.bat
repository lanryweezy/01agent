@echo off
echo ========================================
echo    🖥️ Launching 01Agent Desktop App
echo ========================================
echo.

echo Starting your professional desktop application...
echo.

cd desktop

echo Step 1: Starting React Development Server
echo ========================================
start "01Agent React Server" cmd /k "echo 🔧 React Development Server && echo. && echo Starting on http://localhost:6763 && echo This powers your desktop app UI && echo. && cd 01agent-app && npm start"

echo Waiting for React server to start...
timeout /t 8 /nobreak >nul

echo.
echo Step 2: Launching Electron Desktop Window
echo ========================================
echo 🖥️ Opening native desktop application...
echo.

start "01Agent Desktop" cmd /k "echo 🖥️01Agent Desktop Application && echo. && echo Native desktop window opening... && echo This is your professional AI agent interface && echo. && electron ."

cd ..

echo.
echo ========================================
echo 🎉 Desktop App Launched!
echo ========================================
echo.
echo Your 01Agent desktop app should now be running:
echo.
echo 🖥️ DESKTOP WINDOW: Native Electron application
echo 🔧 REACT SERVER: http://localhost:6763
echo 🔗 BACKEND API: http://localhost:8001
echo.
echo 🧪 Test your desktop app:
echo • Native window controls (minimize, maximize, close)
echo • Professional sci-fi interface
echo • Agent control panels
echo • Performance monitoring
echo • Real-time data updates
echo.
echo If the desktop window doesn't open:
echo 1. Check the Electron window for errors
echo 2. Verify React server is running
echo 3. Ensure backend API is accessible
echo.
echo ========================================
echo Ready for desktop app testing!
echo ========================================
pause