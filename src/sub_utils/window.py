from .session import is_wayland_session
from .logging_utils import log_function_calls


@log_function_calls
def get_active_window():

    if is_wayland_session():
        # TODO: Implement for Wayland
        return None
    else:
        return _get_active_window_xlib()

@log_function_calls
def _get_active_window_xlib():

    ''' Function to get active window '''
    import Xlib
    import Xlib.display

    display = Xlib.display.Display()
    root = display.screen().root

    NET_ACTIVE_WINDOW = display.intern_atom('_NET_ACTIVE_WINDOW')

    root.change_attributes(event_mask=Xlib.X.FocusChangeMask)
    try:
        window_id = root.get_full_property(NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType).value[0]
        window = display.create_resource_object('window', window_id)
    except Xlib.error.XError: #simplify dealing with BadWindow
        window = None

    return window

@log_function_calls
def set_active_window(window):

    if is_wayland_session():
        # TODO: Implement for Wayland
        pass
    else:
        _set_active_window_by_xwindow(window)

@log_function_calls
def _set_active_window_by_xwindow(window):

    ''' Function to set window as active based on x window '''
    import Xlib
    from Xlib.display import Display
    from Xlib import X

    display = Display()

    window.circulate(X.RaiseLowest)
    window.set_input_focus(X.RevertToParent, X.CurrentTime)
    window.configure(stack_mode=X.Above)
    display.flush()
    display.sync()
