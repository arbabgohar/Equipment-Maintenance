@echo off
REM Windows batch script to run the Slack bot server
echo Starting Slack Bot Server...
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

echo Python found. Starting Slack bot server...
echo.
echo NOTE: This window will stay open while the server runs.
echo The server will listen on http://localhost:5000
echo.
echo For local development, use ngrok to expose this server:
echo   ngrok http 5000
echo.
echo ============================================================
echo.

python slack_bot_server.py

REM If we get here, the server stopped
echo.
echo ============================================================
echo Server has stopped.
pause

