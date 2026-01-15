import base64
import json
import os
import socket
import urllib.request

# Base64-encoded Discord webhook URL
WEBHOOK_B64 = "PASTE_BASE64_WEBHOOK_HERE"

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
