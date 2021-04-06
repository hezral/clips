#!/usr/bin/env python3

'''
    Copyright 2018 Adi Hezral (hezral@gmail.com)
    This file is part of Clips ("Application").
    The Application is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    The Application is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this Application.  If not, see <http://www.gnu.org/licenses/>.
'''

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib, Gdk
from main_window import ClipsWindow
from services.clipboard_manager import ClipboardManager
from services.cache_manager import CacheManager
from services.custom_shortcut_settings import CustomShortcutSettings
import utils

import platform
from datetime import datetime

import sys, os
import threading, time

class Clips(Gtk.Application):

    running = False

    def __init__(self):
        super().__init__()

        print(datetime.now(), "startup")
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

        # prepend custom path for icon theme
        self.icon_theme = Gtk.IconTheme.get_default()
        self.icon_theme.prepend_search_path(os.path.join(os.path.dirname(__file__), "..", "data", "icons"))

        # Set shortcut
        # if self.gio_settings.get_value("first-run"):
        #     SHORTCUT = "<Super><Control>C"
        #     ID = "gtk-launch" + " " + self.props.application_id
        #     setup_shortcut = CustomShortcutSettings()
        #     self.gio_settings.set_value("first-run", False)
  
    def do_startup(self):
        Gtk.Application.do_startup(self)

        # app actions
        self.setup_action("hide", self.on_hide_action, "Escape")
        self.setup_action("quit", self.on_quit_action, "<Ctrl>Q")
        self.setup_action("search", self.on_search_action, "<Ctrl>F")
        self.setup_action("enable_app", self.on_clipsapp_action, "<Ctrl>period")
        self.setup_action("settings-view", self.on_switch_views, "<Alt>Right")
        self.setup_action("clips-view", self.on_switch_views, "<Alt>Left")
        self.setup_action("add-column", self.on_column_number_action, "<Alt>Up")
        self.setup_action("del-column", self.on_column_number_action, "<Alt>Down")

        # selected clip actions
        # self.setup_action("protect", self.on_clip_actions, "<Alt>P")
        self.setup_action("reveal", self.on_clip_actions, "<Alt>R")
        self.setup_action("info", self.on_clip_actions, "<Alt>I")
        self.setup_action("view", self.on_clip_actions, "<Alt>V")
        self.setup_action("copy", self.on_clip_actions, "<Alt>C")
        self.setup_action("delete", self.on_clip_actions, "<Alt>D")
        self.setup_action("force_delete", self.on_clip_actions, "<Alt>F")

        # #applicationwindow theme
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", False)

        # set CSS provider
        provider = Gtk.CssProvider()        
        provider.load_from_path(os.path.join(os.path.dirname(__file__), "..", "data", "application.css"))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.main_window:
            # Windows are associated with the application when the last one is closed the application shuts down
            self.main_window = ClipsWindow(application=self)
            self.add_window(self.main_window)
            
        # present the window if its hidden
        self.main_window.present()

        if self.gio_settings.get_value("hide-on-startup") and self.running is False:
            self.main_window.hide()
        else:
            self.main_window.present()

        # link to cache_manager
        self.cache_manager.main_window = self.main_window

        # check if already running
        if self.running is False:

            # check for auto housekeeping
            if self.gio_settings.get_value("auto-housekeeping"):
                print(datetime.now(), "start auto-housekeeping")
                print(datetime.now(), "auto-retention-period", self.gio_settings.get_int("auto-retention-period"))
                self.cache_manager.auto_housekeeping(self.gio_settings.get_int("auto-retention-period"))        

            print(datetime.now(), "start load_clips")

            # load clips
            clips = self.cache_manager.load_clips()

            # update total_clips_label
            self.main_window.total_clips_label.props.label = "Clips: {total}".format(total=len(clips))
            
            if len(clips) != 0:
                self.load_clips_fromdb(clips)
            else:
                self.main_window.stack.set_visible_child_name("info-view")

            # self.main_window.clips_view.flowbox.select_child(self.main_window.clips_view.flowbox.get_child_at_index(0))
            self.running = True

    @utils.RunAsync
    def load_clips_fromdb(self, clips):
        app_startup = True

        for clip in reversed(clips[-10:]):
            GLib.idle_add(self.main_window.clips_view.new_clip, clip, app_startup)
            time.sleep(0.02)

        for clip in reversed(clips[:-10]):
            GLib.idle_add(self.main_window.clips_view.new_clip, clip, app_startup)
            time.sleep(0.01)

        # selects the first flowboxchild
        self.main_window.clips_view.flowbox.select_child(self.main_window.clips_view.flowbox.get_child_at_index(0))
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
            self.main_window.clips_view.flowbox.get_selected_children()[0].grab_focus()

    
    def on_clip_actions(self, action, param):
        if len(self.main_window.clips_view.flowbox.get_selected_children()) != 0:
            flowboxchild = self.main_window.clips_view.flowbox.get_selected_children()[0]
            if flowboxchild.is_selected():
                clips_container = flowboxchild.get_children()[0]
                clips_container.on_clip_action(action=action.props.name)

    def on_switch_views(self, action, param):
        if self.main_window is not None:
            if action.props.name == "settings-view":
                self.main_window.settings_view.show_all()
                self.main_window.stack.set_visible_child_name("settings-view")
                self.main_window.view_switch.props.active = True
            if action.props.name == "clips-view":
                self.main_window.clips_view.show_all()
                self.main_window.stack.set_visible_child_name("clips-view")
                self.main_window.view_switch.props.active = False

    def on_column_number_action(self, action, param):
        if self.main_window is not None:
            current_column_number = self.gio_settings.get_int("min-column-number")
            if action.props.name == "add-column":
                new_column_number = current_column_number + 1
            if action.props.name == "del-column":
                new_column_number = current_column_number - 1
            
            if new_column_number != 0:
                self.main_window.settings_view.on_min_column_number_changed(new_column_number)

    def on_clipsapp_action(self, action=None, param=None):
        if self.cache_manager.clipboard_monitoring:
            try:
                self.clipboard_manager.clipboard.disconnect_by_func(self.cache_manager.update_cache)
                self.cache_manager.clipboard_monitoring = False
                self.main_window.clipsapp_toggle.props.tooltip_text = "Clipboard Monitoring: Disabled"
                self.main_window.clipsapp_toggle.get_style_context().add_class("app-action-disabled")
                self.main_window.clipsapp_toggle.get_style_context().remove_class("app-action-enabled")
                print(datetime.now(), "clipboard monitoring disabled")
            except:
                print(datetime.now(), "clipboard monitoring disabling failed")
        else:
            try:
                self.clipboard_manager.clipboard.connect("owner-change", self.cache_manager.update_cache, self.clipboard_manager)
                self.cache_manager.clipboard_monitoring = True
                self.main_window.clipsapp_toggle.props.tooltip_text = "Clipboard Monitoring: Enabled"
                self.main_window.clipsapp_toggle.get_style_context().add_class("app-action-enabled")
                self.main_window.clipsapp_toggle.get_style_context().remove_class("app-action-disabled")
                print(datetime.now(), "clipboard monitoring enabled")
            except:
                print(datetime.now(), "clipboard monitoring enabling failed")

    def on_hide_action(self, action, param):
        if self.main_window is not None:
            self.main_window.hide()

    def on_quit_action(self, action, param):
        if self.main_window is not None:
            self.main_window.destroy()

# comment out once ready for deployment
if __name__ == "__main__":
    app = Clips()
    app.run(sys.argv)
