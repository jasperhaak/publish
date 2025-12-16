@echo off
title Quartz Publisher GUI

REM Run the standalone GUI
python quartz_publisher_gui_standalone.py

REM If there's an error, show it
if errorlevel 1 (
    echo.
    echo Error: Could not start the GUI application
    echo.
    echo Possible solutions:
    echo 1. Make sure you're in the quartz-publisher directory
    echo 2. Check that Python is installed: python --version
    echo.
    pause
)