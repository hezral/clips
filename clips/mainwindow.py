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
from gi.repository import Gtk, Gdk, Pango, GdkPixbuf
from widgets.infoview import InfoView
from widgets.clipslistrow import ClipsListRow



class Clips(Gtk.ApplicationWindow):
    def __init__(self):
        super().__init__()
        
        #applicationwindow construct
        self.props.title = "Clips"
        self.props.resizable = False
        self.props.border_width = 0
        self.set_icon_name("com.github.hezral.clips")
        self.get_style_context().add_class("rounded")
        self.set_default_size(400, 480)
        self.set_keep_above(True)
        self.props.window_position = Gtk.WindowPosition.CENTER
        
        #applicationwindow theme
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)

        #header construct
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        #headerbar.get_style_context().add_class(Gtk.STYLE_CLASS_FLAT)

        #header search field
        search_entry = Gtk.SearchEntry()
        search_entry.props.placeholder_text = "Search Something\u2026"
        search_entry.set_hexpand(True)   
        search_entry.set_halign(Gtk.Align.FILL)
        search_entry.set_size_request(400,32)
        
        SEARCH_ENTRY_CSS = """
        .large-search-entry {
            font-size: 125%;
        }
        """
        search_text_provider = Gtk.CssProvider()
        search_text_provider.load_from_data(bytes(SEARCH_ENTRY_CSS.encode()))
        search_entry.get_style_context().add_provider(search_text_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        search_entry.get_style_context().add_class("large-search-entry")

        #header box to hold widgets
        box = Gtk.HBox(orientation=Gtk.Orientation.HORIZONTAL)
        box.add(search_entry)

        #header construct
        headerbar.add(box)
        headerbar.show_all()

        #self.set_titlebar(box)
        self.set_titlebar(headerbar)


            





        #listbox construct
        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        list_box.set_activate_on_single_click(False)

        #listbox functions
        #function for styling alternate rows using filters
        def filter_func(row, data, notify_destroy):
            if(row.get_index() % 2 == 0):
                row.get_style_context().add_class("background")
            else:
                row.get_style_context().add_class("view")
            #return False if row.data == 'Fail' else True
            return True

        #function for displaying row buttons on row selection
        def on_row_selected(widget, row):
            global last_row_selected_idx
            last_row_idx = last_row_selected_idx
            last_row = widget.get_row_at_index(last_row_idx)
            
            new_row = row
            new_row_idx = new_row.get_index()     

            last_row.delete_button.hide()
            new_row.delete_button.show()
            
            last_row_selected_idx = new_row_idx

        #function for triggering actions on row activation
        def on_row_activated(widget):
            print('nothing')
        
        #rows construct
        items = """
        This is a sorted ListBox Fail
        This is a sorted ListBox Fail
        This is a sorted ListBox Fail
        """.split()
        for item in items:
            #list_box.add(ClipsListRow(item))
            list_box.add(ClipsListRow(item))
        
        list_box.set_filter_func(filter_func, None, False)

        global last_row_selected_idx
        last_row_selected_idx = 0

        list_box.connect('row-selected', on_row_selected)
        list_box.connect_after('activate_cursor_row', on_row_activated)
        
        list_box.show()

        #list box scrollwindow
        list_box_scrollwin = Gtk.ScrolledWindow()
        list_box_scrollwin.set_vexpand(True)
        list_box_scrollwin.add(list_box)
        list_box_scrollwin.show()
        

        #view for no clipboard items
        info_view = InfoView("No Clips Found","Start Copying Stuffs", "system-os-installer")
        info_view.show_all()

        stack_view = Gtk.Stack()
        info_view.set_visible(True)
        list_box_scrollwin.set_visible(True)
        stack_view.add_named(list_box_scrollwin, "listbox")
        stack_view.add_named(info_view, "infoview")
        stack_view.set_visible_child_name("infoview")
        stack_view.set_visible_child_name("listbox")
        stack_view.show()

        #self.add(list_box_scrollwin)
        self.add(stack_view)

        self.show()
        #self.show()



app = Clips()
app.connect("destroy", Gtk.main_quit)
Gtk.main()