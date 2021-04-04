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
from gi.repository import Gtk, GdkPixbuf

import os
resource_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "images")

class InfoView(Gtk.Grid):
    def __init__(self, title, description, icon):
        super().__init__()
        
        self.props.name = "info-view"

        title_label = Gtk.Label(title)
        title_label.get_style_context().add_class("h1")
        description_label = Gtk.Label(description)
        icon_image = Gtk.Image()
        
        icon_image.set_from_icon_name(icon, Gtk.IconSize.DIALOG)
        icon_image.set_pixel_size(96)

        icon_box = Gtk.EventBox()
        icon_box.set_valign(Gtk.Align.START)
        icon_box.add(icon_image)

        scale = self.get_scale_factor()
        help_switch_views_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=os.path.join(resource_path, "help_switch_views.png"), width=200*scale, height=200*scale, preserve_aspect_ratio=True)
        help_switch_views_image = Gtk.Image().new_from_pixbuf(help_switch_views_pixbuf)

        self.props.column_spacing = 12
        self.props.row_spacing = 6
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.props.expand = True
        self.props.margin = 24
        self.attach(icon_box, 0, 1, 1, 1)
        self.attach(title_label, 0, 2, 1, 1)
        self.attach(description_label, 0, 3, 1, 1)
        self.attach(help_switch_views_image, 0, 4, 1, 1)

class HelpView(Gtk.Grid):
    def __init__(self, title, description, icon):
        super().__init__()

        self.props.name = "help-view"