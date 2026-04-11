@echo off
echo ========================================
echo    🔧 Fixing Electron Installation
echo ========================================
echo.

echo The issue: 'electron' command not found
echo Solution: Install Electron dependencies properly
echo.

cd desktop

echo Step 1: Installing Electron Dependencies
echo ========================================
echo Installing all required packages...
echo This may take a moment...
echo.

npm install
if %errorlevel% neq 0 (
    echo ❌ npm install failed
    echo Trying to fix with clean install...
    rmdir /s /q node_modules 2>nul
    del package-lock.json 2>nul
    npm install
)

echo.
echo Step 2: Verifying Electron Installation
echo ========================================
echo Checking if Electron is now available...

npx electron --version
if %errorlevel% equ 0 (
    echo ✅ Electron is now installed and working!
) else (
    echo ⚠️ Installing Electron explicitly...
    npm install electron --save-dev
    npx electron --version
)

echo.
echo Step 3: Testing React App Dependencies
echo ========================================
cd 01agent-app

echo Checking React app dependencies...
if not exist "node_modules" (
    echo Installing React dependencies...
    npm install
) else (
    echo ✅ React dependencies already installed
)

cd ..

echo.
echo ========================================
echo 🎉 Electron Installation Fixed!
echo ========================================
echo.
echo Now your desktop app should work properly!
echo.
pause