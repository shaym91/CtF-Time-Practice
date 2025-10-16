@echo off
echo ============================================================
echo 🎯 CTF COMPETITION 2024 - WINDOWS STARTUP
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.7+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found!
echo.

REM Install dependencies
echo 📦 Installing dependencies...
pip install flask pytz
if errorlevel 1 (
    echo ❌ Failed to install dependencies!
    echo Try: pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Dependencies installed!
echo.

REM Start the server
echo 🚀 Starting CTF Platform...
echo 🌐 Server will be available at: http://localhost:5000
echo ⏰ Competition Time: 5 PM - 5 AM (Bangladesh Time)
echo 🎯 18 INSANE Challenges Ready!
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python run.py

pause
