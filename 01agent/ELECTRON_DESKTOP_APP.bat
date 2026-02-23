@echo off
echo ========================================
echo    🖥️ 01Agent Electron Desktop App
echo ========================================
echo.

echo Starting your REAL desktop application...
echo.

echo Step 1: Starting Backend API...
cd backend
start "01Agent Backend" cmd /k "echo 🔧 Backend API Server && echo. && uvicorn simple_main:app --host 0.0.0.0 --port 8001"
cd ..

echo Waiting for backend...
timeout /t 3 /nobreak >nul

echo.
echo Step 2: Building React Frontend...
cd desktop\01agent-app
echo Building React app for Electron...
cmd /c "npm run build"
cd ..

echo.
echo Step 3: Starting Electron Desktop App...
echo This will open the actual desktop application window!
echo.

REM Install desktop dependencies if needed
if not exist "node_modules" (
    echo Installing Electron dependencies...
    npm install
)

echo Launching 01Agent Desktop Application...
npm start

cd ..

echo.
echo ========================================
echo 🖥️ Desktop App Launched!
echo ========================================
echo.
echo Your 01Agent desktop application should now be running as:
echo • A native desktop window (not browser)
echo • Side panel interface (like Cursor/Kiro IDE)
echo • Always-on-top overlay when agent is active
echo • Native desktop integration
echo.
pause