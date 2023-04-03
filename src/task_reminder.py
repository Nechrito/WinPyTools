import tkinter as tk
import time
import json
import tempfile
import os

root: tk.Tk = None
root = tk.Tk()
# def exit_program(element: tk.Tk):
#         element.destroy()
        
#         if element != root:
#             root.destroy()
            
#         exit(0)
        
def exit_program():
    root.destroy()
    exit(0)

def save_settings(duration, message):
    settings = {"duration": int(duration), "message": message}
    with open(os.path.join(tempfile.gettempdir(), 'reminder_settings.json'), 'w') as file:
        json.dump(settings, file)

def load_settings():
    try:
        with open(os.path.join(tempfile.gettempdir(), 'reminder_settings.json'), 'r') as file:
            settings = json.load(file)
            return settings['duration'], settings['message']
    except FileNotFoundError:
        return 1800, "Focus on your tasks!"

import threading

def show_reminder(message, display_duration, exit_event):
    def exit_program():
        exit_event.set()
        reminder.destroy()
        try:
            if root:
                root.destroy()  # Add this line to close the settings window and exit the program
        except:
            print("Error closing reminder window.")
        finally:
            exit(0)  # Add this line to exit the program
        
    if exit_event.is_set():
        return


    reminder = tk.Tk()
    reminder.title("Task Reminder")
    reminder.attributes('-topmost', True)  # Keep the window on top
    reminder.attributes("-toolwindow", True)  # Hide from taskbar
    reminder.resizable(0, 0)  # Disable resizing the window
    #reminder.protocol("WM_DELETE_WINDOW", exit_program)  # Disable closing the window
    reminder.overrideredirect(True)
    tk.Label(reminder, text=message, font=("Helvetica", 20)).pack(padx=20, pady=20)
    tk.Button(reminder, text="Exit", command=exit_program, font=("Helvetica", 14)).pack(pady=10)

    # Center the window on the screen
    reminder.update_idletasks()
    width = reminder.winfo_width()
    height = reminder.winfo_height()
    x = (reminder.winfo_screenwidth() // 2) - (width // 2)
    y = (reminder.winfo_screenheight() // 2) - (height // 2)
    reminder.geometry(f'{width}x{height}+{x}+{y}')
    
    reminder.after(display_duration * 1000, reminder.destroy)
    reminder.mainloop()

def start_reminders(duration, message, display_duration, exit_event):
    while not exit_event.is_set():
        show_reminder(message, display_duration, exit_event)
        time.sleep(duration)
        
def create_settings_window():
    def save_and_start():
        wait_duration_seconds = int(wait_duration_seconds_var.get())
        display_duration_seconds = int(display_duration_seconds_var.get())
        message = message_var.get()
        save_settings(wait_duration_seconds, message)
        root.destroy()
        reminder_thread = threading.Thread(target=start_reminders, args=(wait_duration_seconds, message, display_duration_seconds, exit_event))
        reminder_thread.start()

    root.attributes("-toolwindow", True)  # Hide from taskbar
    root.title("Task Reminder Settings")

    tk.Label(root, text="Wait Duration (seconds):", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    tk.Label(root, text="Display Duration (seconds):", font=("Helvetica", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
    tk.Label(root, text="Reminder Message:", font=("Helvetica", 14)).grid(row=2, column=0, padx=10, pady=10, sticky="w")

    wait_duration_seconds_var = tk.StringVar()
    display_duration_seconds_var = tk.StringVar()
    message_var = tk.StringVar()

    wait_duration, message = load_settings()
    wait_duration_seconds_var.set(str(wait_duration))
    display_duration_seconds_var.set("5")  # Set a default value for display_duration
    message_var.set(message)

    tk.Entry(root, textvariable=wait_duration_seconds_var, font=("Helvetica", 14)).grid(row=0, column=1, padx=10, pady=10)
    tk.Entry(root, textvariable=display_duration_seconds_var, font=("Helvetica", 14)).grid(row=1, column=1, padx=10, pady=10)
    tk.Entry(root, textvariable=message_var, font=("Helvetica", 14)).grid(row=2, column=1, padx=10, pady=10)

    tk.Button(root, text="Save and Start", command=save_and_start, font=("Helvetica", 14)).grid(row=3, columnspan=2, pady=10)

     # Add the Exit button
    tk.Button(root, text="Exit", command=exit_program, font=("Helvetica", 14)).grid(row=4, columnspan=2, pady=10)

    root.mainloop()


exit_event = threading.Event()
try:
    create_settings_window()
except:
    print("Error creating settings window.")
    exit(0)