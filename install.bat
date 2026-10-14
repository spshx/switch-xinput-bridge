@echo off
setlocal
cd /d "%~dp0"
title switch-xinput-bridge - install

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
    echo Python 3.9 or newer is required: https://www.python.org/downloads/
    echo Tick "Add python.exe to PATH" during setup, then run this again.
    echo Or download the ready-made switch-xinput-bridge.exe from the Releases page instead.
    pause
    exit /b 1
)

echo Creating virtual environment in .venv ...
%PY% -m venv .venv || goto :fail
echo Installing switch-xinput-bridge and its dependencies ...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check --quiet . || goto :fail

echo.
echo Installed. Make sure the ViGEmBus driver is installed too:
echo   https://github.com/nefarius/ViGEmBus/releases
echo Then double-click start.bat (or test-controller.bat to check your buttons).
pause
exit /b 0

:fail
echo.
echo Installation failed, see the messages above.
pause
exit /b 1
