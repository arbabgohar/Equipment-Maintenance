@echo off
REM Test script to check if everything is set up correctly
echo ============================================================
echo Testing Equipment Maintenance System Setup
echo ============================================================
echo.

REM Check Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo    ERROR: Python not found!
    echo    Please install Python from https://www.python.org/
    pause
    exit /b 1
) else (
    python --version
    echo    OK - Python is installed
)
echo.

REM Check if files exist
echo [2/4] Checking required files...
if exist "maintenance_checker.py" (
    echo    OK - maintenance_checker.py found
) else (
    echo    ERROR - maintenance_checker.py not found!
    pause
    exit /b 1
)

if exist "equipment_data.json" (
    echo    OK - equipment_data.json found
) else (
    echo    ERROR - equipment_data.json not found!
    pause
    exit /b 1
)

if exist "config.json" (
    echo    OK - config.json found
) else (
    echo    ERROR - config.json not found!
    pause
    exit /b 1
)
echo.

REM Check dependencies
echo [3/4] Checking Python dependencies...
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo    WARNING - 'requests' module not found
    echo    Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo    ERROR - Failed to install dependencies!
        pause
        exit /b 1
    )
) else (
    echo    OK - 'requests' module found
)

python -c "import dateutil" >nul 2>&1
if errorlevel 1 (
    echo    WARNING - 'python-dateutil' module not found
    echo    Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo    ERROR - Failed to install dependencies!
        pause
        exit /b 1
    )
) else (
    echo    OK - 'python-dateutil' module found
)
echo.

REM Try to run a test
echo [4/4] Running test check...
echo.
python maintenance_checker.py
if errorlevel 1 (
    echo.
    echo    ERROR - Program failed to run!
    echo    Check the error message above.
    pause
    exit /b 1
) else (
    echo.
    echo    OK - Program ran successfully!
)
echo.
echo ============================================================
echo Setup check complete! You can now run run_continuous.bat
echo ============================================================
pause

