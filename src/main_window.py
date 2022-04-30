# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Granite, Gdk, GLib
from .clips_view import ClipsView
from .settings_view import SettingsView
from .info_view import InfoView

class ClipsWindow(Gtk.ApplicationWindow):

    position = []

    def __init__(self, *args, **kwargs):
        super().__init__(
                        title="Clips", 
                        name = "main-window",
                        window_position = Gtk.WindowPosition.CENTER,
                        *args, **kwargs
                    )

        self.utils = self.props.application.utils
        self.app = self.props.application
        self.gio_settings = self.props.application.gio_settings
        self.gtk_settings = self.props.application.gtk_settings

        self.clips_view = ClipsView(self.app)
        self.settings_view = SettingsView(self.app)
        self.info_view = InfoView(self.app, "No Clips Found","Start Copying Stuffs", "system-os-installer")

        self.stack = Gtk.Stack()
        self.stack.props.name = "main-stack"
        self.stack.props.transition_type = Gtk.StackTransitionType.CROSSFADE
        self.stack.props.transition_duration = 150
        self.stack.add_named(self.clips_view, self.clips_view.get_name())
        self.stack.add_named(self.settings_view, self.settings_view.get_name())
        self.stack.add_named(self.info_view, self.info_view.get_name())

        self.main_view = Gtk.Grid(name = "main-view")
        self.main_view.attach(self.stack, 0, 0, 3, 1)
        self.main_view.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), 0, 1, 3, 1)
        self.main_view.attach(self.generate_actionbar(), 0, 2, 1, 1)
        self.main_view.attach(self.generate_statusbar(), 1, 2, 1, 1)
        self.main_view.attach(self.generate_viewswitch(), 2, 2, 1, 1)

        self.set_titlebar(self.generate_headerbar())
        self.get_style_context().add_class("rounded")
        self.set_display_settings()
        self.set_main_window_size()
        self.add(self.main_view)
        self.show_all()

        self.connect("map", self.save_window_state)
        self.connect("delete-event", self.on_close_window)
        self.connect("hide", self.on_close_window)
        self.connect("destroy", self.on_close_window)
        self.connect("key-press-event", self.on_search_as_you_type)
        # self.connect("configure-event", self.on_configure_event)

    def set_display_settings(self):
        if not self.gio_settings.get_value("persistent-mode"):
            if self.app.window_manager is not None:
                self.app.window_manager._run(callback=self.on_persistent_mode)
        
        if self.gio_settings.get_value("sticky-mode"):
            self.stick()
        
        if self.gio_settings.get_value("always-on-top"):
            self.set_keep_above(True)

    def set_main_window_size(self, column_number=None, windowhints=None, base_size=[], min_size=[], max_size=[]):
        if column_number is None:
            column_number = self.gio_settings.get_int("min-column-number")

        if len(base_size) == 0:
            base_width, base_height = [340, 450]

        if len(min_size) == 0:
            min_width, min_height = [base_width, base_height]

        if len(max_size) == 0:
            max_width, max_height = [base_width, base_height]

        # min_width, min_height = min_size
        # min_width = 340

        geometry_attr = ['base_width', 'base_height']
        geometry_attr = ['min_width', 'min_height']
        geometry_attr = ['max_width', 'max_height']

        proceed = True

        if column_number == 1:
            base_width = min_width = 360

        elif column_number == 2:
            base_width = min_width = 600

        elif column_number == 3:
            base_width = min_width = 800

        elif column_number == 4:
            base_width = min_width = 958
        
        elif column_number == 5:
            base_width = 1100
            min_width = 958

        # elif column_number > 5:
        #     proceed = False
        
        if proceed:
            self.resize(base_width, base_height)
            self.set_size_request(min_width, base_height)            
            geometry = Gdk.Geometry()
            
            setattr(geometry, 'min_width', min_width)
            setattr(geometry, 'min_height', min_height)

            # setattr(geometry, 'max_width', max_width)
            # setattr(geometry, 'max_height', max_height)
            
            # setattr(geometry, 'base_width', base_width)
            # setattr(geometry, 'base_height', base_height)

            self.set_geometry_hints(None, geometry, Gdk.WindowHints.MIN_SIZE)
            # self.set_geometry_hints(None, geometry, Gdk.WindowHints.MIN_SIZE | Gdk.WindowHints.MAX_SIZE | Gdk.WindowHints.BASE_SIZE)

    def save_window_state(self, *args):
        w, h = self.get_size()
        x, y = self.get_position()

        self.app.gio_settings.set_int("pos-x", x)
        self.app.gio_settings.set_int("pos-y", y)
        self.app.gio_settings.set_int("window-height", h)
        self.app.gio_settings.set_int("window-width", w)

    def move_window(self, *args):
        # print("map", self.app.gio_settings.get_int("pos-x"), self.app.gio_settings.get_int("pos-y"))
        self.save_window_state()
        self.move(self.app.gio_settings.get_int("pos-x"), self.app.gio_settings.get_int("pos-y"))

    def on_close_window(self, window=None, event=None):
        self.save_window_state()
        # print(event, self.app.gio_settings.get_int("pos-x"), self.app.gio_settings.get_int("pos-y"))
        return False

    def on_configure_event(self, widget, event):
        self.app.logger.debug(event.x, event.y)

    def on_search_as_you_type(self, window, eventkey):
        proceed = False
        # print(Gdk.keyval_name(eventkey.keyval), len(Gdk.keyval_name(eventkey.keyval)), eventkey.state.value_names, len(eventkey.state.value_names))

        if eventkey.state.value_names == ['GDK_SHIFT_MASK'] and len(Gdk.keyval_name(eventkey.keyval)) == 1:
            proceed = True

        if eventkey.state.value_names == ['GDK_SHIFT_MASK', 'GDK_MOD2_MASK'] and len(Gdk.keyval_name(eventkey.keyval)) == 1:
            proceed = True

        if eventkey.state.value_names == ['GDK_MOD2_MASK'] and len(Gdk.keyval_name(eventkey.keyval)) == 1:
            proceed = True

        if eventkey.state.value_names == [] and len(Gdk.keyval_name(eventkey.keyval)) == 1:
            proceed = True
        
        if proceed:
            if self.is_visible() and self.searchentry.has_focus() is False:
                self.searchentry.grab_focus()

    def on_persistent_mode(self, wm_class):
        if wm_class is not None:
           if self.app.props.application_id not in wm_class:
                self.hide()

    def on_search_entry_key_pressed(self, search_entry, eventkey):
        key = Gdk.keyval_name(eventkey.keyval).lower()
        if self.clips_view.flowbox.get_child_at_index(0) is not None and key == "down": 
            self.clips_view.flowbox.select_child(self.clips_view.flowbox.get_child_at_index(0))
            self.clips_view.flowbox.get_child_at_index(0).grab_focus()

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
                
                
            elif self.gio_settings.get_boolean("first-run") is False and view_switch is None and gparam is None and action is None:
                if total_clips_in_db == 0:
                    self.info_view.noclips_view = self.info_view.generate_noclips_view()
                    self.searchentry.props.text = ""
                    self.info_view.show_all()
                    self.settings_view.hide()
                    self.clips_view.hide()
                    self.stack.set_visible_child(self.info_view)
                elif total_clips_in_db > 0:
                    self.stack.set_visible_child(self.clips_view)
                    self.clips_view.show_all()
                    self.settings_view.hide()
                    self.info_view.hide()
                else:
                    pass
                self.view_switch.props.active = False

        if action is not None:
            if action == "settings-view":
                self.stack.set_visible_child(self.settings_view)
                # self.set_main_window_size(min_size=)
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
                # self.set_main_window_size(min_size=)
                self.settings_view.show_all()
                self.info_view.hide()
                self.clips_view.hide()
            else:
                if total_clips_in_db == 0:
                    if self.gio_settings.get_boolean("first-run"):
                        self.info_view.welcome_view = self.info_view.generate_welcome_view()
                    else:
                        self.info_view.noclips_view = self.info_view.generate_noclips_view()
                        self.searchentry.props.text = ""

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

        if self.app.app_startup is False:
            if self.stack.get_visible_child() == self.clips_view:
                self.searchentry.props.sensitive = True
            else:
                self.searchentry.props.sensitive = False
        
    def on_button_press(self, button, eventbutton):

        if eventbutton.button == 1:
            self.app.on_clipsapp_action()
        # if eventbutton.button == 3:
        #     self.window_menu = Gtk.Menu()
        #     one_min = Gtk.MenuItem()
        #     one_min.props.label = "Disable 1 min"
        #     one_min.connect("activate", self.on_menu_activate)
        #     self.window_menu.append(one_min)
        #     self.window_menu.show_all()
        #     self.window_menu.popup_at_widget(button, Gdk.Gravity.NORTH, Gdk.Gravity.SOUTH_WEST, None)

    def on_menu_activate(self, menuitem):
        self.app.logger.debug(menuitem.props.label)

    def generate_headerbar(self):
        self.searchentry = Gtk.SearchEntry()
        self.searchentry.props.placeholder_text = "Search Clips"
        self.searchentry.props.hexpand = False
        self.searchentry.props.name = "search-entry"

        self.searchentry.connect("focus-in-event", self.on_searchbar_activate, "in")
        self.searchentry.connect("focus-out-event", self.on_searchbar_activate, "out")
        # self.searchentry.connect_after("delete-text", self.on_searchbar_activate, "delete")
        # self.searchentry.connect("icon-press", self.on_quicksearch_activate)
        
        self.searchentry.connect("search-changed", self.on_search_entry_changed)
        self.searchentry.connect("key-press-event", self.on_search_entry_key_pressed)

        searchbar = Gtk.Grid()
        searchbar.props.name = "search-bar"
        searchbar.props.hexpand = True
        searchbar.props.halign = Gtk.Align.START
        searchbar.attach(self.searchentry, 0, 0, 1, 1)

        overlay = Gtk.Overlay()
        overlay.add(searchbar)

        headerbar = Gtk.HeaderBar()
        headerbar.props.show_close_button = self.gio_settings.get_value("show-close-button")
        headerbar.props.has_subtitle = False
        headerbar.props.custom_title = overlay
        return headerbar

    def generate_statusbar(self):
        self.total_clips_label = Gtk.Label("Clips: {total}".format(total=self.props.application.total_clips))
        self.total_clips_label.props.has_tooltip = True
        self.total_clips_label.connect("query-tooltip", self.on_total_clips_tooltip)
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
        self.clipsapp_toggle.connect("button-press-event", self.on_button_press)
        
        actionbar = Gtk.Grid()
        actionbar.props.name = "app-actionbar"
        actionbar.props.halign = Gtk.Align.START
        actionbar.props.valign = Gtk.Align.CENTER
        actionbar.props.margin_left = 3
        actionbar.attach(self.clipsapp_toggle, 0, 0, 1, 1)
        return actionbar

    def generate_viewswitch(self):
        self.view_switch = Granite.ModeSwitch.from_icon_name("com.github.hezral.clips-flowbox-symbolic", "com.github.hezral.clips-settings-symbolic")
        self.view_switch.props.valign = Gtk.Align.CENTER
        self.view_switch.props.halign = Gtk.Align.END
        self.view_switch.props.margin = 4
        self.view_switch.props.name = "view-switch"
        self.view_switch.get_children()[1].props.can_focus = False
        self.view_switch.connect_after("notify::active", self.on_view_visible)
        return self.view_switch

    def update_total_clips_label(self, event, count=1):
        total_clips = int(self.total_clips_label.props.label.split(": ")[1])
        if event == "add":
            total_clips = total_clips + count
        elif event == "delete":
            total_clips = total_clips - count
        self.total_clips_label.props.label = "Clips: {total}".format(total=total_clips)

    def on_total_clips_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        grid = Gtk.Grid()
        grid.props.column_spacing = 4
        grid.props.row_spacing = 2

        total_clips_by_type = self.app.cache_manager.get_total_clips_by_type()
        i = 0
        j = 0
        for clip_type in total_clips_by_type:
            type_label = Gtk.Label("{0}: ".format(clip_type[0]))
            type_label.props.halign = Gtk.Align.END
            type_label.props.expand = True
            total_label = Gtk.Label(clip_type[1])
            total_label.props.halign = Gtk.Align.START
            total_label.props.expand = True

            grid.attach(type_label, i, j, 1, 1)
            grid.attach(total_label, i+1, j, 1, 1)
            j = j + 1

        grid.show_all()
        tooltip.set_custom(None)
        tooltip.set_custom(grid)
        return True


