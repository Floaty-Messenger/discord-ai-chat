$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
# 看门狗：群聊程序卡死（5 分钟没更新 state\alive.txt）就强制结束它，后台运行.bat 会在 30 秒后自动重启
$mutex = New-Object System.Threading.Mutex($false, 'Local\AIGroupChatWatchdog')
if (-not $mutex.WaitOne(0)) { exit }   # 已经有一个看门狗在跑了
$state = Join-Path $dir 'state'
$log = Join-Path $state 'bot.log'
while ($true) {
  Start-Sleep -Seconds 60
  if (Test-Path (Join-Path $state 'stop.flag')) { continue }   # 你主动停的，不管
  $alive = Join-Path $state 'alive.txt'
  $pidFile = Join-Path $state 'bot.pid'
  if (-not (Test-Path $alive) -or -not (Test-Path $pidFile)) { continue }
  $age = ((Get-Date) - (Get-Item $alive).LastWriteTime).TotalMinutes
  if ($age -lt 5) { continue }
  $botPid = 0
  [int]::TryParse((Get-Content $pidFile -Raw).Trim(), [ref]$botPid) | Out-Null
  $proc = Get-Process -Id $botPid -ErrorAction SilentlyContinue
  if ($proc -and $proc.ProcessName -like 'python*') {
    Add-Content -Path $log -Value "===== watchdog: no heartbeat for $([int]$age) min, restarting ($(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')) ====="
    Stop-Process -Id $botPid -Force -ErrorAction SilentlyContinue
  }
  (Get-Item $alive).LastWriteTime = Get-Date   # 给重启留时间，别连着杀
}
