# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2023 Adi Hezral <hezral@gmail.com>

"""
Universal active window manager using AT-SPI accessibility bus.
Works on both X11 and Wayland sessions.
Requires --no-a11y-bus flag when running in flatpak.

This implementation uses event-driven approach (no polling) by subscribing
to AT-SPI DBus signals for window focus and activation events.
"""

import sys
from typing import Dict, Optional, Callable

import gi
gi.require_version('GLib', '2.0')
gi.require_version('Gio', '2.0')
from gi.repository import GLib, Gio


class ActiveWindowManager():
    """Wayland-compatible active window manager using AT-SPI event subscription."""

    def __init__(self, gtk_application=None):
        super().__init__()
        self.app = gtk_application
        self.last_seen = {'title': None}
        self.atspi_conn = None
        self.main_loop = None
        self._initialized = False  # Track if manager has been started
        
    def _get_property(self, connection, destination, path, interface, prop_name):
        """Helper to read properties using raw Gio DBus calls."""
        try:
            ret = connection.call_sync(
                destination,
                path,
                "org.freedesktop.DBus.Properties",
                "Get",
                GLib.Variant("(ss)", (interface, prop_name)),
                GLib.VariantType("(v)"),
                Gio.DBusCallFlags.NONE,
                -1,
                None
            )
            return ret.get_child_value(0).get_variant().unpack()
        except Exception as e:
            if self.app:
                self.app.logger.debug(f"Error getting property {prop_name}: {e}")
            return None

    def _on_signal(self, connection, sender_name, object_path, interface_name, signal_name, parameters, user_data):
        """Event callback for AT-SPI signals."""
        # Unpack parameters
        args = parameters.unpack()
        
        # Filter 1: Only care about Focus or Activate
        is_focused = (signal_name == "StateChanged" and args[0] == "focused" and args[1] == 1)
        is_activate = (signal_name == "Activate")
        
        if not (is_focused or is_activate):
            return

        try:
            # A. Identify the App (Jump to Root)
            # This is the most reliable way to get the App Name
            app_root_path = "/org/a11y/atspi/accessible/root"
            app_name = self._get_property(connection, sender_name, app_root_path, "org.a11y.atspi.Accessible", "Name")
            
            # Fallback: Try ToolkitName if Name is empty
            if not app_name:
                app_name = self._get_property(connection, sender_name, app_root_path, "org.a11y.atspi.Application", "ToolkitName")

            # If this is a Window:Activate event, but we couldn't find a valid name,
            # we IGNORE it. This allows the Object:StateChanged event (which happens 
            # simultaneously) to handle it instead.
            if is_activate and (not app_name or app_name == ""):
                return 
                
            # B. Identify the Element (Window Title or Widget Name)
            element_name = self._get_property(connection, sender_name, object_path, "org.a11y.atspi.Accessible", "Name")

            # Cleanup strings for display
            display_app = app_name if app_name else f"Unknown({sender_name})"
            display_element = element_name if element_name else "Untitled"

            # Always update and trigger callback (removed deduping to fix persistent mode)
            # This ensures the callback runs even when clicking back to the same app
            self.last_seen['title'] = display_app
            
            if self.app:
                self.app.logger.info(f"Active app changed to: {display_app} - {display_element}")
            
            # Trigger the callback
            self.handle_change(self.last_seen)

        except Exception as e:
            if self.app:
                self.app.logger.debug(f"Error in signal handler: {e}")

    def _run(self, callback):
        """Initialize AT-SPI event subscription."""
        self.callback = callback
        
        if self._initialized:
             return

        try:
            # A. Connect to Session Bus to find AT-SPI
            session_bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            reply = session_bus.call_sync(
                "org.a11y.Bus", "/org/a11y/bus", "org.a11y.Bus", "GetAddress", None,
                GLib.VariantType("(s)"), Gio.DBusCallFlags.NONE, -1, None
            )
            atspi_address = reply.unpack()[0]
            
            if self.app:
                self.app.logger.info(f"Found AT-SPI bus at: {atspi_address}")

        except Exception as e:
            if self.app:
                self.app.logger.error(f"Could not find AT-SPI bus: {e}")
                self.app.logger.warning("Active window detection disabled")
            return

        # B. Connect to the AT-SPI Bus
        try:
            self.atspi_conn = Gio.DBusConnection.new_for_address_sync(
                atspi_address,
                Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT | Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,
                None, None
            )
        except Exception as e:
            if self.app:
                self.app.logger.error(f"Could not connect to AT-SPI socket: {e}")
            return

        if self.atspi_conn:
            if self.app:
                self.app.logger.info("Connected to AT-SPI. Registering events...")

            # C. Register Event Types
            try:
                # 1. Register Object Focus
                self.atspi_conn.call_sync(
                    "org.a11y.atspi.Registry", "/org/a11y/atspi/registry", "org.a11y.atspi.Registry", 
                    "RegisterEvent", GLib.Variant("(s)", ("object:state-changed:focused",)), 
                    None, Gio.DBusCallFlags.NONE, -1, None
                )
                # 2. Register Window Activate
                self.atspi_conn.call_sync(
                    "org.a11y.atspi.Registry", "/org/a11y/atspi/registry", "org.a11y.atspi.Registry", 
                    "RegisterEvent", GLib.Variant("(s)", ("window:activate",)), 
                    None, Gio.DBusCallFlags.NONE, -1, None
                )
                
                if self.app:
                    self.app.logger.info("AT-SPI events registered successfully")
                    
            except Exception as e:
                if self.app:
                    self.app.logger.warning(f"Failed to register events: {e}")

            # D. Subscribe to signals
            self.atspi_conn.signal_subscribe(
                None, "org.a11y.atspi.Event.Object", "StateChanged", 
                None, None, Gio.DBusSignalFlags.NONE, self._on_signal, None
            )
            self.atspi_conn.signal_subscribe(
                None, "org.a11y.atspi.Event.Window", "Activate", 
                None, None, Gio.DBusSignalFlags.NONE, self._on_signal, None
            )
            
            self._initialized = True  # Mark as initialized
            
            if self.app:
                self.app.logger.info("active_window_manager (AT-SPI event-driven) started")

    def _stop(self):
        """Stop the active window manager."""
        if self.app:
            self.app.logger.info("active_window_manager (AT-SPI) stopped")
        
        # Unsubscribe from signals if connection exists
        if self.atspi_conn:
            try:
                # Note: signal_unsubscribe would require subscription IDs
                # For now, just close the connection
                self.atspi_conn.close_sync(None)
            except Exception as e:
                if self.app:
                    self.app.logger.debug(f"Error closing AT-SPI connection: {e}")
        
        self._initialized = False

    def handle_change(self, new_state: dict):
        """This method is called when the active window changes."""
        if self.callback:
            GLib.idle_add(self.callback, new_state['title'])
