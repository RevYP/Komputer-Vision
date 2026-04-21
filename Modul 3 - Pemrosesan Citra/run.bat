@echo off
echo.
echo ========================================
echo  Smart Document Scanner - Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python tidak terinstall!
    echo Download dari https://www.python.org
    pause
    exit /b 1
)

REM Create virtual environment if not exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Mengaktifkan virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Menginstall dependencies...
pip install -r requirements.txt

REM Run the application
echo.
echo Menjalankan Smart Document Scanner...
echo.
python scanner_gui.py

pause
