@echo off
echo Starting Quartz Publisher GUI...
echo ==============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Run the GUI application
python quartz_publisher_gui.py

REM If the script exits with an error, pause so user can see it
if errorlevel 1 (
    echo.
    echo The application encountered an error. Press any key to exit.
    pause
)