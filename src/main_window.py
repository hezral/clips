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

import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Granite, GObject, Gdk, Gio
from views.clips_view import ClipsView
from views.settings_view import SettingsView
from views.info_view import InfoView

class ClipsWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.utils = self.props.application.utils
        self.app = self.props.application
        self.gio_settings = self.props.application.gio_settings
        self.gtk_settings = self.props.application.gtk_settings

        #------ views ----#
        self.clips_view = ClipsView(self.app)
        self.settings_view = SettingsView(self.app)
        self.info_view = InfoView(self.app, "No Clips Found","Start Copying Stuffs", "system-os-installer")

        #------ stack ----#
        self.stack = Gtk.Stack()
        self.stack.props.name = "main-stack"
        self.stack.props.transition_type = Gtk.StackTransitionType.CROSSFADE
        self.stack.props.transition_duration = 150
        self.stack.add_named(self.clips_view, self.clips_view.get_name())
        self.stack.add_named(self.settings_view, self.settings_view.get_name())
        self.stack.add_named(self.info_view, self.info_view.get_name())

        #------ headerbar ----#
        self.set_titlebar(self.generate_headerbar())

        #------ main_view ----#
        self.main_view = Gtk.Grid()
        self.main_view.props.name = "main-view"
        self.main_view.attach(self.stack, 0, 0, 3, 1)
        self.main_view.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), 0, 1, 3, 1)
        self.main_view.attach(self.generate_actionbar(), 0, 2, 1, 1)
        self.main_view.attach(self.generate_statusbar(), 1, 2, 1, 1)
        self.main_view.attach(self.generate_viewswitch(), 2, 2, 1, 1)

        #------ construct ----#
        self.props.title = "Clips"
        self.props.name = "main-window"
        self.props.border_width = 0
        self.props.window_position = Gtk.WindowPosition.CENTER
        self.get_style_context().add_class("rounded")

        self.set_main_window_size()
        self.set_display_settings()
        self.add(self.main_view)
        self.show_all()

    def set_display_settings(self):
        # this is for tracking window state flags for persistent mode
        self.state_flags_changed_count = 0
        self.active_state_flags = ['GTK_STATE_FLAG_NORMAL', 'GTK_STATE_FLAG_DIR_LTR']
        # read settings
        if not self.gio_settings.get_value("persistent-mode"):
            self.state_flags_on = self.connect("state-flags-changed", self.on_persistent_mode)
            # print('state-flags-on')
        if self.gio_settings.get_value("sticky-mode"):
            self.stick()

    def on_persistent_mode(self, widget, event):
        # state flags for window active state
        self.state_flags = self.get_state_flags().value_names
        # print(self.state_flags)
        if not self.state_flags == self.active_state_flags and self.state_flags_changed_count > 1:
            self.hide()
            self.state_flags_changed_count = 0
        else:
            self.state_flags_changed_count += 1
            # print('state-flags-changed', self.state_flags_changed_count)

    def set_main_window_size(self, column_number=None):
        if column_number is None:
            column_number = self.gio_settings.get_int("min-column-number")
        
        default_height = 450
        default_width = 340
        min_width = 340
        proceed = True

        if column_number == 1:
            default_width = min_width = 360

        elif column_number == 2:
            default_width = min_width = 600

        elif column_number == 3:
            default_width = min_width = 800

        elif column_number == 4:
            default_width = min_width = 958
        
        elif column_number == 5:
            default_width = 1100
            min_width = 958

        # elif column_number > 5:
        #     proceed = False
        
        if proceed:
            self.resize(default_width, default_height)
            self.set_size_request(min_width, default_height)            
            geometry = Gdk.Geometry()
            setattr(geometry, 'min_height', default_height)
            setattr(geometry, 'min_width', min_width)
            self.set_geometry_hints(None, geometry, Gdk.WindowHints.MIN_SIZE)

    def generate_headerbar(self):
        self.searchentry = Gtk.SearchEntry()
        self.searchentry.props.placeholder_text = "Search Clips" #"Search Clips\u2026"
        self.searchentry.props.hexpand = False
        self.searchentry.props.name = "search-entry"

        self.searchentry.connect("focus-in-event", self.on_searchbar_activate, "in")
        self.searchentry.connect("focus-out-event", self.on_searchbar_activate, "out")
        # self.searchentry.connect_after("delete-text", self.on_searchbar_activate, "delete")
        # self.searchentry.connect("icon-press", self.on_quicksearch_activate)
        
        self.searchentry.connect("search-changed", self.on_search_entry_changed)

        # sourceapp_appchooser_popover = ClipsFilterPopover(self.app, self.searchentry)
        # sourceapp_filter = Gtk.Button(image=Gtk.Image().new_from_icon_name("application-default-icon", Gtk.IconSize.LARGE_TOOLBAR))
        # sourceapp_filter.props.always_show_image = True
        # sourceapp_filter.props.halign = Gtk.Align.END
        # sourceapp_filter.connect("clicked", self.on_sourceapp_filter, sourceapp_appchooser_popover)

        #------ searchbar ----#
        searchbar = Gtk.Grid()
        searchbar.props.name = "search-bar"
        searchbar.props.hexpand = True
        searchbar.props.halign = Gtk.Align.START
        searchbar.attach(self.searchentry, 0, 0, 1, 1)

        overlay = Gtk.Overlay()
        overlay.add(searchbar)
        # overlay.add_overlay(sourceapp_filter)
        # overlay.set_overlay_pass_through(sourceapp_filter, True)

        headerbar = Gtk.HeaderBar()
        headerbar.props.show_close_button = self.gio_settings.get_value("show-close-button")
        headerbar.props.has_subtitle = False
        headerbar.props.custom_title = overlay
        return headerbar

    def generate_statusbar(self):
        self.total_clips_label = Gtk.Label("Clips: {total}".format(total=self.props.application.total_clips))
        status = Gtk.Grid()
        status.props.name = "app-statusbar"
        status.props.halign = Gtk.Align.START
        status.props.valign = Gtk.Align.CENTER
        status.props.hexpand = True
        status.props.margin_left = 3
        status.attach(self.total_clips_label, 0, 0, 1, 1)
        return status

    def generate_actionbar(self):
        self.clipsapp_toggle = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral.clips-enabled-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        self.clipsapp_toggle.props.name = "app-action-enable"
        self.clipsapp_toggle.props.has_tooltip = True
        self.clipsapp_toggle.props.can_focus = False
        self.clipsapp_toggle.props.tooltip_text = "Clipboard Monitoring: Enabled"
        self.clipsapp_toggle.connect("clicked", self.app.on_clipsapp_action)
        
        self.passwordprotect_toggle = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral.clips-protect-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        self.passwordprotect_toggle.props.name = "app-action-protect"
        self.passwordprotect_toggle.props.has_tooltip = True
        self.passwordprotect_toggle.props.can_focus = False
        self.passwordprotect_toggle.props.tooltip_text = "Password Display/Monitoring: Enabled"
        # self.passwordprotect_toggle.get_style_context().add_class("clips-action-enabled")
        # self.passwordprotect_toggle.connect("clicked", self.on_clips_action, "protect")

        actionbar = Gtk.Grid()
        actionbar.props.name = "app-actionbar"
        actionbar.props.halign = Gtk.Align.START
        actionbar.props.valign = Gtk.Align.CENTER
        actionbar.props.margin_left = 3
        actionbar.attach(self.clipsapp_toggle, 0, 0, 1, 1)
        # actionbar.attach(self.passwordprotect_toggle, 1, 0, 1, 1)
        return actionbar

    def generate_viewswitch(self):
        self.view_switch = Granite.ModeSwitch.from_icon_name("com.github.hezral.clips-flowbox-symbolic", "com.github.hezral.clips-settings-symbolic")
        self.view_switch.props.valign = Gtk.Align.CENTER
        self.view_switch.props.halign = Gtk.Align.END
        self.view_switch.props.margin = 4
        self.view_switch.props.name = "view-switch"
        self.view_switch.connect_after("notify::active", self.on_view_visible)
        return self.view_switch

    def on_sourceapp_filter(self, button, popover):
        popover.set_relative_to(button)
        popover.show_all()
        popover.popup()
        popover.listbox.unselect_all()

    def on_searchbar_activate(self, searchentry, event, type):

        searchbar = self.searchentry.get_parent()

        if type == "in":
            searchbar.props.halign = Gtk.Align.FILL
            self.searchentry.props.hexpand = True
            self.searchentry.props.primary_icon_name = "quick-search"
            self.searchentry.props.name = "search-entry-active"
            self.searchentry.props.primary_icon_activatable = True
            self.searchentry.props.primary_icon_sensitive = True
        elif type == "out":
            if self.searchentry.props.text != "":
                self.searchentry.props.name = "search-entry-active"
            else:
                searchbar.props.halign = Gtk.Align.START
                self.searchentry.props.hexpand = False
                self.searchentry.props.primary_icon_name = "system-search-symbolic"
                self.searchentry.props.name = "search-entry"


    def on_search_entry_changed(self, search_entry):
        self.searchentry.props.primary_icon_name = "system-search-symbolic"
        if self.stack.get_visible_child() == self.clips_view:
            self.clips_view.flowbox.invalidate_filter()
            self.clips_view.flowbox_filter_func(search_entry)

    def on_view_visible(self, view_switch=None, gparam=None, action=None):

        # app startup
        # first-run: welcome_view + help_view
        # normal-run: 0 clips:  no_clips_view
        # normal-run: >0 clips: clips_view
        # app running
        # 0 clips: clips_view >> no_clips_view
        # >0 clips: no_clips_view >> clips_view
        # open settings_view from clips_view: clips_view >> settings_view
        # open settings_view from welcome_view: no_clips_view >> settings_view
        # open settings_view from no_clips_view: no_clips_view >> settings_view
        # open settings_view from help_view: no_clips_view >> settings_view
        # open help_view from settings: settings_view >> help_view
        # shortcut based switching

        self.info_view.show_all()
        self.settings_view.show_all()
        self.clips_view.show_all()

        total_clips_in_db = self.app.cache_manager.get_total_clips()[0][0]

        if view_switch == gparam == action == None:
            if self.gio_settings.get_boolean("first-run") is True and view_switch is None and gparam is None and action is None:
                self.app.on_clipsapp_action()
                self.info_view.welcome_view = self.info_view.generate_welcome_view()
                self.info_view.show_all()
                self.settings_view.hide()
                self.clips_view.hide()
                self.stack.set_visible_child(self.info_view)
                self.gio_settings.set_boolean("first-run", False)
                
            elif self.gio_settings.get_boolean("first-run") is False and view_switch is None and gparam is None and action is None:
                if total_clips_in_db == 0:
                    self.info_view.noclips_view = self.info_view.generate_noclips_view()
                    self.info_view.show_all()
                    self.settings_view.hide()
                    self.clips_view.hide()
                    self.stack.set_visible_child(self.info_view)
                elif total_clips_in_db > 0:
                    self.stack.set_visible_child(self.clips_view)
                    self.clips_view.show_all()
                    self.settings_view.hide()
                    self.info_view.hide()
                    self.view_switch.props.active = False
                else:
                    pass

        if action is not None:
            if action == "settings-view":
                self.stack.set_visible_child(self.settings_view)
                self.view_switch.props.active = True
                self.settings_view.scrolled_window.grab_focus()
            if action == "clips-view":
                self.stack.set_visible_child(self.clips_view)
                self.view_switch.props.active = False
            if action == "help-view":
                self.info_view.generate_help_view()
                self.stack.set_visible_child(self.info_view)
                self.info_view.show_all()
                self.settings_view.hide()
                self.clips_view.hide()

        if view_switch is not None:
            if view_switch.props.active:
                self.stack.set_visible_child(self.settings_view)
                self.settings_view.show_all()
                self.info_view.hide()
                self.clips_view.hide()
            else:
                if total_clips_in_db == 0:
                    self.info_view.noclips_view = self.info_view.generate_noclips_view()
                    self.stack.set_visible_child(self.info_view)
                    self.info_view.show_all()
                    self.settings_view.hide()
                    self.clips_view.hide()
                elif total_clips_in_db > 0:
                    self.stack.set_visible_child(self.clips_view)
                    self.clips_view.show_all()
                    self.settings_view.hide()
                    self.info_view.hide()
                else:
                    pass
        
        if self.stack.get_visible_child() == self.clips_view:
            self.searchentry.props.sensitive = True
        else:
            self.searchentry.props.sensitive = False
        
    def update_total_clips_label(self, event, count=1):
        total_clips = int(self.total_clips_label.props.label.split(": ")[1])
        if event == "add":
            total_clips = total_clips + count
        elif event == "delete":
            total_clips = total_clips - count
        self.total_clips_label.props.label = "Clips: {total}".format(total=total_clips)

