@echo off
title IQ OPTION BOT RUNNER (PATH CHECKER)
cd /d "%~dp0"
cls
echo =======================================================
echo      [IQ OPTION BOT QUICK START]
echo =======================================================
echo  Current Folder: %CD%
echo -------------------------------------------------------
echo  Checking file status...
if exist "bot_iqoption.py" (
    echo  [OK] Found bot_iqoption.py
) else (
    echo  [ERROR] CANNOT FIND bot_iqoption.py IN THIS FOLDER!
    echo  Please check if this .bat file is in the same folder as your bot.
    echo -------------------------------------------------------
    dir /b *.py *.txt
    echo -------------------------------------------------------
)
echo =======================================================
echo   [1] RUN BOT WITH REAL TRADING ACTIVE
echo   [2] RUN BOT WITH SIMULATION/TEST MODE ONLY
echo =======================================================
set /p choice="Enter your choice [1 or 2] and press Enter: "

if "%choice%"=="1" (
    echo Starting Real Trading Mode...
    python bot_iqoption.py --mode=real
) else if "%choice%"=="2" (
    echo Starting Simulation Mode...
    python bot_iqoption.py --mode=demo
) else (
    echo Invalid choice. Exiting...
)
pause
