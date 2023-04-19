import os
import subprocess
import psutil

def get_active_rider_window():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'Rider' in proc.info['name']:
            for cmdline in proc.info['cmdline']:
                if 'Rider' in cmdline:
                    return proc
    return None

def get_opened_file_in_rider(proc):
    for f in proc.open_files():
        if f.path.endswith('.cs'):
            return f.path
    return None

def open_file_in_vscode(file_path):
    subprocess.run(['code', file_path])

rider_proc = get_active_rider_window()
if rider_proc:
    opened_file = get_opened_file_in_rider(rider_proc)
    if opened_file:
        open_file_in_vscode(opened_file)
    else:
        print("No C# file is currently opened in Rider.")
else:
    print("Rider is not running.")
