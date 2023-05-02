import asyncio
import collections
import math
import sys
import time
import pygame
from typing import List, Tuple
import pyautogui
from pygetwindow import pointInRect, getWindowsAt, getWindowsWithTitle, getAllTitles, getAllWindows, getActiveWindow, getActiveWindowTitle
pyautogui.FAILSAFE = False

from pygetwindow import Win32Window
from pygame.joystick import JoystickType

# from pygetwindow import Point as Point
# from pygetwindow import Point as Point_Win32
# from pyautogui import Point as Point_Auto
from pyrect import Rect

Rect_Win32 = collections.namedtuple("Rect", "left top right bottom")
Point = collections.namedtuple("Point", "x y")
Size = collections.namedtuple("Size", "width height")

import keyboard

FPS = 120

async def handle_keyboard_events():
    print("Starting keyboard event handler...")

    while True:
        event = await asyncio.get_event_loop().run_in_executor(None, keyboard.read_event)

        if event.event_type == keyboard.KEY_DOWN:
            print(f"Key {event.name} pressed")
            # Handle key press event
            # TODO: Quit Immediately
            pygame.quit()
            sys.exit()

        elif event.event_type == keyboard.KEY_UP:
            print(f"Key {event.name} released")
            # Handle key release event
        await asyncio.sleep(0.005)
class WindowManager:
    def __init__(self):
        self.dt: float = 0
        self.tick_rate: int = 0

        self.win_count: int = -1

        self.windows: List[Win32Window] = []
        self.overlaps: List[Win32Window] = []
        self.selected: Win32Window
        self.selected_title: str = ""

    def init(self, tick_rate: int, dt: float):

        point = Point(pyautogui.position().x, pyautogui.position().y)

        self.set_selected_window_at(point)

        self.dt = dt
        self.tick_rate = tick_rate

        print(f"resolution: {self.tick_rate}ms")
        print(f"delta time: {self.dt}")

        self.get_windows()

    def get_windows(self):
        all_windows = getAllWindows()

        if len(all_windows) != self.win_count:

            self.win_count = len(all_windows)
            self.windows = [window for window in all_windows if window.width >= 500 and window.height >= 500]
            self.windows.sort(key=lambda win: (win.isActive, win.visible, win.width * win.height))

            print(f"Windows: ({len(self.windows)}) / {len(all_windows)}")

    def get_top_5_windows(self):
        for window in self.overlaps[:2]:
            print(f"{window.title}: ({window.width}x{window.height}) | Active: {window.isActive} | Visible: {window.visible} | SELECTED: True")

        for window in self.windows[-5:]:
            print(f"{window.title}: ({window.width}x{window.height}) | Active: {window.isActive} | Visible: {window.visible}")

    def set_selected_window(self, win: Win32Window) -> Win32Window:
        if self.selected_title == win.title:
            self.selected = win
            return win

        print(f"New Window: {win.title}")

        self.selected_title = win.title
        self.selected = win

        return win

    def set_selected_window_at(self, point: Point) -> Win32Window:
        win = getWindowsAt(point.x, point.y)[0]
        return self.set_selected_window(win)

    def get_overlapping_windows(self, point: Point):
        all_overlaps = getWindowsAt(point.x, point.y)

        if len(all_overlaps) != len(self.overlaps):
            new_overlaps = [window for window in all_overlaps if window not in self.overlaps]

            print(f"Overlapping windows: {new_overlaps} ({len(new_overlaps)}) / {len(all_overlaps)}")

            self.overlaps = all_overlaps

class Controller:
    def __init__(self):
        self.controller: pygame.joystick.JoystickType
        self.movespeed = 50
        self.x_axis = 0
        self.y_axis = 0
        self.is_holding = False

    def init(self):
        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

        self.get_axes()

    def get_axes(self):
        pygame.event.poll()
        self.x_axis = self.controller.get_axis(0)
        self.y_axis = self.controller.get_axis(1)

    def press(self, button):
        if button == "LMB" and not self.is_holding:
            pyautogui.click(button="left")
        elif button == "RMB" and not self.is_holding:
            pyautogui.click(button="right")
        elif button == "ESC":
            pyautogui.press("esc")

    def hold(self):
        if not self.is_holding:
            self.is_holding = True
            pyautogui.mouseDown()

    def release(self):
        if self.is_holding:
            self.is_holding = False
            pyautogui.mouseUp()


