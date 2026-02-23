@echo off
echo ========================================
echo    Enhanced AI Agent - Quick Launch
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

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update requirements
echo Installing/updating requirements...
pip install -r requirements.txt --quiet --disable-pip-version-check

REM Set environment variables if not set
if "%01AGENT_API_URL%"=="" (
    echo WARNING: 01AGENT_API_URL not set
    set /p 01AGENT_API_URL="Enter API URL (e.g., http://localhost:8000): "
)

if "%01AGENT_THREAD_ID%"=="" (
    echo WARNING: 01AGENT_THREAD_ID not set
    set /p 01AGENT_THREAD_ID="Enter Thread ID: "
)

if "%01AGENT_USER_ACCESS_TOKEN%"=="" (
    echo WARNING: 01AGENT_USER_ACCESS_TOKEN not set
    set /p 01AGENT_USER_ACCESS_TOKEN="Enter Access Token: "
)

REM Launch the enhanced agent
echo.
echo Starting Enhanced AI Agent...
echo ========================================
python main.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Agent exited with error code %errorlevel%
    pause
)

deactivate