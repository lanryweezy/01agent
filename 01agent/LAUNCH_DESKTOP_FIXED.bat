@echo off
echo ========================================
echo    🖥️ 01Agent Desktop App (Fixed)
echo ========================================
echo.

echo Starting your professional desktop application...
echo Using npx to run Electron properly
echo.

cd desktop

echo Step 1: Starting React Development Server
echo ========================================
start "01Agent React Server" cmd /k "echo 🔧 React Development Server && echo. && echo Starting on http://localhost:6763 && echo This powers your desktop app UI && echo Press Ctrl+C to stop && echo. && cd 01agent-app && npm start"

echo Waiting for React server to start...
timeout /t 10 /nobreak >nul

echo.
echo Step 2: Launching Electron Desktop Window (Fixed)
echo ========================================
echo 🖥️ Opening native desktop application with npx...
echo.

REM Use npx to run electron from node_modules
start "01Agent Desktop" cmd /k "echo 🖥️ 01Agent Desktop Application && echo. && echo Native desktop window opening... && echo Using npx electron for proper execution && echo Press Ctrl+C to stop desktop app && echo. && npx electron ."

cd ..

echo.
echo ========================================
echo 🎉 Desktop App Launched (Fixed)!
echo ========================================
echo.
echo Your 01Agent desktop app should now be running:
echo.
echo 🖥️ DESKTOP WINDOW: Native Electron application (using npx)
echo 🔧 REACT SERVER: http://localhost:6763
echo 🔗 BACKEND API: http://localhost:8001
echo.
echo 🧪 Test your desktop app:
echo • Native window should open properly now
echo • Professional sci-fi interface
echo • Agent control panels
echo • Performance monitoring
echo • Real-time data updates
echo.
echo If issues persist:
echo 1. Check both command windows for errors
echo 2. Verify React server started on port 6763
echo 3. Ensure backend API is running on port 8001
echo 4. Try: cd desktop && npx electron . (manual launch)
echo.
echo ========================================
echo Desktop app fixed and ready!
echo ========================================
pause