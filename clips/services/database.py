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
import os.path
import hashlib
import sqlite3
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GObject

class ClipsDatabase():
    def __init__(self):

        debugflag = True
        db_file = 'ClipsDatabase.db'

        try:
            if (os.path.exists(db_file)):
                self.db_connection, self.db_cursor = self.open_db(db_file)
            else:
                self.db_connection, self.db_cursor = self.open_db(db_file)
                self.create_table(self.db_cursor)
        except (OSError, sqlite3.Error) as error:
            print("Exception: ", error)

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
        # Initializes the database with the ClipsDB table
        database_cursor.execute('''
            CREATE TABLE ClipsDB (
                id          INTEGER     PRIMARY KEY     NOT NULL,
                type        INTEGER     NOT NULL,
                created     TEXT        NOT NULL        DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW', 'localtime')),
                source_uri  TEXT,
                cache_uri   TEXT,
                data        BLOB,
                checksum    STRING      NOT NULL        UNIQUE
            );
            ''')
    
    def add_record(self, data_tuple):
        # Adds a new record to database
        database_connection = self.db_connection
        database_cursor = self.db_cursor
        data_input = data_tuple

        # insert a clips record
        sqlite_insert_with_param = '''
            INSERT INTO 'ClipsDB'
            ('type', 'source_uri', 'cache_uri', 'data', 'checksum') 
            VALUES
            (?, ?, ?, ?, ?);
            '''
        try:
            database_cursor.execute(sqlite_insert_with_param, data_input)
            database_connection.commit()
            database_cursor.close()
        except sqlite3.Error as error:
            print("Exception sqlite3.Error: ", error)

    def get_checksum(self, data):
        md5sum = hashlib.md5()
        md5sum.update(data)
        checksum = md5sum.hexdigest()
        return checksum

    def debug(self):
        label = Gtk.Label()
        label.props.selectable = True
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

clips = ClipsDatabase()

#print(clips.get_checksum(b'testesttest'))

#m = hashlib.md5()
#m.update(b"Nobody inspects")

#checksum = m.hexdigest()

image = Gtk.Image.new_from_icon_name("system-os-installer", Gtk.IconSize.MENU)


#print(type(image))

#print(image)

#print(clips.get_checksum(image.get_pixbuf()))

#data = ('image/png', '/home/adi', '/home/adi/.config/Clips/cache/filename.png', 'testtest')

#print(len(data))

#data = data + (checksum,)

#print(len(data))

#clips.add_record(data)

#Gtk.main()
# # get developer detail
# sqlite_select_query = """SELECT name, joiningDate from new_developers where id = ?"""
# database_cursor.execute(sqlite_select_query, (1,))
# records = database_cursor.fetchall()

# for row in records:
#     developer= row[0]
#     joining_Date = row[1]
#     print(developer, " joined on", joiningDate)
#     print("joining date type is", type(joining_Date))            # # get developer detail
# sqlite_select_query = """SELECT name, joiningDate from new_developers where id = ?"""
# database_cursor.execute(sqlite_select_query, (1,))
# records = database_cursor.fetchall()

# for row in records:
#     developer= row[0]
#     joining_Date = row[1]
#     print(developer, " joined on", joiningDate)
#     print("joining date type is", type(joining_Date))            # # get developer detail
# sqlite_select_query = """SELECT name, joiningDate from new_developers where id = ?"""
# database_cursor.execute(sqlite_select_query, (1,))
# records = database_cursor.fetchall()

# for row in records:
#     developer= row[0]
#     joining_Date = row[1]
#     print(developer, " joined on", joiningDate)
#     print("joining date type is", type(joining_Date))

