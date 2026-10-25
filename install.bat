@echo off
chcp 65001 >nul
setlocal
cd /d %~dp0
echo ============================================
echo   AI 群聊 一键安装
echo ============================================
echo.

echo [1/6] 安装 Claude Code 命令行（官方安装器）...
where claude >nul 2>nul
if %errorlevel%==0 (
  echo     已经装好了，跳过。
) else (
  curl -fsSL https://claude.ai/install.cmd -o "%TEMP%\claude-install.cmd" && call "%TEMP%\claude-install.cmd" && del "%TEMP%\claude-install.cmd"
)
echo.

echo [2/6] 安装 Codex 命令行（官方安装器）...
where codex >nul 2>nul
if %errorlevel%==0 (
  echo     已经装好了，跳过。
) else (
  powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
)
echo.

echo [3/6] 检查 Git...
where git >nul 2>nul
if %errorlevel%==0 (
  echo     已经装好了。
) else (
  echo     没有 Git，用 winget 安装...
  winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
)
echo.

rem 刷新 PATH，让本窗口能找到刚装好的命令
for /f "delims=" %%p in ('powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('Path','User')"') do set "PATH=%%p;%PATH%"
for /f "delims=" %%p in ('powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('Path','Machine')"') do set "PATH=%%p;%PATH%"
if exist "%USERPROFILE%\.local\bin\claude.exe" set "PATH=%USERPROFILE%\.local\bin;%PATH%"

echo [4/6] 安装 Python 依赖...
python -m pip install -r requirements.txt
echo.

echo [5/6] 检查版本...
claude --version
codex --version
git --version
echo.

git config --global user.name >nul 2>nul
if errorlevel 1 (
  set /p GITNAME=Git 还没设置名字，请输入你的名字（英文）并回车：
  call git config --global user.name "%%GITNAME%%"
)
git config --global user.email >nul 2>nul
if errorlevel 1 (
  set /p GITMAIL=Git 还没设置邮箱，请输入你的邮箱并回车：
  call git config --global user.email "%%GITMAIL%%"
)

if not exist config.json (
  copy config.example.json config.json >nul
  echo 已生成 config.json
)
echo.

echo [6/6] 登录（会打开浏览器）
echo.
echo  先登录 Claude（用你的 Claude Pro 账号）...
claude auth login
if errorlevel 1 (
  echo  如果上面报错：关掉这个窗口，新开一个命令行，输入 claude 回车，按提示在浏览器里登录。
)
echo.
echo  再登录 Codex（选 Sign in with ChatGPT，用你的 GPT Pro 账号）...
codex login
echo.

echo ============================================
echo   安装完成！最后一步：
echo   用记事本打开 config.json，填三个机器人令牌、你的用户 ID、DeepSeek key
echo ============================================
start notepad config.json
pause
