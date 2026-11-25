@echo off
setlocal
cd /d "%~dp0..\.."
if not exist ".venv-inspection\Scripts\python.exe" (
  echo Set up the station environment as described in docs\INSPECTION_STATION.md.
  pause
  exit /b 1
)
set "PYTHONUTF8=1"
".venv-inspection\Scripts\python.exe" -m software.web %*
if errorlevel 1 pause
