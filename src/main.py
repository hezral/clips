# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

import logging
import sys
import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Gio, GLib, Gdk, Granite

from .main_window import ClipsWindow
from .clipboard_manager import ClipboardManager
from .cache_manager import CacheManager
from .shake_listener import ShakeListener
from .active_window_manager import ActiveWindowManager
from .filemanager_backend import FileManagerBackend
from . import utils

from datetime import datetime
import time

id = "com.github.hezral.clips"
debug_log = os.path.join(os.path.dirname(GLib.get_user_data_dir()), id + ".log")
logger = utils.init_logger(id, debug_log)

class Application(Gtk.Application):

    app_id = id
    running = False
    app_startup = True
    clipboard_manager = None
    cache_manager = None
    shake_listener = None
    window_manager = None
    main_window = None
    total_clips = 0
    debug_log = debug_log

    def __init__(self):
        super().__init__()

        self.props.application_id = self.app_id
        self.props.flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE
        self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE, GLib.OptionArg.NONE, "Command line test", None)

        self.gio_settings = Gio.Settings(schema_id=self.app_id)
        self.gtk_settings = Gtk.Settings().get_default()
        self.granite_settings = Granite.Settings.get_default()
        
        self.utils = utils

        self.logger = logger
        if self.gio_settings.get_value("debug-mode"):
            self.logger.setLevel(logging.DEBUG)
            format_str = "%(levelname)s: %(asctime)s %(pathname)s, %(funcName)s:%(lineno)d: %(message)s"
            formatter = logging.Formatter(format_str)
            for handler in self.logger.handlers:
                handler.setFormatter(formatter)
        else:
            self.logger.setLevel(logging.INFO)

        self.logger.info("startup")

        self.clipboard_manager = ClipboardManager(gtk_application=self)
        self.cache_manager = CacheManager(gtk_application=self, clipboard_manager=self.clipboard_manager)
        self.window_manager = ActiveWindowManager(gtk_application=self)
        self.file_manager = FileManagerBackend(gtk_application=self)
        self.create_shakelistener()

        # prepend custom path for icon theme
        self.icon_theme = Gtk.IconTheme.get_default()
        self.icon_theme.prepend_search_path("/run/host/usr/share/pixmaps")
        self.icon_theme.prepend_search_path("/run/host/usr/share/icons")
        self.icon_theme.prepend_search_path("/var/lib/flatpak/exports/share/icons")
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

        if self.app_startup is True:
            if self.gio_settings.get_value("auto-housekeeping"):
                self.logger.info("start auto-housekeeping")
                self.logger.info("auto-retention-period", self.gio_settings.get_int("auto-retention-period"))
                self.cache_manager.auto_housekeeping(self.gio_settings.get_int("auto-retention-period"))

    def do_activate(self):
        # no window
        if self.main_window is None:
            self.logger.info("no window: initializing window")
            self.main_window = ClipsWindow(application=self)
            self.add_window(self.main_window)

            if self.app_startup and self.gio_settings.get_value("hide-on-startup"):
                self.logger.info("app startup: hide on startup enabled")
                self.main_window.hide()
            else:
                self.main_window.present()
                self.main_window.on_view_visible()

            self.cache_manager.main_window = self.main_window
            clips = self.cache_manager.load_clips()
            if len(clips) != 0:
                self.load_clips_fromdb(clips)
        
            self.app_startup = False
            self.running = True

            # delayed trigger to avoid clash with persistent mode getting triggered on window display event
            GLib.timeout_add(250, self.main_window.set_display_settings, None)

        # window hidden
        else:
            self.logger.info("window visible")

            if self.main_window.is_visible():
                self.main_window.hide()

            else:
                for window in self.get_windows():
                    window.destroy()
                self.main_window = None
                self.do_activate()

    @utils.run_async
    @utils.metrics(logger=logger)
    def load_clips_fromdb(self, clips):

        def first_clip(clip): #load first clip to focus 
            self.main_window.clips_view.new_clip(clip)
            self.main_window.clips_view.flowbox.select_child(self.main_window.clips_view.flowbox.get_child_at_index(0))
            self.main_window.clips_view.flowbox.get_child_at_index(0).grab_focus()

        GLib.idle_add(first_clip, clips[-1])
        time.sleep(0.01)

        for clip in reversed(clips[-25:]):
            GLib.idle_add(self.main_window.clips_view.new_clip, clip)
            time.sleep(0.01)

        for clip in reversed(clips[-50:-25]):
            GLib.idle_add(self.main_window.clips_view.new_clip, clip)
            time.sleep(0.05)

        for clip in reversed(clips[:-50]):
            GLib.idle_add(self.main_window.clips_view.new_clip, clip)
            time.sleep(0.10)

        self.logger.info("finish load_clips")

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()

        if "test" in options:
            # This is printed on the main instance
            self.logger.debug("Test argument recieved: %s" % options["test"])

        self.activate()
        return 0
            
    def create_app_actions(self):
        # app actions
        self.create_action("hide", self.on_hide_action, "Escape")
        self.create_action("quit", self.on_quit_action, "<Ctrl>Q")
        self.create_action("search", self.on_search_action, "<Ctrl>F")
        self.create_action("text-mode", self.on_text_mode, "<Ctrl>T")
        self.create_action("enable_app", self.on_clipsapp_action, "<Ctrl>period")
        self.create_action("settings-view", self.on_switch_views, "<Ctrl>Right")
        self.create_action("clips-view", self.on_switch_views, "<Ctrl>Left")
        self.create_action("add-column", self.on_column_number_action, "<Ctrl>Up")
        self.create_action("del-column", self.on_column_number_action, "<Ctrl>Down")

        # selected clip actions
        self.create_action("protect", self.on_clip_actions, "<Ctrl>P")
        self.create_action("multi-select", self.on_clip_actions, "<Ctrl>M")
        self.create_action("reveal", self.on_clip_actions, "<Ctrl>R")
        self.create_action("info", self.on_clip_actions, "<Ctrl>I")
        self.create_action("view", self.on_clip_actions, "<Ctrl>V")
        self.create_action("copy", self.on_clip_actions, "<Ctrl>C")
        self.create_action("copy-plaintext", self.on_clip_actions, "<Alt>C")
        self.create_action("delete", self.on_clip_actions, "<Ctrl>D")
        self.create_action("force_delete", self.on_clip_actions, "<Alt>D")
        self.create_action("quick_copy1", self.on_clip_actions, "<Ctrl>1")
        self.create_action("quick_copy2", self.on_clip_actions, "<Ctrl>2")
        self.create_action("quick_copy3", self.on_clip_actions, "<Ctrl>3")
        self.create_action("quick_copy4", self.on_clip_actions, "<Ctrl>4")
        self.create_action("quick_copy5", self.on_clip_actions, "<Ctrl>5")
        self.create_action("quick_copy6", self.on_clip_actions, "<Ctrl>6")
        self.create_action("quick_copy7", self.on_clip_actions, "<Ctrl>7")
        self.create_action("quick_copy8", self.on_clip_actions, "<Ctrl>8")
        self.create_action("quick_copy9", self.on_clip_actions, "<Ctrl>9")

    def create_action(self, name, callback, shortcutkey):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        self.set_accels_for_action("app.{name}".format(name=name), [shortcutkey])

    def on_search_action(self, action, param):
        if self.main_window is not None and self.main_window.is_visible() and self.main_window.searchentry.has_focus() is False:
            self.main_window.searchentry.grab_focus()
        else:
            self.main_window.searchentry.props.text = ""
            self.main_window.clips_view.flowbox.select_child(self.main_window.clips_view.flowbox.get_child_at_index(0))
            self.main_window.clips_view.flowbox.get_child_at_index(0).grab_focus()
    
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
        if self.cache_manager.clipboard_monitoring is True:
            try:
                self.clipboard_manager.clipboard.disconnect_by_func(self.cache_manager.update_cache)
                self.cache_manager.clipboard_monitoring = False
                self.main_window.clipsapp_toggle.props.tooltip_text = "Clipboard Monitoring: Disabled"
                self.main_window.clipsapp_toggle.get_style_context().add_class("app-action-disabled")
                self.main_window.clipsapp_toggle.get_style_context().remove_class("app-action-enabled")
                self.logger.info("clipboard monitoring disabled")
            except:
                self.logger.info("clipboard monitoring disabling failed")
        elif self.cache_manager.clipboard_monitoring is False or param == "disable":
            try:
                self.clipboard_manager.clipboard.connect("owner-change", self.cache_manager.update_cache, self.clipboard_manager)
                self.cache_manager.clipboard_monitoring = True
                self.main_window.clipsapp_toggle.props.tooltip_text = "Clipboard Monitoring: Enabled"
                self.main_window.clipsapp_toggle.get_style_context().add_class("app-action-enabled")
                self.main_window.clipsapp_toggle.get_style_context().remove_class("app-action-disabled")
                self.logger.info("clipboard monitoring enabled")
            except:
                self.logger.info("clipboard monitoring enabling failed")
            
    def on_hide_action(self, action, param):
        if self.main_window is not None:
            self.main_window.hide()

    def on_quit_action(self, action, param):
        if self.main_window is not None:
            self.main_window.destroy()

    def on_text_mode(self, action=None, param=None):
        hidden = 0

        if self.main_window is not None:

            for flowboxchild in self.main_window.clips_view.flowbox.get_children():
                if flowboxchild.get_children()[0].type not in ["plaintext", "html"]:
                    if not flowboxchild.is_visible():
                        hidden += 1

            if hidden == 0:
                for flowboxchild in self.main_window.clips_view.flowbox.get_children():
                    if flowboxchild.get_children()[0].type not in ["plaintext", "html"]:
                        flowboxchild.hide()
                self.main_window.clips_view.flowbox.props.homogeneous = True
                self.main_window.clips_view.flowbox.props.max_children_per_line = 1
                self.main_window.clips_view.flowbox.props.min_children_per_line = 1
                self.main_window.set_main_window_size(column_number=1)
            else:
                for flowboxchild in self.main_window.clips_view.flowbox.get_children():
                    if flowboxchild.get_children()[0].type not in ["plaintext", "html"]:
                        flowboxchild.show_all()

                self.main_window.clips_view.flowbox.props.homogeneous = False
                self.main_window.clips_view.flowbox.props.max_children_per_line = 8
                self.main_window.clips_view.flowbox.props.min_children_per_line = self.gio_settings.get_int("min-column-number")
                self.main_window.settings_view.on_min_column_number_changed(self.gio_settings.get_int("min-column-number"))


    def on_prefers_color_scheme(self, *args):
        prefers_color_scheme = self.granite_settings.get_prefers_color_scheme()
        self.gtk_settings.set_property("gtk-application-prefer-dark-theme", prefers_color_scheme)

    def create_shakelistener(self, *args):
        if self.shake_listener is not None:
            self.shake_listener.listener.stop()
            self.shake_listener = None
        if self.gio_settings.get_value("shake-reveal"):
            self.shake_listener = ShakeListener(app=self, reveal_callback=self.do_activate, sensitivity=self.gio_settings.get_int("shake-sensitivity"))

def main(version):
    app = Application()
    return app.run(sys.argv)

