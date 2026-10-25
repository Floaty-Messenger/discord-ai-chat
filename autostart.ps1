param([switch]$Remove)
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$startup = [Environment]::GetFolderPath('Startup')
$path = Join-Path $startup 'AI群聊 - Discord.lnk'
if ($Remove) {
  if (Test-Path $path) { Remove-Item $path; Write-Host '已取消开机自启。' } else { Write-Host '本来就没有开机自启。' }
  exit
}
$shell = New-Object -ComObject WScript.Shell
$lnk = $shell.CreateShortcut($path)
$lnk.TargetPath = Join-Path $dir '启动Discord群聊.bat'
$lnk.WorkingDirectory = $dir
$lnk.WindowStyle = 7
$lnk.IconLocation = Join-Path $env:SystemRoot 'System32\imageres.dll,20'
$lnk.Save()
Write-Host '已设置开机自启：登录 Windows 后，Discord 群聊会在任务栏里最小化启动。'
Write-Host '想取消就双击「取消开机自启.bat」。'
