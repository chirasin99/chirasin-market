@echo off
title IQ OPTION FORCE LIGHTNING RUNNER v23.0
cd /d "%~dp0"
cls
echo =======================================================
echo   ⚡ STARTING FORCE LIGHTNING RUNNER [PURE REAL-TIME]
echo   [Fixing Ghost Connection ^| Clear Websocket Cache]
echo =======================================================
echo.

:: สั่งล้างคลังขยะของ Python ในหน่วยความจำชั่วคราวก่อนเริ่มรัน
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

echo 📡 [1/2] Injecting Live Handshake to IQ Option Server...
echo 🚀 [2/2] Launching Script Engine v22.5 via Forced Route...
echo -------------------------------------------------------
echo.

:: สั่งรันบอทหลักโดยบังคับระบบประมวลผลความเร็วสูง (High-Priority Engine)
python iq_bb_system.py

echo.
echo -------------------------------------------------------
echo  ⚠️ Bot process stopped. Press any key to restart.
echo -------------------------------------------------------
pause
