$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $dir 'common.ps1')
$Host.UI.RawUI.WindowTitle = 'AI群聊 - 启动'
$state = Join-Path $dir 'state'
if (-not (Test-Path $state)) { New-Item -ItemType Directory $state | Out-Null }
if (-not (Test-RealPython)) {
  Write-Host ''
  Write-Host '  ⚠️ 这台电脑还没有装 Python，群聊启动不了。请先双击 install.bat。' -ForegroundColor Yellow
  Write-Host ''
  Read-Host '按回车关闭'
  exit 1
}
Start-Process wscript -ArgumentList @('//nologo', "`"$(Join-Path $dir 'hidden.vbs')`"", "`"$(Join-Path $dir '后台运行.bat')`"")
# 看门狗：程序卡死时自动重启（重复启动会自己退出）
Start-Process powershell -WindowStyle Hidden -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$(Join-Path $dir 'watchdog.ps1')`"")
Write-Host ''
Write-Host '  AI群聊 已在后台启动，这个窗口 5 秒后自动关闭。'
Write-Host ''
Write-Host '  - 三个机器人上线后，Discord 成员列表里会显示绿点'
Write-Host '  - 停止：在任意项目频道发 !下线 ，或双击「停止Discord群聊.bat」'
Write-Host "  - 出问题时看日志：$(Join-Path $state 'bot.log')"
Write-Host ''
Start-Sleep -Seconds 5
