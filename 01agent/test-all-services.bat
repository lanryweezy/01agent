@echo off
echo ========================================
echo    01Agent - Service Testing Script
echo ========================================
echo.

echo Testing Backend API...
curl -s http://localhost:8000/health > nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Backend API is running on http://localhost:8000
    echo ✓ Health check: http://localhost:8000/health
    echo ✓ API Docs: http://localhost:8000/docs
) else (
    echo ❌ Backend API is not responding
    echo   Start with: cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000
)

echo.
echo Testing Frontend...
netstat -an | findstr :3000 > nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Frontend is running on http://localhost:3000
) else (
    echo ❌ Frontend is not running
    echo   Start with: cd desktop\01agent-app && npm start
)

echo.
echo Testing AI Agent Dependencies...
cd desktop\aiagent
python -c "import main; print('✓ AI Agent dependencies are working')" 2>nul
if %errorlevel% equ 0 (
    echo ✓ AI Agent is ready to run
    echo   Start with: cd desktop\aiagent && python main.py
) else (
    echo ❌ AI Agent has dependency issues
    echo   Fix with: cd desktop\aiagent && pip install -r requirements.txt
)

cd ..\..\

echo.
echo ========================================
echo Service Status Summary
echo ========================================
echo.
echo 🌐 URLs to test:
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo.
echo 📁 Key files:
echo   Backend:  backend\simple_main.py
echo   Frontend: desktop\01agent-app\
echo   AI Agent: desktop\aiagent\main.py
echo.
echo 📖 Full guide: FINAL_TESTING_GUIDE.md
echo.
pause