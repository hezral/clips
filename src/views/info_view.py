#!/usr/bin/env python3

'''
   Copyright 2018 Adi Hezral (hezral@gmail.com)

   This file is part of Clips.

    Clips is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Clips is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Clips.  If not, see <http://www.gnu.org/licenses/>.
'''

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class InfoView(Gtk.Grid):
    def __init__(self, title, description, icon):
        super().__init__()
        
        title_label = Gtk.Label(title)
        title_label.get_style_context().add_class("h1")
        description_label = Gtk.Label(description)
        icon_image = Gtk.Image()
        
        icon_image.set_from_icon_name(icon, Gtk.IconSize.DIALOG)
        icon_image.set_pixel_size(96)

        icon_box = Gtk.EventBox()
        icon_box.set_valign(Gtk.Align.START)
        icon_box.add(icon_image)

        self.props.name = "info-view"
        self.props.column_spacing = 12
        self.props.row_spacing = 6
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.set_vexpand(True)
        self.props.margin = 24
        self.attach(icon_box, 1, 1, 1, 1)
        self.attach(title_label, 1, 2, 1, 1)
        self.attach(description_label, 1, 3, 1, 1)
        #self.set_visible(True)