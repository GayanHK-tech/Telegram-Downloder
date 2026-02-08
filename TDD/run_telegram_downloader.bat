@echo off
title Telegram Media Downloader
color a
cls
echo.
echo ===============================
echo     Telegram Media Downloader
echo ===============================
echo.

:START
REM --- Check Python ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Python] Not found! Downloading and installing...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe -OutFile python_installer.exe"
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    echo [Python] Installed successfully!
)

REM --- Check Telethon ---
python -c "import telethon" 2>nul
if %errorlevel% neq 0 (
    echo [Telethon] Not found! Installing...
    python -m pip install --upgrade pip
    python -m pip install telethon
    echo [Telethon] Installed successfully!
)

REM --- Run Python script ---
echo.
echo [Progress] Running Telegram Media Downloader (Safe Mode)...

python "%~dp0telegram_media_downloader.py"

:POSTMENU
echo.

echo ===============================
echo       Download Completed!
echo ===============================
echo.

echo 1. Back to Menu (Run Again)
echo 2. Exit
set /p post_choice=Enter your choice: 
if "%post_choice%"=="1" goto START
if "%post_choice%"=="2" goto END
goto POSTMENU

:END

echo Exiting...
pause
exit
