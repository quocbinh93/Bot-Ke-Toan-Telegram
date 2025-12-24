@echo off
echo ==================================
echo DATABASE MIGRATION v1.0 - v2.0
echo ==================================
echo.

REM Check if accounting.db exists
if not exist accounting.db (
    echo Error: accounting.db not found!
    echo Please run the bot first to create database
    pause
    exit /b 1
)

REM Backup
echo Creating backup...
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
copy accounting.db accounting.db.backup_%mydate%_%mytime%
echo Backup created
echo.

REM Run migration
echo Running migration...
python migrate_database.py

if errorlevel 1 (
    echo.
    echo ==================================
    echo MIGRATION FAILED!
    echo ==================================
    echo Please check errors and try again
    pause
    exit /b 1
)

echo.
echo ==================================
echo MIGRATION SUCCESSFUL!
echo ==================================
echo.
echo Next steps:
echo 1. Restart bot: python main.py
echo 2. Set admin role:
echo    UPDATE users SET role = 'admin' WHERE telegram_user_id = YOUR_ID;
echo 3. Test features:
echo    - /admin
echo    - /pending
echo    - /search_date 01/12/2025 31/12/2025
echo.

pause
