@echo off
chcp 65001 >nul
cd /d %~dp0
echo ============================================
echo   安装本地 DSH（DeepSeek Harness）命令行
echo ============================================
echo.
set "PATH=%APPDATA%\npm;%PATH%"
where dsh >nul 2>nul
if %errorlevel%==0 goto test

echo [1/3] 检查 Node.js...
where node >nul 2>nul
if %errorlevel%==0 (
  echo     已经装好了。
) else (
  echo     没有 Node.js，用 winget 安装...
  winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements
  for /f "delims=" %%p in ('powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('Path','Machine')"') do set "PATH=%%p;%PATH%"
  for /f "delims=" %%p in ('powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('Path','User')"') do set "PATH=%%p;%PATH%"
)
echo.
echo [2/3] 安装 DSH 命令行...
call npm install -g @deepseek-ai/dsh
echo.

:test
echo [3/3] 测试（让本地 DSH 用一句话介绍自己）...
dsh --version
echo 用一句话介绍你自己 | dsh --profile headless
echo.
echo ============================================
echo  上面如果正常回答了：本地 DSH 可以用了，群里的 DeepSeek 会自动改用它（能联网、能看项目文件）。
echo  如果报错说没有 key / 模型：运行  dsh web  ，在打开的网页里 Settings - Models 填 DeepSeek key，
echo  然后再双击一次这个文件测试。在那之前群里的 DeepSeek 会继续用 API，不受影响。
echo ============================================
pause
