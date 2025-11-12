@echo off
REM Setup script for Cloudflare Tunnel
echo ============================================================
echo Cloudflare Tunnel Setup for Slack Bot
echo ============================================================
echo.
echo Current directory: %CD%
echo.

REM Check if cloudflared exists
if exist "cloudflared.exe" (
    echo [OK] Found cloudflared.exe
    echo.
    goto :check_server
)

echo [ERROR] cloudflared.exe not found in current directory.
echo.
echo Please download cloudflared:
echo 1. Go to: https://github.com/cloudflare/cloudflared/releases
echo 2. Download: cloudflared-windows-amd64.exe
echo 3. Rename it to: cloudflared.exe
echo 4. Place it in this folder: %CD%
echo.
echo Or download directly:
echo https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
echo.
echo Press any key to exit...
pause >nul
exit /b 1

:check_server
echo Checking if slack_bot_server.py is running...
echo.
timeout /t 2 >nul
curl -s http://localhost:5000/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Could not connect to server on port 5000
    echo.
    echo Make sure slack_bot_server.py is running in another window!
    echo Run: python slack_bot_server.py
    echo.
    echo Press any key to continue anyway, or Ctrl+C to cancel...
    pause >nul
) else (
    echo [OK] Server is running on port 5000
    echo.
)

echo ============================================================
echo Starting Cloudflare Tunnel...
echo ============================================================
echo.
echo IMPORTANT: 
echo 1. Copy the HTTPS URL that appears below (starts with https://)
echo 2. Use it in your Slack slash command configuration
echo 3. Keep this window open while using Slack commands
echo.
echo Press Ctrl+C to stop the tunnel
echo ============================================================
echo.

cloudflared.exe tunnel --url http://localhost:5000

REM If we get here, cloudflared stopped
echo.
echo ============================================================
echo Cloudflare Tunnel has stopped.
echo ============================================================
pause

