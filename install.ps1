$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $dir 'common.ps1')
Set-Location $dir
Write-Host '============================================'
Write-Host '  AI 群聊 一键安装'
Write-Host '============================================'
Write-Host ''

Write-Host '[1/7] 安装 Claude Code 命令行（官方安装器）...'
if (Get-Command claude -ErrorAction SilentlyContinue) {
  Write-Host '    已经装好了，跳过。'
} else {
  Invoke-RestMethod https://claude.ai/install.ps1 | Invoke-Expression
}
Write-Host ''

Write-Host '[2/7] 安装 Codex 命令行（官方安装器）...'
if (Get-Command codex -ErrorAction SilentlyContinue) {
  Write-Host '    已经装好了，跳过。'
} else {
  Invoke-RestMethod https://chatgpt.com/codex/install.ps1 | Invoke-Expression
}
Write-Host ''

Write-Host '[3/7] 检查 Git...'
if (Get-Command git -ErrorAction SilentlyContinue) {
  Write-Host '    已经装好了。'
} else {
  Write-Host '    没有 Git，用 winget 安装...'
  winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
}
Write-Host ''

Write-Host '[4/7] 检查 Python...'
. (Join-Path $dir 'common.ps1')
if (Test-RealPython) {
  Write-Host '    已经装好了。'
} else {
  Write-Host '    没有 Python，用 winget 安装 Python 3.12...'
  winget install --id Python.Python.3.12 -e --scope user --accept-source-agreements --accept-package-agreements
  . (Join-Path $dir 'common.ps1')
  if (-not (Test-RealPython)) {
    Write-Host '    ⚠️ Python 好像没装上。可以去 python.org 下载安装（安装时勾选 Add python.exe to PATH），然后再双击 install.bat。' -ForegroundColor Yellow
  }
}
Write-Host ''

# 刷新 PATH，让本窗口能找到刚装好的命令
. (Join-Path $dir 'common.ps1')

Write-Host '[5/7] 安装 Python 依赖...'
& python -m pip install -r requirements.txt
Write-Host ''

Write-Host '[6/7] 检查版本...'
& python --version
& claude --version
& codex --version
& git --version
Write-Host ''

if (-not (& git config --global user.name)) {
  $n = Read-Host 'Git 还没设置名字，请输入你的名字（英文）并回车'
  & git config --global user.name $n
}
if (-not (& git config --global user.email)) {
  $m = Read-Host 'Git 还没设置邮箱，请输入你的邮箱并回车'
  & git config --global user.email $m
}

$newConfig = $false
if (-not (Test-Path (Join-Path $dir 'config.json'))) {
  Copy-Item (Join-Path $dir 'config.example.json') (Join-Path $dir 'config.json')
  Write-Host '已生成 config.json'
  $newConfig = $true
}
Write-Host ''

Write-Host '[7/7] 登录（会打开浏览器）'
Write-Host ''
Write-Host ' 先登录 Claude（用你的 Claude 账号）...'
& claude auth login
if ($LASTEXITCODE -ne 0) {
  Write-Host ' 如果上面报错：关掉这个窗口，新开一个命令行，输入 claude 回车，按提示在浏览器里登录。'
}
Write-Host ''
Write-Host ' 再登录 Codex（选 Sign in with ChatGPT）...'
& codex login
Write-Host ''

Write-Host '============================================'
if ($newConfig) {
  Write-Host '  安装完成！最后一步：'
  Write-Host '  用记事本打开 config.json，填三个机器人令牌、你的用户 ID、DeepSeek key'
  Start-Process notepad (Join-Path $dir 'config.json')
} else {
  Write-Host '  安装完成！config.json 已经有了，不用再填。'
  Write-Host '  想和主机同步：双击「设置同步.bat」。'
}
Write-Host '============================================'
Read-Host '按回车关闭'
