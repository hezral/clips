import os
import shutil
import subprocess
import logging
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gio, GLib, Gdk
from ..constants import APP_ID

logger = logging.getLogger(APP_ID)
from .logging_utils import log_function_calls


@log_function_calls
def get_active_appinfo_wayland(data=None):

    """
    Get active application info.
    Note: AT-SPI access is restricted in flatpak sandbox, so this currently
    returns "unknown app" on Wayland. Active window detection works on X11 only.
    """
    desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    source_app = "unknown app"
    source_icon = "application-default-icon"

    logger.debug(f"Desktop environment: {desktop_env}")
    logger.debug(f"Active window detection is not available on Wayland (flatpak sandbox restriction)")

    return source_app, source_icon

@log_function_calls
def paste_from_clipboard_wayland(app=None):
    """
    Paste from clipboard using Mutter RemoteDesktop.
    """
    is_terminal = False
    if app and hasattr(app, 'window_manager'):
        active_app = app.window_manager.last_seen.get('title')
        if active_app:
            terminals = ["terminal", "term", "konsole", "uxterm", "xterm", "tilix", "alacritty", "kitty", "gnome-terminal"]
            if any(term in active_app.lower() for term in terminals):
                is_terminal = True
                logger.debug(f"Terminal detected: {active_app}")

    try:
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        res = bus.call_sync(
            "org.gnome.Mutter.RemoteDesktop",
            "/org/gnome/Mutter/RemoteDesktop",
            "org.gnome.Mutter.RemoteDesktop",
            "CreateSession",
            None,
            GLib.VariantType.new("(o)"),
            Gio.DBusCallFlags.NONE,
            -1,
            None
        )
        session_path = res.unpack()[0]
        
        bus.call_sync(
            "org.gnome.Mutter.RemoteDesktop",
            session_path,
            "org.gnome.Mutter.RemoteDesktop.Session",
            "Start",
            None,
            None,
            Gio.DBusCallFlags.NONE,
            -1,
            None
        )

        control_l = Gdk.keyval_from_name("Control_L")
        shift_l = Gdk.keyval_from_name("Shift_L")
        v_key = Gdk.keyval_from_name("v")

        # Helper to send key
        def send_key(keyval, pressed):
            bus.call_sync(
                "org.gnome.Mutter.RemoteDesktop",
                session_path,
                "org.gnome.Mutter.RemoteDesktop.Session",
                "NotifyKeyboardKeysym",
                GLib.Variant("(ub)", [keyval, pressed]),
                None,
                Gio.DBusCallFlags.NONE,
                -1,
                None
            )

        # Press keys
        send_key(control_l, True)
        if is_terminal:
            send_key(shift_l, True)
        send_key(v_key, True)

        # Release keys
        send_key(v_key, False)
        if is_terminal:
            send_key(shift_l, False)
        send_key(control_l, False)

        # Stop session
        bus.call_sync(
            "org.gnome.Mutter.RemoteDesktop",
            session_path,
            "org.gnome.Mutter.RemoteDesktop.Session",
            "Stop",
            None,
            None,
            Gio.DBusCallFlags.NONE,
            -1,
            None
        )
        return True
    except Exception as e:
        logger.debug(f"Error in paste_from_clipboard_wayland: {e}")
        return False

@log_function_calls
def copy_to_clipboard_wayland(clipboard_target, file, type=None):

    """
    Copy content to clipboard using wl-copy on Wayland.

    Note: The caller should set clipboard_manager._skip_clipboard_monitoring flag
    before calling this to prevent the clipboard monitor from capturing the change.
    """
    logger.debug(f"copy_to_clipboard_wayland: target={clipboard_target}, type={type}, file={file}")

    if shutil.which("wl-copy") is not None:
        try:
            if "url" in type:
                with open(file) as _file:
                    data = _file.readlines()[0].rstrip("\n")
                    # Use Popen to avoid blocking - wl-copy needs to stay running in background
                    logger.debug(f"Starting wl-copy for URL (non-blocking)")
                    subprocess.Popen(["wl-copy", data])
            elif "text/plain" in clipboard_target or "text" in type:
                with open(file, 'r') as f:
                    content = f.read()
                    # Use Popen with PIPE for stdin, write asynchronously
                    logger.debug(f"Starting wl-copy for text (non-blocking)")
                    proc = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
                    # Write to stdin and close it, but don't wait for process to complete
                    proc.stdin.write(content.encode('utf-8'))
                    proc.stdin.close()
            else: # for files, images, etc., pipe file content to wl-copy
                # For images and binary files, read and pipe to stdin
                # Use subprocess.run to ensure data is fully written before returning
                logger.debug(f"Starting wl-copy for image/file with type {clipboard_target}")
                with open(file, 'rb') as f:
                    subprocess.run(["wl-copy", "--type", clipboard_target], stdin=f, check=True)
            logger.debug(f"copy_to_clipboard_wayland: Successfully started wl-copy")
            return True
        except (subprocess.CalledProcessError, OSError, BrokenPipeError) as e:
            logger.debug(f"copy_to_clipboard_wayland: Error: {e}")
            return False
    else:
        logger.debug(f"copy_to_clipboard_wayland: wl-copy not found")
        return False

@log_function_calls
def copy_files_to_clipboard_wayland(uris):

    if shutil.which("wl-copy") is not None:
        try:
            # wl-copy expects URI list via stdin for text/uri-list type
            # The uris parameter is already in the correct format (newline-separated file:// URIs)
            logger.debug(f"Starting wl-copy for files with text/uri-list")
            proc = subprocess.Popen(["wl-copy", "--type", "text/uri-list"], stdin=subprocess.PIPE)
            proc.stdin.write(uris.encode('utf-8'))
            proc.stdin.close()
            # Don't wait for the process - wl-copy needs to stay alive to serve clipboard
            return True
        except (OSError, BrokenPipeError) as e:
            logger.debug(f"copy_files_to_clipboard_wayland: Error: {e}")
            return False
    else:
        return False
