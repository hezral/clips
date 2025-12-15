from .session import is_wayland_session
from .wayland_utils import (
    copy_to_clipboard_wayland,
    copy_files_to_clipboard_wayland,
    paste_from_clipboard_wayland
)

def copy_to_clipboard(clipboard_target, file, type=None):
    if is_wayland_session():
        return copy_to_clipboard_wayland(clipboard_target, file, type)
    else:
        return _copy_to_clipboard_xclip(clipboard_target, file, type)

def _copy_to_clipboard_xclip(clipboard_target, file, type=None):
    ''' Function to copy files to clipboard '''
    from subprocess import Popen, PIPE

    try:
        if "url" in type:
            with open(file) as _file:
                data = Popen(['echo', _file.readlines()[0].rstrip("\n").rstrip("\n")], stdout=PIPE)
                Popen(['xclip', '-selection', 'clipboard', '-target', clipboard_target], stdin=data.stdout)
        else:
            Popen(['xclip', '-selection', 'clipboard', '-target', clipboard_target, '-i', file])
        return True
    except:
        return False

def copy_files_to_clipboard(uris):
    if is_wayland_session():
        return copy_files_to_clipboard_wayland(uris)
    else:
        return _copy_files_to_clipboard_xclip(uris)

def _copy_files_to_clipboard_xclip(uris):
    ''' Function to copy files to clipboard from a string of uris in file:// format '''
    from subprocess import Popen, PIPE
    try:
        copyfiles = Popen(['xclip', '-selection', 'clipboard', '-target', 'x-special/gnome-copied-files'], stdin=PIPE)
        copyfiles.communicate(str.encode(uris))
        return True
    except:
        return False

def paste_from_clipboard():
    if is_wayland_session():
        return paste_from_clipboard_wayland()
    else:
        return _paste_from_clipboard_xlib()

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
