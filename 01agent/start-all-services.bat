@echo off
echo ========================================
echo    01Agent - Complete System Startup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16 or higher
    pause
    exit /b 1
)

echo ========================================
echo Step 1: Setting up Backend
echo ========================================

cd backend

REM Create virtual environment for backend if it doesn't exist
if not exist "venv\Scripts\activate.bat" (
    echo Creating backend virtual environment...
    python -m venv venv
)

REM Activate backend virtual environment
call venv\Scripts\activate.bat

REM Install backend dependencies
echo Installing backend dependencies...
pip install -r requirements.txt --quiet

REM Start backend in background
echo Starting backend server...
start "Backend Server" cmd /k "uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

cd ..

echo ========================================
echo Step 2: Setting up Frontend
echo ========================================

cd desktop\01agent-app

REM Install frontend dependencies
echo Installing frontend dependencies...
npm install --silent

REM Start frontend in background
echo Starting frontend application...
start "Frontend App" cmd /k "npm start"

REM Wait a moment for frontend to start
timeout /t 5 /nobreak >nul

cd ..\..

echo ========================================
echo Step 3: Setting up AI Agent
echo ========================================

cd desktop\aiagent

REM Create virtual environment for agent if it doesn't exist
if not exist "venv\Scripts\activate.bat" (
    echo Creating agent virtual environment...
    python -m venv venv
)

REM Activate agent virtual environment
call venv\Scripts\activate.bat

REM Install agent dependencies
echo Installing agent dependencies...
pip install -r requirements.txt --quiet

REM Check environment variables
if "%01AGENT_API_URL%"=="" (
    echo Setting default API URL...
    set 01AGENT_API_URL=http://localhost:8000
)

if "%01AGENT_THREAD_ID%"=="" (
    echo WARNING: 01AGENT_THREAD_ID not set
    set /p 01AGENT_THREAD_ID="Enter Thread ID (or press Enter to skip): "
)

if "%01AGENT_USER_ACCESS_TOKEN%"=="" (
    echo WARNING: 01AGENT_USER_ACCESS_TOKEN not set
    set /p 01AGENT_USER_ACCESS_TOKEN="Enter Access Token (or press Enter to skip): "
)

echo ========================================
echo All Services Status
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to start the AI Agent...
pause >nul

REM Start AI Agent
echo Starting AI Agent...
python main.py

echo.
echo ========================================
echo Startup Complete!
echo ========================================
echo.
echo Services running:
echo - Backend API: http://localhost:8000
echo - Frontend UI: http://localhost:3000
echo - AI Agent: Active
echo.
pause