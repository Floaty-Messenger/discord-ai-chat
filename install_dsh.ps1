$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $dir 'common.ps1')
Set-Location $dir
Write-Host '============================================'
Write-Host '  安装本地 DSH（DeepSeek Harness）命令行'
Write-Host '============================================'
Write-Host ''
if (-not (Get-Command dsh -ErrorAction SilentlyContinue)) {
  Write-Host '[1/3] 检查 Node.js...'
  if (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Host '    已经装好了。'
  } else {
    Write-Host '    没有 Node.js，用 winget 安装...'
    winget install --id OpenJS.NodeJS.LTS -e --accept-source-agreements --accept-package-agreements
    . (Join-Path $dir 'common.ps1')
  }
  Write-Host ''
  Write-Host '[2/3] 安装 DSH 命令行...'
  & npm install -g '@deepseek-ai/dsh'
  . (Join-Path $dir 'common.ps1')
  Write-Host ''
}
Write-Host '[3/3] 测试（让本地 DSH 用一句话介绍自己）...'
& dsh --version
'用一句话介绍你自己' | & dsh --profile headless
Write-Host ''
Write-Host '============================================'
Write-Host ' 上面如果正常回答了：本地 DSH 可以用了。群里的 DeepSeek 派活（要动文件）时会用它，普通聊天仍走 API。'
Write-Host ' 如果报错说没有 key / 模型：运行  dsh web  ，在打开的网页里 Settings - Models 填 DeepSeek key，'
Write-Host ' 然后再双击一次这个文件测试。在那之前群里的 DeepSeek 会继续用 API，不受影响。'
Write-Host '============================================'
Read-Host '按回车关闭'
