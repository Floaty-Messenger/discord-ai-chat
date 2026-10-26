@echo off
chcp 65001 >nul
cd /d %~dp0
set NOPAUSE=1
call start.bat --setup-sync
echo.
pause
