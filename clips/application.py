#!/usr/bin/env python3

'''
   Copyright 2018 Adi Hezral (hezral@gmail.com)

   This file is part of Clips.

    Clips is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Clips is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Clips.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib
from constants import ClipsAttributes
from mainwindow import ClipsWindow
from services.manager import ClipsManager


class Clips(Gtk.Application):
    def __init__(self):
        super().__init__()

        self.props.application_id = ClipsAttributes.application_id
        self.props.flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE
        self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE, GLib.OptionArg.NONE, "Command line test", None)

        self.instance = None
        self.window = None

        manager = ClipsManager()
        manager.clipboard.connect('owner-change', manager.clipboard_changed)
        
        
    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application 
            # when the last one is closed the application shuts down
            self.window = ClipsWindow(application=self)

        self.window.present()
        #elf.window.connect('key-press-event', self.window.check)

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()

        if "test" in options:
            # This is printed on the main instance
            print("Test argument recieved: %s" % options["test"])

        self.activate()
        return 0

    def get_default(self):
        if not self.instance:
            self.instance = Clips()
            return instance

if __name__ == "__main__":
    app = Clips()
    app.run(sys.argv)
