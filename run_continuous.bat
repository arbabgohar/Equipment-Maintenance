@echo off
REM Windows batch script to run the maintenance checker continuously
echo Starting Equipment Maintenance Notification System...
echo.
echo Current directory: %CD%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python or add it to your system PATH.
    pause
    exit /b 1
)

echo Python found. Starting maintenance checker...
echo.
echo NOTE: This window will stay open while the program runs.
echo Press Ctrl+C to stop the program.
echo.
echo ============================================================
echo.

python maintenance_checker.py --continuous

REM If we get here, the program stopped
echo.
echo ============================================================
echo Program has stopped.
pause

