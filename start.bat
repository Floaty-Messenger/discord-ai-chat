@echo off
setlocal
cd /d %~dp0
set PYTHONUTF8=1
set "PATH=%USERPROFILE%\.local\bin;%APPDATA%\npm;%LOCALAPPDATA%\Programs\OpenAI\Codex\bin;%PATH%"
for /f "delims=" %%p in ('powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('Path','User')"') do set "PATH=%%p;%PATH%"
for /d %%d in ("%LOCALAPPDATA%\Programs\Python\Python3*") do set "PYDIR=%%d"
if defined PYDIR set "PATH=%PYDIR%;%PYDIR%\Scripts;%PATH%"
chcp 65001 >nul
python bot.py %*
set "RC=%errorlevel%"
if not defined NOPAUSE pause
exit /b %RC%
