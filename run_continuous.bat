@echo off
REM Windows batch script to run the maintenance checker continuously
echo Starting Equipment Maintenance Notification System...
echo.
python maintenance_checker.py --continuous
pause

