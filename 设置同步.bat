@echo off
chcp 65001 >nul
cd /d %~dp0
echo ============================================
echo   设置同步：两台电脑共用一个私人 GitHub 仓库
echo   （项目文件、记忆、聊天记录都会同步）
echo ============================================
echo.
echo 先在 GitHub 上新建一个「私人」（Private）空仓库，
echo 然后把它的网址粘贴到这里，比如：
echo   https://github.com/你的用户名/ai-group-chat-data
echo 直接按回车 = 关闭同步
echo.
set "URL="
set /p URL=仓库网址：
set NOPAUSE=1
call start.bat --set-sync "%URL%"
echo.
echo 每台电脑都要运行一次这个文件。设置好后重启群聊才生效。
pause
