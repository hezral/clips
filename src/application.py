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

import sys, os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib, Gdk
#from constants import ClipsAttributes
from main_window import ClipsWindow
from services.clipboard_manager import ClipboardManager
from services.cache_manager import CacheManager


class Clips(Gtk.Application):
    def __init__(self):
        super().__init__()

        # construct
        self.props.application_id = "com.github.hezral.clips"
        self.props.flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE
        self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE, GLib.OptionArg.NONE, "Command line test", None)

        # objects
        self.clipboard_manager = ClipboardManager()
        self.cache_manager = CacheManager(gtk_application=self, clipboard_manager=self.clipboard_manager)
        
        # re-initialize some objects
        self.window = None

        
    def do_startup(self):
        Gtk.Application.do_startup(self)

        # setup quiting app using Escape, Ctrl+Q
        hide_action = Gio.SimpleAction.new("hide", None)
        hide_action.connect("activate", self.on_hide_action)
        self.add_action(hide_action)
        self.set_accels_for_action("app.hide", ["Escape"])

        # show_action = Gio.SimpleAction.new("show", None)
        # show_action.connect("activate", self.on_show_action)
        # self.add_action(show_action)
        # self.set_accels_for_action("app.show", ["<Super>C"])

        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit_action)
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Ctrl>Q"])

        # #applicationwindow theme
        # settings = Gtk.Settings.get_default()
        # settings.set_property("gtk-application-prefer-dark-theme", True)

        # set CSS provider
        provider = Gtk.CssProvider()
        provider.load_from_path(os.path.join(os.path.dirname(__file__), "..", "data", "application.css"))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application 
            # when the last one is closed the application shuts down
            self.window = ClipsWindow(application=self)
        # self.window.present()
        self.add_window(self.window)
        #self.window.connect('key-press-event', self.window.check)
        manager = ClipboardManager()
        manager.clipboard.connect('owner-change', manager.clipboard_changed)

        import signal
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit) 

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()

        if "test" in options:
            # This is printed on the main instance
            print("Test argument recieved: %s" % options["test"])

        self.activate()
        return 0

    def close_window(self):
        pass

    def get_default(self):
        if not self.instance:
            self.instance = Clips()
            return self.instance

    def on_hide_action(self, action, param):
        if self.window is not None:
            self.window.hide()

    def on_show_action(self, action, param):
        if self.window is not None:
            self.window.show()

    def on_quit_action(self, action, param):
        if self.window is not None:
            self.window.destroy()

if __name__ == "__main__":
    # just for debugging at CLI to enable CTRL+C quit

    app = Clips()
    app.run(sys.argv)
