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
import os
import hashlib
import sqlite3
import tempfile
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf, Gdk
from urllib.parse import urlparse


class CacheManager():
    def __init__(self, cachedir):

        # initiatialize database file
        db_file = 'com.github.hezral.clips.db'
        try:
            if (os.path.exists(db_file)):
                self.db_connection, self.db_cursor = self.open_db(db_file)
            else:
                self.db_connection, self.db_cursor = self.open_db(db_file)
                self.create_table(self.db_cursor)
        except (OSError, sqlite3.Error) as error:
            print("Exception: ", error)

        # initialize cache directory
        if cachedir: 
            self.file_cache = cachedir
        else:
            self.file_cache = 'cache'
        try:
            if not os.path.exists(self.file_cache):
                os.makedirs(self.file_cache)
        except OSError as error:
            print("Excption: ", error)

    
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
                target      TEXT        NOT NULL,
                created     TEXT        NOT NULL        DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%S.%f', 'NOW', 'localtime')),
                source      TEXT,
                source_app  TEXT,
                source_icon TEXT,
                cache_uri   TEXT
            );
            ''')
    
    def add_record(self, data_tuple):

        sqlite_insert_with_param = '''
            INSERT INTO 'ClipsDB'
            ('target', 'created', 'source', 'source_app', 'source_icon', 'cache_uri') 
            VALUES
            (?, ?, ?, ?, ?, ?);
            '''
        try:
            self.db_cursor.execute(sqlite_insert_with_param, data_tuple)
            self.db_connection.commit()
            #database_cursor.close()
        except sqlite3.Error as error:
            print("Exception sqlite3.Error: ", error)
        finally:
            print(self.db_cursor.lastrowid)
            self.select_record(self.db_cursor.lastrowid)

    def store_cache(self, data_tuple):

        if not None in data_tuple:
            target, content, source_app, source_icon, created = data_tuple

            temp_filename = 'temp-' + tempfile.gettempprefix()

            if target == targets[0]: # x-special/gnome-copied-files or uri list
                source = 'file-manager'
                cache_filetype = '.uri'
                temp_cache_uri = os.path.join(self.file_cache, temp_filename + cache_filetype)

                # save content to temp file
                content = content.get_data().decode("utf-8") 
                uris=[] #for file copy items, don't keep files in cache to avoid storage issues, just get the original uri
                for i in content.splitlines():
                    uris.append(urlparse(i).path.replace('%20',' '))
                uri_list = '\n'.join(uris)

                file = open(temp_cache_uri,"w")
                file.write(uri_list)
                file.close()

            elif target == targets[1]: # image/png
                if 'Workspace' in source_app:
                    source = 'screenshot'
                else:
                    source = 'application'
                cache_filetype = '.png'
                temp_cache_uri = os.path.join(self.file_cache, temp_filename + cache_filetype)

                # save content to temp file
                content.savev(temp_cache_uri, 'png', [], [])

                # create thumbnail
                # thumbnail = content.scale_simple(content.get_width()//2,content.get_height()//2, GdkPixbuf.InterpType.BILINEAR)

            elif target == targets[2]: # text/html
                source = 'selection'
                cache_filetype = '.html'
                temp_cache_uri = os.path.join(self.file_cache, temp_filename + cache_filetype)

                content = content.get_data().decode("utf-8") # decode from bytes to string for html/text targets
                # save content to temp file
                file = open(temp_cache_uri,"w")
                file.write(content)
                file.close()

            elif target == targets[3]: # text/richtext
                source = 'selection'
                cache_filetype = '.rtf'
                temp_cache_uri = os.path.join(self.file_cache, temp_filename + cache_filetype)

                content = content.get_data() # for rich text, save the bytes to .rtf file directly
                # save content to temp file
                file = open(temp_cache_uri,"wb") # need to write in binary
                file.write(content)
                file.close()
            
            elif target == targets[4]: # text/plain
                source = 'selection'
                cache_filetype = '.txt'
                temp_cache_uri = os.path.join(self.file_cache, temp_filename + cache_filetype)

                # save content to temp file
                file = open(temp_cache_uri,"w")
                file.write(content)
                file.close()

            else:
                print('Clips: Unsupported target type')


            checksum = self.get_checksum(open(temp_cache_uri, 'rb').read())
            cache_uri = self.file_cache + '/' + checksum + cache_filetype
            os.renames(temp_cache_uri, cache_uri)
            record = (str(target), created, source, source_app, source_icon, cache_uri)
            self.add_record(record)

    def select_record(self, id):
        
        data_param = (str(id),) #pass in a sequence ie list

        sqlite_select_with_param = '''
            SELECT * FROM 'ClipsDB'
            WHERE
            id = ?;
            '''
        self.db_cursor.execute(sqlite_select_with_param, data_param)
        records = self.db_cursor.fetchall()
        for row in records:
            print("db:", row)
    
    def search_record(self, data_tuple):
        pass

    def save_cache_file(self, data):
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
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit) # just for debugging at CLI to enable CTRL+C quit





def new_clip(*args):
    clipboard = locals().get('args')[0]
    event = locals().get('args')[1]
    # target, content, source_app, source_icon, created = manager.clipboard_changed(clipboard, event)
    data = manager.clipboard_changed(clipboard, event)
    datastore.store_cache(data)

from clipboard_manager import ClipboardManager
manager = ClipboardManager()
targets = manager.targets

from constants import ClipsConfig
config = ClipsConfig()


datastore = CacheManager(cachedir=None)


manager.clipboard.connect("owner-change", new_clip)


GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)
Gtk.main()
