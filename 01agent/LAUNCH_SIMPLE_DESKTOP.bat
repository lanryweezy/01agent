@echo off
echo ========================================
echo    🖥️ 01Agent Simple Desktop Launch
echo ========================================
echo.

echo Starting your desktop app with simplified configuration...
echo This bypasses complex features to ensure basic functionality works
echo.

cd desktop

echo Step 1: Starting React Development Server
echo ========================================
start "01Agent React Server" cmd /k "echo 🔧 React Development Server && echo. && echo Starting on http://localhost:6763 && echo This powers your desktop app UI && echo Press Ctrl+C to stop && echo. && cd 01agent-app && npm start"

echo Waiting for React server to start...
timeout /t 10 /nobreak >nul

echo.
echo Step 2: Launching Simple Electron Desktop Window
echo ========================================
echo 🖥️ Opening simplified desktop application...
echo Using main.simple.js to avoid complex features
echo.

REM Use the simplified main file
start "01Agent Simple Desktop" cmd /k "echo 🖥️ 01Agent Simple Desktop Application && echo. && echo Native desktop window opening... && echo Using simplified configuration && echo Press Ctrl+C to stop desktop app && echo. && npx electron main.simple.js"

cd ..

echo.
echo ========================================
echo 🎉 Simple Desktop App Launched!
echo ========================================
echo.
echo Your simplified 01Agent desktop app should now be running:
echo.
echo 🖥️ DESKTOP WINDOW: Native Electron application (simplified)
echo 🔧 REACT SERVER: http://localhost:6763
echo 🔗 BACKEND API: http://localhost:8001
echo.
echo 🧪 Test your desktop app:
echo • Native window should open without errors
echo • Professional interface loads
echo • Basic navigation works
echo • No complex features (WSL, background mode, etc.)
echo.
echo This simplified version focuses on core desktop functionality:
echo • Native desktop window
echo • React UI integration
echo • Basic agent controls
echo • Performance monitoring
echo • Clean, professional interface
echo.
echo ========================================
echo Simplified desktop app ready for testing!
echo ========================================
pause