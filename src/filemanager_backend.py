# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

from datetime import datetime

from pydbus import SessionBus
from gi.repository import GObject, Gio

class FileManagerBackend(GObject.GObject):
    def __init__(self):
        GObject.GObject.__init__(self)

        self.bus = SessionBus()
        # self.proxy = self.bus.get("org.freedesktop.FileManager1", "/org/freedesktop/FileManager1")
        self.proxy = self.bus.get(".FileManager1")
        print(datetime.now(), "file manager backend started")

    def show_files_in_file_manager(self, path):
        uri = Gio.File.new_for_path(path)
        self.proxy.ShowItems([uri.get_uri()], "")

    def show_folders_in_file_manager(self, path):
        uri = Gio.File.new_for_path(path)
        print(uri.get_uri())
        self.proxy.ShowFolders([uri.get_uri()], "")