# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2023 Your Name <your@email.com>


import os
from contextlib import contextmanager
from typing import Any, Dict, Optional, Tuple, Union

import threading
import gi
from gi.repository import GLib

from pydbus import SessionBus
from pydbus.generic import signal

class ActiveWindowManager():
    """A Wayland-compatible active window manager."""

    stop_thread = False
    id_thread = None
    callback = None

    def __init__(self, gtk_application=None):
        super().__init__()
        self.app = gtk_application
        self.last_seen = {'title': None}
        self.desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()

    def _run(self, callback):
        self.callback = callback

        def init_manager():
            if "gnome" in self.desktop_env or "pantheon" in self.desktop_env:
                self.run_gnome_pantheon()
            else:
                self.app.logger.warning(
                    f"Unsupported desktop environment for Wayland: {self.desktop_env}"
                )

        self.thread = threading.Thread(target=init_manager)
        self.thread.daemon = True
        self.thread.start()
        self.app.logger.info("active_window_manager (Wayland) started")

    def run_gnome_pantheon(self):
        
        loop = GLib.MainLoop()
        
        def on_focus_changed(sender, obj, iface, signal, params):
            wm_class = params[0]
            if wm_class and wm_class != self.last_seen['title']:
                self.last_seen['title'] = wm_class
                self.handle_change(self.last_seen)
        
        bus = SessionBus()
        try:
            shell_proxy = bus.get("org.gnome.Shell")
            
            # Get initial focus
            self.get_initial_focus(shell_proxy)
            
            # Subscribe to focus changes
            bus.subscribe(
                sender="org.gnome.Shell",
                iface="org.gnome.Shell",
                signal="FocusAppChanged",
                object="/org/gnome/Shell",
                arg0=None,
                flags=0,
                signal_fired=on_focus_changed
            )
            
            loop.run()
        except Exception as e:
            self.app.logger.error(f"Failed to connect to GNOME Shell D-Bus: {e}")


    def _stop(self):
        self.app.logger.info("active_window_manager (Wayland) stopped")
        self.stop_thread = True

    def get_initial_focus(self, shell_proxy):
        try:
            windows = shell_proxy.get_windows()
            for window in windows:
                if window.HasFocus:
                    self.on_focus_changed(window.WmClass)
                    break
        except Exception as e:
            self.app.logger.error(f"Failed to get initial window focus: {e}")

    def on_focus_changed(self, wm_class):
        if wm_class and wm_class != self.last_seen['title']:
            self.last_seen['title'] = wm_class
            self.handle_change(self.last_seen)

    def handle_change(self, new_state: dict):
        """This method is called when the active window changes."""
        GLib.idle_add(self.callback, new_state['title'])
