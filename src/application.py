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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib, Gdk
from main_window import ClipsWindow
from services.clipboard_manager import ClipboardManager
from services.cache_manager import CacheManager
import utils

import platform
from datetime import datetime

import sys, os
import threading, time


class Clips(Gtk.Application):

    running = False

    def __init__(self):
        super().__init__()

        # construct
        self.props.application_id = "com.github.hezral.clips"
        self.props.flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE
        self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE, GLib.OptionArg.NONE, "Command line test", None)

        #-- settings ----#
        self.gio_settings = Gio.Settings(schema_id="com.github.hezral.clips")
        self.gtk_settings = Gtk.Settings().get_default()

        # objects
        self.utils = utils
        self.clipboard_manager = ClipboardManager(gtk_application=self)
        self.cache_manager = CacheManager(gtk_application=self, clipboard_manager=self.clipboard_manager)
        

        # re-initialize some objects
        self.main_window = None
        self.total_clips = 0


        
    def do_startup(self):
        Gtk.Application.do_startup(self)

        self.setup_action("hide", self.on_hide_action, "Escape")
        self.setup_action("quit", self.on_quit_action, "<Ctrl>Q")
        self.setup_action("search", self.on_search_action, "<Ctrl>F")

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
            self.add_window(self.main_window)
            
        # present the window if its hidden
        self.main_window.present()

        # if not self.gio_settings.get_value("hide-on-startup") and self.running is False:
        #     self.main_window.hide()
        # else:
        #     self.main_window.present()

        # link to cache_manager
        self.cache_manager.main_window = self.main_window

        # clips_view = self.main_window.utils.get_widget_by_name(widget=self.main_window, child_name="clips-view", level=0)
        #clips_view = self.main_window.clips_view
        self.main_window.clips_view.cache_manager = self.cache_manager
        self.main_window.clips_view.clipboard_manager = self.clipboard_manager

        if self.running is False:
            print(datetime.now(), "start load_clips")
            clips = self.cache_manager.load_clips()

            # update total_clips_label
            self.main_window.total_clips_label.props.label = "Clips: {total}".format(total=len(clips))
            
            if len(clips) != 0:
                thread = threading.Thread(target=self.load_clips_fromdb, args=(clips, self.main_window.clips_view, self.cache_manager.cache_filedir))
                thread.daemon = True
                thread.start()

            self.running = True


    # def load_clips_fromdb(self, focus, clip_pos_start, clip_pos_end, clips, clips_view, cache_filedir):
    def load_clips_fromdb(self, clips, clips_view, cache_filedir):
        app_startup = True
        # initially load last 20 clips 
        for clip in reversed(clips[-10:]):
            GLib.idle_add(clips_view.new_clip, cache_filedir, clip, app_startup)
            time.sleep(0.15)
            #print(clip[0])
        #if focus:
        clips_view.flowbox.get_child_at_index(0).grab_focus()

        for clip in reversed(clips[-20:-10]):
            GLib.idle_add(clips_view.new_clip, cache_filedir, clip, app_startup)
            time.sleep(0.05)
            #print(clip[0])

        for clip in reversed(clips[-30:-20]):
            GLib.idle_add(clips_view.new_clip, cache_filedir, clip, app_startup)
            time.sleep(0.05)
            #print(clip[0])

        for clip in reversed(clips[:-30]):
            GLib.idle_add(clips_view.new_clip, cache_filedir, clip, app_startup)
            time.sleep(0.05)
            #print(clip[0])

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

    def setup_action(self, name, callback, shortcutkey):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        self.set_accels_for_action("app.{name}".format(name=name), [shortcutkey])

    def on_search_action(self, action, param):
        # focus on searchentry
        if self.main_window is not None and self.main_window.is_visible() and self.main_window.searchentry.has_focus() is False:
            self.main_window.searchentry.grab_focus()
        # focus back on first flowboxchild
        else:
            self.main_window.clips_view.flowbox.get_child_at_index(0).grab_focus()

    def on_hide_action(self, action, param):
        if self.main_window is not None:
            self.main_window.hide()

    def on_quit_action(self, action, param):
        if self.main_window is not None:
            self.main_window.destroy()

    def run_async(func):
        '''
        https://github.com/learningequality/ka-lite-gtk/blob/341813092ec7a6665cfbfb890aa293602fb0e92f/kalite_gtk/mainwindow.py
        http://code.activestate.com/recipes/576683-simple-threading-decorator/
            run_async(func)
                function decorator, intended to make "func" run in a separate
                thread (asynchronously).
                Returns the created Thread object
                E.g.:
                @run_async
                def task1():
                    do_something
                @run_async
                def task2():
                    do_something_too
        '''
        from threading import Thread
        from functools import wraps

        @wraps(func)
        def async_func(*args, **kwargs):
            func_hl = Thread(target=func, args=args, kwargs=kwargs)
            func_hl.start()
            # Never return anything, idle_add will think it should re-run the
            # function because it's a non-False value.
            return None

        return async_func

# comment out once ready for deployment
if __name__ == "__main__":
    app = Clips()
    app.run(sys.argv)
