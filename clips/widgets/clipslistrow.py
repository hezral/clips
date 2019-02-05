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

        def generate_toolbar_button(self, image, tooltip):
            toolbar_button = Gtk.EventBox()
            #toolbar_button = Gtk.Button().new_from_icon_name()
            toolbar_button.add(image)
            toolbar_button.set_tooltip_text(tooltip)
            toolbar_button.props.margin = 4
            toolbar_button.props.can_focus = False
            toolbar_button.props.can_default = True
            #toolbar_button.get_style_context().add_provider(button_css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            #toolbar_button.get_style_context().add_class("toolbar-button")
            #toolbar_button.get_style_context().add_class("button")
            #toolbar_button.get_style_context().add_class("transition")
            return toolbar_button
            
        BUTTONS_OVERLAY_CSS = """
        .toolbar-button {
            color: #000000;
            border: none;
            box-shadow: none;
            background: none;
        }

        .toolbar-button:hover {
            color: #000000;
            border: none;
        }

        .transition {
            transition: 200ms;
            transition-timing-function: ease;
        }
        """
        button_css = Gtk.CssProvider()
        button_css.load_from_data(bytes(BUTTONS_OVERLAY_CSS.encode()))


        thumb_clips_generic = Gtk.Image()
        thumb_clips_generic.props.valign = Gtk.Align.CENTER
        thumb_clips_generic.props.halign = Gtk.Align.CENTER
        thumb_clips_generic.props.pixel_size = 64
        #thumb_clips_generic.props.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size()

        icon = Gtk.Image.new_from_icon_name("utilities-terminal", Gtk.IconSize.DIALOG)
        icon.set_pixel_size(64)

        delete_image = Gtk.Image.new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        copy_image = Gtk.Image.new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        view_image = Gtk.Image.new_from_icon_name("view-private-symbolic", Gtk.IconSize.SMALL_TOOLBAR)

        self.delete_button = generate_toolbar_button(self, delete_image, "Delete clip")
        self.copy_button = generate_toolbar_button(self, copy_image, "Copy to clipboard")
        self.view_button = generate_toolbar_button(self, view_image, "View clip")



        name_label = Gtk.Label(data)

        vertical_box = Gtk.Box(Gtk.Orientation.VERTICAL, 6)
        vertical_box.add(name_label)

        row = Gtk.Box(Gtk.Orientation.HORIZONTAL, 12)
        row.props.margin = 12
        # row.props.margin_top = 12
        # row.props.margin_bottom = 12
        # row.props.margin_left = 24
        # row.props.margin_right = 24       
        row.add(icon)
        row.add(vertical_box)

        row.pack_end(self.delete_button, False, False, False)
        row.pack_end(self.copy_button, False, False, False)
        row.pack_end(self.view_button, False, False, False)

        self.add(row)
        self.data = data
        self.show_all()
        self.delete_button.hide()
        self.copy_button.hide()
        self.view_button.hide()

    def show_buttons(self):
        self.delete_button.show()
        self.copy_button.show()
        self.view_button.show()
    
    def hide_buttons(self):
        self.delete_button.hide()
        self.copy_button.hide()
        self.view_button.hide()



        