import os
import time
import ctypes
import subprocess
from shutil import copyfile

# Define the location of Paint 3D project files
PAINT3D_PROJECTS_PATH = os.path.join(os.environ['USERPROFILE'], '3D Objects')

# Define the backup directory
BACKUP_DIR = os.path.join(os.environ['USERPROFILE'], 'Paint3D_Backups')
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# Check if Paint 3D is running
def is_paint3d_running():
    process_list = os.popen('tasklist /FI "IMAGENAME eq PaintStudio.View.exe"').read()
    return "PaintStudio.View.exe" in process_list

# Save and close Paint 3D
def save_and_close_paint3d():
    subprocess.Popen("taskkill /IM PaintStudio.View.exe /F")

# Backup Paint 3D project files
def backup_paint3d_projects():
    for file in os.listdir(PAINT3D_PROJECTS_PATH):
        if file.endswith(".glb"):
            source = os.path.join(PAINT3D_PROJECTS_PATH, file)
            destination = os.path.join(BACKUP_DIR, f"{file}_{time.strftime('%Y%m%d_%H%M%S')}")
            copyfile(source, destination)

def main():
    if is_paint3d_running():
        save_and_close_paint3d()
        time.sleep(2)  # Give some time for Paint 3D to save and close
        backup_paint3d_projects()

if __name__ == "__main__":
    main()
