import os
import sys
import shutil
import subprocess
from pathlib import Path

APP_NAME = "SecurityServices"
INSTALL_DIR = os.path.join(os.environ["ProgramFiles"], APP_NAME)

SYSTEM_TASK_NAME = "MyApp_SystemAgent"
USER_TASK_NAME = "MyApp_UserAgent"

PYTHON_EXE = Path(sys.executable).with_name("pythonw.exe")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SYSTEM_SRC = os.path.join(BASE_DIR, "system_agent.py")
USER_SRC = os.path.join(BASE_DIR, "user_agent.py")

SYSTEM_DST = os.path.join(INSTALL_DIR, "system_agent.py")
USER_DST = os.path.join(INSTALL_DIR, "user_agent.py")

# ---- CREATE INSTALL DIRECTORY ----
os.makedirs(INSTALL_DIR, exist_ok=True)

# ---- COPY FILES ----
shutil.copy2(SYSTEM_SRC, SYSTEM_DST)
shutil.copy2(USER_SRC, USER_DST)

# ---- CREATE SYSTEM STARTUP TASK ----
subprocess.run(
    [
        "schtasks",
        "/create",
        "/f",
        #"/sc", "onstart",
        "/sc", "minute",
        "/mo", "1",
        "/ru", "SYSTEM",
        "/rl", "highest",
        "/tn", SYSTEM_TASK_NAME,
        "/tr", f'"{PYTHON_EXE}" "{SYSTEM_DST}" >> C:\\Windows\\Temp\\SecutiryServicesLogsSystem.txt 2>&1'
        #"/ri", "1",
        #"/du", "00:30"
    ],
    check=True
)

# ---- CREATE USER LOGON TASK ----
subprocess.run(
    [
        "schtasks",
        "/create",
        "/f",
        #"/sc", "onlogon",
        "/sc", "minute",
        "/mo", "1",
        "/ru", os.getlogin(),
        "/tn", USER_TASK_NAME,
        "/tr", f'"{PYTHON_EXE}" "{USER_DST}" >> C:\\Windows\\Temp\\SecutiryServicesLogsUser.txt 2>&1',
        #"/ri", "1",
        #"/du", "00:30"
    ],
    check=True
)

print(f"Installed to: {INSTALL_DIR}")
print("Tasks created")
print(f'"{PYTHON_EXE}" "{SYSTEM_DST}"')
print(f'"{PYTHON_EXE}" "{USER_DST}"')
print("Installation completed successfully.")
