@echo off
echo ========================================
echo    01Agent - System Requirements Check
echo ========================================
echo.

echo Checking Python...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    echo Please install Python 3.8+ from https://python.org
    goto :end
)
echo OK: Python is available

echo.
echo Checking Node.js...
node --version 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found
    echo Please install Node.js 16+ from https://nodejs.org
    goto :end
)
echo OK: Node.js is available

echo.
echo Checking npm...
npm --version 2>nul
if %errorlevel% neq 0 (
    echo ERROR: npm not found
    goto :end
)
echo OK: npm is available

echo.
echo Checking pip...
pip --version 2>nul
if %errorlevel% neq 0 (
    echo ERROR: pip not found
    goto :end
)
echo OK: pip is available

echo.
echo ========================================
echo Directory Structure Check
echo ========================================

if exist "backend\main.py" (
    echo OK: Backend found
) else (
    echo ERROR: Backend not found
)

if exist "desktop\01agent-app\package.json" (
    echo OK: Frontend found
) else (
    echo ERROR: Frontend not found
)

if exist "desktop\aiagent\main.py" (
    echo OK: AI Agent found
) else (
    echo ERROR: AI Agent not found
)

echo.
echo ========================================
echo System Check Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run: setup-environment.bat
echo 2. Run: start-all-services.bat
echo.

:end
pause