#installed processes
import win32gui
import win32process
import psutil
import socket
import json 
import sys
import subprocess
import time
from pathlib import Path

#TO RUN SCRIPT: pythonw.exe "C:\Andrew C\Hackathon\Script Tests\app_monitor.py"

#host data
HOST = "127.0.0.1"
PORT = 5000
PROJECT_DIR = Path(r"C:\Andrew C\\Hackathon\\Project NAME TBD")
PROJECT_MAIN = PROJECT_DIR / "main.py"
LOCKED_APPS_FILE = PROJECT_DIR / "locked_apps.txt"

#shared config
hackathon_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(hackathon_dir))
import shared_config

shared_config.presage_main_run = False

def open_presage_process():
    #Pause monitoring until the Presage Pygame process closes.
    print("Opening Presage authentication...")
    shared_config.presage_main_run = True
    presage_process = subprocess.Popen(
        [sys.executable, str(PROJECT_MAIN), "--presage"],
        cwd=PROJECT_DIR,
    )
    #presage_process.wait()
    while shared_config.presage_main_run:
        time.sleep(1)  # Wait for 1 second before checking again
    
    print("Presage closed. Resuming application monitoring...")


def get_open_applications():
    applications = []

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return #if window isnt visible skip it (removes background processes)
            
        title = win32gui.GetWindowText(hwnd) #title of window

        if not title:
            return

        try: #try to get the application name and window title, if it fails skip it
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)

            applications.append({
                "pid": pid, #PROCESS ID i.e. 1234
                "name": process.name(), #OPERATION NAME i.e. "chrome.exe"
                "window": title #WINDOW TITLE i.e. "Hackathon - Google Docs"
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    win32gui.EnumWindows(callback, None)

    return applications

def read_textfile(file_path):
    entries = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            # .strip() removes the trailing newline character (\n)
            entry = line.strip()
            if entry:
                entries.append(entry)
    return entries

def main():
    allowed_pids = set()

    while True:
        applications = get_open_applications()
        active_pids = {application["pid"] for application in applications}
        allowed_pids.intersection_update(active_pids)
        locked_apps = [entry.lower() for entry in read_textfile(LOCKED_APPS_FILE)]
        locked_application = None

        for application in applications:
            if application["pid"] in allowed_pids:
                continue
            process_name = Path(application["name"]).stem.lower()
            window_title = application["window"].lower()
            if process_name in locked_apps or any(
                locked_app in window_title for locked_app in locked_apps
            ):
                locked_application = application
                break

        if locked_application:
            print(
                f"Locked application detected: {locked_application['name']} - "
                f"{locked_application['window']}",
                flush=True,
            )
            if open_presage_process():
                allowed_pids.add(locked_application["pid"])

        time.sleep(3)

if __name__ == "__main__":
    main()