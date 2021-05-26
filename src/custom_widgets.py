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
gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Granite, GObject, Gdk

def generate_custom_dialog(dialog_parent_widget, dialog_title, dialog_content_widget, action_button_label, action_button_name, action_callback, data=None):

    parent_window = dialog_parent_widget.get_toplevel()

    def close_dialog(button):
        window.destroy()

    def on_key_press(window, eventkey):
        if eventkey.keyval == 65307: #63307 is esc key
            window.destroy()

    header = Gtk.HeaderBar()
    header.props.show_close_button = True
    header.props.decoration_layout = "close:"
    header.props.title = dialog_title
    header.get_style_context().add_class("default-decoration")
    header.get_style_context().add_class(Gtk.STYLE_CLASS_FLAT)

    dialog_parent_widget.ok_button = Gtk.Button(label=action_button_label)
    dialog_parent_widget.ok_button.props.name = action_button_name
    dialog_parent_widget.ok_button.props.hexpand = True
    dialog_parent_widget.ok_button.props.halign = Gtk.Align.END
    dialog_parent_widget.ok_button.set_size_request(65,25)
    dialog_parent_widget.ok_button.get_style_context().add_class("destructive-action")

    dialog_parent_widget.cancel_button = Gtk.Button(label="Cancel")
    dialog_parent_widget.cancel_button.props.expand = False
    dialog_parent_widget.cancel_button.props.halign = Gtk.Align.END
    dialog_parent_widget.cancel_button.set_size_request(65,25)

    dialog_parent_widget.ok_button.connect("clicked", action_callback, (data, dialog_parent_widget.cancel_button))
    dialog_parent_widget.cancel_button.connect("clicked", close_dialog)

    grid = Gtk.Grid()
    grid.props.expand = True
    grid.props.margin_top = 10
    grid.props.margin_bottom = grid.props.margin_left = grid.props.margin_right = 20
    grid.props.row_spacing = 10
    grid.props.column_spacing = 10
    grid.attach(dialog_content_widget, 0, 0, 2, 1)
    grid.attach(dialog_parent_widget.ok_button, 0, 1, 1, 1)
    grid.attach(dialog_parent_widget.cancel_button, 1, 1, 1, 1)

    window = Gtk.Window()
    window.set_size_request(150,100)
    window.get_style_context().add_class("rounded")
    window.set_titlebar(header)
    window.props.transient_for = parent_window
    window.props.modal = True
    window.props.resizable = False
    window.props.window_position = Gtk.WindowPosition.CENTER_ON_PARENT
    window.add(grid)
    window.show_all()
    window.connect("destroy", close_dialog)
    window.connect("key-press-event", on_key_press)

    dialog_parent_widget.cancel_button.grab_focus()

    return window

