param(
    [Parameter(Mandatory = $true)]
    [string]$Owner,

    [string]$Path = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$lockFile = Join-Path (Join-Path $projectRoot "state") "session_locks.json"

if (!(Test-Path $lockFile)) {
    Write-Output "No lock file found."
    exit 0
}

$data = Get-Content -Raw -Path $lockFile | ConvertFrom-Json
if ($null -eq $data -or $null -eq $data.locks) {
    Write-Output "No active locks."
    exit 0
}

$before = @($data.locks)
if ([string]::IsNullOrWhiteSpace($Path)) {
    $after = @($before | Where-Object { $_.owner -ne $Owner })
} else {
    $after = @($before | Where-Object { -not ($_.owner -eq $Owner -and $_.path -eq $Path) })
}

([pscustomobject]@{ locks = $after }) | ConvertTo-Json -Depth 8 | Set-Content -Path $lockFile -Encoding UTF8
Write-Output ("UNLOCKED count={0}" -f (@($before).Count - @($after).Count))
