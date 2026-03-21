# EvoPyramid OS: Nexus Ignition (PowerShell Edition)
$host.ui.RawUI.WindowTitle = "EvoPyramid Nexus Ignition"
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "========================================" -ForegroundColor Magenta
Write-Host "      EVOPYRAMID OS: NEXUS IGNITION     " -ForegroundColor Cyan
Write-Host "      Status: Trinity Protocol V4       " -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

# Check for uv
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "[NEXUS] Starting via UV..." -ForegroundColor Blue
    uv run python Nexus_Boot.py
} else {
    Write-Host "[NEXUS] UV not found. Using system python..." -ForegroundColor Yellow
    python Nexus_Boot.py
}

Read-Host "Press Enter to exit..."
