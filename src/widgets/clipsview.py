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

class ClipsView(Gtk.Grid):
    def __init__(self, listbox):
        super().__init__()
        
        scrolled_view = Gtk.ScrolledWindow()
        scrolled_view.set_hexpand(True)
        scrolled_view.set_vexpand(True)
        scrolled_view.add(listbox)
        scrolled_view.show()
        scrolled_view.set_visible(True)
        separator = Gtk.Separator()
        separator.set_orientation(Gtk.Orientation.HORIZONTAL)
        status_bar = Gtk.Label()
        status_bar.props.margin = 1
        status_bar.props.halign = Gtk.Align.END
        self.attach(scrolled_view, 0, 0, 1, 1)
        self.attach(separator, 0, 1, 1, 1)
        self.attach(status_bar, 0, 2, 1, 1)
        self.set_visible(True)