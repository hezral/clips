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

import sys
import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Gio, GLib, Gdk, Granite
from .main_window import ClipsWindow
from .clipboard_manager import ClipboardManager
from .cache_manager import CacheManager
from .custom_shortcut_settings import CustomShortcutSettings
from . import utils

import platform
from datetime import datetime

import sys, os
import threading, time

class Application(Gtk.Application):

    running = False
    app_startup = True

    def __init__(self):
        super().__init__()

        print(datetime.now(), "startup")

        self.props.application_id = "com.github.hezral.clips"
        self.props.flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE
        self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE, GLib.OptionArg.NONE, "Command line test", None)

        self.gio_settings = Gio.Settings(schema_id="com.github.hezral.clips")
        self.gtk_settings = Gtk.Settings().get_default()
        self.granite_settings = Granite.Settings.get_default()
        self.utils = utils
        self.clipboard_manager = ClipboardManager(gtk_application=self)
        self.cache_manager = CacheManager(gtk_application=self, clipboard_manager=self.clipboard_manager)
        self.main_window = None
        self.total_clips = 0

        # prepend custom path for icon theme
        self.icon_theme = Gtk.IconTheme.get_default()
        self.icon_theme.prepend_search_path("/run/host/usr/share/pixmaps")
        self.icon_theme.prepend_search_path("/run/host/usr/share/icons")
        self.icon_theme.prepend_search_path(os.path.join(GLib.get_home_dir(), ".local/share/flatpak/exports/share/icons"))
        self.icon_theme.prepend_search_path(os.path.join(os.path.dirname(__file__), "data", "icons"))

    def do_startup(self):
        Gtk.Application.do_startup(self)

        # self.create_app_shortcut() # doesn't work in flatpak anymore
        self.create_app_actions()

        if self.gio_settings.get_value("theme-optin"):
            prefers_color_scheme = self.granite_settings.get_prefers_color_scheme()
            self.gtk_settings.set_property("gtk-application-prefer-dark-theme", prefers_color_scheme)
            self.granite_settings.connect("notify::prefers-color-scheme", self.on_prefers_color_scheme)

        if "io.elementary.stylesheet" not in self.gtk_settings.props.gtk_theme_name:
            self.gtk_settings.set_property("gtk-theme-name", "io.elementary.stylesheet.blueberry")

        provider = Gtk.CssProvider()        
        provider.load_from_path(os.path.join(os.path.dirname(__file__), "data", "application.css"))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def do_activate(self):
        if not self.main_window:
            self.main_window = ClipsWindow(application=self)
            self.add_window(self.main_window)

        if self.gio_settings.get_value("hide-on-startup") and self.running is False:
            self.main_window.hide()
        else:
            self.main_window.set_keep_above(True)
            self.main_window.present()
            GLib.timeout_add(100, self.main_window.set_keep_above, False) # need to put time gap else won't work to bring window front

        self.cache_manager.main_window = self.main_window

        if self.running is False:
            if self.gio_settings.get_value("auto-housekeeping"):
                print(datetime.now(), "start auto-housekeeping")
                print(datetime.now(), "auto-retention-period", self.gio_settings.get_int("auto-retention-period"))
                self.cache_manager.auto_housekeeping(self.gio_settings.get_int("auto-retention-period"))        

            print(datetime.now(), "start load_clips")

            clips = self.cache_manager.load_clips()
            
            if len(clips) != 0:
                self.load_clips_fromdb(clips)

            self.main_window.on_view_visible()

            self.running = True
            self.app_startup = False
            

    @utils.run_async
    def load_clips_fromdb(self, clips):
        
        for clip in reversed(clips[-25:]):
            GLib.idle_add(self.main_window.clips_view.new_clip, clip)
            time.sleep(0.01)

        for clip in reversed(clips[:-25]):
            GLib.idle_add(self.main_window.clips_view.new_clip, clip)
            time.sleep(0.05)

        if self.main_window.clips_view.flowbox.get_child_at_index(0) is not None:
            self.main_window.clips_view.flowbox.select_child(self.main_window.clips_view.flowbox.get_child_at_index(0))
            self.main_window.clips_view.flowbox.get_child_at_index(0).grab_focus()

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

    def create_app_shortcut(self):
        if self.gio_settings.get_boolean("first-run"):
            SHORTCUT = "<Super><Control>c"
            ID = "gtk-launch" + " " + self.props.application_id
            setup_shortcut = CustomShortcutSettings()
            has_shortcut = False
            for shortcut in setup_shortcut.list_custom_shortcuts():
                if shortcut[1] == ID:
                    has_shortcut = True

            if has_shortcut is False:
                shortcut = setup_shortcut.create_shortcut()
                if shortcut is not None:
                    setup_shortcut.edit_shortcut(shortcut, SHORTCUT)
                    setup_shortcut.edit_command(shortcut, ID)
            
    def create_app_actions(self):
        # app actions
        self.create_action("hide", self.on_hide_action, "Escape")
        self.create_action("quit", self.on_quit_action, "<Ctrl>Q")
        self.create_action("search", self.on_search_action, "<Ctrl>F")
        self.create_action("enable_app", self.on_clipsapp_action, "<Alt>period")
        self.create_action("settings-view", self.on_switch_views, "<Alt>Right")
        self.create_action("clips-view", self.on_switch_views, "<Alt>Left")
        self.create_action("add-column", self.on_column_number_action, "<Alt>Up")
        self.create_action("del-column", self.on_column_number_action, "<Alt>Down")

        # selected clip actions
        self.create_action("protect", self.on_clip_actions, "<Alt>P")
        self.create_action("multi-select", self.on_clip_actions, "<Alt>M")
        self.create_action("reveal", self.on_clip_actions, "<Alt>R")
        self.create_action("info", self.on_clip_actions, "<Alt>I")
        self.create_action("view", self.on_clip_actions, "<Alt>V")
        self.create_action("copy", self.on_clip_actions, "<Alt>C")
        self.create_action("delete", self.on_clip_actions, "<Alt>D")
        self.create_action("force_delete", self.on_clip_actions, "<Alt>F")
        self.create_action("quick_copy1", self.on_clip_actions, "<Alt>1")
        self.create_action("quick_copy2", self.on_clip_actions, "<Alt>2")
        self.create_action("quick_copy3", self.on_clip_actions, "<Alt>3")
        self.create_action("quick_copy4", self.on_clip_actions, "<Alt>4")
        self.create_action("quick_copy5", self.on_clip_actions, "<Alt>5")
        self.create_action("quick_copy6", self.on_clip_actions, "<Alt>6")
        self.create_action("quick_copy7", self.on_clip_actions, "<Alt>7")
        self.create_action("quick_copy8", self.on_clip_actions, "<Alt>8")
        self.create_action("quick_copy9", self.on_clip_actions, "<Alt>9")

    def create_action(self, name, callback, shortcutkey):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        self.set_accels_for_action("app.{name}".format(name=name), [shortcutkey])

    def on_search_action(self, action, param):
        if self.main_window is not None and self.main_window.is_visible() and self.main_window.searchentry.has_focus() is False:
            self.main_window.searchentry.grab_focus()
        else:
            self.main_window.clips_view.flowbox.get_selected_children()[0].grab_focus()
    
    def on_clip_actions(self, action, param):
        if len(self.main_window.clips_view.flowbox.get_selected_children()) != 0:

            quick_copy_accels = ["1","2","3","4","5","6","7","8","9"]
            if action.props.name[-1] in quick_copy_accels:
                index = int(action.props.name[-1]) - 1
                flowboxchild = self.main_window.clips_view.flowbox.get_child_at_index(index)
                self.main_window.clips_view.flowbox.select_child(flowboxchild)
                flowboxchild.do_activate(flowboxchild)
                # do_activate triggers on_child_activated that sets current_selected_flowboxchild_index to index of selected flowboxchild
                # need to reset index to 0 due to copy action will update created timestamp and flowbox will sort it to first item
                self.main_window.clips_view.current_selected_flowboxchild_index = 0
                if flowboxchild.is_selected():
                    clips_container = flowboxchild.get_children()[0]
                    clips_container.on_clip_action(action="copy")
            
            elif action.props.name == "multi-select":
                if self.main_window.clips_view.multi_select_mode:
                    self.main_window.clips_view.off_multi_select()
                else:
                    self.main_window.clips_view.on_multi_select()

            else:
                flowboxchild = self.main_window.clips_view.flowbox.get_selected_children()[0]
                if flowboxchild.is_selected():
                    clips_container = flowboxchild.get_children()[0]
                    clips_container.on_clip_action(action=action.props.name)

    def on_switch_views(self, action, param):
        if self.main_window is not None:
            self.main_window.on_view_visible(action=action.props.name)

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

    def on_prefers_color_scheme(self, *args):
        prefers_color_scheme = self.granite_settings.get_prefers_color_scheme()
        self.gtk_settings.set_property("gtk-application-prefer-dark-theme", prefers_color_scheme)
        

def main(version):
    app = Application()
    return app.run(sys.argv)

