@echo off
echo ========================================
echo    📦 Building 01Agent Windows Installer
echo ========================================
echo.

echo Creating professional Windows installer (.exe) for your desktop app
echo This will build a complete installer package for distribution
echo.

cd desktop

echo Step 1: Preparing React Build
echo ========================================
echo Building optimized React production files...
cd 01agent-app
npm run build
if %errorlevel% neq 0 (
    echo ❌ React build failed
    pause
    exit /b 1
)
echo ✅ React build completed
cd ..

echo.
echo Step 2: Installing Build Dependencies
echo ========================================
echo Ensuring electron-builder is available...
npm install electron-builder --save-dev
if %errorlevel% neq 0 (
    echo ❌ Failed to install electron-builder
    pause
    exit /b 1
)
echo ✅ Build dependencies ready

echo.
echo Step 3: Building Windows Installer
echo ========================================
echo Creating Windows installer (.exe)...
echo This may take several minutes...
echo.

npm run build
if %errorlevel% equ 0 (
    echo ✅ Windows installer built successfully!
    echo.
    echo 📦 Your installer is ready:
    if exist "dist\*.exe" (
        for %%f in (dist\*.exe) do (
            echo    File: %%f
            echo    Size: 
            dir "%%f" | findstr /C:"%%~nxf"
        )
    )
    echo.
    echo 🎉 Installation package created!
    echo You can now distribute this .exe file to install 01Agent on any Windows PC
) else (
    echo ❌ Build failed
    echo Checking for common issues...
    
    echo.
    echo Trying alternative build method...
    npx electron-builder --win
    
    if %errorlevel% equ 0 (
        echo ✅ Alternative build succeeded!
    ) else (
        echo ❌ Build failed with alternative method too
        echo.
        echo Common solutions:
        echo 1. Ensure all dependencies are installed: npm install
        echo 2. Check that React build exists: npm run react-build
        echo 3. Verify package.json build configuration
        echo 4. Try: npx electron-builder --win --publish=never
    )
)

cd ..

echo.
echo ========================================
echo 📦 Installer Build Complete!
echo ========================================
echo.

if exist "desktop\dist\*.exe" (
    echo ✅ SUCCESS: Windows installer created!
    echo.
    echo 📁 Location: desktop\dist\
    echo 📦 Files created:
    dir desktop\dist\*.exe /b
    echo.
    echo 🚀 Your 01Agent installer is ready for distribution!
    echo.
    echo What you can do with this installer:
    echo • Install 01Agent on any Windows PC
    echo • Share with others for easy installation
    echo • Deploy to multiple computers
    echo • Create desktop shortcuts automatically
    echo • Add to Windows Programs list
    echo.
    echo The installer includes:
    echo • Complete Electron desktop app
    echo • All React UI components
    echo • Native Windows integration
    echo • Automatic updates capability
    echo • Professional installation experience
) else (
    echo ⚠️ No installer files found in desktop\dist\
    echo Check the build output above for errors
)

echo.
echo ========================================
echo Ready for distribution!
echo ========================================
pause