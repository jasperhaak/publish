@echo off
echo Starting Quartz Publisher GUI (Debug Mode)...
echo ==============================
echo Current directory: %CD%
echo Python version:
python --version
echo.
echo Running GUI...
echo ==============================
echo.

python quartz_publisher_gui.py

echo.
echo ==============================
echo Exit code: %errorlevel%
if errorlevel 1 (
    echo An error occurred!
    echo.
    echo Common issues:
    echo 1. Make sure you're running from the quartz-publisher directory
    echo 2. Check if quartz_publisher.py is in the same directory
    echo 3. Ensure Python is properly installed
    echo.
)
echo Press any key to close this window...
pause >nul