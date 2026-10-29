@echo off
setlocal
cd /d "%~dp0..\.."
if not exist ".venv\Scripts\python.exe" (
  echo Python environment missing. See docs\COVER_CAPTURE.md for installation.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" "scripts\capture_covers.py" %*
if errorlevel 1 pause
