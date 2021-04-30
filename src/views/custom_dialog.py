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
from gi.repository import Gtk, Gdk

def generate_custom_dialog(self, title, content_widget, action_label, action_name, callback, data=None):

    parent = self.get_toplevel()

    def close_dialog(button):
        custom_window.destroy()

    def on_key_press(window, eventkey):
        if eventkey.keyval == 65307: #63307 is esc key
            custom_window.destroy()

    header = Gtk.HeaderBar()
    header.props.show_close_button = True
    header.props.decoration_layout = "close:"
    header.props.title = title
    header.get_style_context().add_class("default-decoration")
    header.get_style_context().add_class(Gtk.STYLE_CLASS_FLAT)

    self.ok_button = Gtk.Button(label=action_label)
    self.ok_button.props.name = action_name
    self.ok_button.props.hexpand = True
    self.ok_button.props.halign = Gtk.Align.END
    self.ok_button.set_size_request(65,25)
    self.ok_button.get_style_context().add_class("destructive-action")

    self.cancel_button = Gtk.Button(label="Cancel")
    self.cancel_button.props.expand = False
    self.cancel_button.props.halign = Gtk.Align.END
    self.cancel_button.set_size_request(65,25)

    self.ok_button.connect("clicked", callback, (data, self.cancel_button))
    self.cancel_button.connect("clicked", close_dialog)

    grid = Gtk.Grid()
    grid.props.expand = True
    grid.props.margin = 10
    grid.props.row_spacing = 10
    grid.props.column_spacing = 10
    grid.attach(content_widget, 0, 0, 2, 1)
    grid.attach(self.ok_button, 0, 1, 1, 1)
    grid.attach(self.cancel_button, 1, 1, 1, 1)

    custom_window = Gtk.Window()
    custom_window.set_size_request(150,100)
    custom_window.get_style_context().add_class("rounded")
    custom_window.set_titlebar(header)
    custom_window.props.transient_for = parent
    custom_window.props.modal = True
    custom_window.add(grid)
    custom_window.show_all()
    custom_window.connect("destroy", close_dialog)
    custom_window.connect("key-press-event", on_key_press)

    self.cancel_button.grab_focus()

    return custom_window