@echo off
echo ========================================
echo    🚀 01Agent Desktop App Launcher
echo ========================================
echo.

echo Starting your complete AI Agent desktop application...
echo.

echo Step 1: Starting Backend API...
cd backend
start "01Agent Backend" cmd /k "echo 🔧 Backend API Server && echo. && echo Starting on http://localhost:8001 && echo. && uvicorn simple_main:app --host 0.0.0.0 --port 8001"
cd ..

echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo.
echo Step 2: Starting Interactive Desktop App...
cd desktop\01agent-app
start "01Agent Desktop App" cmd /k "echo 💻 Interactive Desktop Application && echo. && echo Starting on http://localhost:6763 && echo. && echo This is your main interface to control the AI agent && echo. && npm start"
cd ..\..

echo.
echo ========================================
echo 🎉 Your 01Agent Desktop App is Starting!
echo ========================================
echo.
echo 🌐 Open these URLs in your browser:
echo.
echo   💻 MAIN APP:     http://localhost:6763
echo   🔧 Backend API:  http://localhost:8001
echo   📚 API Docs:     http://localhost:8001/docs
echo.
echo ⏱️  Please wait 30-60 seconds for the app to fully load
echo.
echo 🎯 What you'll see:
echo   • Modern React interface with sidebar navigation
echo   • Agent control dashboard
echo   • Performance monitoring
echo   • Task management
echo   • Settings and configuration
echo.
echo 🤖 To start the AI Agent:
echo   cd desktop\aiagent
echo   set 01AGENT_API_URL=http://localhost:8001
echo   python main.py
echo.
echo ========================================
echo Your interactive desktop app is loading!
echo Open http://localhost:6763 in your browser
echo ========================================
echo.
pause