# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

from datetime import datetime

from gi.repository import GObject, Gio, GLib
from .utils import log_function_calls


class FileManagerBackend(GObject.GObject):
    @log_function_calls
    def __init__(self, gtk_application=None):

        GObject.GObject.__init__(self)

        self.app = gtk_application
        try:
            self.proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                Gio.DBusProxyFlags.NONE,
                None,
                "org.freedesktop.FileManager1",
                "/org/freedesktop/FileManager1",
                "org.freedesktop.FileManager1",
                None,
            )
            self.app.logger.info("file manager backend started")
        except Exception as e:
            self.app.logger.error(f"Failed to initialize file manager backend: {e}")
            self.proxy = None

    @log_function_calls
    def show_files_in_file_manager(self, path):

        if not self.proxy:
            return

        uri = Gio.File.new_for_path(path)
        try:
            self.proxy.call_sync(
                "ShowItems",
                GLib.Variant("(ass)", ([uri.get_uri()], "")),
                Gio.DBusCallFlags.NONE,
                -1,
                None
            )
        except Exception as e:
            self.app.logger.error(f"Failed to show items: {e}")

    @log_function_calls
    def show_folders_in_file_manager(self, path):

        if not self.proxy:
            return

        uri = Gio.File.new_for_path(path)
        try:
            self.proxy.call_sync(
                "ShowFolders",
                GLib.Variant("(ass)", ([uri.get_uri()], "")),
                Gio.DBusCallFlags.NONE,
                -1,
                None
            )
        except Exception as e:
            self.app.logger.error(f"Failed to show folders: {e}")