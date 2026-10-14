@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\switch-xinput-bridge.exe" (
    echo Not installed yet. Run install.bat first.
    pause
    exit /b 1
)
title switch-xinput-bridge (keep this window open while playing)
".venv\Scripts\switch-xinput-bridge.exe" %*
pause
