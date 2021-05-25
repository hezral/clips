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
from gi.repository import Gtk

def generate_custom_dialog(dialog_parent_widget, dialog_title, dialog_content_widget, action_button_label, action_button_name, action_callback, data=None):

    dialog_parent_widget = dialog_parent_widget.get_toplevel()

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
    window.props.transient_for = dialog_parent_widget
    window.props.modal = True
    window.props.window_position = Gtk.WindowPosition.CENTER_ON_PARENT
    window.add(grid)
    window.show_all()
    window.connect("destroy", close_dialog)
    window.connect("key-press-event", on_key_press)

    dialog_parent_widget.cancel_button.grab_focus()

    return window