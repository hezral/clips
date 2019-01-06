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

class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, data):
        super(ListBoxRowWithData, self).__init__()
        self.data = data
        self.add(Gtk.Label(data))

class Clips(Gtk.ApplicationWindow):
    def __init__(self):
        #super(Clips, self).__init__(title="Clips", resizable=False, border_width=6)
        Gtk.ApplicationWindow.__init__(self, title="Clips", resizable=False, border_width=6)

        #set window style, size
        self.get_style_context().add_class("rounded")
        self.set_default_size(500, 480)
        self.set_keep_above(True)
        self.props.window_position = Gtk.WindowPosition.CENTER

        #set application theme
        #settings = Gtk.Settings.get_default()
        #settings.set_property("gtk-application-prefer-dark-theme", False)

        
        #headerbar
        headerbar = Gtk.HeaderBar()
        #headerbar.props.title = "Clips"
        headerbar.set_show_close_button(True)
        #headerbar.has_subtitle = False
        #headerbar.get_style_context().add_class(Gtk.STYLE_CLASS_FLAT)

        #search headerbar
        search_entry = Gtk.SearchEntry()
        search_entry.props.placeholder_text = "Search Clipboard\u2026"
        search_entry.set_hexpand(True)
        #search_entry.props.vexpand = True
        '''
        search_entry.props.margin_left = 5
        search_entry.props.margin_left = 5
        search_entry.props.margin_right = 5
        search_entry.props.margin_top = 5
        search_entry.props.margin_bottom = 5
        '''

        #box headerbar
        box = Gtk.HBox(spacing=10)
        box.get_style_context().add_class("linked")
        #Gtk.StyleContext.add_class(box.get_style_context(), "linked")
        #pack headerbar
        #headerbar.pack_end(search_entry)
        #headerbar.pack_start(search_entry)
        box.add(search_entry)
        headerbar.add(box)
        
        #set headerbar
        #self.set_titlebar(box)
        self.set_titlebar(headerbar)

        SEARCH_ENTRY_CSS = """
        .large-search-entry {
            font-size: 175%;
        }
        """
        #search_text_provider = Gtk.CssProvider()
        #search_text_provider.load_from_data(search_text,-1)
        #search_entry.get_style_context().add_provider(search_text_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        #search_entry.get_style_context().add_class("large-search-entry")

        font_size_provider = Gtk.CssProvider()
        font_size_provider.load_from_data(bytes(SEARCH_ENTRY_CSS.encode()))
        style_context = search_entry.get_style_context()
        style_context.add_provider(font_size_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        style_context.add_class("large-search-entry")

        #list box
        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        list_box.set_activate_on_single_click(False)

        #rows
        items = 'This is a sorted ListBox FailThis is a sorted ListBox FailThis is a sorted ListBox FailThis is a sorted ListBox FailThis is a sorted ListBox FailThis is a sorted ListBox Fail'.split()
        for item in items:
            list_box.add(ListBoxRowWithData(item))

        #list box scrollwindow
        list_box_scrollwin = Gtk.ScrolledWindow()
        list_box_scrollwin.set_vexpand(True)
        list_box_scrollwin.add(list_box)
        list_box_scrollwin.show_all()

        self.add(list_box_scrollwin)
        self.show_all()

app = Clips()
app.connect("destroy", Gtk.main_quit)
Gtk.main()