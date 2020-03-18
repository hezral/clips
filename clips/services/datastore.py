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
import os.path
import hashlib
import sqlite3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject, GdkPixbuf
from urllib.parse import urlparse
from manager import ClipsManager

class ClipsDatastore():
    def __init__(self, debugflag):

        debugflag = debugflag
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
                data        BLOB
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
            ('type', 'source', 'cache_uri', 'data') 
            VALUES
            (?, ?, ?, ?);
            '''
        try:
            database_cursor.execute(sqlite_insert_with_param, data_input)
            database_connection.commit()
            database_cursor.close()
        except sqlite3.Error as error:
            print("Exception sqlite3.Error: ", error)

    def store_cache(self, data_tuple):
        pass

    def select_record(self, data_tuple):
        #
        # # get developer detail
        # sqlite_select_query = """SELECT name, joiningDate from new_developers where id = ?"""
        # database_cursor.execute(sqlite_select_query, (1,))
        # records = database_cursor.fetchall()
        # for row in records:
        #     developer= row[0]
        #     joining_Date = row[1]
        #     print(developer, " joined on", joiningDate)
        #     print("joining date type is", type(joining_Date))            # # get developer detail
        pass

    def search_record(self, data_tuple):
        pass

    def get_checksum(self, data):
        checksum = hashlib.md5(data).hexdigest()
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




GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)

manager = ClipsManager(debugflag=False)


def new_clip(*args, **kwargs):
    clipboard = locals().get('args')[0]
    event = locals().get('args')[1]
    target, content = manager.clipboard_changed(clipboard, event)
    
    
    
    if (target is not None) and (content is not None):
        #print(target, type(content))
        #print(type(content.get_data()))
        #print(type(content.get_pixbuf()))
        #print(clipsdb.get_checksum(content.get_data().decode('utf-8').encode('utf-8')))
        if target == manager.image_target:
            source = 'screenshot'
            cache_uri = '/home/adi/Downloads/content.png'
            #save file
            content.savev(cache_uri, 'png', [], [])
            print(clipsdb.get_checksum(open(cache_uri, 'rb').read()))
            #create thumbnail
            thumbnail = content.scale_simple(content.get_width()//2,content.get_height()//2, GdkPixbuf.InterpType.BILINEAR)
            data = content
            pass
        elif target == manager.uri_target:
            source = 'file-manager'
            content = content.get_data().decode("utf-8") 
            uris=[]
            for i in content.splitlines():
                uris.append(urlparse(i).path.replace('%20',' '))
            uri_list = '\n'.join(uris)
            data = uri_list
            pass
        elif target == manager.html_target:
            source = 'selection'
            content = content.get_data().decode("utf-8") #decode from bytes to string for html/text targets
            data = content
            pass
        elif target == manager.text_target:
            source = 'selection'
            data = content
            pass
        else:
            print('Clips: Unsupported target type')
        # data_tuple = (type, source, cache_uri, data)
        # clips.add_record(data)
        #print(type(data))
        #print(data)
    else:
        print("Clips: No content in the clipboard")


manager.clipboard.connect("owner-change", new_clip)
clipsdb = ClipsDatastore(debugflag=False)

Gtk.main()
