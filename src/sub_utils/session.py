import os

def is_wayland_session():
    return "WAYLAND_DISPLAY" in os.environ
