@echo off
cd /d %~dp0
if not exist state mkdir state
if exist state\stop.flag del state\stop.flag
set NOPAUSE=1
set PYTHONUNBUFFERED=1
:loop
echo ===== %date% %time% start ===== >> state\bot.log
call start.bat >> state\bot.log 2>&1
rem exit code 3 = already running
if errorlevel 3 if not errorlevel 4 goto end
if exist state\stop.flag goto end
echo ===== exited, restarting in 30 s ===== >> state\bot.log
timeout /t 30 /nobreak >nul
if exist state\stop.flag goto end
goto loop
:end
