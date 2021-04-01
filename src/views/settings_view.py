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
from gi.repository import Gtk, Gio, Pango, GObject, Gdk



# ----------------------------------------------------------------------------------------------------

class SettingsView(Gtk.Grid):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app
        gio_settings = app.gio_settings
        gtk_settings = app.gtk_settings

        # display behaviour -------------------------------------------------

        # theme switch ----#
        theme_switch = SubSettings(type="switch", name="theme-switch", label="Switch between Dark/Light theme", sublabel=None, separator=True)
        theme_switch.switch.bind_property("active", gtk_settings, "gtk-application-prefer-dark-theme", GObject.BindingFlags.SYNC_CREATE)
        gio_settings.bind("prefer-dark-style", theme_switch.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        # persistent mode ----#
        persistent_mode = SubSettings(type="switch", name="persistent-mode", label="Persistent mode", sublabel="Stays open and updates as new clips added",separator=True)
        persistent_mode.switch.connect_after("notify::active", self.on_switch_activated)
        gio_settings.bind("persistent-mode", persistent_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)
        
        # sticky mode ----#
        sticky_mode = SubSettings(type="switch", name="sticky-mode", label="Sticky mode", sublabel="Display on all workspaces",separator=True)
        sticky_mode.switch.connect_after("notify::active", self.on_switch_activated)
        gio_settings.bind("sticky-mode", sticky_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        # show close button ----#
        show_close_button = SubSettings(type="switch", name="show-close-button", label="Show close button", sublabel=None,separator=True)
        show_close_button.switch.connect_after("notify::active", self.on_switch_activated)
        gio_settings.bind("show-close-button", show_close_button.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        # hide on startup ----#
        hide_onstartup_mode = SubSettings(type="switch", name="hide-on-startup", label="Hide on startup", sublabel="Hides Clips app window on startup", separator=True)
        hide_onstartup_mode.switch.connect_after("notify::active", self.on_switch_activated)
        gio_settings.bind("hide-on-startup", hide_onstartup_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        # min column number ----#
        min_column_number = SubSettings(type="spinbutton", name="min-column-number", label="Columns", sublabel="Set minimum number of columns", separator=False, data=(1,9,1))
        min_column_number.spinbutton.connect("value-changed", self.on_spinbutton_activated)
        gio_settings.bind("min-column-number", min_column_number.spinbutton, "value", Gio.SettingsBindFlags.DEFAULT)

        display_behaviour_settings = SettingsGroup("Display & Behaviour", (theme_switch, show_close_button, hide_onstartup_mode, persistent_mode, sticky_mode, min_column_number, ))

        # app behaviour -------------------------------------------------


        # auto housekeeping ----#
        autopurge_mode = SubSettings(type="switch", name="auto-housekeeping", label="Auto housekeeping clips", sublabel="Automatic housekeeping Clips after retention period", separator=True)
        autopurge_mode.switch.connect_after("notify::active", self.on_switch_activated)
        gio_settings.bind("auto-housekeeping", autopurge_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        # auto retention period ----#
        auto_retention_period = SubSettings(type="spinbutton", name="auto-retention-period", label="Rentention period", sublabel="Days to retain clips before house keeping", separator=False, data=(0,365,5))
        auto_retention_period.spinbutton.connect_after("value-changed", self.on_spinbutton_activated)
        gio_settings.bind("auto-retention-period", auto_retention_period.spinbutton, "value", Gio.SettingsBindFlags.DEFAULT)

        app_settings = SettingsGroup("Configuration", (autopurge_mode, auto_retention_period, ))

        # danger zone -------------------------------------------------
        
        # delete all ----#
        delete_all = SubSettings(type="button", name="delete-all", label="Delete all clips", sublabel=None, separator=False, data=(Gtk.Image().new_from_icon_name("dialog-warning", Gtk.IconSize.MENU),))
        delete_all.button.connect("clicked", self.on_button_clicked)
        delete_all.button.get_style_context().add_class("destructive-action")

        danger_zone = SettingsGroup("Danger Zone", (delete_all, ))



        #------ flowbox ----#
        self.flowbox = Gtk.FlowBox()
        self.flowbox.props.name = "settings-flowbox"
        self.flowbox.add(display_behaviour_settings)
        self.flowbox.add(app_settings)
        self.flowbox.add(danger_zone)
        self.flowbox.props.homogeneous = False
        self.flowbox.props.row_spacing = 20
        self.flowbox.props.column_spacing = 20
        self.flowbox.props.margin = 10
        self.flowbox.props.selection_mode = Gtk.SelectionMode.NONE

        #------ scrolled_window ----#
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.props.expand = True
        scrolled_window.props.hscrollbar_policy = Gtk.PolicyType.NEVER
        scrolled_window.add(self.flowbox)
        
        # construct--------#
        self.props.name = "settings-view"
        self.get_style_context().add_class(self.props.name)
        self.props.expand = True
        # # self.props.margin = 10
        # # self.props.margin_top = 12
        # self.props.row_spacing = 10
        # self.props.column_spacing = 10
        self.attach(scrolled_window, 0, 0, 1, 1)
        # self.attach(display_behaviour_settings, 0, 0, 1, 1)
        # self.attach(app_settings, 0, 1, 1, 1)
        # self.attach(danger_zone, 0, 2, 1, 1)
        

    def on_button_clicked(self, button):
        print("clicked")

    def on_spinbutton_activated(self, spinbutton):
        
        name = spinbutton.get_name()
        window = self.get_toplevel()

        print("spin:", name, "value:", spinbutton.props.value, )

        if self.is_visible():
            if name == "min-column-number":

                window.set_main_window_size(column_number=spinbutton.props.value)
                flowbox = self.app.utils.GetWidgetByName(widget=window, child_name="flowbox", level=0)
                flowbox.props.min_children_per_line = spinbutton.props.value
                

            if name == "auto-retention-period":
                print("spin:", spinbutton, spinbutton.props.value, name)

    def on_switch_activated(self, switch, gparam):
        name = switch.get_name()

        window = self.get_toplevel()
        headerbar = [child for child in window.get_children() if isinstance(child, Gtk.HeaderBar)][0]

        if self.is_visible():

            if name == "persistent-mode":
                if switch.get_active():
                    #print('state-flags-on')
                    window.disconnect_by_func(window.on_persistent_mode)
                else:
                    window.connect("state-flags-changed", window.on_persistent_mode)
                    #print('state-flags-off')

            if name == "sticky-mode":
                if switch.get_active():
                    window.stick()
                else:
                    window.unstick()

            if name == "show-close-button":
                if switch.get_active():
                    headerbar.set_show_close_button(True)
                else:
                    headerbar.set_show_close_button(False)
                    headerbar.hide()
                    headerbar.show_all()

            if name == "auto-housekeeping":
                print("auto-housekeeping")

            if name == "hide-on-startup":
                print("hide-on-startup")

# ----------------------------------------------------------------------------------------------------

class SettingsGroup(Gtk.Grid):
    def __init__(self, group_label, subsettings_list, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # settings grid --------#
        grid = Gtk.Grid()
        grid.props.margin = 8
        grid.props.hexpand = True
        grid.props.row_spacing = 8
        grid.props.column_spacing = 10

        i = 0
        for subsetting in subsettings_list:
            grid.attach(subsetting, 0, i, 1, 1)
            i += 1

        # subsettingsgroup frame --------#
        frame = Gtk.Frame()
        frame.props.name = "settings-group-frame"
        frame.props.hexpand = True
        frame.add(grid)

        # subsettingsgroup label --------#
        label = Gtk.Label(group_label)
        label.props.name = "settings-group-label"
        label.props.halign = Gtk.Align.START
        label.props.margin_left = 4

        self.props.name = "settings-group"
        self.props.halign = Gtk.Align.FILL
        self.props.hexpand = True
        self.props.row_spacing = 4
        self.props.can_focus = False
        self.attach(label, 0, 0, 1, 1)
        self.attach(frame, 0, 1, 1, 1)
        # self.set_size_request(460, -1)

# ----------------------------------------------------------------------------------------------------

class SubSettings(Gtk.Grid):
    def __init__(self, type, name, label, sublabel=None, separator=True, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
        # box--------#
        box = Gtk.VBox()
        box.props.spacing = 2
        box.props.hexpand = True

        # label--------#
        label_text = Gtk.Label(label)
        label_text.props.halign = Gtk.Align.START
        box.add(label_text)
        
        # sublabel--------#
        if sublabel is not None:
            sub_label = Gtk.Label(sublabel)
            sub_label.props.halign = Gtk.Align.START
            sub_label.props.wrap_mode = Pango.WrapMode.WORD
            sub_label.props.max_width_chars = 30
            sub_label.props.justify = Gtk.Justification.LEFT
            #sub_label.props.wrap = True
            sub_label.get_style_context().add_class("settings-sub-label")
            box.add(sub_label)

        if type == "switch":
            self.switch = Gtk.Switch()
            self.switch.props.name = name
            self.switch.props.halign = Gtk.Align.END
            self.switch.props.valign = Gtk.Align.CENTER
            self.switch.props.hexpand = False
            self.attach(self.switch, 1, 0, 1, 2)

        if type == "spinbutton":
            self.spinbutton = Gtk.SpinButton().new_with_range(min=data[0], max=data[1], step=data[2])
            self.spinbutton.props.name = name
            self.attach(self.spinbutton, 1, 0, 1, 2)

        if type == "button":
            self.button = Gtk.Button(label=label, image=data[0])
            self.button.props.name = name
            self.button.props.hexpand = False
            self.button.props.always_show_image = True
            self.attach(self.button, 1, 0, 1, 2)

        # separator --------#
        if separator:
            row_separator = Gtk.Separator()
            row_separator.props.hexpand = True
            row_separator.props.valign = Gtk.Align.CENTER
            self.attach(row_separator, 0, 2, 2, 1)
        
        # SubSettings construct--------#
        self.props.name = name
        self.props.hexpand = True
        self.props.row_spacing = 8
        self.props.column_spacing = 10
        self.attach(box, 0, 0, 1, 2)
        
# ----------------------------------------------------------------------------------------------------
    
class AppChooserPopover(Gtk.Popover):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.props.name = "appchooser"

        choose_button = Gtk.Button(label="Choose")
        choose_button.connect("clicked", self.on_button_clicked())
        choose_button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        choose_button.props.sensitive = False

        app_listbox = AppListBox()
        app_listbox.connect("row-selected", self.on_row_selected())
        app_listbox.connect("row-activated", self.on_row_activated())

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_size_request(-1, 300)
        scrolled_window.props.expand = True
        scrolled_window.add(app_listbox)
        scrolled_window.connect("edge-overshot", self.on_edget_overshot())

        search_entry = Gtk.SearchEntry


        # search_entry = new Gtk.SearchEntry ()
        # search_entry.placeholder_text = _ ("Search apps…")
        # search_entry.margin_bottom = search_entry.margin_top = search_entry.margin_start = search_entry.margin_end = 12
        # search_entry.hexpand = true
        # search_entry.search_changed.connect (on_search_entry_changed)

        # var box = new Gtk.Box (Gtk.Orientation.VERTICAL, 0)
        # box.add (search_entry)
        # box.add (new Gtk.Separator (Gtk.Orientation.HORIZONTAL))
        # box.pack_start (scrolled, true, true)
        # box.add (new Gtk.Separator (Gtk.Orientation.HORIZONTAL))
        # box.add (button_box)
        # add (box)

        # public AppChooserPopover () {
        #     Object ()
        # }

    def on_row_selected(self, *args):
        print("on-row-selected", locals())

        # private void on_row_selected (Gtk.ListBoxRow ? row) {
        #     choose_button.sensitive = row != null
        # }

    def on_row_activated(self, *args):
        print("on-row-activated", locals())

        # private void on_row_activated (Gtk.ListBoxRow row) {
        #     send_selected ()
        # }

    def on_button_clicked(self, button):
        print("choose button clicked")

        # private void send_selected () {
        #     Workspaces.Widgets.AppRow ? app = app_list_box.get_selected_app ()
        #     if (app != null) {
        #         selected (app.app_info)
        #     }
        # }

    def on_edget_overshot(self, *args):
        print("on-edge-overshot", locals())
        # private void on_edge_overshot (Gtk.PositionType position) {
        #     if (position == Gtk.PositionType.BOTTOM) {
        #         app_list_box.load_next_apps ()
        #     }
        # }

    def on_search_entry_changed(self, *args):
        print("on-search-entry-changed", locals())

        # private void on_search_entry_changed () {
        #     app_list_box.invalidate_filter ()
        #     app_list_box.search (search_entry.text)
        # }
# all_apps = Gio.AppInfo.get_all()  # Returns a list of DesktopAppInfo objects (see docs)

# # For example, print display name and description of all apps
# for app in all_apps:
#     print(app.get_display_name())

class AppListBox(Gtk.ListBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label = "app-listbox"