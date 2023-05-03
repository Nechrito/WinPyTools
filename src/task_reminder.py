import os
import shutil
import tempfile
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import time
import json
import threading

from datetime import datetime
from plyer import notification

root: tk.Tk = None
reminder: tk.Tk = None

exit_event = threading.Event()

font_name: str = "Helvetica"

title: str = "Task Reminder"
settings_file: str = "reminder_settings.json"
settings_dir: str = ""

if os.name == "nt":
    settings_dir = os.path.join(os.getenv("LOCALAPPDATA"), title)
else:
    settings_dir = os.path.join(
        os.path.expanduser("~"), ".cache", "task_reminder")

settings_path = os.path.join(settings_dir, settings_file)

# Create the temp_directory
os.makedirs(settings_dir, exist_ok=True)


def process_persistent_path():
    if not os.path.exists(settings_path):
        print("Settings file not found, creating a new one")
        os.makedirs(settings_dir, exist_ok=True)
        save_settings(1200, 5, "Don't forget to take a break!")
    print(f"Settings path: {settings_path}")


def terminate_instances():
    import psutil

    # get a list of all running processes
    self_pid = os.getpid()
    for proc in psutil.process_iter():

        # our process is named python so we need to check the full path
        if "python" in proc.name():

            if os.path.basename(__file__).replace(".py", "") in repr(proc.cmdline()):

                if proc.pid == self_pid:
                    continue
                print("Terminating process: ", proc.pid)
                psutil.Process(proc.pid).kill()
                break


def exit_program():
    print("Exiting from main window")
    exit_event.set()
    try:
        root.destroy()
    finally:
        exit(1)

# Save settings to a file


def save_settings(wait_duration_seconds, display_duration_seconds, message):
    settings_data = {
        "wait_duration_seconds": wait_duration_seconds,
        "display_duration_seconds": display_duration_seconds,
        "message": message
    }

    with open(settings_path, "w") as f:
        json.dump(settings_data, f, indent=4)

# Load settings from a file


def load_settings():

    # # Create a default settings file if it doesn't exist
    # if not os.path.exists(settings_path):
    #     save_settings(3600, 5, "Don't forget to take a break!")

    try:
        with open(settings_path, "r") as f:
            settings_data = json.load(f)
            wait_duration_seconds = settings_data["wait_duration_seconds"]
            display_duration_seconds = settings_data["display_duration_seconds"]
            message = settings_data["message"]
            return wait_duration_seconds, display_duration_seconds, message
    except FileNotFoundError:
        return 3600, 5, "Don't forget to take a break!"

# Show the reminder


def show_reminder(message, display_duration, exit_event):
    def exit_program():
        print("Exiting from reminder")
        exit_event.set()
        reminder.destroy()
        try:
            root.destroy()
        finally:
            exit(1)

    if exit_event.is_set():
        return

    reminder = ThemedTk(theme="arc")
    # reminder.title("Reminder")
    reminder.attributes('-topmost', True)
    reminder.attributes("-toolwindow", True)
    reminder.overrideredirect(1)  # Hide the window border and title bar

    bg_color = reminder.cget('bg')  # Get the window background color
    tk.Label(reminder, text=message, font=(font_name, 20),
             bg=bg_color).pack(padx=20, pady=20)

    # Create a new style for the bigger Exit button
    style = ttk.Style()
    style.configure('BiggerExit.TButton', padding=10, font=(font_name, 12))

    ttk.Button(reminder, text="Exit", command=exit_program,
               style='BiggerExit.TButton').pack(pady=14)

    reminder.update_idletasks()
    width = reminder.winfo_width()
    height = reminder.winfo_height()
    x = (reminder.winfo_screenwidth() // 2) - (width // 2)
    y = (reminder.winfo_screenheight() // 2) - (height // 2)
    reminder.geometry(f'{width}x{height}+{x}+{y}')

    reminder.after(display_duration * 1000, reminder.destroy)
    reminder.mainloop()

# Start the reminders


def start_reminders(duration, message, display_duration, exit_event):
    while not exit_event.is_set():
        show_reminder(message, display_duration, exit_event)
        time.sleep(duration)

# Create the settings window


def create_settings_window():
    def save_and_start():
        interval_choice = interval_var.get()
        if interval_choice == "Hourly":
            wait_duration_seconds = 3600
        elif interval_choice == "Daily":
            wait_duration_seconds = 86400
        else:
            wait_duration_seconds = int(wait_duration_seconds_var.get())

        display_duration_seconds = int(display_duration_seconds_var.get())
        message = message_var.get()
        save_settings(wait_duration_seconds, display_duration_seconds, message)
        root.destroy()

        reminder_thread = threading.Thread(target=start_reminders, args=(
            wait_duration_seconds, message, display_duration_seconds, exit_event))
        reminder_thread.start()

    root = ThemedTk(theme="arc")
    root.title("Reminder Settings")

    style = ttk.Style()
    style.configure('Custom.TEntry', padding=14, font=(font_name, 12))
    style.configure('Custom.TButton', padding=6, font=(
        font_name, 12))  # Reduced padding values
    style.configure('Custom.TCombobox', padding=14, font=(font_name, 12))

    labels = ["Reminder Interval", "Pause Interval",
              "Show Time", "Reminder Message"]
    for i, text in enumerate(labels):
        tk.Label(root, text=text, font=(font_name, 14)).grid(
            row=i, column=0, padx=5, pady=7, sticky="w")

    interval_var = tk.StringVar()
    wait_duration_seconds_var = tk.StringVar()
    display_duration_seconds_var = tk.StringVar()
    message_var = tk.StringVar()

    wait_duration_seconds_saved, display_duration_seconds_saved, message_saved = load_settings()
    wait_duration_seconds_var.set(wait_duration_seconds_saved)
    display_duration_seconds_var.set(display_duration_seconds_saved)
    message_var.set(message_saved)

    interval_combobox = ttk.Combobox(root, textvariable=interval_var, values=(
        "Hourly", "Daily", "Custom"), state="readonly", style='Custom.TCombobox')
    interval_combobox.grid(row=0, column=1, padx=10, pady=14)

    entries = [wait_duration_seconds_var,
               display_duration_seconds_var, message_var]
    for i, var in enumerate(entries):
        ttk.Entry(root, textvariable=var, style='Custom.TEntry').grid(
            row=i+1, column=1, padx=10, pady=14)

    ttk.Button(root, text="Save and Start", command=save_and_start,
               style='Custom.TButton').grid(row=4, columnspan=2, pady=14)
    ttk.Button(root, text="Exit", command=exit_program,
               style='Custom.TButton').grid(row=5, columnspan=2, pady=14)

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    root.mainloop()


terminate_instances()
process_persistent_path()

try:
    create_settings_window()
except Exception as e:
    print("Error creating settings window: " + str(e))
    exit(0)
