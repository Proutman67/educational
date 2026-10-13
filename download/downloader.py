import os
import requests
import subprocess
from pathlib import Path
import sys

# ===== CONFIG =====
OWNER = "Proutman67"          # github username or org
REPO = "educational"       # repository name
SUBFOLDER = "setup"      # path inside repo
FILE_TO_RUN = "install.py"    # file to call after download
BRANCH = "main"            # usually "main" or "master"
# ==================

API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{SUBFOLDER}?ref={BRANCH}"

PYTHON_EXE = Path(sys.executable).with_name("pythonw.exe")

def download_files():
    response = requests.get(API_URL)
    response.raise_for_status()
    files = response.json()

    for item in files:
        if item["type"] == "file":
            file_name = item["name"]
            download_url = item["download_url"]

            print(f"Downloading {file_name}...")
            file_data = requests.get(download_url).content

            with open(file_name, "wb") as f:
                f.write(file_data)

def run_file():
    print(f"\nRunning {FILE_TO_RUN}...\n")
    subprocess.run([PYTHON_EXE, FILE_TO_RUN], check=True)

if __name__ == "__main__":
    download_files()
    run_file()