import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import time
import json
import tempfile
import os
import threading

root: tk.Tk = None
reminder: tk.Tk = None

exit_event = threading.Event()

font_name: str = "Inter Medium"

def exit_program():
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

    with open("reminder_settings.json", "w") as f:
        json.dump(settings_data, f, indent=4)

# Load settings from a file
def load_settings():
    try:
        with open("reminder_settings.json", "r") as f:
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
        print("Exiting program")
        exit_event.set()
        reminder.destroy()
        try:
            root.destroy()
        finally:
            exit(1)

    if exit_event.is_set():
        return

    reminder = ThemedTk(theme="arc")
    #reminder.title("Reminder")
    reminder.attributes('-topmost', True)
    reminder.attributes("-toolwindow", True)
    reminder.overrideredirect(1)  # Hide the window border and title bar

    bg_color = reminder.cget('bg')  # Get the window background color
    tk.Label(reminder, text=message, font=(font_name, 20), bg=bg_color).pack(padx=20, pady=20)
    ttk.Button(reminder, text="Exit", command=exit_program, style='Custom.TButton').pack(pady=10) 

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

        reminder_thread = threading.Thread(target=start_reminders, args=(wait_duration_seconds, message, display_duration_seconds, exit_event))
        reminder_thread.start()

    root = ThemedTk(theme="arc")
    root.title("Task Reminder Settings")

    style = ttk.Style()
    style.configure('Custom.TEntry', font=(font_name, 14))
    style.configure('Custom.TButton', font=(font_name, 14))
    style.configure('Custom.TMenubutton', font=(font_name, 14))
    style.configure('Custom.TCombobox', font=(font_name, 14))

    tk.Label(root, text="Reminder Interval:", font=(font_name, 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    tk.Label(root, text="Pause Interval (s):", font=(font_name, 14)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
    tk.Label(root, text="Show Time (s):", font=(font_name, 14)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
    tk.Label(root, text="Reminder Message:", font=(font_name, 14)).grid(row=3, column=0, padx=10, pady=10, sticky="w")

    interval_var = tk.StringVar()
    wait_duration_seconds_var = tk.StringVar()
    display_duration_seconds_var = tk.StringVar()
    message_var = tk.StringVar()

    # Load saved settings
    wait_duration_seconds_saved, display_duration_seconds_saved, message_saved = load_settings()
    wait_duration_seconds_var.set(wait_duration_seconds_saved)
    display_duration_seconds_var.set(display_duration_seconds_saved)
    message_var.set(message_saved)

    interval_combobox = ttk.Combobox(root, textvariable=interval_var, values=("Hourly", "Daily", "Custom"), state="readonly", style='Custom.TCombobox')
    interval_combobox.grid(row=0, column=1, padx=10, pady=10)

    ttk.Entry(root, textvariable=wait_duration_seconds_var, style='Custom.TEntry').grid(row=1, column=1, padx=10, pady=10)
    ttk.Entry(root, textvariable=display_duration_seconds_var, style='Custom.TEntry').grid(row=2, column=1, padx=10, pady=10)
    ttk.Entry(root, textvariable=message_var, style='Custom.TEntry').grid(row=3, column=1, padx=10, pady=10)

    ttk.Button(root, text="Save and Start", command=save_and_start, style='Custom.TButton').grid(row=4, columnspan=2, pady=10)
    ttk.Button(root, text="Exit", command=exit_program, style='Custom.TButton').grid(row=5, columnspan=2, pady=10)

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()

try:
    create_settings_window()
except Exception as e:
    print("Error creating settings window: " + str(e))
    exit(0)
