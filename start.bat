@echo off
setlocal
cd /d %~dp0
set PYTHONUTF8=1
set "PATH=%USERPROFILE%\.local\bin;%APPDATA%\npm;%LOCALAPPDATA%\Programs\OpenAI\Codex\bin;%PATH%"
for /f "delims=" %%p in ('powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('Path','User')"') do set "PATH=%%p;%PATH%"
rem Use the python on PATH if it already has the packages; otherwise the one install.ps1 put in LocalAppData
python -c "import discord" >nul 2>nul
if not errorlevel 1 goto run
for /d %%d in ("%LOCALAPPDATA%\Programs\Python\Python3*") do set "PYDIR=%%d"
if defined PYDIR set "PATH=%PYDIR%;%PYDIR%\Scripts;%PATH%"
:run
chcp 65001 >nul
python bot.py %*
set "RC=%errorlevel%"
if not defined NOPAUSE pause
exit /b %RC%
