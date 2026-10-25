$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktop = [Environment]::GetFolderPath('Desktop')
$shell = New-Object -ComObject WScript.Shell
$items = @(
  @{ Name = 'AI群聊 - 本地聊天'; Target = '本地聊天.bat'; Icon = 'imageres.dll,76' },
  @{ Name = 'AI群聊 - Discord'; Target = '启动Discord群聊.bat'; Icon = 'imageres.dll,20' }
)
foreach ($i in $items) {
  $lnk = $shell.CreateShortcut((Join-Path $desktop ($i.Name + '.lnk')))
  $lnk.TargetPath = Join-Path $dir $i.Target
  $lnk.WorkingDirectory = $dir
  $lnk.IconLocation = Join-Path $env:SystemRoot ('System32\' + $i.Icon)
  $lnk.Save()
  Write-Host ('已创建桌面图标：' + $i.Name)
}
