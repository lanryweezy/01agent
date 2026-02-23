@echo off
echo ========================================
echo    📦 01Agent Windows Installer Builder
echo ========================================
echo.

echo Building professional Windows installer for 01Agent
echo This creates a complete .exe installer for distribution
echo.

cd desktop

echo Step 1: Clean Previous Builds
echo ========================================
echo Cleaning old build files...
if exist "dist" rmdir /s /q "dist"
if exist "01agent-app\build" rmdir /s /q "01agent-app\build"
echo ✅ Build directories cleaned

echo.
echo Step 2: Install Dependencies
echo ========================================
echo Installing desktop dependencies...
npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install desktop dependencies
    pause
    exit /b 1
)

echo Installing React app dependencies...
cd 01agent-app
npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install React dependencies
    pause
    exit /b 1
)
cd ..
echo ✅ All dependencies installed

echo.
echo Step 3: Build React Production App
echo ========================================
echo Building optimized React application...
cd 01agent-app
npm run build
if %errorlevel% neq 0 (
    echo ❌ React build failed
    pause
    exit /b 1
)
cd ..
echo ✅ React app built successfully

echo.
echo Step 4: Install Electron Builder
echo ========================================
echo Ensuring electron-builder is available...
npm install electron-builder --save-dev
echo ✅ Electron builder ready

echo.
echo Step 5: Build Windows Installer
echo ========================================
echo Creating Windows installer (.exe)...
echo This may take 5-10 minutes...
echo.

REM Try the standard build command first
npm run build
if %errorlevel% equ 0 (
    echo ✅ Standard build succeeded!
    goto :check_output
)

echo Standard build failed, trying alternative...
npx electron-builder --win --publish=never
if %errorlevel% equ 0 (
    echo ✅ Alternative build succeeded!
    goto :check_output
)

echo Both builds failed, trying manual approach...
npx electron-builder --win --config.directories.output=dist
if %errorlevel% equ 0 (
    echo ✅ Manual build succeeded!
    goto :check_output
)

echo ❌ All build attempts failed
goto :build_failed

:check_output
echo.
echo Step 6: Verifying Build Output
echo ========================================
if exist "dist" (
    echo ✅ Dist directory created
    dir dist /b
    echo.
    
    if exist "dist\*.exe" (
        echo ✅ Windows installer found:
        for %%f in (dist\*.exe) do (
            echo    📦 %%~nxf
            echo    📏 Size: 
            dir "%%f" | findstr /C:"%%~nxf"
        )
        goto :build_success
    ) else (
        echo ⚠️ No .exe installer found, checking for unpacked version...
        if exist "dist\win-unpacked" (
            echo ✅ Unpacked Windows build found
            echo    📁 Location: dist\win-unpacked\
            if exist "dist\win-unpacked\01Agent.exe" (
                echo    🖥️ Executable: 01Agent.exe
            )
            goto :build_partial
        ) else (
            echo ❌ No Windows build output found
            goto :build_failed
        )
    )
) else (
    echo ❌ No dist directory found
    goto :build_failed
)

:build_success
cd ..
echo.
echo ========================================
echo 🎉 INSTALLER BUILD SUCCESSFUL!
echo ========================================
echo.
echo ✅ Your Windows installer is ready!
echo.
echo 📦 Installer Location: desktop\dist\
echo 📁 Files created:
dir desktop\dist\*.exe /b 2>nul
echo.
echo 🚀 Distribution Ready:
echo • Share the .exe file with users
echo • Professional Windows installation
echo • One-click install experience
echo • Desktop shortcuts included
echo • Start Menu integration
echo • Automatic uninstaller
echo.
echo 🎯 Installation Features:
echo • Custom install location
echo • Desktop shortcut creation
echo • Start Menu entry
echo • Windows integration
echo • Professional appearance
echo.
goto :end

:build_partial
cd ..
echo.
echo ========================================
echo ⚠️ PARTIAL BUILD SUCCESS
echo ========================================
echo.
echo ✅ Desktop app built successfully
echo ❌ Installer package not created
echo.
echo 📁 App Location: desktop\dist\win-unpacked\
echo 🖥️ Executable: desktop\dist\win-unpacked\01Agent.exe
echo.
echo You have a working desktop app, but no installer.
echo Users would need to:
echo 1. Extract the win-unpacked folder
echo 2. Run 01Agent.exe directly
echo.
echo To create an installer, try:
echo   npx electron-builder --win --config.nsis.oneClick=false
echo.
goto :end

:build_failed
cd ..
echo.
echo ========================================
echo ❌ BUILD FAILED
echo ========================================
echo.
echo The Windows installer build failed.
echo.
echo 🔧 Troubleshooting steps:
echo 1. Ensure all dependencies are installed
echo 2. Check that React build succeeded
echo 3. Verify package.json build configuration
echo 4. Try manual build: npx electron-builder --win
echo.
echo 📋 Common solutions:
echo • Delete node_modules and reinstall: npm install
echo • Clear npm cache: npm cache clean --force
echo • Update electron-builder: npm install electron-builder@latest
echo • Check Windows build tools are installed
echo.
goto :end

:end
echo ========================================
echo Build process complete
echo ========================================
pause