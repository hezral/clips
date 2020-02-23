#!/usr/bin/env python3

'''
    Copyright 2018 Adi Hezral (hezral@gmail.com)

    This file is part of Clips.

    Clips is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Clips is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Clips.  If not, see <http://www.gnu.org/licenses/>.
'''

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango
from datetime import datetime

class ClipsListRow(Gtk.ListBoxRow):
    def __init__(self, data):
        super().__init__()

        self.data = data

        #css styles
        LISTROW_CSS = """
        @define-color colorPrimary #F012BE;
        @define-color textColorPrimary #ffffff;

        .toolbar-button {
            color: #F012BE;
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

        .font-bold {
            font-weight: bold;
        }

        .clips-timestamp-font {
            font-size: 0.9em;
        }

        .clips-row:selected {
            background-color: shade (#233038, 0.95);
        }

        .clips-timestamp {
            color: #AAAAAA;
        }        
        """
        
        listrow_css = Gtk.CssProvider()
        listrow_css.load_from_data(bytes(LISTROW_CSS.encode()))

        #function for toolbar
        def generate_toolbar(self, icon, tooltip):
            toolbar_button = Gtk.Button().new_from_icon_name(icon, Gtk.IconSize.SMALL_TOOLBAR)
            toolbar_button.set_tooltip_text(tooltip)
            toolbar_button.props.can_focus = False
            toolbar_button.props.can_default = True
            toolbar_button.set_size_request(32, 32)
            
            toolbar_button.get_style_context().add_provider(listrow_css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            toolbar_button.get_style_context().remove_class("button")
            toolbar_button.get_style_context().add_class("toolbar-button")
            toolbar_button.get_style_context().add_class("transition")

            toolbar_hbox = Gtk.HBox()
            toolbar_hbox.pack_start(toolbar_button, 0, 0, 0)

            toolbar_vbox = Gtk.VBox()
            toolbar_vbox.pack_start(toolbar_hbox, 0, 0, 0)
            toolbar_vbox.set_valign(Gtk.Align.CENTER)
            return toolbar_vbox

        #generate toolbar buttons
        self.delete_button = generate_toolbar(self, "edit-delete-symbolic", "Delete clip")
        self.copy_button = generate_toolbar(self, "edit-copy-symbolic", "Copy to clipboard")

        #check data type 
        if type(data) == str:
            data_type_icon_name = "text-x-generic"
        elif type(data) == gi.repository.Gtk.Image: 
            data_type_icon_name = "image-x-generic"
        else:
            data_type_icon_name = "empty"

        data_type_icon = Gtk.Image.new_from_icon_name(data_type_icon_name, Gtk.IconSize.DIALOG)
        data_type_icon.set_pixel_size(32)

        #clips label 
        data_label = Gtk.Label(str(data))
        print(type(data))
        data_label.get_style_context().add_provider(listrow_css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        data_label.get_style_context().add_class("font-bold")
        data_label.props.ellipsize = Pango.EllipsizeMode.END
        data_label.props.max_width_chars = 25
        data_label.props.halign = Gtk.Align.START
        data_label.props.valign = Gtk.Align.END
        data_label.set_max_width_chars(25)
        data_label.set_line_wrap(True)
        data_label.set_size_request(10, -1)

        #clips content
        contents = Gtk.Label(str(data))
        contents.set_hexpand(False)
        contents.set_line_wrap(True)
        contents.set_max_width_chars(50)
        contents.props.halign = Gtk.Align.START
        contents.props.valign = Gtk.Align.END

        #clips timestamp
        created_timestamp = datetime.now()
        timestamp_label = Gtk.Label(self.timestamp(created_timestamp))
        timestamp_label.set_tooltip_text(created_timestamp.strftime('%c'))
        timestamp_label.props.halign = Gtk.Align.START
        timestamp_label.props.valign = Gtk.Align.START
        timestamp_label.props.max_width_chars = 45
        timestamp_label.props.ellipsize = Pango.EllipsizeMode.END
        timestamp_label.get_style_context().add_provider(listrow_css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        timestamp_label.get_style_context().add_class("clips-timestamp-font")
        

        #grid for content and timestamp
        main_grid = Gtk.Grid()
        main_grid.attach(data_label, 1, 0, 1, 1)
        main_grid.attach(contents, 1, 1, 1, 1)
        main_grid.attach(timestamp_label, 1, 2, 1, 1)


        #construct the row
        row_box = Gtk.Box(Gtk.Orientation.HORIZONTAL, 12)
        row_box.props.margin = 12
        row_box.pack_start(data_type_icon, False, False, False)
        row_box.pack_start(main_grid, False, False, False)
        row_box.pack_end(self.delete_button, False, False, False)
        row_box.pack_end(self.copy_button, False, False, False)
        
        #self.get_style_context().add_provider(clipslistrow_css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        #self.get_style_context().add_class("clips-row")
        self.add(row_box)
        self.show_all()

    def timestamp(self, time=False):
        """
        Get a datetime object or a int() Epoch timestamp and return a
        pretty string like 'an hour ago', 'Yesterday', '3 months ago',
        'just now', etc
        """
        now = datetime.now()
        if type(time) is int:
            diff = now - datetime.fromtimestamp(time)
        elif isinstance(time,datetime):
            diff = now - time
        elif not time:
            diff = now - now
        second_diff = diff.seconds
        day_diff = diff.days

        if day_diff < 0:
            return ''

        if day_diff == 0:
            if second_diff < 10:
                return "just now"
            if second_diff < 60:
                return str(second_diff) + " seconds ago"
            if second_diff < 120:
                return "a minute ago"
            if second_diff < 3600:
                return str(second_diff / 60) + " minutes ago"
            if second_diff < 7200:
                return "an hour ago"
            if second_diff < 86400:
                return str(second_diff / 3600) + " hours ago"
        if day_diff == 1:
            return "Yesterday"
        if day_diff < 7:
            return str(day_diff) + " days ago"
        if day_diff < 31:
            return str(day_diff / 7) + " weeks ago"
        if day_diff < 365:
            return str(day_diff / 30) + " months ago"
        return str(day_diff / 365) + " years ago"

    def show_buttons(self):
        #function to show the toolbar buttons
        self.delete_button.show()
        self.copy_button.show()
    
    def hide_buttons(self):
        #function to hide the toolbar buttons
        self.delete_button.hide()
        self.copy_button.hide()