@echo off
echo Starting ROOP Face Swapper...
echo.

if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Choose mode:
echo 1. Local only (127.0.0.1:7860)
echo 2. Share publicly (generates public link)
choice /c 12 /n /m "Enter choice (1 or 2): "

if errorlevel 2 (
    python app.py --share
) else (
    python app.py
)

pause
