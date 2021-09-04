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

from typing import overload
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gio, GLib
import os
resource_path = os.path.join(os.path.dirname(__file__), "data", "images")

from . import custom_widgets

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

    def generate_welcome_view(self):
        self.clear_info_view()

        self.password_editor = custom_widgets.PasswordEditor(
            main_label="Before you start copying stuff, set a password to protect sensitive data", 
            gtk_application=self.app,
            type="editor",
            callback=self.on_set_password)

        self.setpassword_button = Gtk.Button("Set Password")
        self.setpassword_button.props.hexpand = False
        self.setpassword_button.props.name = "setpassword"
        self.setpassword_button.props.valign = Gtk.Align.CENTER
        self.setpassword_button.props.halign = Gtk.Align.END
        self.setpassword_button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
        self.setpassword_button.connect("clicked", self.password_editor.set_password)

        self.skippassword_button = Gtk.Button("Skip Protection")
        self.skippassword_button.props.name = "skippassword"
        self.skippassword_button.props.expand = True
        self.skippassword_button.props.valign = Gtk.Align.CENTER
        self.skippassword_button.props.halign = Gtk.Align.END
        self.skippassword_button.connect("clicked", self.on_button_clicked)
            
        setpassword_grid = Gtk.Grid()
        setpassword_grid.props.name = "setpassword"
        setpassword_grid.props.row_spacing = 10
        setpassword_grid.props.column_spacing = 10
        setpassword_grid.props.margin = 2
        setpassword_grid.attach(self.password_editor, 0, 0, 2, 1)
        setpassword_grid.attach(self.skippassword_button, 0, 1, 1, 1)
        setpassword_grid.attach_next_to(self.setpassword_button, self.skippassword_button, 1, 1, 1)

        getstarted_button = Gtk.Button("Quick Start Guide")
        getstarted_button.props.name = "getstarted"
        getstarted_button.props.hexpand = True
        getstarted_button.props.margin = 10
        getstarted_button.props.valign = getstarted_button.props.halign = Gtk.Align.CENTER
        getstarted_button.connect("clicked", self.on_button_clicked)
        getstarted_button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)

        getstarted_label = Gtk.Label("Continue copying stuff (Ctrl+C)\nor view Quick Start Guide")
        getstarted_label.props.name = "welcome-view-sublabel"
        getstarted_label.props.expand = True
        getstarted_label.props.justify = Gtk.Justification.CENTER
        getstarted_label.props.halign = getstarted_label.props.valign = Gtk.Align.CENTER
        getstarted_label.get_style_context().add_class("h3")

        getstarted_grid = Gtk.Grid()
        getstarted_grid.props.name = "getstarted"
        getstarted_grid.props.row_spacing = 10
        getstarted_grid.props.margin = 2
        getstarted_grid.attach(getstarted_label, 0, 0, 3, 1)
        getstarted_grid.attach(getstarted_button, 0, 1, 3, 1)

        self.welcome_view_stack = Gtk.Stack()
        self.welcome_view_stack.props.name = "welcome-view-stack"
        self.welcome_view_stack.props.transition_type = Gtk.StackTransitionType.SLIDE_LEFT
        self.welcome_view_stack.props.transition_duration = 250
        self.welcome_view_stack.add_named(setpassword_grid, setpassword_grid.get_name())
        self.welcome_view_stack.add_named(getstarted_grid, getstarted_grid.get_name())

        title_label = Gtk.Label("Welcome to Clips")
        title_label.props.name = "welcome-view-title"
        title_label.props.expand = True
        title_label.props.halign = title_label.props.valign = Gtk.Align.CENTER
        title_label.get_style_context().add_class("h1")

        grid = Gtk.Grid()
        grid.props.halign = grid.props.valign = Gtk.Align.CENTER
        grid.props.expand = True
        grid.props.row_spacing = 10
        grid.attach(title_label, 0, 0, 2, 1)
        grid.attach(self.welcome_view_stack, 0, 1, 2, 1)

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
            help_run_clips = HelpSubView(prefer_dark_style, image_name="help_run_clips", subtitle_text="Set shortcut for quick launch")
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

    def on_button_clicked(self, button=None, entry=None, label=None, button2=None):
        if button.props.name == "getstarted":
            self.get_style_context().add_class("info-view-fader")
            self.app.main_window.on_view_visible(action="help-view")

        if button.props.name == "skippassword":
            self.welcome_view_stack.set_visible_child_name("getstarted")
            self.app.on_clipsapp_action()
            self.gio_settings.set_boolean("first-run", False)
            self.gio_settings.set_boolean("protected-mode", False)

    def on_set_password(self):
        self.setpassword_button.destroy()
        self.skippassword_button.destroy()
        self.app.on_clipsapp_action()
        self.gio_settings.set_boolean("first-run", False)
        GLib.timeout_add(3000, self.welcome_view_stack.set_visible_child_name, "getstarted")

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
