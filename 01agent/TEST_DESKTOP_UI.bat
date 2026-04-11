@echo off
echo ========================================
echo    🖥️ 01Agent Desktop App UI Testing
echo ========================================
echo.

echo This will test your Electron desktop application:
echo • Native desktop window functionality
echo • React UI components and navigation
echo • Agent control interface
echo • Performance monitoring dashboard
echo • Real-time data updates
echo.

echo Step 1: Backend Verification
echo ========================================
echo Checking if backend is running...
curl -s http://localhost:8001 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend API is running on http://localhost:8001
) else (
    echo ⚠️ Backend not detected. Starting backend...
    cd backend
    start "01Agent Backend" cmd /k "echo 🔧 Backend for Desktop Testing && echo. && uvicorn simple_main:app --host 0.0.0.0 --port 8001"
    cd ..
    echo Waiting for backend to start...
    timeout /t 5 /nobreak >nul
)

echo.
echo Step 2: Desktop App Dependencies
echo ========================================
cd desktop

echo Checking Electron dependencies...
if not exist "node_modules" (
    echo Installing desktop app dependencies...
    echo This may take a moment...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)
echo ✅ Desktop dependencies ready

echo.
echo Step 3: React Frontend Build
echo ========================================
cd 01agent-app

echo Building React app for desktop...
echo This ensures latest UI changes are included...
npm run build >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ React frontend built successfully
) else (
    echo ⚠️ Build had issues, but continuing...
    echo Running build with output for debugging...
    npm run build
)

cd ..

echo.
echo Step 4: Desktop App Launch
echo ========================================
echo 🖥️ Launching 01Agent Desktop Application...
echo.
echo What you should see:
echo • Native desktop window (not browser)
echo • Professional sci-fi styled interface
echo • Login/Dashboard screens
echo • Agent control panels
echo • Performance monitoring
echo • Real-time status updates
echo.

echo Starting desktop app in 3 seconds...
timeout /t 3 /nobreak >nul

echo.
echo 🚀 LAUNCHING DESKTOP APP...
echo ========================================
start "01Agent Desktop UI Test" cmd /k "echo 🖥️ 01Agent Desktop Application && echo. && echo Desktop UI Testing Mode && echo • Test all navigation && echo • Try agent controls && echo • Monitor performance && echo • Check real-time updates && echo. && echo Press Ctrl+C to stop desktop app && echo. && npm start"

cd ..

echo.
echo Step 5: UI Testing Checklist
echo ========================================
echo.
echo 📋 DESKTOP APP UI TESTING CHECKLIST:
echo.
echo 🖥️ WINDOW TESTING:
echo [ ] Native desktop window opened (not browser)
echo [ ] Window has proper title "01Agent"
echo [ ] Window controls work (minimize, maximize, close)
echo [ ] Window appears in taskbar
echo [ ] Window can be resized
echo.
echo 🎨 INTERFACE TESTING:
echo [ ] Login screen displays with sci-fi styling
echo [ ] "Enter Dashboard" button works
echo [ ] Navigation sidebar appears
echo [ ] Modern, professional design loads
echo [ ] Colors and animations work
echo.
echo 🎛️ DASHBOARD TESTING:
echo [ ] Home view loads successfully
echo [ ] Agent Status panel visible
echo [ ] Performance monitoring active
echo [ ] Settings panel accessible
echo [ ] Quick actions buttons present
echo.
echo 🤖 AGENT CONTROL TESTING:
echo [ ] Agent start/stop buttons visible
echo [ ] Agent status indicator present
echo [ ] Connection status displayed
echo [ ] Agent logs/output shown
echo [ ] Real-time updates working
echo.
echo 📊 PERFORMANCE TESTING:
echo [ ] CPU usage displayed
echo [ ] Memory usage shown
echo [ ] System stats updating
echo [ ] Performance graphs/charts
echo [ ] Real-time data refresh
echo.
echo 🔧 FUNCTIONALITY TESTING:
echo [ ] All buttons clickable
echo [ ] Forms accept input
echo [ ] Navigation works smoothly
echo [ ] No console errors
echo [ ] Responsive design works
echo.
echo ========================================
echo 🧪 INTERACTIVE TESTING GUIDE
echo ========================================
echo.
echo Now test your desktop app by:
echo.
echo 1. 🖥️ WINDOW INTERACTION:
echo    • Try minimizing and restoring
echo    • Resize the window
echo    • Move the window around
echo    • Test window controls
echo.
echo 2. 🎨 UI NAVIGATION:
echo    • Click "Enter Dashboard"
echo    • Navigate through sidebar menu
echo    • Test all menu items
echo    • Check responsive design
echo.
echo 3. 🤖 AGENT CONTROLS:
echo    • Try agent start/stop buttons
echo    • Monitor agent status
echo    • Check connection indicators
echo    • View agent logs
echo.
echo 4. 📊 PERFORMANCE MONITOR:
echo    • Watch real-time CPU stats
echo    • Monitor memory usage
echo    • Check system performance
echo    • Verify data updates
echo.
echo 5. 🔧 FEATURE TESTING:
echo    • Test screenshot buttons
echo    • Try automation controls
echo    • Check settings panel
echo    • Test quick actions
echo.
echo ========================================
echo 🎉 Desktop App Testing Active!
echo ========================================
echo.
echo Your 01Agent desktop app should now be running!
echo.
echo 🖥️ DESKTOP APP: Native Electron window
echo 🔧 BACKEND API: http://localhost:8001
echo 📚 API DOCS: http://localhost:8001/docs
echo.
echo Test all features and report any issues!
echo.
pause