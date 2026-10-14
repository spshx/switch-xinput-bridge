@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\switch-xinput-bridge.exe" (
    echo Not installed yet. Run install.bat first.
    pause
    exit /b 1
)
title switch-xinput-bridge - compatibility check
".venv\Scripts\switch-xinput-bridge.exe" --list %*
pause
