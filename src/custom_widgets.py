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
from gi.repository import Gtk, Granite, GObject, Gdk, Pango, GLib

class CustomDialog(Gtk.Window):
    def __init__(self, dialog_parent_widget, dialog_title, dialog_content_widget, action_button_label, action_button_name, action_callback, action_type, size=None, data=None, *args, **kwargs):
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
        header.props.show_close_button = False
        header.props.title = dialog_title
        header.get_style_context().add_class("default-decoration")
        header.get_style_context().add_class(Gtk.STYLE_CLASS_FLAT)

        dialog_parent_widget.ok_button = Gtk.Button(label=action_button_label)
        dialog_parent_widget.ok_button.props.name = action_button_name
        dialog_parent_widget.ok_button.props.expand = False
        dialog_parent_widget.ok_button.props.halign = Gtk.Align.END
        dialog_parent_widget.ok_button.set_size_request(65,25)
        if action_type == "destructive":
            dialog_parent_widget.ok_button.get_style_context().add_class("destructive-action")
        else:
            dialog_parent_widget.ok_button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)


        dialog_parent_widget.cancel_button = Gtk.Button(label="Cancel")
        dialog_parent_widget.cancel_button.props.hexpand = True
        dialog_parent_widget.cancel_button.props.halign = Gtk.Align.END
        dialog_parent_widget.cancel_button.set_size_request(65,25)

        dialog_parent_widget.ok_button.connect("clicked", action_callback, (data, dialog_parent_widget.cancel_button))
        dialog_parent_widget.cancel_button.connect("clicked", close_dialog)

        grid = Gtk.Grid()
        grid.props.expand = True
        grid.props.margin_top = 0
        grid.props.margin_bottom = grid.props.margin_left = grid.props.margin_right = 15
        grid.props.row_spacing = 10
        grid.props.column_spacing = 10
        grid.attach(dialog_content_widget, 0, 0, 2, 1)
        grid.attach(dialog_parent_widget.cancel_button, 0, 1, 1, 1)
        grid.attach(dialog_parent_widget.ok_button, 1, 1, 1, 1)

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

        # dialog_parent_widget.cancel_button.grab_focus()

