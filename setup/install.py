import os
import sys
import shutil
import subprocess

APP_NAME = "SecutiryServices"
INSTALL_DIR = os.path.join(os.environ["ProgramFiles"], APP_NAME)

SYSTEM_TASK_NAME = "MyApp_SystemAgent"
USER_TASK_NAME = "MyApp_UserAgent"

PYTHON_EXE = sys.executable
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
        "/sc", "onstart",
        "/ru", "SYSTEM",
        "/rl", "highest",
        "/tn", SYSTEM_TASK_NAME,
        "/tr", f'"{PYTHON_EXE}" "{SYSTEM_DST}"'
    ],
    check=True
)

# ---- CREATE USER LOGON TASK ----
subprocess.run(
    [
        "schtasks",
        "/create",
        "/f",
        "/sc", "onlogon",
        "/tn", USER_TASK_NAME,
        "/tr", f'"{PYTHON_EXE}" "{USER_DST}"'
    ],
    check=True
)

print("Installation completed successfully.")
print(f"Installed to: {INSTALL_DIR}")
