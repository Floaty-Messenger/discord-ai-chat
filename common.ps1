# 各个脚本共用：设置中文输出、把 Claude / Codex / Git / Python 加进 PATH
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$env:PYTHONUTF8 = '1'
$machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
$user = [Environment]::GetEnvironmentVariable('Path', 'User')
$extra = @(
  (Join-Path $env:USERPROFILE '.local\bin'),
  (Join-Path $env:APPDATA 'npm'),
  (Join-Path $env:LOCALAPPDATA 'Programs\OpenAI\Codex\bin')
)
# 真正的 Python 放在最前面，避免 WindowsApps 里那个只会打开微软商店的假 python
$py = Get-ChildItem (Join-Path $env:LOCALAPPDATA 'Programs\Python') -Directory -Filter 'Python3*' -ErrorAction SilentlyContinue |
  Sort-Object Name -Descending | Select-Object -First 1
if ($py) { $extra = @($py.FullName, (Join-Path $py.FullName 'Scripts')) + $extra }
$env:Path = (($extra + @($user, $machine, $env:Path)) | Where-Object { $_ }) -join ';'

function Test-RealPython {
  try {
    $null = & python -c "import sys" 2>$null
    return ($LASTEXITCODE -eq 0)
  } catch { return $false }
}
