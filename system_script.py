import os
import socket
import requests
import getpass

WEBHOOK_URL = "https://discord.com/api/webhooks/PUT/YOUR/WEBHOOK/HERE"

try:
    username = getpass.getuser()
except Exception:
    username = "N/A"

computer_name = socket.gethostname()

message = (
    "⚙️ **System Startup Detected**\n"
    f"**Running As:** {username}\n"
    f"**Computer:** {computer_name}"
)

requests.post(WEBHOOK_URL, json={"content": message})
