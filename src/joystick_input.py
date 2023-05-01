import pygame
import pyautogui
import time
import pygetwindow as gw
from pyrect import Rect

# gw.pointInRect()

# Function to resize the selected window based on joystick input
def resize_window(x, y, window):
    if window is not None:
        window.resize(window.width + x, window.height + y)
        
def find_selected_window(windows):
    position = pyautogui.position()
    if windows is not None:
        for window in windows:
            left, top = window.topleft
            right, bottom = window.bottomright
            rect = Rect(left, top, right - left, bottom - top)
            if rect.collide(position):
                return window
    return None

# Initialize pygame and joystick
pygame.init()
pygame.joystick.init()

# Assign the PlayStation controller
ps_controller = pygame.joystick.Joystick(0)
ps_controller.init()

# Function to move cursor based on joystick input and snap to the nearest visual element
def move_cursor(x, y):
    current_position = pyautogui.position()
    new_position = (current_position[0] + x, current_position[1] + y)
    pyautogui.moveTo(new_position)

    windows = gw.getAllWindows()
    selected_window = find_selected_window(windows)
    if selected_window is not None:
        snap_window(selected_window, windows)

# Function to handle left and right mouse button clicks
def mouse_click(button):
    if button == "LMB":
        pyautogui.click(button='left')
    elif button == "RMB":
        pyautogui.click(button='right')

# Function to move the selected window based on joystick input
def move_window(x, y, window):
    if window is not None:
        window.move(window.left + x, window.top + y)

# Function to snap the selected window to the screen edges or other windows
def snap_window(window, windows):
    if window is None:
        return
    print(f"snap_window called on {window.title}")
    snap_threshold = 20  # Adjust the threshold as needed
    
    left, top = window.topleft
    right, bottom = window.bottomright
    screen_rect = Rect(left, top, right - left, bottom - top)

    for win in windows:
        if win != window:
            # Snap to the horizontal edges of other windows
            if abs(window.left - win.right) <= snap_threshold:
                window.left = win.right
            elif abs(window.right - win.left) <= snap_threshold:
                window.left = win.left - window.width

            # Snap to the vertical edges of other windows
            if abs(window.top - win.bottom) <= snap_threshold:
                window.top = win.bottom
            elif abs(window.bottom - win.top) <= snap_threshold:
                window.top = win.top - window.height

    # Snap to the screen edges
    if abs(window.left) <= snap_threshold:
        window.left = 0
    elif abs(window.right - screen_rect.width) <= snap_threshold:
        window.left = screen_rect.width - window.width

    if abs(window.top) <= snap_threshold:
        window.top = 0
    elif abs(window.bottom - screen_rect.height) <= snap_threshold:
        window.top = screen_rect.height - window.height

# Main loop to continuously check for joystick input
while True:
    pygame.event.pump()
    time.sleep(0.1)

    # Get joystick axes values for cursor movement
    x_axis = ps_controller.get_axis(0) * 100  # Adjust the sensitivity as needed
    y_axis = ps_controller.get_axis(1) * 100  # Adjust the sensitivity as needed

    # Move cursor based on joystick axes values
    move_cursor(x_axis, y_axis)

    # Check if LMB or RMB are pressed
    lmb_pressed = ps_controller.get_button(0)  # Assuming button 0 is LMB
    rmb_pressed = ps_controller.get_button(1)  # Assuming button 1 is RMB

    # Perform mouse click if LMB or RMB is pressed
    if lmb_pressed:
        mouse_click("LMB")
    elif rmb_pressed:
        mouse_click("RMB")

    # Check if a window movement button is pressed (replace with correct button numbers)
    move_window_pressed = ps_controller.get_button(2)
    snap_window_pressed = ps_controller.get_button(3)

    # Move and snap window if the corresponding buttons are pressed
    if move_window_pressed or snap_window_pressed:
        windows = gw.getAllWindows()
        selected_window = find_selected_window(windows)

        if move_window_pressed:
            move_window(x_axis, y_axis, selected_window)
        elif snap_window_pressed:
            snap_window(selected_window, windows)
