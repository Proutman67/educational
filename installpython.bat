@echo off
setlocal

REM ===== CONFIG =====
set PYTHON_VERSION=3.14.2
set INSTALLER=%~dp0\python-%PYTHON_VERSION%-amd64.exe
set DOWNLOAD_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/%INSTALLER%

REM ===== CHECK ADMIN =====
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Please run this script as Administrator.
    pause
    exit /b 1
)

REM ===== CHECK IF PYTHON EXISTS =====
where python >nul 2>&1
if errorlevel 1 (
    echo Python is NOT installed.
) else (
    echo Python is already installed.
    python --version
    goto :eof
)


REM ===== DOWNLOAD INSTALLER =====
echo Downloading Python %PYTHON_VERSION%...
curl -L -o "%INSTALLER%" "%DOWNLOAD_URL%"
if %errorlevel% neq 0 (
    echo ERROR: Failed to download Python installer.
    exit /b 1
)

REM ===== INSTALL PYTHON =====
echo Installing Python...
"%INSTALLER%" ^
 /quiet ^
 InstallAllUsers=1 ^
 PrependPath=1 ^
 Include_test=0 ^
 SimpleInstall=1

REM ===== CLEANUP =====
del "%INSTALLER%"

timeout 5

REM ===== VERIFY =====
echo Verifying installation...
python --version
pip --version

echo Python installation completed successfully.
pause
