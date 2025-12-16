@echo off
REM Quartz Publisher - Windows batch file wrapper
REM This makes it easier to run the Quartz Publisher on Windows

echo Quartz Publisher
echo ================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Run the Python script
python quartz_publisher.py %*

REM If no arguments were provided, show help
if "%~1"=="" (
    echo.
    echo Usage examples:
    echo   %0 status                    - Show current status
    echo   %0 config --show             - Show configuration
    echo   %0 sync                      - Sync from Obsidian
    echo   %0 build                     - Build site
    echo   %0 preview                   - Preview locally
    echo   %0 deploy                    - Deploy to GitHub Pages
    echo.
)

pause