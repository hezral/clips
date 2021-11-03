# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

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
    def __init__(self, app, reveal_callback, sensitivity=5, *args, **kwargs):
        
        self.app = app
        self.reveal_callback = reveal_callback
        self.init_variables()
        self.init_listener()
        self.needed_shake_count = sensitivity

    def init_variables(self, *args):
        self.showing_timestamp = datetime.now()
        self.shake_slice_timestamp = datetime.now()
        self.shake_timeout_timestamp = datetime.now()
        self.showing_timestamp_diff = 0
        self.shake_slice_timestamp_diff = 0
        self.shake_timeout_timestamp_diff = 0
        
        self.now_x = 0
        self.old_x = 0
        self.min_x = 0
        self.max_x = 0
        self.has_min = 0
        self.has_max = 0

        self.shake_count = 0
        
        self.showing = False
        self.isShaking = False

    def init_listener(self, *args):
        self.listener = mouse.Listener(
            on_move=self.detect_mouse_movement,
            on_click=None,
            on_scroll=None)
        self.listener.start()
        self.running = True
        print(datetime.now(), "shake_listener started")

    def remove_listener(self, *args):
        self.listener.stop()
        self.listener = mouse.Listener(
            on_move=None,
            on_click=None,
            on_scroll=None)
        self.listener.stop()
        self.running = False

    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            try:
                if button.name == "left":
                    self.mouse_pressed = True
            except AttributeError:
                pass
        else:
            self.mouse_pressed = False

    def detect_mouse_movement(self, x, y):
        if self.app.main_window is not None:
            if not self.app.main_window.is_visible():
                # state = "is_shaking:{0}, shake_count:{1}, showing:{2}".format(self.isShaking, self.shake_count, self.showing)
                # details1 = "now_x:{0}, old_x:{1}".format(self.now_x, self.old_x)
                # details2 = "min_x:{0}, max_x:{1}".format(self.min_x, self.max_x)
                # details3 = "has_min:{0}, has_max:{1}".format(self.has_min, self.has_max)
                # details4 = "showing_timestamp:{0}".format(self.showing_timestamp)
                # details5 = "shake_timeout_timestamp:{0}".format(self.shake_timeout_timestamp)
                # details6 = "shake_timeout_timestamp_diff:{0}".format(self.shake_timeout_timestamp_diff)
                # details7 = "shake_slice_timestamp:{0}".format(self.shake_slice_timestamp)
                # details8 = "shake_slice_timestamp_diff:{0}".format(self.shake_slice_timestamp_diff)
                # details9 = "self.shake_timeout_timestamp_diff >= SHAKE_TIMEOUT:{0}".format(self.shake_timeout_timestamp_diff >= SHAKE_TIMEOUT)
                # details10 = "self.shake_slice_timestamp_diff >= SHAKE_SLICE_TIMEOUT:{0}".format(self.shake_slice_timestamp_diff >= SHAKE_SLICE_TIMEOUT)
                # details11 = "self.max_x-self.min_x > SHAKE_DIST:{0}".format(self.max_x-self.min_x > SHAKE_DIST)
                # update = "{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n{8}\n{9}\n{10}\n{11}\n".format(state, details1, details2, details3, details4, details5, details6, details7, details8, details9, details10, details11)
                # update = state
                # print(update)
                # print(x,y)

                self.now_x = x
                if self.now_x < self.old_x:
                    if self.has_min == 0:
                        self.has_min = 1
                        self.min_x = self.now_x
                    else:
                        self.min_x = min(self.min_x, self.now_x)

                elif self.now_x > self.old_x:
                    if self.has_max == 0:
                        self.has_max = 1
                        self.max_x = self.now_x
                    else:
                        self.max_x = max(self.max_x, self.now_x)

                self.old_x = self.now_x

                self.is_shaking()

    def is_shaking(self):
        self.isShaking = False

        self.shake_timeout_timestamp_diff = int((datetime.now()-self.shake_timeout_timestamp).total_seconds()*1000)
        if self.shake_timeout_timestamp_diff >= SHAKE_TIMEOUT:
            self.init_variables()

        self.shake_slice_timestamp_diff = int((datetime.now()-self.shake_slice_timestamp).total_seconds()*1000)
        if self.shake_slice_timestamp_diff >= SHAKE_SLICE_TIMEOUT:
            self.shake_slice_timestamp = datetime.now()

            if self.has_min == 1:
                if self.has_max == 1:
                    if self.max_x-self.min_x > MIN_SHAKE_DIST and self.max_x-self.min_x < MAX_SHAKE_DIST:
                        self.shake_count += 1
                        self.shake_timeout_timestamp = datetime.now()
                        self.has_min = 0
                        self.has_max = 0
            
            if self.shake_count >= self.needed_shake_count:
                self.isShaking = True
                GLib.idle_add(self.reveal_app, None)
                self.init_variables()

    def reveal_app(self, *args):
        self.showing = True
        self.reveal_callback()
        # self.listener.stop()

