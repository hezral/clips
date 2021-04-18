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

        self.props.column_spacing = 0
        self.props.row_spacing = 10
        self.props.expand = True
        self.props.valign = self.props.halign = Gtk.Align.FILL

        # drawing_area = Gtk.DrawingArea()
        # drawing_area.props.expand = True
        # drawing_area.connect("draw", self.draw)

    # def draw(self, drawing_area, cairo_context):
    #     print(self.get_scale_factor())

    def on_button_clicked(self, button):
        if button.props.name == "getstarted":
            self.get_style_context().add_class("info-view-fader")
            self.app.main_window.on_view_visible(action="help-view")
            # startcopying_button = Gtk.Button("Start Copying!")
            # startcopying_button.props.name = "startcopying"
            # startcopying_button.props.expand = False
            # startcopying_button.props.margin = 10
            # startcopying_button.props.valign = Gtk.Align.START
            # startcopying_button.props.halign = Gtk.Align.CENTER
            # startcopying_button.connect("clicked", self.on_button_clicked)
            # startcopying_button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
            # startcopying_button.show_all()
            # self.attach(startcopying_button, 0, 0, 1, 1)
        # else:
        #     self.app.main_window.on_view_visible()

    def generate_welcome_view(self):
        self.clear_info_view()

        grid = Gtk.Grid()
        grid.props.halign = grid.props.valign = Gtk.Align.CENTER
        grid.props.expand = True
        grid.props.row_spacing = 10

        getstarted_button = Gtk.Button("Quick Start Guide")
        getstarted_button.props.name = "getstarted"
        getstarted_button.props.expand = False
        getstarted_button.props.margin = 20
        getstarted_button.props.valign = getstarted_button.props.halign = Gtk.Align.CENTER
        getstarted_button.connect("clicked", self.on_button_clicked)
        getstarted_button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)

        sublabel = Gtk.Label("Continue copying stuff (Ctrl+C) or view Quick Start Guide")
        sublabel.props.name = "welcome-view-sublabel"
        sublabel.props.expand = True
        sublabel.props.halign = sublabel.props.valign = Gtk.Align.CENTER
        sublabel.get_style_context().add_class("h3")

        label = Gtk.Label("Welcome")
        label.props.name = "welcome-view-title"
        label.props.expand = True
        label.props.halign = label.props.valign = Gtk.Align.CENTER
        label.get_style_context().add_class("h1")

        grid.attach(label, 0, 0, 1, 1)
        grid.attach(sublabel, 0, 1, 1, 1)
        grid.attach(getstarted_button, 0, 2, 1, 1)

        self.attach(grid, 0, 0, 1, 1)
        self.show_all()

    def generate_help_view(self):
        self.clear_info_view()
        
        flowbox = Gtk.FlowBox()
        flowbox.props.name = "help-flowbox"
        flowbox.props.homogeneous = False
        flowbox.props.row_spacing = 2
        flowbox.props.column_spacing = 2
        flowbox.props.max_children_per_line = 9
        flowbox.props.min_children_per_line = self.app.gio_settings.get_int("min-column-number")
        flowbox.props.valign = Gtk.Align.START
        flowbox.props.halign = Gtk.Align.FILL
        flowbox.props.selection_mode = Gtk.SelectionMode.NONE

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.props.hscrollbar_policy = Gtk.PolicyType.NEVER
        scrolled_window.add(flowbox)

        self.attach(scrolled_window, 0, 0, 1, 1)

        prefer_dark_style = self.app.gio_settings.get_boolean("prefer-dark-style")

        for child in flowbox.get_children():
            child.destroy()

        if self.help_view is None:
            help_run_clips = HelpSubView(prefer_dark_style, image_name="help_run_clips", subtitle_text="Fast app launch")
            help_hide_clips = HelpSubView(prefer_dark_style, image_name="help_hide_clips", subtitle_text="Run in background")
            help_switch_views = HelpSubView(prefer_dark_style, image_name="help_switch_views", subtitle_text="Switch between views")
            help_column_number = HelpSubView(prefer_dark_style, image_name="help_column_number", subtitle_text="Adjust columns display")
            flowbox.add(help_run_clips)
            flowbox.add(help_hide_clips)
            flowbox.add(help_switch_views)
            flowbox.add(help_column_number)

            help_clip_actions = HelpSubView(prefer_dark_style, image_name="help_clip_actions", subtitle_text="Actions on clips")
            help_quick_copy = HelpSubView(prefer_dark_style, image_name="help_quick_copy", subtitle_text="Quick copy first 9 clips")
            help_doubleclick_copy = HelpSubView(prefer_dark_style, image_name="help_doubleclick_copy", subtitle_text="Double click to copy")
            help_multiselect = HelpSubView(prefer_dark_style, image_name="help_multiselect", subtitle_text="Delete multi clips")
            flowbox.add(help_clip_actions)
            flowbox.add(help_quick_copy)
            flowbox.add(help_doubleclick_copy)
            flowbox.add(help_multiselect)

            help_clip_info = HelpSubView(prefer_dark_style, image_name="help_clip_info", subtitle_text="Hover on icon for extra info")
            help_search = HelpSubView(prefer_dark_style, image_name="help_search", subtitle_text="Search with multi keyword")
            help_clipsapp_toggle = HelpSubView(prefer_dark_style, image_name="help_clipsapp_toggle", subtitle_text="Toggle clipboard monitoring")
            help_settings = HelpSubView(prefer_dark_style, image_name="help_settings", subtitle_text="Explore availble settings")
            flowbox.add(help_clip_info)
            flowbox.add(help_search)
            flowbox.add(help_clipsapp_toggle)
            flowbox.add(help_settings)

            for child in flowbox.get_children():
                child.props.can_focus = False
        
            self.show_all()

            return True

        else:
            pass

    def generate_noclips_view(self):
        self.clear_info_view()

        grid = Gtk.Grid()
        grid.props.halign = grid.props.valign = Gtk.Align.CENTER
        grid.props.expand = True
        grid.props.row_spacing = 10

        sublabel = Gtk.Label("Try copying something (Ctrl+C)")
        sublabel.props.name = "noclips-view-sublabel"
        sublabel.props.expand = True
        sublabel.props.halign = sublabel.props.valign = Gtk.Align.CENTER
        sublabel.get_style_context().add_class("h3")

        label = Gtk.Label("No clips")
        label.props.name = "noclips-view-title"
        label.props.expand = True
        label.props.halign = label.props.valign = Gtk.Align.CENTER
        label.get_style_context().add_class("h1")

        grid.attach(label, 0, 0, 1, 1)
        grid.attach(sublabel, 0, 1, 1, 1)

        self.attach(grid, 0, 0, 1, 1)
        self.show_all()
    
    def clear_info_view(self):
        for child in self.get_children():
            child.destroy()

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
