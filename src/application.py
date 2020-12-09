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
import utils

import platform
from datetime import datetime


class Clips(Gtk.Application):
    def __init__(self):
        super().__init__()

        # construct
        self.props.application_id = "com.github.hezral.clips"
        self.props.flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE
        self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE, GLib.OptionArg.NONE, "Command line test", None)

        # objects
        self.utils = utils
        self.clipboard_manager = ClipboardManager(gtk_application=self)
        self.cache_manager = CacheManager(gtk_application=self, clipboard_manager=self.clipboard_manager)
        

        # re-initialize some objects
        self.main_window = None


        
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
        print(platform.linux_distribution()[2])
        if platform.linux_distribution()[2] == "hera":
            provider.load_from_path(os.path.join(os.path.dirname(__file__), "..", "data", "application.css"))

        if platform.linux_distribution()[2] == "odin":
            provider.load_from_path(os.path.join(os.path.dirname(__file__), "..", "data", "application.css"))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.main_window:
            # Windows are associated with the application 
            # when the last one is closed the application shuts down
            self.main_window = ClipsWindow(application=self)
        # present the window if its hidden
        self.main_window.present()
        # add it back to app
        self.add_window(self.main_window)
        #self.window.connect('key-press-event', self.window.check)

        # link to cache_manager
        self.cache_manager.main_window = self.main_window

        print(datetime.now(), "start load_clips")
        clips_view = self.main_window.utils.get_widget_by_name(widget=self.main_window, child_name="clips-view", level=0)
        clips_view.cache_manager = self.cache_manager
        clips_view.clipboard_manager = self.clipboard_manager

        clips = self.cache_manager.load_clips()

        clips_view.load_from_cache()
        
        print(datetime.now(), "finish load_clips")



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
        if self.main_window is not None:
            self.main_window.hide()

    def on_show_action(self, action, param):
        if self.main_window is not None:
            self.main_window.show()

    def on_quit_action(self, action, param):
        if self.main_window is not None:
            self.main_window.destroy()

if __name__ == "__main__":
    # just for debugging at CLI to enable CTRL+C quit

    app = Clips()
    app.run(sys.argv)
