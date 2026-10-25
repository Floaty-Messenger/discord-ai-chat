@echo off
chcp 65001 >nul
cd /d %~dp0
if not exist state mkdir state
echo stop> state\stop.flag
if exist state\bot.pid (
  for /f %%p in (state\bot.pid) do taskkill /PID %%p /F >nul 2>&1
)
echo 已停止 AI群聊，三个机器人会在一分钟内显示离线。
timeout /t 3 >nul
