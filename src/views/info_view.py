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
from gi.repository import Gtk, GdkPixbuf, Gio

import os
resource_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "images")

class InfoView(Gtk.Grid):

    help_view = None
    welcome_view = None
    noclips_view = None

    def __init__(self, app, title, description, icon, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.props.name = "info-view"

        self.app = app
        self.gio_settings = self.app.gio_settings

        title_label = Gtk.Label(title)
        title_label.get_style_context().add_class("h1")
        description_label = Gtk.Label(description)
        icon_image = Gtk.Image()
        
        icon_image.set_from_icon_name(icon, Gtk.IconSize.DIALOG)
        icon_image.set_pixel_size(96)

        icon_box = Gtk.EventBox()
        icon_box.set_valign(Gtk.Align.START)
        icon_box.add(icon_image)

        self.props.column_spacing = 0
        self.props.row_spacing = 0
        self.props.expand = True

        # drawing_area = Gtk.DrawingArea()
        # drawing_area.props.expand = True
        # drawing_area.connect("draw", self.draw)

        # flowbox
        self.flowbox = Gtk.FlowBox()
        self.flowbox.props.name = "help-flowbox"
        self.flowbox.props.homogeneous = False
        self.flowbox.props.row_spacing = 2
        self.flowbox.props.column_spacing = 2
        self.flowbox.props.max_children_per_line = 9
        self.flowbox.props.min_children_per_line = app.gio_settings.get_int("min-column-number")
        # self.flowbox.props.margin = 2
        self.flowbox.props.valign = Gtk.Align.START
        self.flowbox.props.halign = Gtk.Align.FILL
        self.flowbox.props.selection_mode = Gtk.SelectionMode.NONE

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.props.hscrollbar_policy = Gtk.PolicyType.NEVER
        scrolled_window.add(self.flowbox)

        # self.attach(drawing_area, 0, 0, 1, 1)
        self.attach(scrolled_window, 0, 0, 1, 1)
        

    # def draw(self, drawing_area, cairo_context):
    #     print(self.get_scale_factor())

    def generate_welcome_view(self):
        print("welcome-view")

    def generate_help_view(self):
        print("help-view")

        if self.help_view is None:

            # resource_directory = Gio.file_new_for_path(resource_path)
            # enum = resource_directory.enumerate_children(Gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE, 0)
            # for info in enum:
            #     content_type = info.get_content_type()
            #     fullpath = f'{PICTURES}/{info.get_name()}'
            #     pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(fullpath, 100, 100, True)
            #     image = Gtk.Image(pixbuf=pixbuf)
            #     flowbox.add(image)

            prefer_dark_style = self.app.gio_settings.get_boolean("prefer-dark-style")

            help_switch_views = HelpSubView(prefer_dark_style, image_name="help_switch_views", subtitle_text="Switch between views")

            help_search = HelpSubView(prefer_dark_style, image_name="help_search", subtitle_text="Search with multi keyword")
            
            help_settings = HelpSubView(prefer_dark_style, image_name="help_settings", subtitle_text="Explore availble settings")
            
            help_run_clips = HelpSubView(prefer_dark_style, image_name="help_run_clips", subtitle_text="Fast app launch")

            help_quick_copy = HelpSubView(prefer_dark_style, image_name="help_quick_copy", subtitle_text="Quick copy first 9 clips")

            help_multiselect = HelpSubView(prefer_dark_style, image_name="help_multiselect", subtitle_text="Delete multi clips")

            help_hide_clips = HelpSubView(prefer_dark_style, image_name="help_hide_clips", subtitle_text="Run in background")
            
            help_doubleclick_copy = HelpSubView(prefer_dark_style, image_name="help_doubleclick_copy", subtitle_text="Double click to copy")
            
            help_column_number = HelpSubView(prefer_dark_style, image_name="help_column_number", subtitle_text="Adjust columns display")

            help_clipsapp_toggle = HelpSubView(prefer_dark_style, image_name="help_clipsapp_toggle", subtitle_text="Toggle clipboard monitoring")

            help_clip_info = HelpSubView(prefer_dark_style, image_name="help_clip_info", subtitle_text="Additional info")
            
            help_clip_actions = HelpSubView(prefer_dark_style, image_name="help_clip_actions", subtitle_text="Actions on clips")
            
            self.flowbox.add(help_run_clips)
            self.flowbox.add(help_hide_clips)
            self.flowbox.add(help_switch_views)
            self.flowbox.add(help_column_number)
            
            self.flowbox.add(help_clip_actions)
            self.flowbox.add(help_quick_copy)
            self.flowbox.add(help_doubleclick_copy)
            self.flowbox.add(help_multiselect)

            self.flowbox.add(help_clip_info)
            self.flowbox.add(help_search)
            self.flowbox.add(help_clipsapp_toggle)
            self.flowbox.add(help_settings)


            for child in self.flowbox.get_children():
                child.props.can_focus = False
        
            self.show_all()

            return True

        else:
            pass


    def generate_noclips_view(self):
        print("welcome-view")
        

# ----------------------------------------------------------------------------------------------------

# class HelpSubView(Gtk.Grid):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.props.name = "help-view"

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
