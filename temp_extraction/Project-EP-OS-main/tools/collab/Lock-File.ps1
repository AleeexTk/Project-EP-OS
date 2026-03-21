param(
    [Parameter(Mandatory = $true)]
    [string]$Owner,

    [Parameter(Mandatory = $true)]
    [string]$Path,

    [string]$Task = "",
    [int]$TtlMinutes = 90
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$stateDir = Join-Path $projectRoot "state"
$lockFile = Join-Path $stateDir "session_locks.json"

if (!(Test-Path $stateDir)) {
    New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
}

if (!(Test-Path $lockFile)) {
    "{`"locks`":[]}" | Set-Content -Path $lockFile -Encoding UTF8
}

$data = Get-Content -Raw -Path $lockFile | ConvertFrom-Json
if ($null -eq $data -or $null -eq $data.locks) {
    $data = [pscustomobject]@{ locks = @() }
}

$now = Get-Date
$activeLocks = @()
foreach ($item in @($data.locks)) {
    $expiresAt = [datetime]$item.expires_at
    if ($expiresAt -gt $now) {
        $activeLocks += $item
    }
}

$conflict = $activeLocks | Where-Object { $_.path -eq $Path -and $_.owner -ne $Owner } | Select-Object -First 1
if ($null -ne $conflict) {
    Write-Error "Lock conflict: '$Path' is already owned by '$($conflict.owner)' until $($conflict.expires_at)."
    exit 1
}

$activeLocks = $activeLocks | Where-Object { -not ($_.path -eq $Path -and $_.owner -eq $Owner) }

$entry = [pscustomobject]@{
    path = $Path
    owner = $Owner
    task = $Task
    locked_at = $now.ToString("o")
    expires_at = $now.AddMinutes($TtlMinutes).ToString("o")
}

$activeLocks += $entry
$out = [pscustomobject]@{ locks = $activeLocks }
$out | ConvertTo-Json -Depth 8 | Set-Content -Path $lockFile -Encoding UTF8

Write-Output ("LOCKED {0} owner={1} expires={2}" -f $Path, $Owner, $entry.expires_at)
