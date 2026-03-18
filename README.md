# Program File and Folder Structure

This README documents the files and folders created by the program, starting from `download/download.bat`. The program assumes that each GitHub URL corresponds to an equivalent file in the local folder structure. The `newsetup` folder is ignored, and `EXPERIMENTAL=False` is assumed for `system_script.py`.

## Files and Folders Created

### Installation Directory
- `C:\Program Files\SecurityServices\`
  - `system_agent.py` (copied from `setup/system_agent.py`)
  - `user_agent.py` (copied from `setup/user_agent.py`)

### Temporary Files and Directories
- `%TEMP%\MyTempWork\` (temporary working directory, cleaned up after execution)
  - `installpython.bat` (downloaded from GitHub)
  - `downloader.py` (downloaded from GitHub)
- `%TEMP%\SecurityServices\` (log directory created by agents)
  - `debug.log` (debug log file for agents)
- Random temporary files in `%TEMP%` with random names and extensions (created by agents to run downloaded scripts)

### Log Files
- `C:\Windows\Temp\SecutiryServicesLogsSystem.txt` (system agent log, if logging is enabled)
- `C:\Windows\Temp\SecutiryServicesLogsUser.txt` (user agent log, if logging is enabled)

## Scheduled Tasks Created

The program creates the following scheduled tasks using `schtasks`:

### System Task
- **Task Name**: `MyApp_SystemAgent`
- **Run As**: `SYSTEM`
- **Schedule**: Every 1 minute
- **Command**: `"pythonw.exe" "C:\Program Files\SecurityServices\system_agent.py"`

### User Task
- **Task Name**: `MyApp_UserAgent` (or `MyApp_UserAgent{base64_encoded_username}` if username does not end with "pt_ptsi")
- **Run As**: Current logged-in user (`DOMAIN\Username`)
- **Schedule**: Every 1 minute
- **Command**: `"pythonw.exe" "C:\Program Files\SecurityServices\user_agent.py"`

## Program Flow
1. `download/download.bat` downloads and executes `installpython.bat` to install Python if not present.
2. Downloads and runs `downloader.py`.
3. `downloader.py` downloads files from the `setup` folder on GitHub and runs `install.py`.
4. `install.py` sets up the installation directory, copies agent files, and creates scheduled tasks.
5. The scheduled tasks run the agents, which download and execute `system_script.py` and `user_script.py` respectively in a loop.
