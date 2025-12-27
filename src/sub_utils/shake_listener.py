# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
from ..utils import log_function_calls


import time
from datetime import datetime

from pynput import mouse

SHAKE_DIST = 100
MIN_SHAKE_DIST = 50
MAX_SHAKE_DIST = 250
SHAKE_SLICE_TIMEOUT = 75 # ms
SHAKE_TIMEOUT = 500 # ms
EVENT_TIMEOUT = 100 # ms
SHOWING_TIMEOUT = 2500 #ms
NEEDED_SHAKE_COUNT = 5

class ShakeListener():
    @log_function_calls
    def __init__(self, app, reveal_callback, sensitivity=5, *args, **kwargs):

        self.app = app
        self.reveal_callback = reveal_callback
        
        # Optimized detection constants
        self.VELOCITY_THRESHOLD = 5 # Lowered to increase sensitivity
        self.MIN_REVERSALS = 4
        self.TIME_WINDOW = 1.0 # Increased to be more forgiving
        
        self.init_variables()
        self.init_listener()

        # Initial sensitivity setup
        self.update_sensitivity(sensitivity)

    @log_function_calls
    def update_sensitivity(self, sensitivity):
        """Updates the number of reversals needed based on sensitivity (3-10)."""
        # Mapping: Higher sensitivity = fewer reversals needed
        # 3 -> 10 reversals
        # 5 -> 8 reversals
        # 10 -> 4 reversals
        self.needed_reversals = max(3, 13 - int(float(sensitivity)))
        self.app.logger.debug(f"Shake sensitivity updated: {sensitivity} (needed_reversals: {self.needed_reversals})")

    @log_function_calls
    def init_variables(self, *args):
        self.reversals = []
        self.last_x_dir = 0
        self.last_y_dir = 0
        self.last_pos = None # (x, y)
        self.showing = False

    @log_function_calls
    def init_listener(self, *args):

        self.listener = mouse.Listener(
            on_move=self.detect_mouse_movement,
            on_click=None,
            on_scroll=None)
        self.listener.start()
        self.running = True
        self.app.logger.info("shake_listener started")

    @log_function_calls
    def remove_listener(self, *args):

        self.listener.stop()
        self.listener = mouse.Listener(
            on_move=None,
            on_click=None,
            on_scroll=None)
        self.listener.stop()
        self.running = False

    @log_function_calls
    def on_mouse_click(self, x, y, button, pressed):

        if pressed:
            try:
                if button.name == "left":
                    self.mouse_pressed = True
            except AttributeError:
                pass
        else:
            self.mouse_pressed = False

    @log_function_calls
    def detect_mouse_movement(self, x, y, *args):
        """Processes absolute mouse coordinates into deltas for shake detection."""
        if self.app.main_window is not None and not self.app.main_window.is_visible():
            if self.last_pos is None:
                self.last_pos = (x, y)
                return

            dx = x - self.last_pos[0]
            dy = y - self.last_pos[1]
            self.last_pos = (x, y)

            if self.process_motion(dx, dy):
                GLib.idle_add(self.reveal_app)

    @log_function_calls
    def process_motion(self, dx, dy):
        """Core detection logic: counts direction reversals within a time window."""
        now = datetime.now()

        # 1. Filter old reversals
        self.reversals = [t for t in self.reversals if (now - t).total_seconds() < self.TIME_WINDOW]

        # 2. Velocity filter (ignore slow movements/noise)
        velocity = (dx**2 + dy**2)**0.5
        if velocity < self.VELOCITY_THRESHOLD:
            return False
            
        # Optional: log high velocity movements for debugging
        # self.app.logger.debug(f"Motion: dx={dx:.1f}, dy={dy:.1f}, vel={velocity:.1f}")

        # 3. Detect current direction
        current_x_dir = 1 if dx > 0 else (-1 if dx < 0 else 0)
        current_y_dir = 1 if dy > 0 else (-1 if dy < 0 else 0)

        # 4. Check for reversals (X or Y)
        reversed_x = (self.last_x_dir != 0 and current_x_dir != 0 and self.last_x_dir != current_x_dir)
        reversed_y = (self.last_y_dir != 0 and current_y_dir != 0 and self.last_y_dir != current_y_dir)

        if reversed_x or reversed_y:
            self.reversals.append(now)
            self.app.logger.debug(f"Reversal detected! Window count: {len(self.reversals)}/{self.needed_reversals}")
            if len(self.reversals) >= self.needed_reversals:
                self.app.logger.debug("SHAKE DETECTED!")
                self.reversals = []
                return True

        if current_x_dir != 0: self.last_x_dir = current_x_dir
        if current_y_dir != 0: self.last_y_dir = current_y_dir
        
        return False


    @log_function_calls
    def reveal_app(self, *args):

        self.showing = True
        self.reveal_callback()
        # self.listener.stop()

