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

class Clips(Gtk.Dialog):
    def __init__(self):
        super(Clips, self).__init__()
        self.set_keep_above(True)
        self.props.window_position = Gtk.WindowPosition.CENTER
        self.set_default_size(640, 480)
        self.show_all()
        self.get_action_area().visible = False

win = Clips()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()