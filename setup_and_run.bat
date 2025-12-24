@echo off
echo ===================================
echo TELEGRAM ACCOUNTING BOT - SETUP
echo ===================================
echo.

echo [1/3] Activating conda environment...
call conda activate telegram_bot
if errorlevel 1 (
    echo ERROR: Failed to activate environment
    pause
    exit /b 1
)

echo [2/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ===================================
echo INSTALLATION COMPLETE!
echo ===================================
echo.
echo Starting bot...
echo.
python main.py

pause
