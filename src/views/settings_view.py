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
        self.gio_settings = app.gio_settings
        self.gtk_settings = app.gtk_settings
        
        # construct---
        self.props.name = "settings-view"
        self.get_style_context().add_class(self.props.name)
        self.props.expand = True

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.props.expand = True
        scrolled_window.props.hscrollbar_policy = Gtk.PolicyType.NEVER

        self.flowbox = Gtk.FlowBox()
        self.flowbox.props.name = "settings-flowbox"
        self.flowbox.props.homogeneous = False
        self.flowbox.props.row_spacing = 20
        self.flowbox.props.column_spacing = 20
        self.flowbox.props.margin = 10
        self.flowbox.props.selection_mode = Gtk.SelectionMode.NONE
        scrolled_window.add(self.flowbox)
        self.attach(scrolled_window, 0, 0, 1, 1)


        # display behaviour -------------------------------------------------

        # theme switch
        theme_switch = SubSettings(type="switch", name="theme-switch", label="Switch between Dark/Light theme", sublabel=None, separator=True)
        theme_switch.switch.bind_property("active", self.gtk_settings, "gtk-application-prefer-dark-theme", GObject.BindingFlags.SYNC_CREATE)
        theme_switch.switch.connect_after("notify::active", self.on_switch_activated)
        self.gio_settings.bind("prefer-dark-style", theme_switch.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        # persistent mode
        persistent_mode = SubSettings(type="switch", name="persistent-mode", label="Persistent mode", sublabel="Stays open and updates as new clips added",separator=True)
        persistent_mode.switch.connect_after("notify::active", self.on_switch_activated)
        self.gio_settings.bind("persistent-mode", persistent_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)
        
        # sticky mode
        sticky_mode = SubSettings(type="switch", name="sticky-mode", label="Sticky mode", sublabel="Display on all workspaces",separator=True)
        sticky_mode.switch.connect_after("notify::active", self.on_switch_activated)
        self.gio_settings.bind("sticky-mode", sticky_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        # show close button
        show_close_button = SubSettings(type="switch", name="show-close-button", label="Show close button", sublabel=None,separator=True)
        show_close_button.switch.connect_after("notify::active", self.on_switch_activated)
        self.gio_settings.bind("show-close-button", show_close_button.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        # hide on startup
        hide_onstartup_mode = SubSettings(type="switch", name="hide-on-startup", label="Hide on startup", sublabel="Hides Clips app window on startup", separator=True)
        self.gio_settings.bind("hide-on-startup", hide_onstartup_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        # min column number
        min_column_number = SubSettings(type="spinbutton", name="min-column-number", label="Columns", sublabel="Set minimum number of columns", separator=False, params=(1,9,1))
        min_column_number.spinbutton.connect("value-changed", self.on_spinbutton_activated)
        self.gio_settings.bind("min-column-number", min_column_number.spinbutton, "value", Gio.SettingsBindFlags.DEFAULT)

        display_behaviour_settings = SettingsGroup("Display & Behaviour", (theme_switch, show_close_button, hide_onstartup_mode, persistent_mode, sticky_mode, min_column_number, ))
        self.flowbox.add(display_behaviour_settings)

        # housekeeping -------------------------------------------------

        # auto housekeeping
        autopurge_mode = SubSettings(type="switch", name="auto-housekeeping", label="Auto housekeeping clips", sublabel="Automatic housekeeping Clips after retention period", separator=True)
        # autopurge_mode.switch.connect_after("notify::active", self.on_switch_activated)
        self.gio_settings.bind("auto-housekeeping", autopurge_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        # auto retention period
        auto_retention_period = SubSettings(type="spinbutton", name="auto-retention-period", label="Rentention period", sublabel="Days to retain clips before house keeping", separator=True, params=(0,365,5))
        # auto_retention_period.spinbutton.connect_after("value-changed", self.on_spinbutton_activated)
        self.gio_settings.bind("auto-retention-period", auto_retention_period.spinbutton, "value", Gio.SettingsBindFlags.DEFAULT)

        # run housekeeping now
        run_houseekeeping_now = SubSettings(type="button", name="run-housekeeping-now", label="Run housekeeping now", sublabel="no last run date", separator=True, params=("Run now", Gtk.Image().new_from_icon_name("edit-clear", Gtk.IconSize.LARGE_TOOLBAR),))
        run_houseekeeping_now.button.connect("clicked", self.on_button_clicked, run_houseekeeping_now)
        run_houseekeeping_now.button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)

        # delete all
        delete_all = SubSettings(type="button", name="delete-all", label="Delete all clips from cache", sublabel=None, separator=False, params=("Delete all", Gtk.Image().new_from_icon_name("dialog-warning", Gtk.IconSize.LARGE_TOOLBAR),))
        delete_all.button.connect("clicked", self.on_button_clicked)
        delete_all.button.get_style_context().add_class("destructive-action")

        app_settings = SettingsGroup("Housekeeping", (autopurge_mode, auto_retention_period, run_houseekeeping_now, delete_all, ))
        self.flowbox.add(app_settings)

        # exceptions -------------------------------------------------

        # excluded app
        excluded_apps_list_values = self.gio_settings.get_value("excluded-apps").get_strv()
        excluded_apps_list = SubSettings(type="listbox", name="excluded-apps", label=None, sublabel=None, separator=False, params=(excluded_apps_list_values, ), utils=self.app.utils)

        excluded_appchooser_popover = AppChooserPopover(params=(excluded_apps_list, ))
        excluded_apps = SubSettings(type="button", name="excluded-apps", label="Exclude apps", sublabel="Copy events are excluded for apps selected", separator=False, params=("Select app", Gtk.Image().new_from_icon_name("application-default-icon", Gtk.IconSize.LARGE_TOOLBAR), ))
        excluded_apps.button.connect("clicked", self.on_button_clicked, (excluded_appchooser_popover, ))
        excluded_apps.button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)

        excluded = SettingsGroup("Excluded Apps", (excluded_apps, excluded_apps_list, ))
        self.flowbox.add(excluded)

        # # protected app -------------------------------------------------
        # protected_apps_list_values = self.gio_settings.get_value("protected-apps").get_strv()
        # protected_apps_list = SubSettings(type="listbox", name="protected-apps", label=None, sublabel=None, separator=False, params=(protected_apps_list_values, ))

        # protected_appchooser_popover = AppChooserPopover(params=(protected_apps_list, ))
        # protected_apps = SubSettings(type="button", name="protected-apps", label="Protected apps", sublabel="Contents copied will be protected", separator=False, params=("Select app", Gtk.Image().new_from_icon_name("application-default-icon", Gtk.IconSize.LARGE_TOOLBAR), ))
        # protected_apps.button.connect("clicked", self.on_button_clicked, (protected_appchooser_popover, ))
        # protected_apps.button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)

        # protected = SettingsGroup("Protected Apps", (protected_apps, protected_apps_list, ))
        # self.flowbox.add(protected)

        # help -------------------------------------------------
        view_guides = SubSettings(type="button", name="view-help", label="Guides", sublabel="Guides on how to use Clips", separator=True, params=("View Guides", Gtk.Image().new_from_icon_name("help-contents", Gtk.IconSize.LARGE_TOOLBAR),))
        view_guides.button.connect("clicked", self.on_button_clicked)
        view_guides.button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        
        report_issue = SubSettings(type="button", name="report-issue", label="Have a feature or issue?", sublabel="Report and help make Clips better", separator=False, params=("Report issue", Gtk.Image().new_from_icon_name("help-faq", Gtk.IconSize.LARGE_TOOLBAR),))
        report_issue.button.connect("clicked", self.on_button_clicked)
        report_issue.button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)

        help = SettingsGroup("Help", (view_guides, report_issue, ))
        self.flowbox.add(help)

        # disable focus on flowboxchilds
        for child in self.flowbox.get_children():
            child.props.can_focus = False
        
    def on_button_clicked(self, button, params=None):
        name = button.get_name()

        if name == "excluded-apps" or name == "protected-apps":
            app_chooser_popover = params[0]
            app_chooser_popover.set_relative_to(button)
            app_chooser_popover.show_all()
            app_chooser_popover.popup()

        if name == "delete-all":
            window = self.get_toplevel()
            dialog = Gtk.Dialog.new()
            dialog.props.title="Confirm Delete All"
            dialog.props.transient_for = window
            btn_ok = Gtk.Button(label="Delete all", image=Gtk.Image().new_from_icon_name("dialog-warning", Gtk.IconSize.MENU))
            btn_ok.props.always_show_image = True
            btn_ok.get_style_context().add_class("destructive-action")
            btn_cancel = Gtk.Button(label="Cancel")
            dialog.add_action_widget(btn_ok, Gtk.ResponseType.OK)
            dialog.add_action_widget(btn_cancel, Gtk.ResponseType.CANCEL)
            dialog.set_default_size(150, 100)
            label = Gtk.Label(label="Attention! This action will delete all clips from the cache and no recovery")
            box = dialog.get_content_area()
            box.props.margin = 10
            box.add(label)
            dialog.show_all()
            btn_cancel.grab_focus()
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                window.props.application.cache_manager.delete_all_record()
            dialog.destroy()

        if name == "run-housekeeping-now":
            # from datetime import datetime
            # # main_window = self.get_toplevel()
            # # sublabel_text = params.sublabel_text          
            self.app.cache_manager.auto_housekeeping(self.gio_settings.get_int("auto-retention-period"), manual_run=True)

        if name == "view-help":
            print("view-help")

        if name == "report-issue":
            print("view-help")
            Gtk.show_uri_on_window(None, "https://github.com/hezral/clips/issues/new", Gdk.CURRENT_TIME)

    def on_spinbutton_activated(self, spinbutton):        
        name = spinbutton.get_name()
        main_window = self.get_toplevel()

        if self.is_visible():
            if name == "min-column-number":
                self.on_min_column_number_changed(spinbutton.props.value)
                
            if name == "auto-retention-period":
                print("spin:", spinbutton, spinbutton.props.value, name)

    def on_switch_activated(self, switch, gparam):
        name = switch.get_name()
        main_window = self.get_toplevel()
        
        if self.is_visible():

            if name == "persistent-mode":
                if switch.get_active():
                    # print('state-flags-on')
                    main_window.disconnect_by_func(main_window.on_persistent_mode)
                else:
                    main_window.connect("state-flags-changed", main_window.on_persistent_mode)
                    # print('state-flags-off')

            if name == "sticky-mode":
                if switch.get_active():
                    main_window.stick()
                else:
                    main_window.unstick()

            if name == "show-close-button":
                if main_window is not None:
                    headerbar = [child for child in main_window.get_children() if isinstance(child, Gtk.HeaderBar)][0]

                    if switch.get_active():
                        headerbar.set_show_close_button(True)
                    else:
                        headerbar.set_show_close_button(False)
                        headerbar.hide()
                        headerbar.show_all()

            if name == "auto-housekeeping":
                print("auto-housekeeping")

            if name == "theme-switch":
                print("theme-switch")
                if main_window.info_view.help_view:
                    print("three")
                    for child in main_window.info_view.flowbox.get_children():
                        child.destroy()
                    main_window.info_view.help_view = main_window.info_view.generate_help_view()

    def on_min_column_number_changed(self, value):
        main_window = self.get_toplevel()
        main_window.set_main_window_size(column_number=value)
        clips_flowbox = self.app.utils.get_widget_by_name(widget=main_window, child_name="flowbox", level=0)
        help_flowbox = self.app.utils.get_widget_by_name(widget=main_window, child_name="help-flowbox", level=0)
        clips_flowbox.props.min_children_per_line = value
        if help_flowbox is not None:
            help_flowbox.props.min_children_per_line = value
        self.gio_settings.set_int(key="min-column-number", value=value)

# ----------------------------------------------------------------------------------------------------

class SettingsGroup(Gtk.Grid):
    def __init__(self, group_label, subsettings_list, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # settings grid ---
        grid = Gtk.Grid()
        grid.props.margin = 8
        grid.props.hexpand = True
        grid.props.row_spacing = 8
        grid.props.column_spacing = 10

        i = 0
        for subsetting in subsettings_list:
            grid.attach(subsetting, 0, i, 1, 1)
            i += 1

        # subsettingsgroup frame ---
        frame = Gtk.Frame()
        frame.props.name = "settings-group-frame"
        frame.props.hexpand = True
        frame.add(grid)

        # subsettingsgroup label ---
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
    def __init__(self, type, name, label=None, sublabel=None, separator=True, params=None, utils=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
        # box---
        box = Gtk.VBox()
        box.props.spacing = 2
        box.props.hexpand = True

        # label---
        if label is not None:
            self.label_text = Gtk.Label(label)
            self.label_text.props.halign = Gtk.Align.START
            box.add(self.label_text)
        
        # sublabel---
        if sublabel is not None:
            self.sublabel_text = Gtk.Label(sublabel)
            self.sublabel_text.props.halign = Gtk.Align.START
            self.sublabel_text.props.wrap_mode = Pango.WrapMode.WORD
            self.sublabel_text.props.max_width_chars = 30
            self.sublabel_text.props.justify = Gtk.Justification.LEFT
            #self.sublabel_text.props.wrap = True
            self.sublabel_text.get_style_context().add_class("settings-sub-label")
            box.add(self.sublabel_text)

        if type == "switch":
            self.switch = Gtk.Switch()
            self.switch.props.name = name
            self.switch.props.halign = Gtk.Align.END
            self.switch.props.valign = Gtk.Align.CENTER
            self.switch.props.hexpand = False
            self.attach(self.switch, 1, 0, 1, 2)

        if type == "spinbutton":
            self.spinbutton = Gtk.SpinButton().new_with_range(min=params[0], max=params[1], step=params[2])
            self.spinbutton.props.name = name
            self.attach(self.spinbutton, 1, 0, 1, 2)

        if type == "button":
            if len(params) == 1:
                self.button = Gtk.Button(label=params[0])
            else:
                self.button = Gtk.Button(label=params[0], image=params[1])
            self.button.props.name = name
            self.button.props.hexpand = False
            self.button.props.always_show_image = True
            label = [child for child in self.button.get_children()[0].get_child() if isinstance(child, Gtk.Label)][0]
            label.props.valign = Gtk.Align.CENTER
            self.attach(self.button, 1, 0, 1, 2)

        if type == "listbox" and "-apps" in name:
            self.last_row_selected_idx = 0
            self.listbox = Gtk.ListBox()
            self.listbox.props.name = name
            self.listbox.connect("row-selected", self.on_row_selected)
            icon = None
            if params is not None:
                for app in params[0]:
                    app_name, icon_name = utils.get_appinfo(app)
                    self.add_listboxrow(app_name, icon_name)

            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.props.shadow_type = Gtk.ShadowType.ETCHED_IN
            scrolled_window.add(self.listbox)
            scrolled_window.set_size_request(-1, 150)
            self.attach(scrolled_window, 0, 1, 1, 1)

        # separator ---
        if separator:
            row_separator = Gtk.Separator()
            row_separator.props.hexpand = True
            row_separator.props.valign = Gtk.Align.CENTER
            self.attach(row_separator, 0, 2, 2, 1)
        
        # SubSettings construct---
        self.props.name = name
        self.props.hexpand = True
        self.props.row_spacing = 8
        self.props.column_spacing = 10
        self.attach(box, 0, 0, 1, 2)

    def get_appinfo(self, app_name):
        all_apps = Gio.AppInfo.get_all()
        try:
            appinfo = [child for child in all_apps if child.get_name() == app_name][0]
        except:
            appinfo = None
        finally:
            return appinfo

    def get_gio_settings_values(self, key_name):
        main_window = self.get_toplevel()
        gio_settings = main_window.props.application.gio_settings
        settings_values = gio_settings.get_value(key_name).get_strv()
        return settings_values, gio_settings

    def add_listboxrow(self, app_name, icon_name, add_new=False):
        key_name = self.listbox.props.name

        if add_new:
            settings_values, gio_settings = self.get_gio_settings_values(key_name)
            if app_name not in settings_values:
                settings_values.append(app_name)
                gio_settings.set_strv(key_name, settings_values)
                print(app_name, "added in {name} list".format(name=key_name))
            else:
                print(app_name, "already in {name} list".format(name=key_name))

        app_label = Gtk.Label(app_name)
        icon_size = 32 * self.get_scale_factor()
        app_icon = Gtk.Image().new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        app_icon.set_pixel_size(icon_size)

        grid = Gtk.Grid()
        grid.props.column_spacing = 10
        grid.props.margin = 6
        grid.attach(app_icon, 0, 0, 1, 1)
        grid.attach(app_label, 1, 0, 1, 1)

        delete_row_button = Gtk.Button(image=Gtk.Image().new_from_icon_name("list-remove", Gtk.IconSize.MENU))
        delete_row_button.props.always_show_image = True
        delete_row_button.props.halign = Gtk.Align.END
        delete_row_button.props.margin_right = 10
        delete_row_button.connect("clicked", self.delete_listboxrow)

        delete_row_revealer = Gtk.Revealer()
        delete_row_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        delete_row_revealer.props.transition_duration = 250
        delete_row_revealer.add(delete_row_button)

        overlay = Gtk.Overlay()
        overlay.add(grid)
        overlay.add_overlay(delete_row_revealer)

        row = Gtk.ListBoxRow()
        row.app_name = app_name
        row.add(overlay)

        self.listbox.add(row)
        self.listbox.show_all()

    def delete_listboxrow(self, button):
        selected_row = self.listbox.get_selected_row()        
        key_name = self.listbox.props.name
        settings_values, gio_settings = self.get_gio_settings_values(key_name)

        if selected_row.app_name in settings_values:
            settings_values.remove(selected_row.app_name)
            gio_settings.set_strv(key_name, settings_values)
            selected_row.destroy()
            print(selected_row.app_name, "removed from {name} list".format(name=key_name))
        else:
            print(selected_row.app_name, "not in {name} list".format(name=key_name))
        
    def on_row_selected(self, listbox, listboxrow):
        last_row_idx = self.last_row_selected_idx
        last_row = listbox.get_row_at_index(last_row_idx)
        new_row = listboxrow
        if new_row is not None:
            new_row_idx = new_row.get_index()
            
            last_row.get_children()[0].get_children()[1].set_reveal_child(False)
            new_row.get_children()[0].get_children()[1].set_reveal_child(True)
            self.last_row_selected_idx = new_row_idx

# ----------------------------------------------------------------------------------------------------

class AppChooserPopover(Gtk.Popover):
    def __init__(self, params=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.subsettings = params[0]
        self.subsettings_listbox = self.subsettings.listbox

        self.choose_button = Gtk.Button(label="Choose")
        self.choose_button.connect("clicked", self.add_selected)
        self.choose_button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        self.choose_button.props.sensitive = False
        self.choose_button.props.margin = 6
        
        self.app_listbox = AppListBox()
        self.app_listbox.connect("row-selected", self.on_row_selected)
        self.app_listbox.connect("row-activated", self.on_row_activated)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_size_request(-1, 300)
        scrolled_window.props.expand = True
        scrolled_window.add(self.app_listbox)
        # scrolled_window.connect("edge-overshot", self.on_edget_overshot)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.props.placeholder_text = "Search..."
        self.search_entry.props.margin = 6
        self.search_entry.props.hexpand = True
        self.search_entry.connect("search-changed", self.on_search_entry_changed)

        grid = Gtk.Grid()
        grid.attach(self.search_entry, 0, 0, 1, 1)
        grid.attach(Gtk.Separator(), 0, 1, 1, 1)
        grid.attach(scrolled_window, 0, 2, 1, 1)
        grid.attach(Gtk.Separator(), 0, 3, 1, 1)
        grid.attach(self.choose_button, 0, 4, 1, 1)

        self.props.name = "app-chooser"
        self.set_size_request(260, -1)
        self.add(grid)

    def on_row_selected(self, *args):
        self.choose_button.props.sensitive = True

    def on_row_activated(self, *args):
        self.add_selected()

    def on_button_clicked(self, button):
        if self.app_listbox.get_selected_row() is not None:
            self.add_selected()
        
    def add_selected(self, *args):
        app_name = self.app_listbox.get_selected_row().app_name 
        icon_name = self.app_listbox.get_selected_row().icon_name
        self.subsettings.add_listboxrow(app_name, icon_name, add_new=True)
        self.popdown()

    def on_edget_overshot(self, *args):
        print("on-edge-overshot", locals())
        # private void on_edge_overshot (Gtk.PositionType position) {
        #     if (position == Gtk.PositionType.BOTTOM) {
        #         app_list_box.load_next_apps ()
        #     }
        # }

    def on_search_entry_changed(self, search_entry):
        self.app_listbox.invalidate_filter()
        self.app_listbox.app_listbox_filter_func(search_entry)

# ----------------------------------------------------------------------------------------------------

class AppListBoxRow(Gtk.ListBoxRow):
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
        self.props.name = "app-listboxrow"
        self.app_name = app_name
        self.icon_name = icon_name

# ----------------------------------------------------------------------------------------------------

class AppListBox(Gtk.ListBox):

    LOADING_COUNT = 100
    max_index = -1
    current_index = 0
    search_query = ""
    search_cancellable = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.apps = []

        all_apps = Gio.AppInfo.get_all()

        for app in all_apps: # Returns a list of DesktopAppInfo objects (see docs)
            if app.should_show():
                icon = app.get_icon()
                if icon is not None:
                    icon_name = icon.to_string()
                else:
                    icon_name = "application-other"
                name = app.get_name()
                app = (name, icon_name)
                self.apps.append(app)
        
        self.apps.sort(key=self.sort_apps)
        self.max_index = len(self.apps) - 1

        for app in self.apps:
            self.add(AppListBoxRow(app_name=app[0], icon_name=app[1]))

        self.props.name = "app-listbox"
        
        self.props.selection_mode = Gtk.SelectionMode.BROWSE
        self.props.activate_on_single_click = False
        # self.load_next_apps()

    def sort_apps(self, val):
        return val[0].lower()

    def sort_func(self, row_1, row_2, data, notify_destroy):
        return row_1.app.name.lower() > row_2.app.name.lower()
    
    def app_listbox_filter_func(self, search_entry):
        def filter_func(row, text):
            if text.lower() in row.app_name.lower():
                return True
            else:
                return False

        text = search_entry.get_text()
        self.set_filter_func(filter_func, text)

    def load_next(self):
        index = self.current_index + self.LOADING_COUNT
        bound = max(0, min(index, len(self.max_index)-1))

        if self.current_index >= bound:
            pass
        
        apps_to_load = self.apps[self.current_index:bound]

        for app in apps_to_load:
            self.add_app(app)

        current_index = index
        self.show_all()
