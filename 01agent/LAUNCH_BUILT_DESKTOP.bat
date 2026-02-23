@echo off
echo ========================================
echo    🖥️ 01Agent Desktop (Built Version)
echo ========================================
echo.

echo Starting your desktop app using pre-built React files...
echo This uses the already compiled React build for faster startup
echo.

cd desktop

echo Step 1: Checking Built React App
echo ========================================
if exist "01agent-app\build\index.html" (
    echo ✅ React app build found
    echo Using pre-built React files for desktop app
) else (
    echo ❌ React build not found
    echo Building React app now...
    cd 01agent-app
    npm run build
    cd ..
)

echo.
echo Step 2: Launching Desktop App with Built Files
echo ========================================
echo 🖥️ Opening desktop application...
echo Using built React files (no dev server needed)
echo.

REM Launch Electron with the simplified main file
start "01Agent Desktop Built" cmd /k "echo 🖥️ 01Agent Desktop Application && echo. && echo Native desktop window opening... && echo Using built React files && echo Press Ctrl+C to stop desktop app && echo. && npx electron main.simple.js"

cd ..

echo.
echo ========================================
echo 🎉 Built Desktop App Launched!
echo ========================================
echo.
echo Your 01Agent desktop app should now be running:
echo.
echo 🖥️ DESKTOP WINDOW: Native Electron application
echo 📦 REACT FILES: Using pre-built static files
echo 🔗 BACKEND API: http://localhost:8001 (if running)
echo.
echo 🧪 Test your desktop app:
echo • Native window opens instantly
echo • Professional interface loads from built files
echo • No development server needed
echo • Faster startup and performance
echo.
echo Benefits of built version:
echo • ⚡ Faster loading
echo • 🎯 Production-ready
echo • 🔒 More stable
echo • 📦 Self-contained
echo.
echo If you see the desktop window, your app is working!
echo.
echo ========================================
echo Built desktop app ready!
echo ========================================
pause