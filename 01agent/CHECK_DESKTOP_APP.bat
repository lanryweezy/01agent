@echo off
echo ========================================
echo    🔍 01Agent Desktop App Status Check
echo ========================================
echo.

echo Checking if your desktop app is running...
echo.

REM Check if backend is running
echo 🔧 Backend API Status:
curl -s http://localhost:8001 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend is running on http://localhost:8001
) else (
    echo ❌ Backend is not running
    echo    Start with: cd backend && uvicorn simple_main:app --host 0.0.0.0 --port 8001
)

echo.

REM Check if frontend is running
echo 💻 Frontend App Status:
netstat -an | findstr :6763 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is running on http://localhost:6763
) else (
    echo ❌ Frontend is not running
    echo    Start with: cd desktop\01agent-app && npm start
)

echo.
echo ========================================
echo 🌐 Your Desktop App URLs:
echo ========================================
echo.
echo 💻 MAIN DESKTOP APP: http://localhost:6763
echo    ↳ This is your interactive dashboard
echo    ↳ Click "🚀 Enter Dashboard" to access
echo.
echo 🔧 BACKEND API:      http://localhost:8001
echo    ↳ API endpoints for agent communication
echo.
echo 📚 API DOCS:         http://localhost:8001/docs
echo    ↳ Interactive API documentation
echo.
echo ========================================
echo 🎯 What Your Desktop App Provides:
echo ========================================
echo.
echo ✨ Interactive Dashboard:
echo    • Agent control panel
echo    • Performance monitoring
echo    • Task management
echo    • Quick action buttons
echo    • Backend status display
echo.
echo 🎛️ Features Available:
echo    • Start/stop AI agent
echo    • Take screenshots
echo    • UI automation controls
echo    • Real-time performance stats
echo    • Direct API access
echo.
echo ========================================
echo 🚀 Ready to Use Your Desktop App!
echo ========================================
echo.
pause