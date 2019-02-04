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
from gi.repository import Gtk, Gdk

class ClipsListRow(Gtk.ListBoxRow):
    def __init__(self, data):
        super().__init__()

        def generate_delete_button(self, delete_image):
            delete_button = Gtk.EventBox()
            delete_button.add(delete_image)
            delete_button.set_tooltip_text("Remove this clip")
            return delete_button

        def generate_edit_button():
            edit_button = Gtk.EventBox ()
            edit_button.add(edit_image)
            edit_button.set_tooltip_text("Edit this alias")


        thumb_clips_generic = Gtk.Image()
        thumb_clips_generic.props.valign = Gtk.Align.CENTER
        thumb_clips_generic.props.halign = Gtk.Align.CENTER
        thumb_clips_generic.props.pixel_size = 64
        #thumb_clips_generic.props.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size()

        delete_image = Gtk.Image.new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        edit_image = Gtk.Image.new_from_icon_name("document-properties-symbolic", Gtk.IconSize.SMALL_TOOLBAR)

        icon = Gtk.Image.new_from_icon_name("utilities-terminal", Gtk.IconSize.DIALOG)
        icon.set_pixel_size(64)
        vertical_box = Gtk.Box(Gtk.Orientation.VERTICAL, 6)

        self.delete_button = generate_delete_button(self, delete_image)
        #self.delete_button = Gtk.EventBox()
        #self.delete_button.add(delete_image)
        #self.delete_button.set_tooltip_text("Remove this clip")

        name_label = Gtk.Label(data)

        vertical_box.add(name_label)

        row = Gtk.Box(Gtk.Orientation.HORIZONTAL, 12)
        row.props.margin = 12
        row.add(icon)
        row.add(vertical_box)

        row.pack_end(self.delete_button, False, False, False)

        self.add(row)
        self.data = data
        self.show_all()
        self.delete_button.hide()

        