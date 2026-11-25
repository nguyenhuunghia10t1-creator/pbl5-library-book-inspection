@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0..\.."
set "pio=%USERPROFILE%\.platformio\penv\Scripts\platformio.exe"
if not exist "%pio%" set "pio=platformio"
if /i "%~1"=="--build-only" goto build
if not "%~1"=="" goto usage
if not exist ".venv-inspection\Scripts\python.exe" (
  echo Set up the station Python environment first.
  goto failed
)
set "boardPort="
set "matches=0"
for /f "tokens=1" %%P in ('.venv-inspection\Scripts\python.exe -m serial.tools.list_ports "10C4:EA60" --include-links -q') do (
  set /a matches+=1 >nul
  set "boardPort=%%P"
)
if not "!matches!"=="1" (
  echo Expected one CP210x ESP32. Found !matches!. Connect only the target board and try again.
  goto failed
)
echo Target: USB inspection firmware on !boardPort!.
echo Disconnect motor and servo power and close the station console and serial monitor.
choice /C YN /N /M "Start flash now? [Y/N] "
if errorlevel 2 exit /b 1
"%pio%" run --project-dir firmware/esp32 --environment esp32dev --target upload --upload-port "!boardPort!"
if errorlevel 1 goto failed
echo Flash verified. Open ManualMechanics.cmd for the first test.
pause
exit /b 0
:build
"%pio%" run --project-dir firmware/esp32 --environment esp32dev
exit /b %errorlevel%
:usage
echo Usage: FlashInspection.cmd [--build-only]
:failed
pause
exit /b 1
