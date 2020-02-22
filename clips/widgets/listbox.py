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

class ClipsListBox(Gtk.ListBox):
    def __init__(self):
        super().__init__()
        
        #listbox construct
        global last_row_selected_idx
        last_row_selected_idx = 0

        self.set_filter_func(self.filter_func, None, False)
        self.connect('row-selected', self.on_row_selected)
        self.connect_after('activate_cursor_row', self.on_row_activated)
        self.connect_after('row-activated', self.on_row_selected)        

    #listbox_view function for styling alternate rows using filters
    def filter_func(self, row, data, notify_destroy):
        if(row.get_index() % 2 == 0):
            row.get_style_context().add_class("background")
        else:
            row.get_style_context().add_class("view")
        #return False if row.data == 'Fail' else True
        return True

    #listbox_view function for displaying row buttons on row selection
    def on_row_selected(self, widget, row):
        global last_row_selected_idx
        last_row_idx = last_row_selected_idx
        last_row = widget.get_row_at_index(last_row_idx)
        new_row = row
        new_row_idx = new_row.get_index()
        last_row.hide_buttons()
        new_row.show_buttons()
        last_row_selected_idx = new_row_idx

    #listbox_view function for triggering actions on row activation
    def on_row_activated(self, widget, row):
        print('nothing')

    #custom add function
    def add_row(self, listboxrow):
        self.add(listboxrow)
        listboxrow.hide_buttons()
        print(type(listboxrow))

