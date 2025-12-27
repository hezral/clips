# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

"""
Display backend detection for Clips.
Provides robust X11 vs Wayland detection, replacing the simple env check.
"""

import os
from enum import Enum
from typing import Optional
from .logging_utils import log_function_calls



class DisplayBackend(Enum):
    X11 = "x11"
    WAYLAND = "wayland"
    UNKNOWN = "unknown"


_detected_backend: Optional[DisplayBackend] = None


@log_function_calls
def detect_display_backend() -> DisplayBackend:

    """
    Detect the current display backend with proper precedence.
    
    Checks (in order):
    1. GDK_BACKEND environment override
    2. XDG_SESSION_TYPE 
    3. WAYLAND_DISPLAY / DISPLAY presence
    """
    global _detected_backend
    
    if _detected_backend is not None:
        return _detected_backend
    
    xdg_session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
    wayland_display = os.environ.get('WAYLAND_DISPLAY')
    display = os.environ.get('DISPLAY')
    gdk_backend = os.environ.get('GDK_BACKEND', '').lower()
    
    # GDK_BACKEND override takes precedence
    if gdk_backend == 'x11':
        _detected_backend = DisplayBackend.X11
    elif gdk_backend == 'wayland':
        _detected_backend = DisplayBackend.WAYLAND
    # XDG_SESSION_TYPE is the standard way
    elif xdg_session_type == 'wayland':
        _detected_backend = DisplayBackend.WAYLAND
    elif xdg_session_type == 'x11':
        _detected_backend = DisplayBackend.X11
    # Fallback to checking display env vars
    elif wayland_display and not display:
        _detected_backend = DisplayBackend.WAYLAND
    elif display and not wayland_display:
        _detected_backend = DisplayBackend.X11
    elif wayland_display and display:
        # Both set (XWayland scenario) - prefer Wayland native
        _detected_backend = DisplayBackend.WAYLAND
    else:
        _detected_backend = DisplayBackend.UNKNOWN
    
    return _detected_backend


@log_function_calls
def is_wayland() -> bool:

    """Check if running on Wayland."""
    return detect_display_backend() == DisplayBackend.WAYLAND


# def is_x11() -> bool:
#     """Check if running on X11."""
#     return detect_display_backend() == DisplayBackend.X11


@log_function_calls
def is_wayland_session() -> bool:

    """Alias for backward compatibility with existing utils.is_wayland_session()."""
    return is_wayland()


@log_function_calls
def get_backend_name() -> str:

    """Get human-readable backend name for logging."""
    return detect_display_backend().value


@log_function_calls
def is_wayland_session_actual() -> bool:

    """
    Check if the actual session is Wayland, ignoring GDK_BACKEND override.

    This is useful for determining clipboard monitoring strategy:
    - If session is Wayland, we should try Wayland clipboard monitoring
    - Even if GDK_BACKEND is forcing X11 mode for GTK
    """
    xdg_session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
    wayland_display = os.environ.get('WAYLAND_DISPLAY')

    # Check XDG_SESSION_TYPE first
    if xdg_session_type == 'wayland':
        return True

    # Fallback: check for WAYLAND_DISPLAY
    if wayland_display:
        return True

    return False
