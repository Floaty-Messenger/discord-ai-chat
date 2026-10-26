$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $dir 'common.ps1')
Set-Location $dir
Write-Host '============================================'
Write-Host '  设置同步：两台电脑共用一个私人 GitHub 仓库'
Write-Host '  （项目文件、记忆、聊天记录都会同步）'
Write-Host '============================================'
Write-Host ''
if (-not (Test-RealPython)) {
  Write-Host '⚠️ 这台电脑还没有装 Python。请先双击 install.bat，装好后再运行这个文件。' -ForegroundColor Yellow
  Read-Host '按回车关闭'
  exit 1
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Host '⚠️ 这台电脑还没有装 Git。请先双击 install.bat，装好后再运行这个文件。' -ForegroundColor Yellow
  Read-Host '按回车关闭'
  exit 1
}
Write-Host '先在 GitHub 上新建一个「私人」（Private）空仓库，'
Write-Host '然后把它的网址粘贴到这里，比如：'
Write-Host '  https://github.com/你的用户名/ai-group-chat-data'
Write-Host '两台电脑要填同一个网址。直接按回车 = 关闭同步'
Write-Host ''
$url = Read-Host '仓库网址'
$u = "$url".Trim()
& python bot.py "--set-sync=$u"
Write-Host ''
Write-Host '每台电脑都要运行一次这个文件。设置好后重启群聊才生效。'
Read-Host '按回车关闭'
