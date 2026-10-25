@echo off
chcp 65001 >nul
title AI群聊 - 启动
cd /d %~dp0
if not exist state mkdir state
wscript //nologo "%~dp0hidden.vbs" "%~dp0后台运行.bat"
echo.
echo   AI群聊 已在后台启动，这个窗口 5 秒后自动关闭。
echo.
echo   - 三个机器人上线后，Discord 成员列表里会显示绿点
echo   - 停止：在任意项目频道发 !下线 ，或双击「停止Discord群聊.bat」
echo   - 出问题时看日志：%~dp0state\bot.log
echo.
timeout /t 5 >nul