class Cursor:
    def __init__(self, win: WindowManager):
        self.win: WindowManager = win
        self.point: Point = Point(0, 0)
        self.speed: float = 0.0
        self.is_moving: bool = False

    def init(self, speed: float):
        self.speed = 2009
        self.get_position()
        
    def move_to_relative(self, x: float, y: float) -> Point:
        dx = x - self.point.x
        dy = y - self.point.y
        return self.move(dx, dy)

    def move(self, dx: float, dy: float) -> Point:
        
        # Calculate the target position
        target_x = self.point.x + dx
        target_y = self.point.y + dy

        # Move the mouse cursor over time
        duration = math.sqrt((dx ** 2) + (dy ** 2)) / self.speed 
        
        pyautogui.moveTo(target_x, target_y, duration=duration)

        # Update the internal state
        self.point = Point(target_x, target_y)

        return self.point

    def get_position(self, x: float = 0, y: float = 0) -> Point:
        pos = pyautogui.position()
        

        if abs(pos.x - self.point.x) < abs(x) and abs(pos.y - self.point.y) < abs(y):
            print(f"{self.point}: {pos}")
            self.point = Point(pos.x, pos.y)
        else:
            self.point = Point(pos.x + x, pos.y + y)
        return self.point

    def set_position(self, x: float, y: float) -> None:
        x_rel, y_rel = self.get_relative_movement(x, y)

        pyautogui.moveRel(x_rel * self.speed, y_rel * self.speed, duration=0)

        self.point = Point(self.point.x + x_rel * self.speed, self.point.y + y_rel * self.speed)

    def get_relative_movement(self, x: float, y: float) -> Tuple[float, float]:
        x_rel = x - self.point.x
        y_rel = y - self.point.y

        return x_rel, y_rel
class MainLoop:
    def __init__(self, window_manager: WindowManager, cursor: Cursor, controller: Controller):
        self.win: WindowManager = window_manager
        self.cursor: Cursor = cursor
        self.controller: Controller = controller

    async def main_loop(self):
        pygame.init()
        pygame.event.pump()

        pygame.time.Clock().tick(FPS)

        dt: float = pygame.time.get_ticks() / 1000

        tick_rate = pygame.time.get_ticks()

        self.win.init(tick_rate=tick_rate, dt=dt)

        self.cursor.init(2 * 1000)

        self.controller.init()

        while True:
            pygame.event.pump()

            self.controller.get_axes()

            # Get the currently pressed buttons on the joystick
            # LMB = 0, RMB = 1, Move = 2, Snap = 3
            a_pressed = self.controller.controller.get_button(0)  # button 0 = A
            b_pressed = self.controller.controller.get_button(1)  # button 1 = B

            if a_pressed:
                self.controller.press("LMB")
            elif b_pressed:
                self.controller.press("RMB")
            await asyncio.sleep(0.01)
class App:          
    
    def __init__(self):        
        self.has_moved: bool = False
        self.queue: asyncio.Queue = asyncio.Queue()
        
        self.win = WindowManager()
        self.cursor: Cursor = Cursor(self.win)
        
        self.controller: Controller = Controller()
        self.main = MainLoop(self.win, self.cursor, self.controller)
    
    async def handle_events(self):
        await asyncio.sleep(0.001)

    async def refresh_task(self):
        print("Refresh Task Started")

        while True:
            pygame.event.pump()
            
            current_time = pygame.time.get_ticks()

            delay = 1 / FPS - (pygame.time.get_ticks() - current_time) / 1000.0
            
            self.win.dt = delay

            await self.handle_events()

    async def run(self):
        
        print("App started")

        self.queue = asyncio.Queue()

        self.tasks = [
            asyncio.ensure_future(self.main.main_loop()),
            asyncio.ensure_future(self.refresh_task()),
            asyncio.ensure_future(self.windows_task()),
            asyncio.ensure_future(self.handle_events()),
            asyncio.ensure_future(handle_keyboard_events()),
            asyncio.ensure_future(self.move_task()),
        ]

        print("Tasks started")

        await asyncio.gather(*self.tasks)

        print("App ended")

    async def move_task(self):
        print("Move task started")
        
        clock = pygame.time.Clock()
        
        dx_accum = 0
        dy_accum = 0
        
        while True:
            # limit the frame rate to 120 fps
            clock.tick(FPS) 
            pygame.event.pump()

            self.controller.get_axes()
                
            dx, dy = self.controller.x_axis, self.controller.y_axis
            
            self.cursor.get_position(self.controller.x_axis, self.controller.y_axis)
            
            dx = 0 if abs(dx) < 0.1 else dx
            dy = 0 if abs(dy) < 0.1 else dy
            
            dx_accum += dx * self.cursor.speed * self.win.dt
            dy_accum += dy * self.cursor.speed * self.win.dt
            
            if abs(dx_accum) >= 1 or abs(dy_accum) >= 1:
                # self.cursor.set_position(dx_accum, dy_accum)
                self.cursor.move(dx_accum, dy_accum)
                
                dx_accum -= math.trunc(dx_accum)
                dy_accum -= math.trunc(dy_accum)

            await asyncio.sleep(self.win.dt)

    async def windows_task(self):
        print("Windows task started")

        while True:
            self.win.get_overlapping_windows(self.cursor.point)
            
            await asyncio.sleep(1)

async def main():
    print("Starting")
    
    pygame.init()
    
    print("Pygame initialized")
    
    app = App()
    
    print("App initialized")
    
    try:
        print("Running")
        await app.run()
        print("Finished")
        
    except KeyboardInterrupt as e:
        print(f"Stopping because of {e}")
        
        # app.controller.controller.quit()
    
        pygame.quit()
        sys.exit()
        
    print(f"Done")

    pygame.quit()
    sys.exit()
    
if __name__ == "__main__":
    asyncio.run(main())