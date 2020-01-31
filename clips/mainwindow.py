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
from widgets.headerbar import ClipsHeaderBar
from widgets.listboxrow import ClipsListRow
from widgets.info import InfoView

class ClipsWindow(Gtk.ApplicationWindow):
    def __init__(self):
        super().__init__()
        
        #applicationwindow construct
        self.props.title = "Clips"
        self.props.resizable = False
        self.props.border_width = 0
        self.set_icon_name("com.github.hezral.clips")
        self.get_style_context().add_class("rounded")
        self.set_default_size(360, 480)
        self.set_keep_above(True)
        self.props.window_position = Gtk.WindowPosition.CENTER
        
        #applicationwindow theme
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)

        #headerbar construct
        headerbar = ClipsHeaderBar()
        self.set_titlebar(headerbar)

        #listbox construct
        global last_row_selected_idx
        last_row_selected_idx = 0
        listbox_view = Gtk.ListBox()

        #listbox_view function for styling alternate rows using filters
        def filter_func(row, data, notify_destroy):
            if(row.get_index() % 2 == 0):
                row.get_style_context().add_class("background")
            else:
                row.get_style_context().add_class("view")
            #return False if row.data == 'Fail' else True
            return True

        #listbox_view function for displaying row buttons on row selection
        def on_row_selected(widget, row):
            global last_row_selected_idx
            last_row_idx = last_row_selected_idx
            last_row = widget.get_row_at_index(last_row_idx)
            new_row = row
            new_row_idx = new_row.get_index()
            last_row.hide_buttons()
            new_row.show_buttons()
            last_row_selected_idx = new_row_idx

        #listbox_view function for triggering actions on row activation
        def on_row_activated(widget, row):
            print('nothing')

        listbox_view.set_filter_func(filter_func, None, False)
        listbox_view.connect('row-selected', on_row_selected)
        listbox_view.connect_after('activate_cursor_row', on_row_activated)
        listbox_view.connect_after('row-activated', on_row_selected)        

        #initial launch add some rows
        welcome_text = "Welcome to Clips"
        listbox_view.add(ClipsListRow(welcome_text))
        
        welcome_image = Gtk.Image.new_from_icon_name("system-os-installer", Gtk.IconSize.MENU)
        welcome_image.set_pixel_size(96)
        listbox_view.add(ClipsListRow(welcome_image))

        #scrolled window
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.add(listbox_view)
        scrolled_window.show()
        scrolled_window.set_visible(True)

        #welcome view
        info_view = InfoView("No Clips Found","Start Copying Stuffs", "system-os-installer")
        info_view.set_visible(True)

        #search view

        #settings view

        #stack view
        stack_view = Gtk.Stack()
        stack_view.add_named(scrolled_window, "listbox_view")
        stack_view.add_named(info_view, "infoview")
        stack_view.set_visible_child_name("infoview")
        stack_view.set_visible_child_name("listbox_view")

        self.add(stack_view)
        self.show()
        self.show_all()

        #hack to hide toolbar buttons on all rows
        for row in listbox_view:
            row.hide_buttons()

app = ClipsWindow()
app.connect("destroy", Gtk.main_quit)
Gtk.main()