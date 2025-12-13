# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

"""
Wayland clipboard monitor using wl-clipboard (wl-paste --watch).

This provides background clipboard monitoring on Wayland compositors that
don't support the wlr-data-control/ext-data-control protocols (like Gala).

Falls back to using the wl-paste command from the wl-clipboard package,
which polls the clipboard for changes.
"""

import subprocess
import threading
from typing import Optional, Callable, List
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import GLib, Gdk


class WlClipboardSelectionData:
    """
    Mimics Gtk.SelectionData interface for wl-clipboard data.
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


class WlClipboardMonitor:
    """
    Background clipboard monitor using wl-clipboard polling.

    Polls clipboard every 500ms for changes using wl-paste. Works on any
    Wayland compositor, including those without data-control protocol (like Gala).
    """

    def __init__(self, gtk_application):
        self.app = gtk_application
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._on_clipboard_change: Optional[Callable] = None

    def set_clipboard_callback(self, callback: Callable):
        """Set callback for clipboard changes."""
        self._on_clipboard_change = callback

    def is_available(self) -> bool:
        """Check if wl-clipboard (wl-paste) is available."""
        try:
            result = subprocess.run(
                ['wl-paste', '--version'],
                capture_output=True,
                timeout=2
            )
            available = result.returncode == 0
            if available:
                self.app.logger.info("wl-clipboard (wl-paste) is available")
            else:
                self.app.logger.warning("wl-paste command failed")
            return available
        except FileNotFoundError:
            self.app.logger.warning(
                "wl-clipboard not found. Install with: sudo apt install wl-clipboard"
            )
            return False
        except Exception as e:
            self.app.logger.error(f"Error checking wl-clipboard: {e}")
            return False

    def start(self):
        """Start clipboard monitoring using wl-paste polling."""
        if self._running:
            return

        if not self.is_available():
            raise RuntimeError("wl-clipboard not available")

        self._running = True
        self._thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="clips-wlclipboard-monitor"
        )
        self._thread.start()

        self.app.logger.info("wl-clipboard polling monitor started (checking every 2 seconds)")

    def stop(self):
        """Stop clipboard monitoring."""
        self._running = False

        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

        self.app.logger.info("wl-clipboard monitor stopped")

    def _monitor_loop(self):
        """
        Main monitoring loop using polling.

        Since wl-paste --watch requires data-control protocol (which Gala lacks),
        we use polling instead: check clipboard every 500ms for changes.
        """
        import hashlib
        import time

        # Initialize with current clipboard to avoid treating it as "new"
        last_hash = self._get_clipboard_hash()
        self.app.logger.debug(f"wl-clipboard monitor initialized (initial hash: {last_hash})")

        while self._running:
            try:
                # Get current clipboard content hash
                current_hash = self._get_clipboard_hash()

                # If hash changed, clipboard has new content
                if current_hash and current_hash != last_hash:
                    self.app.logger.debug(f"Clipboard changed: {last_hash} -> {current_hash}")
                    last_hash = current_hash
                    self._process_clipboard_change()

                # Poll every 2 seconds (less aggressive, reduces interference)
                time.sleep(2.0)

            except Exception as e:
                if self._running:
                    self.app.logger.error(f"wl-clipboard monitor error: {e}")
                    time.sleep(1)

    def _process_clipboard_change(self):
        """Process clipboard change and notify callback."""
        if not self._on_clipboard_change:
            return

        try:
            # Get available MIME types
            mime_types = self._get_mime_types()

            if not mime_types:
                return

            self.app.logger.debug(f"wl-clipboard: {mime_types}")

            # Create a data getter function
            def get_data(mime_type: str) -> Optional[bytes]:
                return self._get_clipboard_data(mime_type)

            # Schedule callback on main GTK thread
            GLib.idle_add(
                self._on_clipboard_change,
                mime_types,
                get_data
            )

        except Exception as e:
            self.app.logger.error(f"Error processing clipboard: {e}")

    def _get_mime_types(self) -> List[str]:
        """Get list of available MIME types in clipboard."""
        try:
            result = subprocess.run(
                ['wl-paste', '--list-types'],
                capture_output=True,
                timeout=1
            )

            if result.returncode != 0:
                return []

            # Parse MIME types from output
            mime_types = result.stdout.decode('utf-8').strip().split('\n')
            return [mt.strip() for mt in mime_types if mt.strip()]

        except Exception as e:
            self.app.logger.error(f"Error getting MIME types: {e}")
            return []

    def _get_clipboard_hash(self) -> Optional[str]:
        """Get a hash of the current clipboard content to detect changes."""
        import hashlib

        try:
            # Try to get text content first (most common)
            # Use very short timeout and suppress errors to minimize interference
            result = subprocess.run(
                ['wl-paste', '--no-newline'],
                capture_output=True,
                timeout=0.5,
                stderr=subprocess.DEVNULL
            )

            if result.returncode == 0 and result.stdout:
                # Hash the content
                return hashlib.md5(result.stdout).hexdigest()
            else:
                return None

        except subprocess.TimeoutExpired:
            # Skip this cycle if wl-paste is taking too long
            return None
        except Exception:
            return None

    def _get_clipboard_data(self, mime_type: str) -> Optional[bytes]:
        """Get clipboard data for a specific MIME type."""
        try:
            result = subprocess.run(
                ['wl-paste', '--type', mime_type],
                capture_output=True,
                timeout=2
            )

            if result.returncode == 0:
                return result.stdout
            else:
                return None

        except Exception as e:
            self.app.logger.debug(f"Error getting clipboard data for {mime_type}: {e}")
            return None

    def get_selection_data(self, mime_type: str, data: bytes) -> WlClipboardSelectionData:
        """Create a SelectionData-compatible object."""
        return WlClipboardSelectionData(data, mime_type)

    def convert_to_gdk_atom(self, mime_type: str) -> Gdk.Atom:
        """Convert MIME type string to Gdk.Atom."""
        return Gdk.Atom.intern(mime_type, False)
