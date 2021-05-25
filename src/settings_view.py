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
from gi.repository import Gtk, Gio, Pango, GObject, Gdk, GLib, Granite
from . import custom_widgets
from . import utils

# ----------------------------------------------------------------------------------------------------

class SettingsView(Gtk.Grid):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app
        self.gio_settings = app.gio_settings
        self.gtk_settings = app.gtk_settings
        self.granite_settings = app.granite_settings
        
        # construct---
        self.props.name = "settings-view"
        self.get_style_context().add_class(self.props.name)
        self.props.expand = True

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.props.expand = True
        self.scrolled_window.props.can_focus = True
        self.scrolled_window.props.hscrollbar_policy = Gtk.PolicyType.NEVER

        self.flowbox = Gtk.FlowBox()
        self.flowbox.props.name = "settings-flowbox"
        self.flowbox.props.homogeneous = False
        self.flowbox.props.row_spacing = 20
        self.flowbox.props.column_spacing = 20
        self.flowbox.props.margin = 10
        self.flowbox.props.selection_mode = Gtk.SelectionMode.NONE
        self.flowbox.props.valign = Gtk.Align.START
        self.flowbox.props.halign = Gtk.Align.FILL
        self.scrolled_window.add(self.flowbox)
        self.attach(self.scrolled_window, 0, 0, 1, 1)

        # display behaviour -------------------------------------------------
        theme_switch = SubSettings(type="switch", name="theme-switch", label="Switch between Dark/Light theme", sublabel=None, separator=False)
        theme_optin = SubSettings(type="checkbutton", name="theme-optin", label=None, sublabel=None, separator=True, params=("Follow System Appearance Style",))

        theme_switch.switch.bind_property("active", self.gtk_settings, "gtk-application-prefer-dark-theme", GObject.BindingFlags.SYNC_CREATE)

        self.granite_settings.connect("notify::prefers-color-scheme", self.on_appearance_style_change, theme_switch)
        theme_switch.switch.connect_after("notify::active", self.on_switch_activated)
        theme_optin.checkbutton.connect_after("notify::active", self.on_checkbutton_activated, theme_switch)
        
        self.gio_settings.bind("prefer-dark-style", theme_switch.switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self.gio_settings.bind("theme-optin", theme_optin.checkbutton, "active", Gio.SettingsBindFlags.DEFAULT)

        persistent_mode = SubSettings(type="switch", name="persistent-mode", label="Persistent mode", sublabel="Stays open and updates as new clips added",separator=True)
        persistent_mode.switch.connect_after("notify::active", self.on_switch_activated)
        self.gio_settings.bind("persistent-mode", persistent_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)
        
        sticky_mode = SubSettings(type="switch", name="sticky-mode", label="Sticky mode", sublabel="Display on all workspaces",separator=True)
        sticky_mode.switch.connect_after("notify::active", self.on_switch_activated)
        self.gio_settings.bind("sticky-mode", sticky_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        show_close_button = SubSettings(type="switch", name="show-close-button", label="Show close button", sublabel=None,separator=True)
        show_close_button.switch.connect_after("notify::active", self.on_switch_activated)
        self.gio_settings.bind("show-close-button", show_close_button.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        hide_onstartup_mode = SubSettings(type="switch", name="hide-on-startup", label="Hide on startup", sublabel="Hides Clips app window on startup", separator=True)
        self.gio_settings.bind("hide-on-startup", hide_onstartup_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        min_column_number = SubSettings(type="spinbutton", name="min-column-number", label="Columns", sublabel="Set minimum number of columns", separator=False, params=(1,9,1))
        min_column_number.spinbutton.connect("value-changed", self.on_spinbutton_activated)
        self.gio_settings.bind("min-column-number", min_column_number.spinbutton, "value", Gio.SettingsBindFlags.DEFAULT)

        display_behaviour_settings = SettingsGroup("Display & Behaviour", (theme_switch, theme_optin, show_close_button, hide_onstartup_mode, persistent_mode, sticky_mode, min_column_number, ))
        self.flowbox.add(display_behaviour_settings)

        # housekeeping -------------------------------------------------
        auto_housekeeping_mode = SubSettings(type="switch", name="auto-housekeeping", label="Auto housekeeping clips", sublabel="Automatic housekeeping Clips after retention period", separator=True)
        self.gio_settings.bind("auto-housekeeping", auto_housekeeping_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        auto_retention_period = SubSettings(type="spinbutton", name="auto-retention-period", label="Rentention period", sublabel="Days to retain clips before house keeping", separator=True, params=(0,365,5))
        self.gio_settings.bind("auto-retention-period", auto_retention_period.spinbutton, "value", Gio.SettingsBindFlags.DEFAULT)

        run_houseekeeping_now = SubSettings(type="button", name="run-housekeeping-now", label="Run housekeeping now", sublabel="no last run date", separator=True, params=("Run now", Gtk.Image().new_from_icon_name("edit-clear", Gtk.IconSize.LARGE_TOOLBAR),))
        run_houseekeeping_now.button.connect("clicked", self.on_button_clicked, run_houseekeeping_now)

        delete_all = SubSettings(type="button", name="delete-all", label="Delete all clips from cache", sublabel=None, separator=False, params=("Delete all", Gtk.Image().new_from_icon_name("dialog-warning", Gtk.IconSize.LARGE_TOOLBAR),))
        delete_all.button.connect("clicked", self.on_button_clicked)
        delete_all.button.get_style_context().add_class("destructive-action")

        app_settings = SettingsGroup("Housekeeping", (auto_housekeeping_mode, auto_retention_period, run_houseekeeping_now, delete_all, ))
        self.flowbox.add(app_settings)

        # exceptions -------------------------------------------------
        excluded_apps_list_values = self.gio_settings.get_value("excluded-apps").get_strv()
        excluded_apps_list = SubSettings(type="listbox", name="excluded-apps", label=None, sublabel=None, separator=False, params=(excluded_apps_list_values, ), utils=self.app.utils)

        excluded_apps = SubSettings(type="button", name="excluded-apps", label="Exclude apps", sublabel="Copy events are excluded for apps selected", separator=False, params=("Select app", Gtk.Image().new_from_icon_name("application-default-icon", Gtk.IconSize.LARGE_TOOLBAR), ))
        excluded_apps.button.connect("clicked", self.on_button_clicked, (excluded_apps_list, ))

        excluded = SettingsGroup("Excluded Apps", (excluded_apps, excluded_apps_list, ))
        self.flowbox.add(excluded)

        # protected app -------------------------------------------------
        protected_apps_list_values = self.gio_settings.get_value("protected-apps").get_strv()
        protected_apps_list = SubSettings(type="listbox", name="protected-apps", label=None, sublabel=None, separator=False, params=(protected_apps_list_values, ), utils=self.app.utils)

        protected_apps = SubSettings(type="button", name="protected-apps", label="Protected apps", sublabel="Contents copied will be protected", separator=False, params=("Select app", Gtk.Image().new_from_icon_name("application-default-icon", Gtk.IconSize.LARGE_TOOLBAR), ))
        protected_apps.button.connect("clicked", self.on_button_clicked, (protected_apps_list, ))

        protected = SettingsGroup("Protected Apps", (protected_apps, protected_apps_list, ))
        self.flowbox.add(protected)

        # others -------------------------------------------------
        add_shortcut = SubSettings(type="button", name="add-shortcut", label="Add Shortcut", sublabel="Launch with keyboard shortcut like ⌘+Ctrl+C", separator=True, params=(" Add", Gtk.Image().new_from_icon_name("com.github.hezral.clips", Gtk.IconSize.LARGE_TOOLBAR),))
        add_shortcut.button.connect("clicked", self.on_button_clicked)

        reset_password = SubSettings(type="button", name="reset-password", label="Reset Password", sublabel="All protected clips will be changed", separator=True, params=(" Reset", Gtk.Image().new_from_icon_name("preferences-system-privacy", Gtk.IconSize.LARGE_TOOLBAR),))
        reset_password.button.connect("clicked", self.on_button_clicked)

        unprotect_timeout = SubSettings(type="spinbutton", name="unprotect-timeout", label="Timeout", sublabel="Timeout(sec) after revealing protected clips", separator=False, params=(1,1800,1))
        unprotect_timeout.spinbutton.connect("value-changed", self.on_spinbutton_activated)
        self.gio_settings.bind("unprotect-timeout", unprotect_timeout.spinbutton, "value", Gio.SettingsBindFlags.DEFAULT)

        others = SettingsGroup("Other", (add_shortcut, reset_password, unprotect_timeout))
        self.flowbox.add(others)

        # help -------------------------------------------------
        view_guides = SubSettings(type="button", name="view-help", label="Guides", sublabel="Guides on how to use Clips", separator=True, params=("View Guides", Gtk.Image().new_from_icon_name("help-contents", Gtk.IconSize.LARGE_TOOLBAR),))
        view_guides.button.connect("clicked", self.on_button_clicked)
        
        report_issue = SubSettings(type="button", name="report-issue", label="Have a feature request or issue?", sublabel="Report and help make Clips better", separator=True, params=("Report issue", Gtk.Image().new_from_icon_name("help-faq", Gtk.IconSize.LARGE_TOOLBAR),))
        report_issue.button.connect("clicked", self.on_button_clicked)

        buyme_coffee = SubSettings(type="button", name="buy-me-coffee", label="Show Support", sublabel="Thanks for supporting me!", separator=False, params=("Coffee Time", Gtk.Image().new_from_icon_name("com.github.hezral.clips-coffee", Gtk.IconSize.LARGE_TOOLBAR), ))
        buyme_coffee.button.connect("clicked", self.on_button_clicked)

        help = SettingsGroup("Support", (view_guides, report_issue, buyme_coffee))
        self.flowbox.add(help)

        # disable focus on flowboxchilds
        for child in self.flowbox.get_children():
            child.props.can_focus = False

    def on_checkbutton_activated(self, checkbutton, gparam, widget):
        name = checkbutton.get_name()
        theme_switch = widget
        if name == "theme-optin":
            if self.gio_settings.get_value("theme-optin"):
                prefers_color_scheme = self.granite_settings.get_prefers_color_scheme()
                sensitive = False
            else:
                prefers_color_scheme = Granite.SettingsColorScheme.NO_PREFERENCE
                theme_switch.switch.props.active = self.gio_settings.get_value("prefer-dark-style")
                sensitive = True

            self.gtk_settings.set_property("gtk-application-prefer-dark-theme", prefers_color_scheme)
            self.granite_settings.connect("notify::prefers-color-scheme", self.app.on_prefers_color_scheme)

            if "DARK" in prefers_color_scheme.value_name:
                active = True
            else:
                active = False

            theme_switch.switch.props.active = active
            theme_switch.props.sensitive = sensitive

    def on_appearance_style_change(self, granite_settings, gparam, widget):
        theme_switch = widget
        if theme_switch.switch.props.active:
            theme_switch.switch.props.active = False
        else:
            theme_switch.switch.props.active = True
        


    def on_button_clicked(self, button, params=None):
        name = button.get_name()

        if name == "excluded-apps" or name == "protected-apps":
            app_chooser_popover = AppChooserPopover(params=(params[0], ))
            app_chooser_popover.set_relative_to(button)
            app_chooser_popover.show_all()
            app_chooser_popover.popup()

        if name == "delete-all":
            label = Gtk.Label(label="Attention! This action will delete all clips from the cache and no recovery")
            if params:
                self.app.cache_manager.delete_all_record()
                self.delete_all_dialog.destroy()
            else:
                self.delete_all_dialog = custom_widgets.generate_custom_dialog(self, "Delete All Clips", label, "Delete All", "delete-all", self.on_button_clicked, (True, ))

        if name == "run-housekeeping-now":
            self.app.cache_manager.auto_housekeeping(self.gio_settings.get_int("auto-retention-period"), manual_run=True)

        if name == "view-help":
            self.app.main_window.on_view_visible(action="help-view")

        if name == "report-issue":
            Gtk.show_uri_on_window(None, "https://github.com/hezral/clips/issues/new", Gdk.CURRENT_TIME)

        if name == "buy-me-coffee":
            Gtk.show_uri_on_window(None, "https://www.buymeacoffee.com/hezral", Gdk.CURRENT_TIME)

        if name == "add-shortcut":
            Gtk.show_uri_on_window(None, "settings://input/keyboard/shortcuts", GLib.get_current_time())

        if name == "reset-password":

            # label = Gtk.Label(label="This will reset the password and also all protected clips")

            # current_password_label = Granite.HeaderLabel("Current Password")

            # current_password_entry = Gtk.Entry()
            # current_password_entry.visibility = False
            # current_password_entry.set_icon_tooltip_text(Gtk.EntryIconPosition.SECONDARY, "Press to authenticate")

            # current_password_error_label = Gtk.Label("<span font_size=\"small\">{0}</span>".format("Authentication failed"))
            # current_password_error_label.props.halign = Gtk.Align.END
            # current_password_error_label.props.justify = Gtk.Justification.RIGHT
            # current_password_error_label.props.max_width_chars = 55
            # current_password_error_label.props.use_markup = True
            # current_password_error_label.props.wrap = True
            # current_password_error_label.props.xalign = 1
            # current_password_error_revealer = Gtk.Revealer()
            # current_password_error_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
            # current_password_error_revealer.add(current_password_error_label)
            # current_password_error_revealer.get_child().get_style_context().add_class(Gtk.STYLE_CLASS_ERROR)

            # # current_password_entry.changed.connect (() => {
            # #     if (current_password_entry.text.length > 0) {
            # #         current_password_entry.set_icon_from_icon_name (Gtk.EntryIconPosition.SECONDARY, "go-jump-symbolic")
            # #     } else {
            # #         current_password_entry.set_icon_from_icon_name (Gtk.EntryIconPosition.SECONDARY, null)
            # #     }

            # #     current_pw_error.reveal_child = False
            # # })

            # # current_password_entry.activate.connect (password_auth)
            # # current_password_entry.icon_release.connect (password_auth)

            # # current_password_entry.focus_out_event.connect (() => {
            # #     password_auth ()

            # password_entry_label = Granite.HeaderLabel("Choose a Password")

            # password_entry = Granite.ValidatedEntry()
            # password_entry.props.hexpand = True
            # password_entry.props.visibility = False

            # password_levelbar = Gtk.LevelBar().new_for_interval(0.0, 100.0)
            # password_levelbar.props.mode = Gtk.LevelBarMode.CONTINUOUS
            # password_levelbar.add_offset_value("low", 30.0)
            # password_levelbar.add_offset_value("middle", 50.0)
            # password_levelbar.add_offset_value("high", 80.0)
            # password_levelbar.add_offset_value("full", 100.0)

            # password_error_label = Gtk.Label("<span font_size=\"small\">{0}</span>".format("."))
            # password_error_label.props.halign = Gtk.Align.END
            # password_error_label.props.justify = Gtk.Justification.RIGHT
            # password_error_label.props.max_width_chars = 55
            # password_error_label.props.use_markup = True
            # password_error_label.props.wrap = True
            # password_error_label.props.xalign = 1
            # password_error_revealer = Gtk.Revealer()
            # password_error_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
            # password_error_revealer.add(password_error_label)
            # password_error_revealer.get_child().get_style_context().add_class(Gtk.STYLE_CLASS_WARNING)

            # confirm_label = Granite.HeaderLabel("Confirm Password")

            # confirm_entry = Granite.ValidatedEntry()
            # confirm_entry.props.sensitive = False
            # confirm_entry.props.visibility = False

            # confirm_entry_label = Gtk.Label("<span font_size=\"small\">{0}</span>".format("."))
            # confirm_entry_label.props.halign = Gtk.Align.END
            # confirm_entry_label.props.justify = Gtk.Justification.RIGHT
            # confirm_entry_label.props.max_width_chars = 55
            # confirm_entry_label.props.use_markup = True
            # confirm_entry_label.props.wrap = True
            # confirm_entry_label.props.xalign = 1
            # confirm_entry_revealer = Gtk.Revealer()
            # confirm_entry_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
            # confirm_entry_revealer.add(confirm_entry_label)
            # confirm_entry_revealer.get_child().get_style_context().add_class(Gtk.STYLE_CLASS_ERROR)

            # revealoldpassword_button = Gtk.CheckButton().new_with_label("Reveal password")
            # revealoldpassword_button.bind_property("active", password_entry, "visibility", GObject.BindingFlags.DEFAULT)
            # revealoldpassword_button.bind_property("active", confirm_entry, "visibility", GObject.BindingFlags.DEFAULT)

            # # password_entry.connect("changed", self.password_is_valid, )
            # #             password_entry.changed.connect (() => {
            # #     pw_entry.is_valid = check_password ()
            # #     validate_form ()
            # # })

            # # confirm_entry.changed.connect (() => {
            # #     confirm_entry.is_valid = confirm_password ()
            # #     validate_form ()
            # # })

            # grid = Gtk.Grid()
            # grid.props.row_spacing = 4
            # grid.props.orientation = Gtk.Orientation.VERTICAL
            # grid.add(label)
            # grid.add(current_password_label)
            # grid.add(current_password_entry)
            # grid.add(current_password_error_revealer)
            # grid.add(password_entry_label)
            # grid.add(password_entry)
            # grid.add(password_levelbar)
            # grid.add(password_error_revealer)
            # grid.add(confirm_label)
            # grid.add(confirm_entry)
            # grid.add(confirm_entry_revealer)
            # grid.add(revealoldpassword_button)

            # self.resetpassword_dialog = custom_widgets.generate_custom_dialog(self, "Reset Password", grid, "Reset", "setpassword", self.on_button_clicked, (confirm_entry, password_entry, label))
            # # revealoldpassword_button.connect("clicked", self.on_button_clicked, oldpassword_entry)
            # # revealnewpassword_button.connect("clicked", self.on_button_clicked, newpassword_entry)
            # # newpassword_entry.connect("activate", self.on_newpassword_entry_activated)

            #-------------------------------------------------------
            label = Gtk.Label(label="This will reset the password and also all protected clips")
            oldpassword_entry = Gtk.Entry()
            oldpassword_entry.props.input_purpose = Gtk.InputPurpose.PASSWORD
            oldpassword_entry.props.visibility = False
            oldpassword_entry.props.hexpand = True
            oldpassword_entry.props.placeholder_text = " current password"
            oldpassword_entry.props.halign = Gtk.Align.FILL
            oldpassword_entry.props.valign = Gtk.Align.CENTER
            oldpassword_entry.set_size_request(280,32)

            newpassword_entry = Gtk.Entry()
            newpassword_entry.props.input_purpose = Gtk.InputPurpose.PASSWORD
            newpassword_entry.props.visibility = False
            newpassword_entry.props.hexpand = True
            newpassword_entry.props.placeholder_text = " new password"
            newpassword_entry.props.halign = Gtk.Align.FILL
            newpassword_entry.props.valign = Gtk.Align.CENTER
            newpassword_entry.set_size_request(280,32)

            revealoldpassword_button = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral.clips-hidepswd", Gtk.IconSize.LARGE_TOOLBAR))
            revealoldpassword_button.props.hexpand = True
            revealoldpassword_button.props.name = "revealpassword"
            revealoldpassword_button.props.halign = Gtk.Align.END
            revealoldpassword_button.props.valign = Gtk.Align.CENTER

            revealnewpassword_button = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral.clips-hidepswd", Gtk.IconSize.LARGE_TOOLBAR))
            revealnewpassword_button.props.hexpand = True
            revealnewpassword_button.props.name = "revealpassword"
            revealnewpassword_button.props.halign = Gtk.Align.END
            revealnewpassword_button.props.valign = Gtk.Align.CENTER

            grid = Gtk.Grid()
            grid.props.row_spacing = 10
            grid.attach(label, 0, 0, 2, 1)
            grid.attach(revealoldpassword_button, 0, 1, 1, 1)
            grid.attach(oldpassword_entry, 0, 1, 1, 1)
            grid.attach(revealnewpassword_button, 0, 2, 1, 1)
            grid.attach(newpassword_entry, 0, 2, 1, 1)
            self.resetpassword_dialog = custom_widgets.generate_custom_dialog(self, "Reset Password", grid, "Reset", "setpassword", self.on_button_clicked, (newpassword_entry, oldpassword_entry, label))
            revealoldpassword_button.connect("clicked", self.on_button_clicked, oldpassword_entry)
            revealnewpassword_button.connect("clicked", self.on_button_clicked, newpassword_entry)
            newpassword_entry.connect("activate", self.on_newpassword_entry_activated)
            #-------------------------------------------------------


        if button.props.name == "revealpassword":
            if params.props.text != "":
                if params.props.visibility:
                    params.props.visibility = False
                    button.set_image(Gtk.Image().new_from_icon_name("com.github.hezral.clips-hidepswd", Gtk.IconSize.LARGE_TOOLBAR))
                else:
                    params.props.visibility = True
                    button.set_image(Gtk.Image().new_from_icon_name("com.github.hezral.clips-revealpswd", Gtk.IconSize.LARGE_TOOLBAR))

        if button.props.name == "setpassword":
            newpassword_entry = params[0][0]
            oldpassword_entry = params[0][1]
            label = params[0][2]
            cancel_button = params[1]
            newpassword = newpassword_entry.props.text
            oldpassword = oldpassword_entry.props.text
            if newpassword != "" and oldpassword != "":
                get_password, get_password_data = self.app.utils.do_authentication("get")
                if oldpassword == get_password_data:
                    get_password, set_password = self.app.utils.do_authentication("reset", newpassword)
                    if get_password[0] and set_password[0]:
                        button.destroy()
                        cancel_button.props.label = "Close"
                        self.timeout_on_setpassword(label, newpassword_entry, oldpassword_entry)
                        self.app.cache_manager.reset_protected_clips(get_password[1])
                    else:
                        label.set_text("Password set failed: {error}".format(error=set_password[1]))
                else:
                    oldpassword_entry.props.placeholder_text = "Current password incorrect"
                    oldpassword_entry.props.text = ""

    def on_spinbutton_activated(self, spinbutton):        
        name = spinbutton.get_name()
        main_window = self.get_toplevel()

        if self.is_visible():
            if name == "min-column-number":
                self.on_min_column_number_changed(spinbutton.props.value)
                
            if name == "auto-retention-period":
                print("spin:", spinbutton, spinbutton.props.value, name)

            if name == "unprotect-timeout":
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

            if name == "theme-switch":
                if main_window.info_view.help_view:
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

    def on_newpassword_entry_activated(self, entry):
        self.ok_button.emit("clicked")

    def timeout_on_setpassword(self, label, entry1, entry2):

        def update_label(timeout):
            label.props.label = "Password succesfully reset ({i})".format(i=timeout)

        @self.app.utils.run_async
        def timeout_label(self, label):
            import time
            for i in reversed(range(3)):
                GLib.idle_add(update_label, (i))
                time.sleep(1)
            try:
                self.resetpassword_dialog.destroy()
            except:
                pass

        entry1.props.sensitive = entry2.props.sensitive = False
        timeout_label(self, label)

    def password_is_valid(self, *args):
        print(locals())
        print("password is valid")
        self.check_password()
        self.validate_form()
    
    def check_password(self):
        print("check password")
    
    def validate_form(self):
        print("validate form")

# ----------------------------------------------------------------------------------------------------

class SettingsGroup(Gtk.Grid):
    def __init__(self, group_label, subsettings_list, *args, **kwargs):
        super().__init__(*args, **kwargs)

        grid = Gtk.Grid()
        grid.props.margin = 8
        grid.props.hexpand = True
        grid.props.row_spacing = 8
        grid.props.column_spacing = 10

        i = 0
        for subsetting in subsettings_list:
            grid.attach(subsetting, 0, i, 1, 1)
            i += 1

        frame = Gtk.Frame()
        frame.props.name = "settings-group-frame"
        frame.props.hexpand = True
        frame.add(grid)

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
            if len(params) >1:
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

            self.scrolled_window = Gtk.ScrolledWindow()
            self.scrolled_window.props.shadow_type = Gtk.ShadowType.ETCHED_IN
            self.scrolled_window.add(self.listbox)
            self.scrolled_window.set_size_request(-1, 150)
            self.attach(self.scrolled_window, 0, 1, 1, 1)

        if type == "checkbutton":
            self.checkbutton = Gtk.CheckButton().new_with_label(params[0])
            self.checkbutton.props.name = name
            self.attach(self.checkbutton, 0, 0, 1, 2)

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

    def get_gio_settings_values(self, key_name):
        main_window = self.get_toplevel()
        gio_settings = main_window.props.application.gio_settings
        settings_values = gio_settings.get_value(key_name).get_strv()
        return settings_values, gio_settings

    def add_listboxrow(self, app_name, icon_name, add_new=False):
        skip_add = False
        key_name = self.listbox.props.name

        if add_new:
            settings_values, gio_settings = self.get_gio_settings_values(key_name)
            if app_name not in settings_values:
                settings_values.append(app_name)
                gio_settings.set_strv(key_name, settings_values)
                print(app_name, "added in {name} list".format(name=key_name))
            else:
                print(app_name, "already in {name} list".format(name=key_name))
                skip_add = True

        if skip_add is False:
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

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_size_request(-1, 300)
        self.scrolled_window.props.expand = True
        self.scrolled_window.add(self.app_listbox)
        # self.scrolled_window.connect("edge-overshot", self.on_edget_overshot)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.props.placeholder_text = "Search..."
        self.search_entry.props.margin = 6
        self.search_entry.props.hexpand = True
        self.search_entry.connect("search-changed", self.on_search_entry_changed)

        grid = Gtk.Grid()
        grid.attach(self.search_entry, 0, 0, 1, 1)
        grid.attach(Gtk.Separator(), 0, 1, 1, 1)
        grid.attach(self.scrolled_window, 0, 2, 1, 1)
        grid.attach(Gtk.Separator(), 0, 3, 1, 1)
        grid.attach(self.choose_button, 0, 4, 1, 1)

        self.props.name = "app-chooser"
        self.set_size_request(260, -1)
        self.add(grid)
        self.connect("closed", self.on_closed)

    def on_closed(self, *args):
        self.destroy()

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

        all_apps = utils.get_all_apps()

        for app in all_apps:
            app_icon = all_apps[app][0]
            app_name = app
            app = (app_name, app_icon)
            self.apps.append(app)
        
        self.apps.sort(key=self.sort_apps)
        self.max_index = len(self.apps) - 1

        for app in self.apps:
            self.add(AppListBoxRow(app_name=app[0], icon_name=app[1]))

        self.props.name = "app-listbox"
        
        self.props.selection_mode = Gtk.SelectionMode.BROWSE
        self.props.activate_on_single_click = False

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
