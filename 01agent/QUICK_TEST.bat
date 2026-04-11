@echo off
echo ========================================
echo    01Agent - Quick Service Test
echo ========================================
echo.

echo Testing Backend...
cd backend
start "Backend" cmd /k "uvicorn simple_main:app --host 0.0.0.0 --port 8001"
cd ..

echo.
echo Testing Frontend...
cd desktop\01agent-app
start "Frontend" cmd /k "npm start"
cd ..\..

echo.
echo ========================================
echo Services Started!
echo ========================================
echo.
echo Backend:  http://localhost:8001
echo Frontend: http://localhost:6763 (may take 30-60 seconds)
echo API Docs: http://localhost:8001/docs
echo.
echo Press any key to continue...
pause >nul