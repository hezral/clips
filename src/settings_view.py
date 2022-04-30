# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

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
        theme_optin = SubSettings(type="checkbutton", name="theme-optin", label=None, sublabel=None, separator=True, params=("Follow system appearance style",))

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

        always_on_top = SubSettings(type="switch", name="always-on-top", label="Always on top", sublabel="Display above all windows",separator=True)
        always_on_top.switch.connect_after("notify::active", self.on_switch_activated)
        self.gio_settings.bind("always-on-top", always_on_top.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        show_close_button = SubSettings(type="switch", name="show-close-button", label="Show close button", sublabel="Close to quit Clips",separator=True)
        show_close_button.switch.connect_after("notify::active", self.on_switch_activated)
        self.gio_settings.bind("show-close-button", show_close_button.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        hide_onstartup_mode = SubSettings(type="switch", name="hide-on-startup", label="Hide on startup", sublabel="Hides Clips app window on startup", separator=True)
        self.gio_settings.bind("hide-on-startup", hide_onstartup_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        min_column_number = SubSettings(type="spinbutton", name="min-column-number", label="Columns", sublabel="Set minimum number of columns", separator=False, params=(1,9,1))
        min_column_number.spinbutton.connect("value-changed", self.on_spinbutton_activated)
        self.gio_settings.bind("min-column-number", min_column_number.spinbutton, "value", Gio.SettingsBindFlags.DEFAULT)

        display_behaviour_settings = SettingsGroup("Display & Behaviour", (theme_switch, theme_optin, show_close_button, hide_onstartup_mode, persistent_mode, always_on_top, sticky_mode, min_column_number, ))
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

        # excluded apps -------------------------------------------------
        excluded_apps_list_values = self.gio_settings.get_value("excluded-apps").get_strv()
        excluded_apps_list = SubSettings(type="listbox", name="excluded-apps", label=None, sublabel=None, separator=False, params=(excluded_apps_list_values, ), utils=self.app.utils)

        excluded_apps = SubSettings(type="button", name="excluded-apps", label=None, sublabel="Apps will not be monitored", separator=False, params=("Select app", Gtk.Image().new_from_icon_name("application-default-icon", Gtk.IconSize.LARGE_TOOLBAR), ))
        excluded_apps.button.connect("clicked", self.on_button_clicked, (excluded_apps_list, ))

        excluded = SettingsGroup("Excluded Apps", (excluded_apps, excluded_apps_list, ))
        self.flowbox.add(excluded)

        # file types  -------------------------------------------------
        file_types_list_values = self.gio_settings.get_value("file-types").get_strv()
        file_types_list = SubSettings(type="listbox", name="file-types", label=None, sublabel=None, separator=False, params=(file_types_list_values, ), utils=self.app.utils)

        file_types = SubSettings(type="button", name="file-types", label=None, sublabel="File types will be skipped", separator=False, params=("Select type", Gtk.Image().new_from_icon_name("application-octet-stream", Gtk.IconSize.LARGE_TOOLBAR), ))
        file_types.button.connect("clicked", self.on_button_clicked, (file_types_list, ))

        filetype = SettingsGroup("Excluded File Types", (file_types, file_types_list, ))
        self.flowbox.add(filetype)

        # keywords  -------------------------------------------------
        keywords_list_values = self.gio_settings.get_value("keywords").get_strv()
        keywords_list = SubSettings(type="listbox", name="keywords", label=None, sublabel=None, separator=False, params=(keywords_list_values, ), utils=self.app.utils)

        keywords = SubSettings(type="entry", name="keywords", label=None, sublabel="Any matches will be skipped", separator=False, params=None)
        keywords.entry.connect("activate", self.on_entry_activated, (keywords_list, ))

        keyword = SettingsGroup("Excluded Keywords", (keywords, keywords_list, ))
        self.flowbox.add(keyword)

        # protected apps -------------------------------------------------
        protected_apps_list_values = self.gio_settings.get_value("protected-apps").get_strv()
        protected_apps_list = SubSettings(type="listbox", name="protected-apps", label=None, sublabel=None, separator=False, params=(protected_apps_list_values, ), utils=self.app.utils)

        protected_apps = SubSettings(type="button", name="protected-apps", label=None, sublabel="Contents copied will be protected", separator=False, params=("Select app", Gtk.Image().new_from_icon_name("application-default-icon", Gtk.IconSize.LARGE_TOOLBAR), ))
        protected_apps.button.connect("clicked", self.on_button_clicked, (protected_apps_list, ))

        protected = SettingsGroup("Protected Apps", (protected_apps, protected_apps_list, ))
        self.flowbox.add(protected)

        # others -------------------------------------------------
        add_shortcut = SubSettings(type="button", name="add-shortcut", label="Add Shortcut", sublabel="Launch with keyboard shortcut like ⌘+Ctrl+C\nSet with 'gtk-launch com.github.hezral.clips'", separator=True, params=(" Add", Gtk.Image().new_from_icon_name("com.github.hezral.clips", Gtk.IconSize.LARGE_TOOLBAR),))
        add_shortcut.button.connect("clicked", self.on_button_clicked)

        reset_password = SubSettings(type="button", name="reset-password", label="Reset Password", sublabel="All protected clips will be changed", separator=True, params=(" Reset", Gtk.Image().new_from_icon_name("dialog-password", Gtk.IconSize.LARGE_TOOLBAR),))
        reset_password.button.connect("clicked", self.on_button_clicked)

        protected_mode_button_icon = Gtk.Image().new_from_icon_name("preferences-system-privacy", Gtk.IconSize.LARGE_TOOLBAR)
        if self.app.gio_settings.get_value("protected-mode"):
            protected_mode_state = "On"
            protected_mode_button_label = "Disable"
            protected_mode_button_icon.props.sensitive = False
        else:
            protected_mode_state = "Off"
            protected_mode_button_label = "Enable"
            protected_mode_button_icon.props.sensitive = True
        protected_mode = SubSettings(type="button", name="protected-mode", label="Protected Mode: {0}".format(protected_mode_state), sublabel="Toggle protected mode", separator=True, params=(protected_mode_button_label, protected_mode_button_icon,))
        protected_mode.button.connect("clicked", self.on_button_clicked, reset_password)

        unprotect_timeout = SubSettings(type="spinbutton", name="unprotect-timeout", label="Protected Reveal Timeout", sublabel="Timeout(sec) after revealing protected clips", separator=True, params=(1,1800,1))
        unprotect_timeout.spinbutton.connect("value-changed", self.on_spinbutton_activated)
        self.gio_settings.bind("unprotect-timeout", unprotect_timeout.spinbutton, "value", Gio.SettingsBindFlags.DEFAULT)

        quick_paste = SubSettings(type="switch", name="quick-paste", label="Quick paste", sublabel="Paste contents in active window after copy action",separator=True)
        self.gio_settings.bind("quick-paste", quick_paste.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        shake_reveal = SubSettings(type="switch", name="shake-reveal", label="Shake to reveal   ! experimental !", sublabel="Shake mouse to reveal app",separator=True)
        # shake_reveal.switch.connect_after("notify::active", self.on_switch_activated)
        self.app.gio_settings.bind("shake-reveal", shake_reveal.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        shake_sensitivity = SubSettings(type="spinbutton", name="shake-sensitivity", label="Shake sensitivity", sublabel="Adjust shake to reveal sensitivity", separator=False, params=(3,10,1))
        shake_sensitivity.spinbutton.connect("value-changed", self.on_spinbutton_activated)
        self.app.gio_settings.bind("shake-sensitivity", shake_sensitivity.spinbutton, "value", Gio.SettingsBindFlags.DEFAULT)

        others = SettingsGroup("Other", (add_shortcut, protected_mode, unprotect_timeout, reset_password, quick_paste, shake_reveal, shake_sensitivity))
        self.flowbox.add(others)

        # support -------------------------------------------------
        view_guides = SubSettings(type="button", name="view-help", label="Guides", sublabel="Guides on how to use Clips", separator=True, params=("View Guides", Gtk.Image().new_from_icon_name("help-contents", Gtk.IconSize.LARGE_TOOLBAR),))
        view_guides.button.connect("clicked", self.on_button_clicked)
        
        report_issue = SubSettings(type="button", name="report-issue", label="Have a feature request or issue?", sublabel="Report and help make Clips better", separator=True, params=("Report issue", Gtk.Image().new_from_icon_name("help-faq", Gtk.IconSize.LARGE_TOOLBAR),))
        report_issue.button.connect("clicked", self.on_button_clicked)

        buyme_coffee = SubSettings(type="button", name="buy-me-coffee", label="Show Support", sublabel="Thanks for supporting me!", separator=True, params=("Coffee Time", Gtk.Image().new_from_icon_name("com.github.hezral.clips-coffee", Gtk.IconSize.LARGE_TOOLBAR), ))
        buyme_coffee.button.connect("clicked", self.on_button_clicked)

        whats_new = SubSettings(type="button", name="whats-new", label="Whats New", sublabel="Latest release details", separator=True, params=("What's New", Gtk.Image().new_from_icon_name("software-update-available", Gtk.IconSize.LARGE_TOOLBAR), ))
        whats_new.button.connect("clicked", self.on_button_clicked)

        debug_mode = SubSettings(type="switch", name="debug-mode", label="Debug Mode", sublabel="For troubleshooting (restart required)",separator=False)
        self.gio_settings.bind("debug-mode", debug_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        debug_log = SubSettings(type="button", name="debug-log", label=None, sublabel="View debug log", separator=False, params=("Debug Log", Gtk.Image().new_from_icon_name("bug", Gtk.IconSize.LARGE_TOOLBAR), ))
        debug_log.button.connect("clicked", self.on_button_clicked)

        help = SettingsGroup("Support", (view_guides, report_issue, buyme_coffee, whats_new, debug_mode, debug_log))
        self.flowbox.add(help)

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
            content_type = "apps"
            app_chooser_popover = ListChooserPopover(subsettings=params[0], content_type=content_type)
            app_chooser_popover.set_relative_to(button)
            app_chooser_popover.show_all()
            app_chooser_popover.popup()

        if name == "file-types":
            content_type = "file-types"
            filetype_chooser_popover = ListChooserPopover(subsettings=params[0], content_type=content_type)
            filetype_chooser_popover.set_relative_to(button)
            filetype_chooser_popover.show_all()
            filetype_chooser_popover.popup()

        if name == "delete-all":
            label = Gtk.Label(label="Attention! This action will delete all clips from the cache and no recovery")
            if params:
                self.app.cache_manager.delete_all_record()
                self.delete_all_dialog.destroy()
            else:
                self.delete_all_dialog = custom_widgets.CustomDialog(
                dialog_parent_widget=self,
                dialog_title="Delete All Clips",
                dialog_content_widget=label,
                action_button_label="Delete All",
                action_button_name="delete-all",
                action_callback=self.on_button_clicked,
                action_type="destructive",
                size=None,
                data=(
                    True,
                    )
                )

        if name == "run-housekeeping-now":
            self.app.cache_manager.auto_housekeeping(self.gio_settings.get_int("auto-retention-period"), manual_run=True)

        if name == "view-help":
            self.app.main_window.on_view_visible(action="help-view")

        if name == "report-issue":
            Gtk.show_uri_on_window(None, "https://github.com/hezral/clips/issues/new", Gdk.CURRENT_TIME)

        if name == "buy-me-coffee":
            Gtk.show_uri_on_window(None, "https://www.buymeacoffee.com/hezral", Gdk.CURRENT_TIME)

        if name == "whats-new":
            Gtk.show_uri_on_window(None, "https://github.com/hezral/clips/releases", Gdk.CURRENT_TIME)

        if name == "add-shortcut":
            Gtk.show_uri_on_window(None, "settings://input/keyboard/shortcuts", GLib.get_current_time())

        if name == "debug-log":
            self.app.file_manager.show_files_in_file_manager(self.app.debug_log)

        if name == "reset-password":

            if self.app.gio_settings.get_value("protected-mode"):
                type = "full"
                title = "Reset Password"
                button_label = "Reset"
                copy_text = "Reset password for unlocking protected clips\nand update all protected clip's password"
            else:
                type = "editor"
                title = "Set Password"
                button_label = "Set"
                copy_text = "Set password for unlocking protected clips"
            
            password_editor = custom_widgets.PasswordEditor(
                main_label=copy_text, 
                gtk_application=self.app,
                type=type)

            if self.app.gio_settings.get_value("protected-mode"):
                callback = password_editor.reset_password
            else:
                callback = password_editor.set_password

            self.resetpassword_dialog = custom_widgets.CustomDialog(
                dialog_parent_widget=self,
                dialog_title=title,
                dialog_content_widget=password_editor,
                action_button_label=button_label,
                action_button_name="setpassword",
                action_callback=callback,
                action_type="destructive",
                size=[450,-1],
                data=(
                    None,
                    )
                )

        if name == "protected-mode":
            reset_password_button = params.button
            protected_mode_label_text = button.get_parent().label_text

            if self.app.gio_settings.get_value("protected-mode"):
                self.gio_settings.set_boolean("protected-mode", False)
                button.props.label = "Enable"
                button.props.image.props.sensitive = True
                protected_mode_label_text.props.label = "Protected Mode: Off"
            else:
                self.gio_settings.set_boolean("protected-mode", True)
                button.props.label = "Disable"
                button.props.image.props.sensitive = False
                protected_mode_label_text.props.label = "Protected Mode: On"
            
            label = [child for child in button.get_children()[0].get_child() if isinstance(child, Gtk.Label)][0]
            label.props.valign = Gtk.Align.CENTER

            authenticated, authenticate_return = self.app.utils.do_authentication("get")
            if authenticated and authenticate_return is None:
                reset_password_button = params.button
                reset_password_button.emit("clicked")

    def on_spinbutton_activated(self, spinbutton):        
        name = spinbutton.get_name()
        main_window = self.get_toplevel()

        if self.is_visible():
            if name == "min-column-number":
                self.on_min_column_number_changed(spinbutton.props.value)
                
            # if name == "auto-retention-period":
            #     print("spin:", spinbutton, spinbutton.props.value, name)

            # if name == "unprotect-timeout":
            #     print("spin:", spinbutton, spinbutton.props.value, name)

            if name == "shake-sensitivity":
                # print("spin:", spinbutton, spinbutton.props.value, name, main_window.app.shake_listener.needed_shake_count)
                if self.app.shake_listener is not None:
                    self.app.shake_listener.needed_shake_count = spinbutton.props.value
                    # print(self.app.shake_listener.needed_shake_count)

    def on_switch_activated(self, switch, gparam):
        name = switch.get_name()
        main_window = self.get_toplevel()
        
        if self.is_visible():

            if name == "persistent-mode":
                if switch.get_active():
                    self.app.window_manager._stop()
                else:
                    self.app.window_manager._run(callback=main_window.on_persistent_mode)

            if name == "sticky-mode":
                if switch.get_active():
                    main_window.stick()
                else:
                    main_window.unstick()

            if name == "always-on-top":
                if switch.get_active():
                    main_window.set_keep_above(True)
                else:
                    main_window.set_keep_above(False)

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
        main_window.clips_view.flowbox.props.min_children_per_line = value
        if hasattr(main_window.info_view, 'flowbox'):
            main_window.info_view.flowbox.props.min_children_per_line = value
        self.gio_settings.set_int(key="min-column-number", value=value)

    def on_entry_activated(self, entry, params):
        new_keyword = entry.props.text
        subsettings = params[0]
        subsettings.add_listboxrow(new_keyword, None, add_new=True)

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
            self.button.props.valign = Gtk.Align.START
            self.button.set_size_request(90, -1)
            if len(params) >1:
                label = [child for child in self.button.get_children()[0].get_child() if isinstance(child, Gtk.Label)][0]
                label.props.valign = Gtk.Align.CENTER
            self.attach(self.button, 1, 0, 1, 2)

        if type == "listbox":
            self.last_row_selected_idx = 0
            self.listbox = Gtk.ListBox()
            self.listbox.props.name = name
            self.listbox.connect("row-selected", self.on_row_selected)
            icon = None
            # if ("-apps" in name or "-types" in name)
            if params is not None:
                if "-apps" in name:
                    for app in params[0]:
                        app_name, icon_name = utils.get_appinfo(app)
                        self.add_listboxrow(app_name, icon_name)
                if "-types" in name:
                    for type in params[0]:
                        icon_name = utils.get_mimetype_icon(type)
                        self.add_listboxrow(type, icon_name)
                if "keywords" in name:
                    for keyword in params[0]:
                        self.add_listboxrow(keyword)

            self.scrolled_window = Gtk.ScrolledWindow()
            self.scrolled_window.props.shadow_type = Gtk.ShadowType.ETCHED_IN
            self.scrolled_window.add(self.listbox)
            self.scrolled_window.set_size_request(-1, 150)
            self.attach(self.scrolled_window, 0, 1, 1, 1)

        if type == "checkbutton":
            self.checkbutton = Gtk.CheckButton().new_with_label(params[0])
            self.checkbutton.props.name = name
            self.attach(self.checkbutton, 0, 0, 1, 2)

        if type == "entry":
            self.entry = Gtk.Entry()
            self.entry.props.name = name
            self.entry.props.halign = Gtk.Align.END
            self.entry.props.valign = Gtk.Align.START
            self.entry.props.hexpand = False
            self.entry.props.placeholder_text = "Enter keyword.."
            self.entry.set_size_request(-1, 34)
            self.attach(self.entry, 1, 0, 1, 2)

        if separator:
            row_separator = Gtk.Separator()
            row_separator.props.hexpand = True
            row_separator.props.valign = Gtk.Align.CENTER
            self.attach(row_separator, 0, 2, 2, 1)
        
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

    def add_listboxrow(self, item, icon_name=None, add_new=False):
        skip_add = False
        key_name = self.listbox.props.name

        if add_new:
            settings_values, gio_settings = self.get_gio_settings_values(key_name)
            if item not in settings_values:
                settings_values.append(item)
                gio_settings.set_strv(key_name, settings_values)
                # print(item, "added in {name} list".format(name=key_name))
            else:
                # print(item, "already in {name} list".format(name=key_name))
                skip_add = True

        if skip_add is False:
            grid = Gtk.Grid()
            grid.props.column_spacing = 10
            grid.props.margin = 6
            
            app_label = Gtk.Label(item)
            grid.attach(app_label, 1, 0, 1, 1)
            
            if icon_name is not None:
                icon_size = 32 * self.get_scale_factor()
                app_icon = Gtk.Image().new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
                app_icon.set_pixel_size(icon_size)
                grid.attach(app_icon, 0, 0, 1, 1)

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
            row.app_name = item
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
            # print(selected_row.app_name, "removed from {name} list".format(name=key_name))
        # else:
            # print(selected_row.app_name, "not in {name} list".format(name=key_name))
        
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

class ListChooserPopover(Gtk.Popover):
    def __init__(self, subsettings=None, content_type=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.subsettings = subsettings
        self.subsettings_listbox = self.subsettings.listbox

        self.choose_button = Gtk.Button(label="Choose")
        self.choose_button.connect("clicked", self.add_selected)
        self.choose_button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        self.choose_button.props.sensitive = False
        self.choose_button.props.margin = 6
        
        self.item_listbox = ItemsListBox(type=content_type)
        self.item_listbox.connect("row-selected", self.on_row_selected)
        self.item_listbox.connect("row-activated", self.on_row_activated)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_size_request(-1, 300)
        self.scrolled_window.props.expand = True
        self.scrolled_window.add(self.item_listbox)
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
        if self.item_listbox.get_selected_row() is not None:
            self.add_selected()
        
    def add_selected(self, *args):
        item_name = self.item_listbox.get_selected_row().item_name 
        icon_name = self.item_listbox.get_selected_row().icon_name
        self.subsettings.add_listboxrow(item_name, icon_name, add_new=True)
        self.popdown()

    def on_edget_overshot(self, *args):
        ...
        # print("on-edge-overshot", locals())
        # private void on_edge_overshot (Gtk.PositionType position) {
        #     if (position == Gtk.PositionType.BOTTOM) {
        #         app_list_box.load_next_apps ()
        #     }
        # }

    def on_search_entry_changed(self, search_entry):
        self.item_listbox.invalidate_filter()
        self.item_listbox.app_listbox_filter_func(search_entry)

# ----------------------------------------------------------------------------------------------------

class ItemListBoxRow(Gtk.ListBoxRow):
    def __init__(self, item_name, icon_name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        icon_size = 24 * self.get_scale_factor()
        icon = Gtk.Image().new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        icon.set_pixel_size(icon_size)

        label = Gtk.Label(item_name)

        grid = Gtk.Grid()
        grid.props.margin = 6
        grid.props.column_spacing = 12
        grid.attach(icon, 0, 0, 1, 1)
        grid.attach(label, 1, 0, 1, 1)

        self.add(grid)
        self.props.name = "app-listboxrow"
        self.item_name = item_name
        self.icon_name = icon_name

# ----------------------------------------------------------------------------------------------------

class ItemsListBox(Gtk.ListBox):

    LOADING_COUNT = 100
    max_index = -1
    current_index = 0
    search_query = ""
    search_cancellable = None
    list_items = None

    def __init__(self, type=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.type = type

        if type == "apps":
            self.apps = []
            all_apps = utils.get_all_apps()
            for app in all_apps:
                app_icon = all_apps[app][0]
                if "#" in app:
                    app_name = app.split("#")[0]
                else:
                    app_name = app
                app = (app_name, app_icon)
                self.apps.append(app)
            self.list_items = self.apps

        if type == "file-types":
            self.content_types = []
            all_content_types = Gio.content_types_get_registered()
            for type in all_content_types:
                type_icon = utils.get_mimetype_icon(type)
                type_item = (type, type_icon)
                self.content_types.append(type_item)
            self.list_items = self.content_types
        
        self.list_items.sort(key=self.sort_list)
        self.max_index = len(self.list_items) - 1

        for item in self.list_items:
            self.add(ItemListBoxRow(item_name=item[0], icon_name=item[1]))

        self.props.name = "items-listbox"
        self.props.selection_mode = Gtk.SelectionMode.MULTIPLE
        self.props.activate_on_single_click = False

    def sort_list(self, val):
        return val[0].lower()

    def sort_func(self, row_1, row_2, data, notify_destroy):
        return row_1.item_name.lower() > row_2.item_name.lower()
    
    def app_listbox_filter_func(self, search_entry):
        def filter_func(row, text):
            if text.lower() in row.item_name.lower():
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

