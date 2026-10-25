@echo off
chcp 65001 >nul
cd /d %~dp0
if not exist state mkdir state
if exist state\stop.flag del state\stop.flag
set NOPAUSE=1
set PYTHONUNBUFFERED=1
:loop
echo ===== %date% %time% 启动 ===== >> state\bot.log
call start.bat >> state\bot.log 2>&1
rem 3 = 已经有一个在运行
if errorlevel 3 if not errorlevel 4 goto end
if exist state\stop.flag goto end
echo ===== 程序退出，30 秒后自动重启 ===== >> state\bot.log
timeout /t 30 /nobreak >nul
if exist state\stop.flag goto end
goto loop
:end
