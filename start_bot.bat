@echo off
echo ========================================
echo   Telegram Accounting Bot Launcher
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [*] Virtual environment not found. Creating...
    python -m venv venv
    echo [+] Virtual environment created
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
echo [*] Checking dependencies...
pip show aiogram >nul 2>&1
if errorlevel 1 (
    echo [*] Installing dependencies...
    pip install -r requirements.txt
)

REM Check if .env exists
if not exist ".env" (
    echo.
    echo [!] WARNING: .env file not found!
    echo [!] Please copy .env.example to .env and fill in your API keys
    echo.
    pause
    exit /b 1
)

REM Run the bot
echo.
echo [+] Starting bot...
echo.
python main.py

pause
