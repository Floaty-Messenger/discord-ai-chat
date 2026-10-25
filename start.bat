@echo off
setlocal
chcp 65001 >nul
cd /d %~dp0
set PYTHONUTF8=1
rem Claude Code 和 Codex 的安装目录，防止 PATH 里没有
set "PATH=%USERPROFILE%\.local\bin;%APPDATA%\npm;%LOCALAPPDATA%\Programs\OpenAI\Codex\bin;%PATH%"
for /f "delims=" %%p in ('powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('Path','User')"') do set "PATH=%%p;%PATH%"
python bot.py %*
if not defined NOPAUSE pause
