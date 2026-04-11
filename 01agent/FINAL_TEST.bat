@echo off
echo ========================================
echo    01Agent - Final Working Test
echo ========================================
echo.

echo Step 1: Starting Backend API...
cd backend
start "Backend API" cmd /k "uvicorn simple_main:app --host 0.0.0.0 --port 8001"
cd ..

echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo.
echo Step 2: Starting Frontend App...
cd desktop\01agent-app
start "Frontend App" cmd /k "npm start"
cd ..\..

echo.
echo ========================================
echo 🎉 SUCCESS! Your App is Starting!
echo ========================================
echo.
echo 🌐 Your Application URLs:
echo   Backend API:  http://localhost:8001
echo   API Docs:     http://localhost:8001/docs
echo   Frontend:     http://localhost:6763
echo.
echo ⏱️  Please wait 30-60 seconds for frontend to fully load
echo.
echo 🧪 Testing Steps:
echo   1. Open http://localhost:8001 - Should show API info
echo   2. Open http://localhost:8001/docs - Should show Swagger UI
echo   3. Open http://localhost:6763 - Should show React app
echo.
echo 🤖 To test AI Agent:
echo   cd desktop\aiagent
echo   set 01AGENT_API_URL=http://localhost:8001
echo   python main.py
echo.
echo ========================================
echo All services are starting up!
echo Check the URLs above in your browser.
echo ========================================
echo.
pause