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
from gi.repository import Gtk, Gdk, Pango

class ClipsListRow(Gtk.ListBoxRow):
    def __init__(self, data):
        super().__init__()

        def generate_toolbar_button(self, image, tooltip):
            toolbar_button = Gtk.EventBox()
            toolbar_button.add(image)
            toolbar_button.set_tooltip_text(tooltip)
            toolbar_button.props.margin = 4
            #toolbar_button.props.can_focus = False
            #toolbar_button.props.can_default = True
            return toolbar_button

        def generate_toolbar_button2(self, icon, tooltip):
            toolbar_button = Gtk.Button().new_from_icon_name(icon, Gtk.IconSize.SMALL_TOOLBAR)
            toolbar_button.set_tooltip_text(tooltip)
            toolbar_button.props.can_focus = False
            toolbar_button.props.can_default = True
            toolbar_button.set_size_request(32, 32)

            toolbar_button.get_style_context().add_provider(button_css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            toolbar_button.get_style_context().add_class("toolbar-button")
            toolbar_button.get_style_context().remove_class("button")
            toolbar_button.get_style_context().add_class("transition")

            toolbar_hbox = Gtk.HBox()
            toolbar_hbox.pack_start(toolbar_button, 0, 0, 0)

            toolbar_vbox = Gtk.VBox()
            toolbar_vbox.pack_start(toolbar_hbox, 0, 0, 0)
            toolbar_vbox.set_valign(Gtk.Align.CENTER)
            return toolbar_vbox


        def generate_thumbnail_image(self, image, tooltip):
            thumbnail_image = Gtk.Image()
            return thumbnail_image


        BUTTONS_OVERLAY_CSS = """
        .toolbar-button {
            color: #FF00FF;
            border: none;
            box-shadow: none;
            border-radius: 50%;
            background: none;
        }

        .toolbar-button:hover {
            color: #FF00FF;
            background-color: rgba(0,0,0,0.2);
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

        # image_cover = new Gtk.Image ();
        # image_cover.valign = Gtk.Align.CENTER;
        # image_cover.halign = Gtk.Align.CENTER;
        # image_cover.pixel_size = 32;
        # image_cover.pixbuf = new Gdk.Pixbuf.from_file_at_size (track.cover, 32, 32);

        icon = Gtk.Image.new_from_icon_name("utilities-terminal", Gtk.IconSize.DIALOG)
        icon.set_pixel_size(64)

        #delete_image = Gtk.Image.new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        #copy_image = Gtk.Image.new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        #view_image = Gtk.Image.new_from_icon_name("view-private-symbolic", Gtk.IconSize.SMALL_TOOLBAR)

        #self.delete_button = generate_toolbar_button(self, delete_image, "Delete clip")
        #self.copy_button = generate_toolbar_button(self, copy_image, "Copy to clipboard")
        #self.view_button = generate_toolbar_button(self, view_image, "View clip")

        self.delete_button = generate_toolbar_button2(self, "edit-delete-symbolic", "Delete clip")
        self.copy_button = generate_toolbar_button2(self, "edit-copy-symbolic", "Copy to clipboard")
        self.view_button = generate_toolbar_button2(self, "view-private-symbolic", "View clip")

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
        row.pack_end(self.view_button, False, False, False)
        row.pack_end(self.copy_button, False, False, False)
        



        
        # grid = Gtk.Grid()
        # grid.props.column_spacing = 12
        # grid.props.row_spacing = 3
        # grid.props.margin = 10
        # grid.props.margin_bottom = grid.props.margin_top = 10

        # grid.attach(icon, 1, 1, 1, 1)
        # grid.attach(vertical_box, 2, 1, 1, 1)
        # grid.attach(self.copy_button, 4, 1, 1, 1)

        # title_label = new Gtk.Label ("<b>%s</b>".printf (track.title));
        # title_label.ellipsize = Pango.EllipsizeMode.END;
        # title_label.use_markup = true;
        # title_label.halign = Gtk.Align.START;
        # title_label.valign = Gtk.Align.END;

        # artist_album_label = new Gtk.Label ("%s - %s".printf (track.artist, track.album));
        # artist_album_label.halign = Gtk.Align.START;
        # artist_album_label.valign = Gtk.Align.START;
        # artist_album_label.ellipsize = Pango.EllipsizeMode.END;

        # duration_label = new Gtk.Label (Application.utils.get_formated_duration (track.duration));
        # duration_label.halign = Gtk.Align.END;
        # duration_label.hexpand = true;

        # var main_grid = new Gtk.Grid ();
        # main_grid.margin = 3;
        # main_grid.margin_start = 6;
        # main_grid.margin_end = 12;
        # main_grid.column_spacing = 6;
        # main_grid.attach (image_cover, 0, 0, 1, 2);
        # main_grid.attach (title_label, 1, 0, 1, 1);
        # main_grid.attach (artist_album_label, 1, 1, 1, 1);
        # main_grid.attach (duration_label, 2, 0, 2, 2);

        # add (main_grid);

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



        