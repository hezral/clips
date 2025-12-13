# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

"""
DBus Clipboard Monitor for Clips

Listens to clipboard change signals from the clips-clipboard-daemon and
integrates with the existing clipboard_manager.py processing code.
"""

import subprocess
import os
from typing import Optional, Callable, List

from pydbus import SessionBus
from gi.repository import GLib
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk


# DBus service details (must match daemon)
DBUS_SERVICE = "com.github.hezral.clips.Clipboard"
DBUS_PATH = "/com/github/hezral/clips/Clipboard"
DBUS_INTERFACE = "com.github.hezral.clips.Clipboard"


class DBusClipboardSelectionData:
    """
    Mimics Gtk.SelectionData interface for DBus clipboard data.
    Compatible with clipboard_manager.py processing code.
    """

    def __init__(self, data: bytes, mime_type: str):
        self._data = data
        self._mime_type = mime_type

    def get_data(self) -> bytes:
        return self._data

    def get_text(self) -> Optional[str]:
        if self._data is None:
            return None
        try:
            return self._data.decode('utf-8')
        except:
            return None

    def get_data_type(self) -> str:
        return self._mime_type


class DBusClipboardMonitor:
    """
    Clipboard monitor using DBus signals from clips-clipboard-daemon.

    This avoids the polling overhead in the main app by delegating to
    a separate daemon process.
    """

    def __init__(self, gtk_application):
        self.app = gtk_application
        self._on_clipboard_change: Optional[Callable] = None
        self._bus = None
        self._daemon_proxy = None
        self._signal_match = None
        self._running = False

    def set_clipboard_callback(self, callback: Callable):
        """Set callback for clipboard changes."""
        self._on_clipboard_change = callback

    def is_available(self) -> bool:
        """Check if DBus clipboard daemon is available."""
        try:
            # Initialize DBus
            bus = SessionBus()

            # Try to get daemon object
            daemon = bus.get(DBUS_SERVICE, DBUS_PATH)

            # Ping to verify it's alive
            if daemon.Ping():
                self.app.logger.info("Found running clipboard daemon")
                return True
            return False

        except Exception as e:
            if "was not provided" in str(e) or "not found" in str(e).lower():
                # Daemon not running, try to start it
                return self._start_daemon()
            self.app.logger.error(f"DBus error: {e}")
            return False

    def _start_daemon(self) -> bool:
        """Attempt to start the clipboard daemon."""
        try:
            self.app.logger.info("Starting clipboard daemon...")

            # Find the daemon script
            daemon_script = os.path.join(
                os.path.dirname(__file__),
                'clips_clipboard_daemon.py'
            )

            if not os.path.exists(daemon_script):
                self.app.logger.error(f"Daemon script not found: {daemon_script}")
                return False

            # Start daemon as background process
            subprocess.Popen(
                ['python3', daemon_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True  # Detach from parent
            )

            # Wait for daemon to start (max 5 seconds)
            import time
            for i in range(10):
                time.sleep(0.5)
                try:
                    bus = SessionBus()
                    daemon = bus.get(DBUS_SERVICE, DBUS_PATH)
                    if daemon.Ping():
                        self.app.logger.info("Daemon started successfully")
                        return True
                except:
                    continue

            self.app.logger.error("Daemon failed to start within 5 seconds")
            return False

        except Exception as e:
            self.app.logger.error(f"Error starting daemon: {e}")
            return False

    def start(self):
        """Start listening to clipboard signals."""
        if self._running:
            return

        try:
            # Initialize DBus connection
            self._bus = SessionBus()

            # Get daemon proxy
            self._daemon_proxy = self._bus.get(DBUS_SERVICE, DBUS_PATH)

            # Connect to ClipboardChanged signal
            self._signal_match = self._bus.subscribe(
                sender=DBUS_SERVICE,
                object=DBUS_PATH,
                iface=DBUS_INTERFACE,
                signal="ClipboardChanged",
                signal_fired=self._on_clipboard_changed_signal
            )

            self._running = True
            self.app.logger.info("DBus clipboard monitor started")

        except Exception as e:
            self.app.logger.error(f"Failed to start DBus monitor: {e}")
            raise

    def stop(self):
        """Stop listening to clipboard signals."""
        if not self._running:
            return

        try:
            if self._signal_match and self._bus:
                self._bus.unsubscribe(self._signal_match)
                self._signal_match = None

            self._daemon_proxy = None
            self._bus = None
            self._running = False

            self.app.logger.info("DBus clipboard monitor stopped")

        except Exception as e:
            self.app.logger.error(f"Error stopping DBus monitor: {e}")

    def _on_clipboard_changed_signal(self, mime_types):
        """Handle ClipboardChanged signal from daemon."""
        if not self._on_clipboard_change:
            return

        try:
            # Convert DBus array to Python list
            mime_types_list = list(mime_types)

            self.app.logger.debug(f"DBus clipboard signal: {mime_types_list[:3]}...")

            # Create data getter function
            def get_data(mime_type: str) -> Optional[bytes]:
                return self._get_clipboard_data(mime_type)

            # Schedule callback on main thread
            GLib.idle_add(
                self._on_clipboard_change,
                mime_types_list,
                get_data
            )

        except Exception as e:
            self.app.logger.error(f"Error processing clipboard signal: {e}")

    def _get_clipboard_data(self, mime_type: str) -> Optional[bytes]:
        """Get clipboard data from daemon via DBus method call."""
        if not self._daemon_proxy:
            return None

        try:
            data = self._daemon_proxy.GetClipboardData(
                mime_type,
                dbus_interface=DBUS_INTERFACE
            )

            if data:
                return bytes(data)
            return None

        except Exception as e:
            self.app.logger.debug(f"Error getting clipboard data for {mime_type}: {e}")
            return None

    def get_selection_data(self, mime_type: str, data: bytes) -> DBusClipboardSelectionData:
        """Create a SelectionData-compatible object."""
        return DBusClipboardSelectionData(data, mime_type)

    def convert_to_gdk_atom(self, mime_type: str) -> Gdk.Atom:
        """Convert MIME type string to Gdk.Atom."""
        return Gdk.Atom.intern(mime_type, False)
