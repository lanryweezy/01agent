@echo off
echo ========================================
echo    Environment Variables Setup
echo ========================================
echo.

echo Setting up environment variables for 01Agent...
echo.

REM Set default API URL
set 01AGENT_API_URL=http://localhost:8000
echo ✓ 01AGENT_API_URL set to: %01AGENT_API_URL%

REM Prompt for Thread ID
set /p 01AGENT_THREAD_ID="Enter your Thread ID: "
if "%01AGENT_THREAD_ID%"=="" (
    set 01AGENT_THREAD_ID=default-thread-id
    echo ⚠ Using default Thread ID: %01AGENT_THREAD_ID%
) else (
    echo ✓ 01AGENT_THREAD_ID set to: %01AGENT_THREAD_ID%
)

REM Prompt for Access Token
set /p 01AGENT_USER_ACCESS_TOKEN="Enter your Access Token: "
if "%01AGENT_USER_ACCESS_TOKEN%"=="" (
    set 01AGENT_USER_ACCESS_TOKEN=default-access-token
    echo ⚠ Using default Access Token: %01AGENT_USER_ACCESS_TOKEN%
) else (
    echo ✓ 01AGENT_USER_ACCESS_TOKEN set
)

echo.
echo ========================================
echo Environment Setup Complete!
echo ========================================
echo.
echo Current settings:
echo API URL: %01AGENT_API_URL%
echo Thread ID: %01AGENT_THREAD_ID%
echo Access Token: [HIDDEN]
echo.
echo You can now run: start-all-services.bat
echo.
pause