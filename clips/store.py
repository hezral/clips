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

        debugflag = True
        
        db_file = 'ClipsDatabase.db'

        try:
            db_connection, db_cursor = self.open_db(db_file)
            self.create_table(db_cursor)
        except sqlite3.Error as error:
            print("Error while working with SQLite", error)
        # finally:
        #     if not (db_connection.in_transaction):
        #         db_connection.close()
        #         print("sqlite connection is closed")

        if debugflag:
            self.debug()
    
    def open_db(self, database_file):
        connection = sqlite3.connect(database_file) 
        cursor = connection.cursor()
        cursor.execute("PRAGMA database_list;")
        curr_table = cursor.fetchall()
        print(curr_table)
        return connection, cursor

    def create_table(self, database_cursor):
      """Creates a table called notecard_table in the database with the appropriate columns.
      """
      database_cursor.execute('''
          CREATE TABLE ClipsDB (
              id        INTEGER     PRIMARY KEY     NOT NULL,
              type      INTEGER     NOT NULL,
              created   TEXT        NOT NULL        DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW', 'localtime')),
              accessed  TEXT        NOT NULL        DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW', 'localtime')),
              uri       TEXT,
              data      BLOB,
              checksum  STRING      NOT NULL        UNIQUE
          );
          ''')
      
    def debug(self):
        label = Gtk.Label()
        image = Gtk.Image.new_from_icon_name("image-x-generic", Gtk.IconSize.DIALOG)
        window = Gtk.Window(title="Clips Debug Window") #debug window to see contents displayed in Gtk.Window
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.pack_start(image, True, True, 0)
        box.pack_start(label, True, True, 0)
        window.set_border_width(6)
        window.add(box)
        window.show_all()
        window.connect("destroy", Gtk.main_quit)
        # just for debugging at CLI to enable CTRL+C quit
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)

clips = ClipsStore()
Gtk.main()
