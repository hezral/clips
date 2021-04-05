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
    def __init__(self, app, title, description, icon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.props.name = "info-view"

        self.app = app

        prefer_dark_style = self.app.gio_settings.get_boolean("prefer-dark-style")

        title_label = Gtk.Label(title)
        title_label.get_style_context().add_class("h1")
        description_label = Gtk.Label(description)
        icon_image = Gtk.Image()
        
        icon_image.set_from_icon_name(icon, Gtk.IconSize.DIALOG)
        icon_image.set_pixel_size(96)

        icon_box = Gtk.EventBox()
        icon_box.set_valign(Gtk.Align.START)
        icon_box.add(icon_image)
        
        help_switch_views = HelpSubView(prefer_dark_style, image_name="help_switch_views", subtitle_text="Switch between views")
        help_search = HelpSubView(prefer_dark_style, image_name="help_search", subtitle_text="Search with multi keyword")
        help_clip_actions = HelpSubView(prefer_dark_style, image_name="help_clip_actions", subtitle_text="Actions on clips")
        help_hide_clips = HelpSubView(prefer_dark_style, image_name="help_hide_clips", subtitle_text="Run in background")
        help_clipsapp_toggle = HelpSubView(prefer_dark_style, image_name="help_clipsapp_toggle", subtitle_text="Toggle clipboard monitoring")

        self.props.column_spacing = 0
        self.props.row_spacing = 0
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.props.expand = True
        self.props.margin = 10
        # self.attach(icon_box, 0, 1, 1, 1)
        # self.attach(title_label, 0, 2, 1, 1)
        # self.attach(description_label, 0, 3, 1, 1)

        # flowbox
        self.flowbox = Gtk.FlowBox()
        self.flowbox.props.name = "help-flowbox"
        self.flowbox.props.homogeneous = False
        self.flowbox.props.row_spacing = 2
        self.flowbox.props.column_spacing = 2
        self.flowbox.props.max_children_per_line = 4
        self.flowbox.props.min_children_per_line = app.gio_settings.get_int("min-column-number")
        self.flowbox.props.margin = 2
        self.flowbox.props.valign = Gtk.Align.START
        self.flowbox.props.halign = Gtk.Align.FILL
        self.flowbox.props.selection_mode = Gtk.SelectionMode.NONE
            
        self.flowbox.add(help_switch_views)
        self.flowbox.add(help_search)
        self.flowbox.add(help_clip_actions)
        self.flowbox.add(help_hide_clips)
        self.flowbox.add(help_clipsapp_toggle)

        for child in self.flowbox.get_children():
            child.props.can_focus = False


        self.attach(self.flowbox, 0, 0, 1, 1)
        # self.attach(help_switch_views, 0, 0, 1, 1)
        # self.attach(help_search, 1, 0, 1, 1)
        # self.attach(help_clip_actions, 2, 0, 1, 1)
        # self.attach(help_hide_clips, 3, 0, 1, 1)

# ----------------------------------------------------------------------------------------------------

class HelpSubView(Gtk.Grid):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.props.name = "help-view"

# ----------------------------------------------------------------------------------------------------

class HelpSubView(Gtk.Grid):
    def __init__(self, prefer_dark_theme, image_name, subtitle_text, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.props.name = "help-subview"

        if prefer_dark_theme:
            filename = image_name + "_dark.png"
        else:
            filename = image_name + "_light.png"

        scale = self.get_scale_factor()
        image_size = 200 * scale
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=os.path.join(resource_path, filename), width=image_size, height=image_size, preserve_aspect_ratio=True)
        image = Gtk.Image().new_from_pixbuf(pixbuf)

        label = Gtk.Label(subtitle_text)
        label.props.name = "help-subtitle-text"
        label.props.halign = Gtk.Align.CENTER

        self.props.column_spacing = 2
        self.props.row_spacing = 2
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.props.expand = True
        self.attach(image, 0, 0, 1, 1)
        self.attach(label, 0, 1, 1, 1)
