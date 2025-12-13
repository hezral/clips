# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2023 Adi Hezral <hezral@gmail.com>

"""
Universal active window manager using AT-SPI accessibility bus.
Works on both X11 and Wayland sessions.
Requires --no-a11y-bus flag when running in flatpak.
"""

import sys
import threading
import time
from typing import Dict, Optional

import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi, GLib


class ActiveWindowManager():
    """Wayland-compatible active window manager using AT-SPI."""

    stop_thread = False
    id_thread = None
    callback = None

    def __init__(self, gtk_application=None):
        super().__init__()
        self.app = gtk_application
        self.last_seen = {'title': None}
        self._polling_interval = 1.0  # Poll every second

    def _run(self, callback):
        self.callback = callback

        def init_manager():
            try:
                # Initialize AT-SPI connection
                Atspi.init()
                self.app.logger.info("AT-SPI initialized for active window detection")

                # Start polling for active window changes
                self.poll_active_window()

            except Exception as e:
                self.app.logger.error(f"Failed to initialize AT-SPI: {e}")
                self.app.logger.warning("Active window detection disabled")

        self.thread = threading.Thread(target=init_manager)
        self.thread.daemon = True
        self.thread.start()
        self.app.logger.info("active_window_manager (AT-SPI) started")

    def poll_active_window(self):
        """Poll for active window changes using AT-SPI."""
        # Get initial active app on startup
        first_run = True

        while not self.stop_thread:
            try:
                app_name = self.get_active_app()
                # On first run, always set the current app (even if no change)
                if first_run and app_name:
                    self.last_seen['title'] = app_name
                    self.app.logger.debug(f"Initial active app: {app_name}")
                    self.handle_change(self.last_seen)
                    first_run = False
                elif app_name and app_name != self.last_seen['title']:
                    self.last_seen['title'] = app_name
                    self.app.logger.debug(f"Active app changed to: {app_name}")
                    self.handle_change(self.last_seen)
            except Exception as e:
                self.app.logger.debug(f"Error polling active window: {e}")

            time.sleep(self._polling_interval)

    def get_active_app(self) -> Optional[str]:
        """Get the active application name using AT-SPI."""
        try:
            desktop = Atspi.get_desktop(0)
            if not desktop:
                return None

            count = desktop.get_child_count()

            # Loop through all running applications
            for i in range(count):
                app = desktop.get_child_at_index(i)
                if not app:
                    continue

                # Loop through windows of the application
                w_count = app.get_child_count()
                for j in range(w_count):
                    window = app.get_child_at_index(j)
                    if not window:
                        continue

                    try:
                        states = window.get_state_set().get_states()
                        # Check if window is Active (focused)
                        if Atspi.StateType.ACTIVE in states:
                            app_name = app.get_name()
                            return app_name if app_name else None
                    except Exception:
                        continue

            return None

        except Exception as e:
            self.app.logger.debug(f"Error getting active app via AT-SPI: {e}")
            return None

    def _stop(self):
        self.app.logger.info("active_window_manager (AT-SPI) stopped")
        self.stop_thread = True

    def handle_change(self, new_state: dict):
        """This method is called when the active window changes."""
        GLib.idle_add(self.callback, new_state['title'])