class CustomDialog(Gtk.Window):
    def __init__(self, dialog_parent_widget, dialog_title, dialog_content_widget, action_button_label, action_button_name, action_callback, size=None, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        parent_window = dialog_parent_widget.get_toplevel()

        def close_dialog(button):
            dialog_content_widget.destroy()
            self.destroy()

        def on_key_press(self, eventkey):
            if eventkey.keyval == 65307: #63307 is esc key
                dialog_content_widget.destroy()
                self.destroy()

        header = Gtk.HeaderBar()
        header.props.show_close_button = True
        header.props.decoration_layout = "close:"
        header.props.title = dialog_title
        header.get_style_context().add_class("default-decoration")
        header.get_style_context().add_class(Gtk.STYLE_CLASS_FLAT)

        dialog_parent_widget.ok_button = Gtk.Button(label=action_button_label)
        dialog_parent_widget.ok_button.props.name = action_button_name
        dialog_parent_widget.ok_button.props.hexpand = True
        dialog_parent_widget.ok_button.props.halign = Gtk.Align.END
        dialog_parent_widget.ok_button.set_size_request(65,25)
        dialog_parent_widget.ok_button.get_style_context().add_class("destructive-action")

        dialog_parent_widget.cancel_button = Gtk.Button(label="Cancel")
        dialog_parent_widget.cancel_button.props.expand = False
        dialog_parent_widget.cancel_button.props.halign = Gtk.Align.END
        dialog_parent_widget.cancel_button.set_size_request(65,25)

        dialog_parent_widget.ok_button.connect("clicked", action_callback, (data, dialog_parent_widget.cancel_button))
        dialog_parent_widget.cancel_button.connect("clicked", close_dialog)

        grid = Gtk.Grid()
        grid.props.expand = True
        grid.props.margin_top = 10
        grid.props.margin_bottom = grid.props.margin_left = grid.props.margin_right = 20
        grid.props.row_spacing = 10
        grid.props.column_spacing = 10
        grid.attach(dialog_content_widget, 0, 0, 2, 1)
        grid.attach(dialog_parent_widget.ok_button, 0, 1, 1, 1)
        grid.attach(dialog_parent_widget.cancel_button, 1, 1, 1, 1)

        if size is not None:
            self.set_size_request(size[0],size[1])
        else:
            self.set_size_request(150,100)

        self.get_style_context().add_class("rounded")
        self.set_titlebar(header)
        self.props.transient_for = parent_window
        self.props.modal = True
        self.props.resizable = False
        self.props.window_position = Gtk.WindowPosition.CENTER_ON_PARENT
        self.add(grid)
        self.show_all()
        self.connect("destroy", close_dialog)
        self.connect("key-press-event", on_key_press)

        dialog_parent_widget.cancel_button.grab_focus()


class PasswordEditor(Gtk.Grid):
    ''' 
        Widget for password editor interface
        Ported and adapted from:
        https://github.com/elementary/switchboard-plug-useraccounts/blob/99def4bf25d0dccdb000514994b33f1e0327a240/src/Dialogs/ChangePasswordDialog.vala
        https://github.com/elementary/switchboard-plug-useraccounts/blob/99def4bf25d0dccdb000514994b33f1e0327a240/src/Widgets/PasswordEditor.vala
        https://github.com/elementary/switchboard-plug-useraccounts/blob/b5d4cdcde10551a33440594c8fb2d805407b6638/src/Dialogs/NewUserDialog.vala
    '''

    def __init__(self, main_label, gtk_application, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # GObject.signal_new(signal_name, object_class, GObject.SIGNAL-flags, return_type, param_types)
        # param_types is a list object, example [GObject.TYPE_PYOBJECT, GObject.TYPE_STRING]
        if GObject.signal_is_valid_name("validation-changed") is False:
            GObject.signal_new("validation-changed", Gtk.Grid, GObject.SIGNAL_RUN_LAST, GObject.TYPE_BOOLEAN, [GObject.TYPE_PYOBJECT,])
        
        self.set_events(Gdk.EventMask.FOCUS_CHANGE_MASK)

        self.main_label = Gtk.Label(main_label)

        current_password_label = Granite.HeaderLabel("Current Password")

        self.current_password_entry = Gtk.Entry()
        self.current_password_entry.visibility = False
        self.current_password_entry.set_icon_tooltip_text(Gtk.EntryIconPosition.SECONDARY, "Press to authenticate")
        self.current_password_entry.connect("changed", self.on_current_password_entry_changed)
        self.current_password_entry.connect("activate", self.on_current_password_entry_activated)
        self.current_password_entry.connect("icon-release", self.on_current_password_entry_icon_release)
        self.current_password_entry.connect("focus-out-event", self.on_current_password_entry_focus_out)

        self.current_password_error_label = Gtk.Label("<span font_size=\"small\">{0}</span>".format("Authentication failed"))
        self.current_password_error_label.props.halign = Gtk.Align.END
        self.current_password_error_label.props.justify = Gtk.Justification.RIGHT
        self.current_password_error_label.props.max_width_chars = 55
        self.current_password_error_label.props.use_markup = True
        self.current_password_error_label.props.wrap = True
        self.current_password_error_label.props.xalign = 1
        self.current_password_error_revealer = Gtk.Revealer()
        self.current_password_error_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        self.current_password_error_revealer.add(self.current_password_error_label)
        self.current_password_error_revealer.get_child().get_style_context().add_class(Gtk.STYLE_CLASS_ERROR)

        password_entry_label = Granite.HeaderLabel("Choose a Password")

        self.password_entry = Granite.ValidatedEntry()
        self.password_entry.props.activates_default = True
        self.password_entry.props.hexpand = True
        self.password_entry.props.visibility = False
        self.password_entry.connect("changed", self.on_password_entry_changed)

        password_levelbar = Gtk.LevelBar().new_for_interval(0.0, 100.0)
        password_levelbar.props.mode = Gtk.LevelBarMode.CONTINUOUS
        password_levelbar.add_offset_value("low", 30.0)
        password_levelbar.add_offset_value("middle", 50.0)
        password_levelbar.add_offset_value("high", 80.0)
        password_levelbar.add_offset_value("full", 100.0)

        self.password_error_label = Gtk.Label("<span font_size=\"small\">{0}</span>".format("."))
        self.password_error_label.props.halign = Gtk.Align.END
        self.password_error_label.props.justify = Gtk.Justification.RIGHT
        self.password_error_label.props.max_width_chars = 55
        self.password_error_label.props.use_markup = True
        self.password_error_label.props.wrap = True
        self.password_error_label.props.xalign = 1
        self.password_error_revealer = Gtk.Revealer()
        self.password_error_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        self.password_error_revealer.add(self.password_error_label)
        self.password_error_revealer.get_child().get_style_context().add_class(Gtk.STYLE_CLASS_WARNING)

        confirm_label = Granite.HeaderLabel("Confirm Password")

        self.confirm_entry = Granite.ValidatedEntry()
        self.confirm_entry.props.activates_default = True
        self.confirm_entry.props.sensitive = False
        self.confirm_entry.props.visibility = False
        self.confirm_entry.connect("changed", self.on_confirm_entry_changed)

        self.confirm_entry_label = Gtk.Label("<span font_size=\"small\">{0}</span>".format("."))
        self.confirm_entry_label.props.halign = Gtk.Align.END
        self.confirm_entry_label.props.justify = Gtk.Justification.RIGHT
        self.confirm_entry_label.props.max_width_chars = 55
        self.confirm_entry_label.props.use_markup = True
        self.confirm_entry_label.props.wrap = True
        self.confirm_entry_label.props.xalign = 1
        self.confirm_entry_revealer = Gtk.Revealer()
        self.confirm_entry_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        self.confirm_entry_revealer.add(self.confirm_entry_label)
        self.confirm_entry_revealer.get_child().get_style_context().add_class(Gtk.STYLE_CLASS_ERROR)

        self.reveal_password_button = Gtk.CheckButton().new_with_label("Reveal password")
        self.reveal_password_button.bind_property("active", self.password_entry, "visibility", GObject.BindingFlags.DEFAULT)
        self.reveal_password_button.bind_property("active", self.confirm_entry, "visibility", GObject.BindingFlags.DEFAULT)

        self.props.row_spacing = 4
        self.props.orientation = Gtk.Orientation.VERTICAL
        self.add(self.main_label)
        self.add(current_password_label)
        self.add(self.current_password_entry)
        self.add(self.current_password_error_revealer)
        self.add(password_entry_label)
        self.add(self.password_entry)
        self.add(password_levelbar)
        self.add(self.password_error_revealer)
        self.add(confirm_label)
        self.add(self.confirm_entry)
        self.add(self.confirm_entry_revealer)
        self.add(self.reveal_password_button)

    def on_current_password_entry_changed(self, entry):
        print("on_current_password_entry_changed")
        if len(entry.props.text) > 0:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "go-jump-symbolic")
        else:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
        self.current_password_error_revealer.set_reveal_child(False)

    def on_current_password_entry_activated(self, entry):
        print("on_current_password_entry_activated")
        self.password_authentication()

    def on_current_password_entry_icon_release(self, entry, entry_icon_position, event):
        print("on_current_password_entry_icon_release")
        self.password_authentication()

    def on_current_password_entry_focus_out(self, entry, eventfocus):
        print("on_current_password_entry_focus_out")
        self.password_authentication()

    def on_password_entry_changed(self, validate_entry):
        print("on_password_entry_changed")
        validate_entry.props.is_valid = self.check_password()
        self.validate_form(validate_entry)

    def on_confirm_entry_changed(self, validate_entry):
        print("on_confirm_entry_changed")
        validate_entry.props.is_valid = self.confirm_password()
        self.validate_form(validate_entry)

    def password_authentication(self):
        print("password_authentication")
        print(locals())
        # private void password_auth () {
        #     current_pw_entry.set_icon_from_icon_name (Gtk.EntryIconPosition.SECONDARY, "process-working-symbolic");
        #     current_pw_entry.get_style_context ().add_class ("spin");

        #     Passwd.passwd_authenticate (get_passwd_handler (true), current_pw_entry.text, (h, e) => {
        #         if (e != null) {
        #             debug ("Authentication error: %s".printf (e.message));
        #             current_pw_error.reveal_child = true;
        #             is_authenticated = false;
        #             current_pw_entry.set_icon_from_icon_name (Gtk.EntryIconPosition.SECONDARY, "process-error-symbolic");
        #         } else {
        #             debug ("User is authenticated for password change now");
        #             is_authenticated = true;

        #             current_pw_entry.sensitive = false;
        #             current_pw_entry.set_icon_from_icon_name (Gtk.EntryIconPosition.SECONDARY, "process-completed-symbolic");
        #         }
        #         current_pw_entry.get_style_context ().remove_class ("spin");
        #     });
        # }

    def validate_form(self, validate_entry):
        print("validate_form")
        if self.password_entry.props.is_valid and self.confirm_password():
            validate_entry.props.is_valid = True
        self.emit("validation-changed", [validate_entry])

    def check_password(self):
        print("check_password")
        print(locals())
        # private bool check_password () {
        #     if (pw_entry.text == "") {
        #         confirm_entry.text = "";
        #         confirm_entry.sensitive = false;

        #         pw_levelbar.value = 0;

        #         pw_entry.set_icon_from_icon_name (Gtk.EntryIconPosition.SECONDARY, null);
        #         pw_error_revealer.reveal_child = false;
        #     } else {
        #         confirm_entry.sensitive = true;

        #         string? current_pw = null;
        #         if (current_pw_entry != null) {
        #             current_pw = current_pw_entry.text;
        #         }

        #         var pwquality = new PasswordQuality.Settings ();
        #         void* error;
        #         var quality = pwquality.check (pw_entry.text, current_pw, null, out error);

        #         if (quality >= 0) {
        #             pw_entry.set_icon_from_icon_name (Gtk.EntryIconPosition.SECONDARY, "process-completed-symbolic");
        #             pw_error_revealer.reveal_child = false;

        #             pw_levelbar.value = quality;

        #             is_obscure = true;
        #         } else {
        #             pw_entry.set_icon_from_icon_name (Gtk.EntryIconPosition.SECONDARY, "dialog-warning-symbolic");

        #             pw_error_revealer.reveal_child = true;
        #             pw_error_revealer.label = ((PasswordQuality.Error) quality).to_string (error);

        #             pw_levelbar.value = 0;

        #             is_obscure = false;
        #         }
        #         return true;
        #     }

        #     return false;
        # }

    def confirm_password(self):
        print("confirm_password")
        print(locals())
        # private bool confirm_password () {
        #     if (confirm_entry.text != "") {
        #         if (pw_entry.text != confirm_entry.text) {
        #             confirm_entry.set_icon_from_icon_name (Gtk.EntryIconPosition.SECONDARY, "process-error-symbolic");
        #             confirm_entry_revealer.label = _("Passwords do not match");
        #             confirm_entry_revealer.reveal_child = true;
        #         } else {
        #             confirm_entry.set_icon_from_icon_name (Gtk.EntryIconPosition.SECONDARY, "process-completed-symbolic");
        #             confirm_entry_revealer.reveal_child = false;
        #             return true;
        #         }
        #     } else {
        #         confirm_entry.set_icon_from_icon_name (Gtk.EntryIconPosition.SECONDARY, null);
        #         confirm_entry_revealer.reveal_child = false;
        #     }

        #     return false;
        # }

    def get_password(self):
        print("get_password")
        print(locals())
        # public string? get_password () {
        #     if (is_valid) {
        #         return pw_entry.text;
        #     } else {
        #         return null;
        #     }
        # }