# ----------------------------------------------------------------------------------------------------

class ClipsFilterPopover(Gtk.Popover):
    def __init__(self, app, search_entry, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.clips_search_entry = search_entry
        
        self.listbox = ClipsSourceAppListBox(app)
        # self.app_listbox.connect("row-selected", self.on_row_selected)
        self.listbox.connect("row-activated", self.on_row_activated)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_size_request(-1, 150)
        scrolled_window.props.expand = True
        scrolled_window.add(self.listbox)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.props.placeholder_text = "Search..."
        self.search_entry.props.margin = 6
        self.search_entry.props.hexpand = True
        self.search_entry.connect("search-changed", self.on_search_entry_changed)

        grid = Gtk.Grid()
        grid.attach(self.search_entry, 0, 0, 1, 1)
        grid.attach(Gtk.Separator(), 0, 1, 1, 1)
        grid.attach(scrolled_window, 0, 2, 1, 1)
        
        self.props.name = "clips-sourceapp-chooser"
        self.set_size_request(260, -1)
        self.add(grid)

    def on_row_selected(self, *args):
        self.add_selected()

    def on_row_activated(self, *args):
        self.add_selected()
        
    def add_selected(self, *args):
        app_name = self.listbox.get_selected_row().app_name 
        self.clips_search_entry.props.text = app_name
        self.popdown()

    def on_search_entry_changed(self, search_entry):
        self.listbox.invalidate_filter()
        self.listbox.app_listbox_filter_func(search_entry)

# ----------------------------------------------------------------------------------------------------

class ClipsSourceAppListBoxRow(Gtk.ListBoxRow):
    def __init__(self, app_name, icon_name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        icon_size = 24 * self.get_scale_factor()
        icon = Gtk.Image().new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        icon.set_pixel_size(icon_size)

        label = Gtk.Label(app_name)

        grid = Gtk.Grid()
        grid.props.margin = 6
        grid.props.column_spacing = 12
        grid.attach(icon, 0, 0, 1, 1)
        grid.attach(label, 1, 0, 1, 1)

        self.add(grid)
        self.props.name = "clips-sourceapp-listboxrow"
        self.app_name = app_name
        self.icon_name = icon_name

# ----------------------------------------------------------------------------------------------------

class ClipsSourceAppListBox(Gtk.ListBox):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app

        source_apps = self.app.cache_manager.load_source_apps()
        source_apps.sort(key=self.sort_apps)

        for source_app in source_apps:
            print(source_app[0])
            app_name, icon_name = self.app.utils.get_appinfo(source_app[0])
            self.add(ClipsSourceAppListBoxRow(app_name, icon_name))

        self.props.name = "app-listbox"
        
        self.props.selection_mode = Gtk.SelectionMode.BROWSE
        self.props.activate_on_single_click = False

    def sort_apps(self, val):
        return val[0].lower()
    
    def app_listbox_filter_func(self, search_entry):
        def filter_func(row, text):
            if text.lower() in row.app_name.lower():
                return True
            else:
                return False

        text = search_entry.get_text()
        self.set_filter_func(filter_func, text)
