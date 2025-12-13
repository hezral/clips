#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

"""
Clips Clipboard Daemon - DBus Service

A background daemon that monitors the Wayland clipboard and emits DBus signals
when changes are detected. This isolates the polling mechanism from the main app,
preventing UI interference.

DBus Interface: com.github.hezral.clips.Clipboard
Object Path: /com/github/hezral/clips/Clipboard
Signal: ClipboardChanged(mime_types: as)
"""

import subprocess
import hashlib
import time
import sys
import signal
from typing import Optional, List

from pydbus import SessionBus
from gi.repository import GLib

# DBus service details
DBUS_SERVICE = "com.github.hezral.clips.Clipboard"
DBUS_PATH = "/com/github/hezral/clips/Clipboard"
DBUS_INTERFACE = "com.github.hezral.clips.Clipboard"


# DBus interface XML definition
DBUS_XML = f"""
<node>
    <interface name='{DBUS_INTERFACE}'>
        <method name='GetClipboardData'>
            <arg type='s' name='mime_type' direction='in'/>
            <arg type='ay' name='data' direction='out'/>
        </method>
        <method name='Ping'>
            <arg type='b' name='alive' direction='out'/>
        </method>
        <signal name='ClipboardChanged'>
            <arg type='as' name='mime_types'/>
        </signal>
    </interface>
</node>
"""


class ClipboardDaemon:
    """
    DBus service that monitors clipboard and emits signals on changes.
    """

    # Declare pydbus interface
    dbus = DBUS_XML

    def __init__(self, poll_interval=2.0):
        """
        Initialize the daemon.

        Args:
            poll_interval: Seconds between clipboard checks (default: 2.0)
        """
        self.poll_interval = poll_interval
        self.last_hash = None
        self.running = True

        print(f"Clipboard daemon started (polling every {poll_interval}s)")
        print(f"DBus service: {DBUS_SERVICE}")
        print(f"Object path: {DBUS_PATH}")

        # Start monitoring
        GLib.timeout_add(int(poll_interval * 1000), self._check_clipboard)

    def _get_clipboard_hash(self) -> Optional[str]:
        """Get hash of current clipboard content."""
        try:
            result = subprocess.run(
                ['wl-paste', '--no-newline'],
                capture_output=True,
                timeout=0.5,
                stderr=subprocess.DEVNULL
            )

            if result.returncode == 0 and result.stdout:
                return hashlib.md5(result.stdout).hexdigest()
            return None

        except (subprocess.TimeoutExpired, Exception):
            return None

    def _get_mime_types(self) -> List[str]:
        """Get available MIME types in clipboard."""
        try:
            result = subprocess.run(
                ['wl-paste', '--list-types'],
                capture_output=True,
                timeout=1,
                stderr=subprocess.DEVNULL
            )

            if result.returncode == 0:
                mime_types = result.stdout.decode('utf-8').strip().split('\n')
                return [mt.strip() for mt in mime_types if mt.strip()]
            return []

        except (subprocess.TimeoutExpired, Exception):
            return []

    def _check_clipboard(self) -> bool:
        """
        Check clipboard for changes and emit signal if changed.

        Returns:
            bool: True to continue checking, False to stop
        """
        if not self.running:
            return False

        current_hash = self._get_clipboard_hash()

        if current_hash and current_hash != self.last_hash:
            print(f"Clipboard changed: {self.last_hash} -> {current_hash}")
            self.last_hash = current_hash

            # Get MIME types
            mime_types = self._get_mime_types()

            if mime_types:
                print(f"  MIME types: {mime_types[:3]}...")  # Show first 3
                # Emit DBus signal
                self.ClipboardChanged(mime_types)

        return True  # Continue checking

    def ClipboardChanged(self, mime_types):
        """
        DBus signal emitted when clipboard changes.

        Args:
            mime_types: List of available MIME types in clipboard
        """
        # Signal is automatically emitted by pydbus when this is called
        pass

    def GetClipboardData(self, mime_type):
        """
        DBus method to retrieve clipboard data for a specific MIME type.

        Args:
            mime_type: The MIME type to retrieve

        Returns:
            bytes: Clipboard data
        """
        try:
            result = subprocess.run(
                ['wl-paste', '--type', mime_type],
                capture_output=True,
                timeout=2,
                stderr=subprocess.DEVNULL
            )

            if result.returncode == 0:
                return result.stdout
            return b''

        except Exception as e:
            print(f"Error getting clipboard data: {e}")
            return b''

    def Ping(self):
        """
        DBus method to check if daemon is alive.

        Returns:
            bool: Always True
        """
        return True

    def stop(self):
        """Stop the daemon."""
        print("Stopping clipboard daemon...")
        self.running = False


def check_wl_clipboard() -> bool:
    """Check if wl-clipboard is available."""
    try:
        result = subprocess.run(
            ['wl-paste', '--version'],
            capture_output=True,
            timeout=2
        )
        return result.returncode == 0
    except:
        return False


def main():
    """Main entry point."""
    # Check if wl-clipboard is available
    if not check_wl_clipboard():
        print("ERROR: wl-clipboard not found!", file=sys.stderr)
        print("Install with: sudo apt install wl-clipboard", file=sys.stderr)
        return 1

    # Initialize DBus
    bus = SessionBus()

    # Check if daemon is already running
    try:
        existing = bus.get(DBUS_SERVICE, DBUS_PATH)
        if existing.Ping():
            print(f"Daemon already running at {DBUS_SERVICE}")
            return 0
    except:
        pass  # Not running, continue

    # Create daemon
    daemon = ClipboardDaemon(poll_interval=2.0)

    # Publish on DBus
    bus.publish(DBUS_SERVICE, (DBUS_PATH, daemon))

    # Setup signal handlers
    loop = GLib.MainLoop()

    def signal_handler(sig, frame):
        daemon.stop()
        loop.quit()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run main loop
    print("Daemon running. Press Ctrl+C to stop.")

    try:
        loop.run()
    except KeyboardInterrupt:
        daemon.stop()

    print("Daemon stopped.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
