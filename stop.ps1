$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$state = Join-Path $dir 'state'
if (-not (Test-Path $state)) { New-Item -ItemType Directory $state | Out-Null }
Set-Content -Path (Join-Path $state 'stop.flag') -Value 'stop'
$pidFile = Join-Path $state 'bot.pid'
if (Test-Path $pidFile) {
  $p = (Get-Content $pidFile -Raw).Trim()
  if ($p) { Stop-Process -Id ([int]$p) -Force -ErrorAction SilentlyContinue }
}
Write-Host '已停止 AI群聊，三个机器人会在一分钟内显示离线。'
Start-Sleep -Seconds 3
