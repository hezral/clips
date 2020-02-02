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

import signal
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject
import sqlite3



class ClipsStore():
    def __init__(self):
        super().__init__()

        #debug flag
        debugflag = True
        
        database_file = 'ClipsDatabase.db'
        self.database = database_file 

        def open_db(database_file):
            connection = sqlite3.connect(database_file) 
            cursor = connection.cursor()
            cursor.execute("PRAGMA database_list;")
            curr_table = cursor.fetchall()
            print(curr_table)
            pass

        def debug():
          self.label = Gtk.Label()
          self.image = Gtk.Image.new_from_icon_name("image-x-generic", Gtk.IconSize.DIALOG)
          self.window = Gtk.Window(title="Clips Debug Window") #debug window to see contents displayed in Gtk.Window
          self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
          self.box.pack_start(self.image, True, True, 0)
          self.box.pack_start(self.label, True, True, 0)
          self.window.set_border_width(6)
          self.window.add(self.box)
          self.window.show_all()
          self.window.connect("destroy", Gtk.main_quit)
          # just for debugging at CLI to enable CTRL+C quit
          GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)

        if debugflag:
          debug()
        
        open_db(self.database)
        


clips = ClipsStore()
Gtk.main()
