@echo off
title EvoPyramid OS: Nexus Ignition
cd /d "%~dp0"

:: Check for uv
where uv >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [NEXUS] Starting via UV...
    uv run python Nexus_Boot.py
) else (
    echo [NEXUS] UV not found. Using system python...
    python Nexus_Boot.py
)

pause
