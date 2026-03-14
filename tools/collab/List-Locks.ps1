$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$lockFile = Join-Path (Join-Path $projectRoot "state") "session_locks.json"

if (!(Test-Path $lockFile)) {
    Write-Output "No active locks."
    exit 0
}

$data = Get-Content -Raw -Path $lockFile | ConvertFrom-Json
if ($null -eq $data -or $null -eq $data.locks -or @($data.locks).Count -eq 0) {
    Write-Output "No active locks."
    exit 0
}

$now = Get-Date
$active = @($data.locks | Where-Object { [datetime]$_.expires_at -gt $now })
if (@($active).Count -eq 0) {
    Write-Output "No active locks."
    exit 0
}

$active |
    Sort-Object owner, path |
    Select-Object owner, path, task, locked_at, expires_at |
    Format-Table -AutoSize
