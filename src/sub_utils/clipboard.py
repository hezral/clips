from .session import is_wayland_session
from .logging_utils import log_function_calls
import logging
import shutil
import subprocess
from gi.repository import Gio, GLib, Gdk
from ..constants import APP_ID

logger = logging.getLogger(APP_ID)


@log_function_calls
def copy_to_clipboard(clipboard_target, file, type=None):

    if is_wayland_session():
        return copy_to_clipboard_wayland(clipboard_target, file, type)
    else:
        return _copy_to_clipboard_xclip(clipboard_target, file, type)

@log_function_calls
def _copy_to_clipboard_xclip(clipboard_target, file, type=None):

    ''' Function to copy files to clipboard '''

    try:
        if "url" in type:
            with open(file) as _file:
                data = subprocess.Popen(['echo', _file.readlines()[0].rstrip("\n").rstrip("\n")], stdout=subprocess.PIPE)
                subprocess.Popen(['xclip', '-selection', 'clipboard', '-target', clipboard_target], stdin=data.stdout)
        else:
            subprocess.Popen(['xclip', '-selection', 'clipboard', '-target', clipboard_target, '-i', file])
        return True
    except:
        return False

@log_function_calls
def copy_files_to_clipboard(uris):

    if is_wayland_session():
        return copy_files_to_clipboard_wayland(uris)
    else:
        return _copy_files_to_clipboard_xclip(uris)

@log_function_calls
def _copy_files_to_clipboard_xclip(uris):

    ''' Function to copy files to clipboard from a string of uris in file:// format '''
    try:
        copyfiles = subprocess.Popen(['xclip', '-selection', 'clipboard', '-target', 'x-special/gnome-copied-files'], stdin=subprocess.PIPE)
        copyfiles.communicate(str.encode(uris))
        return True
    except:
        return False

@log_function_calls
def paste_from_clipboard(app=None):

    if is_wayland_session():
        return paste_from_clipboard_wayland(app)
    else:
        return _paste_from_clipboard_xlib()

@log_function_calls
def _paste_from_clipboard_xlib():

    '''
    Function to paste from clipboard based on where the mouse pointer is hovering
    '''
    # ported from Clipped: https://github.com/davidmhewitt/clipped/blob/edac68890c2a78357910f05bf44060c2aba5958e/src/ClipboardManager.vala
    import time

    def perform_key_event(accelerator, press, delay):
        import Xlib
        from Xlib import X
        from Xlib.display import Display
        from Xlib.ext.xtest import fake_input
        from Xlib.protocol.event import KeyPress, KeyRelease
        import time

        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, Gdk, GdkX11

        keysym, modifiers = Gtk.accelerator_parse(accelerator)
        display = Display()
        # root = display.screen().root
        # window = root.query_pointer().child
        # window.set_input_focus(X.RevertToParent, X.CurrentTime)
        # window.configure(stack_mode=X.Above)
        # display.sync()

        keycode = display.keysym_to_keycode(keysym)

        if press:
            event_type = X.KeyPress
        else:
            event_type = X.KeyRelease

        if keycode != 0:
            if 'GDK_CONTROL_MASK' in modifiers.value_names:
                modcode = display.keysym_to_keycode(Gdk.KEY_Control_L)
                fake_input(display, event_type, modcode, delay)

            if 'GDK_SHIFT_MASK' in modifiers.value_names:
                modcode = display.keysym_to_keycode(Gdk.KEY_Shift_L)
                fake_input(display, event_type, modcode, delay)

            fake_input(display, event_type, keycode, delay)
            display.sync()

    perform_key_event("<Control>v", True, 100)
    perform_key_event("<Control>v", False, 0)
    logger.debug("paste_from_clipboard_xlib")


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
        logger.debug("paste_from_clipboard_wayland")
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
