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


def open_presage_process():
    #Pause monitoring until the Presage Pygame process closes.
    print("Opening Presage authentication...")
    presage_process = subprocess.Popen(
        [sys.executable, str(PROJECT_MAIN), "--presage"],
        cwd=PROJECT_DIR,
    )
    presage_process.wait()
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
                "name": process.name(), #OPERATION NAME i.e. "chrome.exe"
                "window": title #WINDOW TITLE i.e. "Hackathon - Google Docs"
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    win32gui.EnumWindows(callback, None)

    return applications

def read_textfile(file_path):
    list = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            # .strip() removes the trailing newline character (\n)
            list.append(line.strip())
    return list
            


while True:
    while True:
        valid = False
        if valid == False:
            apps = get_open_applications() #get all applications
            application_names = [app["name"] for app in apps] #get all application names
            application_windows = [app["window"] for app in apps] #get all application window titles    
            locked_apps = read_textfile("C:\\Andrew C\\Hackathon\\Project NAME TBD\\locked_apps.txt") #get locked apps
            for i, application_name in enumerate(application_names): #check if any of the open applications are in the locked apps list
               # print(f"Checking application: {application_name} - {application_windows[i]}") #print the name and window title of the app being checked
                (app_name, app_ext) = application_name.split(".") #split the name and extension of the application
                if app_name in locked_apps:
                    print(f"Locked application detected: {application_name} - {application_windows[i]}") #print the name and window title of the locked app
                    valid=True
            for i, application_window in enumerate(application_windows): #check if any of the open application windows are in the locked apps list
                if locked_apps and any(locked_app.lower() in application_window.lower() for locked_app in locked_apps):
                    print(f"Locked application detected: {application_names[i]} - {application_windows[i]}") #print the name and window title of the locked app
                    valid=True
        if valid == True:
            print("Locked application detected. Pausing monitoring.")
           # sys.exit(1) #exit the script to allow the main.py to open the presage process
            open_presage_process()
            break
        time.sleep(3) #3 sec break