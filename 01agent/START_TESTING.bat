@echo off
echo ========================================
echo    01Agent - Complete Testing Guide
echo ========================================
echo.

echo Step 1: Testing Backend API
echo ========================================
echo Starting simple backend on port 8001...
echo.

start "Backend API" cmd /k "cd backend && uvicorn simple_main:app --host 0.0.0.0 --port 8001"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Step 2: Testing Frontend
echo ========================================
echo Starting React frontend on port 6763...
echo.

start "Frontend App" cmd /k "cd desktop\01agent-app && npm start"

echo Waiting for frontend to start...
timeout /t 10 /nobreak >nul

echo.
echo Step 3: Testing AI Agent
echo ========================================
echo Setting up AI Agent environment...
echo.

cd desktop\aiagent

REM Set environment variables
set 01AGENT_API_URL=http://localhost:8001
set 01AGENT_THREAD_ID=test-thread-123
set 01AGENT_USER_ACCESS_TOKEN=test-token-456

echo Environment variables set:
echo   API_URL: %01AGENT_API_URL%
echo   THREAD_ID: %01AGENT_THREAD_ID%
echo   ACCESS_TOKEN: %01AGENT_USER_ACCESS_TOKEN%

echo.
echo ========================================
echo All Services Starting!
echo ========================================
echo.
echo 🌐 URLs to test:
echo   Backend API:  http://localhost:8001
echo   API Docs:     http://localhost:8001/docs
echo   Frontend:     http://localhost:6763
echo.
echo 📝 Next Steps:
echo   1. Wait 30 seconds for all services to fully load
echo   2. Open your browser and test the URLs above
echo   3. Check that backend shows API info
echo   4. Check that frontend loads without errors
echo   5. Run AI Agent manually: python main.py
echo.
echo Press any key to start AI Agent or Ctrl+C to exit...
pause >nul

echo.
echo Starting AI Agent...
python main.py

cd ..\..

echo.
echo ========================================
echo Testing Complete!
echo ========================================
pause