class PasswordEditor(Gtk.Grid):
    ''' 
        Widget for password editor interface
        Ported and adapted from:
        https://github.com/elementary/switchboard-plug-useraccounts/blob/99def4bf25d0dccdb000514994b33f1e0327a240/src/Dialogs/ChangePasswordDialog.vala
        https://github.com/elementary/switchboard-plug-useraccounts/blob/99def4bf25d0dccdb000514994b33f1e0327a240/src/Widgets/PasswordEditor.vala
        https://github.com/elementary/switchboard-plug-useraccounts/blob/b5d4cdcde10551a33440594c8fb2d805407b6638/src/Dialogs/NewUserDialog.vala
    '''

    is_authenticated = False

    def __init__(self, main_label, gtk_application, type, callback=None, auth_callback=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # GObject.signal_new(signal_name, object_class, GObject.SIGNAL-flags, return_type, param_types)
        # param_types is a list object, example [GObject.TYPE_PYOBJECT, GObject.TYPE_STRING]
        if GObject.signal_lookup("validation-changed", Gtk.Grid) == 0:
            GObject.signal_new("validation-changed", Gtk.Grid, GObject.SIGNAL_RUN_LAST, GObject.TYPE_BOOLEAN, [GObject.TYPE_PYOBJECT,])
        
        self.app = gtk_application
        self.type = type
        self.callback = callback
        self.auth_callback = auth_callback
        self.set_events(Gdk.EventMask.FOCUS_CHANGE_MASK)

        self.props.row_spacing = 4
        self.props.orientation = Gtk.Orientation.VERTICAL

        self.main_label = Gtk.Label(main_label)
        self.main_label.props.wrap_mode = Pango.WrapMode.WORD
        self.main_label.props.max_width_chars = 40
        self.main_label.props.wrap = True
        self.main_label.props.hexpand = True
        self.main_label.props.justify = Gtk.Justification.CENTER
        self.main_label.props.margin_bottom = 10
        self.add(self.main_label)

        if self.type == "authenticate":
            self.generate_authenticate_fields()
        elif self.type == "editor":
            self.generate_editor_fields()
        elif self.type == "full":
            self.generate_authenticate_fields()
            self.generate_editor_fields()

        self.reveal_password_button = Gtk.CheckButton().new_with_label("Reveal password")
        self.add(self.reveal_password_button)

        if self.type == "authenticate":
            self.reveal_password_button.bind_property("active", self.current_password_entry, "visibility", GObject.BindingFlags.DEFAULT)
        elif self.type == "editor":
            self.reveal_password_button.bind_property("active", self.password_entry, "visibility", GObject.BindingFlags.DEFAULT)
            self.reveal_password_button.bind_property("active", self.confirm_entry, "visibility", GObject.BindingFlags.DEFAULT)
        elif self.type == "full":
            self.reveal_password_button.bind_property("active", self.current_password_entry, "visibility", GObject.BindingFlags.DEFAULT)
            self.reveal_password_button.bind_property("active", self.password_entry, "visibility", GObject.BindingFlags.DEFAULT)
            self.reveal_password_button.bind_property("active", self.confirm_entry, "visibility", GObject.BindingFlags.DEFAULT)

        if self.type != "authenticate":
            self.result_label = Gtk.Label("<span font_size=\"small\">{0}</span>".format("."))
            self.result_label.props.halign = Gtk.Align.END
            self.result_label.props.justify = Gtk.Justification.RIGHT
            self.result_label.props.max_width_chars = 55
            self.result_label.props.use_markup = True
            self.result_label.props.wrap = True
            self.result_label.props.xalign = 1
            self.result_label_revealer = Gtk.Revealer()
            self.result_label_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
            self.result_label_revealer.add(self.result_label)
            self.result_label_revealer.get_child().get_style_context().add_class(Gtk.STYLE_CLASS_INFO)
            self.add(self.result_label_revealer)

        if self.type == "authenticate":
            self.current_password_entry.grab_focus()
        elif self.type == "editor":
            self.password_entry.grab_focus()


    def generate_authenticate_fields(self):

        self.current_password_entry = Gtk.Entry()
        self.current_password_entry.props.visibility = False
        self.current_password_entry.set_icon_tooltip_text(Gtk.EntryIconPosition.SECONDARY, "Press to authenticate")

        if self.type != "authenticate":
            self.current_password_headerlabel = Granite.HeaderLabel("Current Password")
            self.add(self.current_password_headerlabel)
            
            self.current_password_entry.connect("icon-release", self.on_current_password_entry_icon_release)
            self.current_password_entry.connect("focus-out-event", self.on_current_password_entry_focus_out)

        self.current_password_entry.connect("changed", self.on_current_password_entry_changed)
        self.current_password_entry.connect("activate", self.on_current_password_entry_activated)

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

        self.add(self.current_password_entry)
        self.add(self.current_password_error_revealer)

    def generate_editor_fields(self):
        self.password_entry_headerlabel = Granite.HeaderLabel("Choose a Password")

        self.password_entry = Granite.ValidatedEntry()
        self.password_entry.props.activates_default = True
        self.password_entry.props.hexpand = True
        self.password_entry.props.visibility = False
        self.password_entry.connect("changed", self.on_password_entry_changed)

        self.password_levelbar = Gtk.LevelBar().new_for_interval(0.0, 100.0)
        self.password_levelbar.props.mode = Gtk.LevelBarMode.CONTINUOUS
        self.password_levelbar.add_offset_value("low", 30.0)
        self.password_levelbar.add_offset_value("middle", 50.0)
        self.password_levelbar.add_offset_value("high", 80.0)
        self.password_levelbar.add_offset_value("full", 100.0)

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

        self.confirm_headerlabel = Granite.HeaderLabel("Confirm Password")

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

        self.add(self.password_entry_headerlabel)
        self.add(self.password_entry)
        self.add(self.password_levelbar)
        self.add(self.password_error_revealer)
        self.add(self.confirm_headerlabel)
        self.add(self.confirm_entry)
        self.add(self.confirm_entry_revealer)

    def on_current_password_entry_changed(self, entry):
        if len(entry.props.text) > 0:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "go-jump-symbolic")
        else:
            entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
        self.current_password_error_revealer.set_reveal_child(False)

    def on_current_password_entry_activated(self, entry):
        if self.type == "authenticate":
            if self.password_authentication():
                self.auth_callback()
        else:
            self.password_authentication()

    def on_current_password_entry_icon_release(self, entry, entry_icon_position, event):
        self.password_authentication()

    def on_current_password_entry_focus_out(self, entry, eventfocus):
        self.password_authentication()

    def on_password_entry_changed(self, validate_entry):
        validate_entry.props.is_valid = self.check_password()
        self.validate_form(validate_entry)

    def on_confirm_entry_changed(self, validate_entry):
        validate_entry.props.is_valid = self.confirm_password()
        self.validate_form(validate_entry)

    def password_authentication(self, *args):
        self.current_password_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "process-working-symbolic")
        self.current_password_entry.get_style_context().add_class("spin")

        authenticated, authenticate_return = self.app.utils.do_authentication("get")

        if authenticated and self.current_password_entry.props.text == authenticate_return:
            self.is_authenticated = True
            self.current_password_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "process-completed-symbolic")
            self.current_password_entry.props.sensitive = False
            self.current_password_entry.get_style_context().remove_class("spin")
            return True
        else:
            self.is_authenticated = False
            if authenticated is False:
                message = "Authentication error: {0}".format(authenticate_return)
            else:
                message = "Authentication error"
            self.current_password_error_label.props.label = message
            self.current_password_error_revealer.set_reveal_child(True)
            self.current_password_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "process-error-symbolic")
            
            self.current_password_entry.get_style_context().remove_class("spin")
            return False

    def validate_form(self, validate_entry):
        if self.password_entry.props.is_valid and self.confirm_password():
            validate_entry.props.is_valid = True
        self.emit("validation-changed", [validate_entry])

    def check_password(self):
        if self.password_entry.props.text == "":
            self.confirm_entry.props.text = ""
            self.confirm_entry.props.sensitive = False

            self.password_levelbar.props.value = 0

            self.password_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
            self.password_error_revealer.set_reveal_child(False)
        
        else:
            self.confirm_entry.props.sensitive = True

            try:
                current_password = self.current_password_entry.props.text
            except:
                current_password = ""


            import pwquality
            password_quality = 0
            password_quality_settings = pwquality.PWQSettings()
            error = None
            try:
                password_quality = password_quality_settings.check(self.password_entry.props.text, current_password, None)
            except pwquality.PWQError as error:
                error_msg = error

            if password_quality >= 0:
                self.password_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "process-completed-symbolic")
                self.password_error_revealer.set_reveal_child(False)

                self.password_levelbar.props.value = password_quality

                self.is_obscure = True
            
            else:
                self.password_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "dialog-warning-symbolic")

                self.password_error_revealer.set_reveal_child(True)
                self.password_error_label = error_msg.to_string()

                self.password_levelbar.props.value = 0

                self.is_obscure = False
            
            return True

        return False

    def confirm_password(self):
        if self.confirm_entry.props.text != "":
            if self.password_entry.props.text != self.confirm_entry.props.text:
                self.confirm_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "process-error-symbolic")
                self.confirm_entry_label.props.label = "Passwords do not match"
                self.confirm_entry_revealer.set_reveal_child(True)
        
            else:
                self.confirm_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "process-completed-symbolic")
                self.confirm_entry_revealer.set_reveal_child(False)
                return True

        else:
                self.confirm_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, None)
                self.confirm_entry_revealer.set_reveal_child(False)

        return False

    def reset_password(self, button, params=None):
        
        cancel_button = params[1]
        if self.password_entry.props.text != "" and self.current_password_entry.props.text != "":
            if self.password_authentication():
                if self.password_entry.props.text == self.confirm_entry.props.text:
                    get_password, set_password = self.app.utils.do_authentication("reset", self.password_entry.props.text)
                    if get_password[0] and set_password[0]:
                        button.destroy()
                        cancel_button.props.label = "Close"
                        self.timeout_on_setpassword()
                        if self.type == "full":
                            self.app.cache_manager.reset_protected_clips(get_password[1])
                    else:
                        self.result_label.set_text("Password set failed: {error}".format(error=set_password[1]))
                    self.result_label_revealer.set_reveal_child(True)

    def set_password(self, button, params=None):

        if self.password_entry.props.text != "":
            if self.password_entry.props.text == self.confirm_entry.props.text:
                set_password = self.app.utils.do_authentication("set", self.password_entry.props.text)
                if set_password[0]:
                    button.destroy()
                    self.timeout_on_setpassword()
                    self.app.gio_settings.set_boolean("protected-mode", True)
                else:
                    self.result_label.set_text("Password set failed: {error}".format(error=set_password[1]))
                self.result_label_revealer.set_reveal_child(True)

    def timeout_on_setpassword(self):

        def update_label(timeout):
            self.result_label.props.label = "Password succesfully set ({i})".format(i=timeout)

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

        if self.callback is not None:
            self.callback()
        timeout_label(self, self.result_label)
