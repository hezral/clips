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
from gi.repository import Gtk, GLib
from urllib.parse import urlparse


class CacheManager():
    def __init__(self, gtk_application=None, clipboard_manager=None):

        # initiatialize database file
        if gtk_application is not None:
            application_id = gtk_application.props.application_id
        else:
            application_id = "com.github.hezral.clips"

        if clipboard_manager is not None:
            clipboard_manager.clipboard.connect("owner-change", self.update_cache, clipboard_manager)
        else:
            from clipboard_manager import ClipboardManager
            clipboard_manager = ClipboardManager()
            clipboard_manager.clipboard.connect("owner-change", self.update_cache, clipboard_manager)

        # initialize cache directory
        self.cache_dir = os.path.join(GLib.get_user_cache_dir(), application_id)
        self.cache_filedir = os.path.join(self.cache_dir, "cache")
        try:
            if not os.path.exists(self.cache_filedir):
                os.makedirs(self.cache_filedir)
        except OSError as error:
            print("Excption: ", error)

        # initialize db file
        db_file = os.path.join(self.cache_dir, application_id + ".db")
        try:
            if (os.path.exists(db_file)):
                self.db_connection, self.db_cursor = self.open_db(db_file)
            else:
                self.db_connection, self.db_cursor = self.open_db(db_file)
                self.create_table(self.db_cursor)
        except (OSError, sqlite3.Error) as error:
            print("Exception: ", error)
    
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
                cache_file   TEXT
            );
            ''')
    
    def add_record(self, data_tuple):

        sqlite_insert_with_param = '''
            INSERT INTO 'ClipsDB'
            ('target', 'created', 'source', 'source_app', 'source_icon', 'cache_file') 
            VALUES
            (?, ?, ?, ?, ?, ?);
            '''
        try:
            self.db_cursor.execute(sqlite_insert_with_param, data_tuple)
            self.db_connection.commit()
            #database_cursor.close()
        except sqlite3.Error as error:
            print("Exception sqlite3.Error: ", error) #add logging
        finally:
            self.select_record(self.db_cursor.lastrowid)

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

    def get_checksum(self, data):
        checksum = hashlib.md5(data).hexdigest()
        return checksum

    def update_cache(self, clipboard, event, clipboard_manager):

        data_tuple = clipboard_manager.clipboard_changed(clipboard, event)

        if not None in data_tuple:
            target, content, source_app, source_icon, created = data_tuple

            temp_filename = 'temp-' + tempfile.gettempprefix()

            if target == clipboard_manager.uri_target: # x-special/gnome-copied-files or uri list
                source = 'file-manager'
                cache_filetype = '.uri'
                temp_cache_uri = os.path.join(self.cache_filedir, temp_filename + cache_filetype)

                content = content.get_data().decode("utf-8") 
                uris=[] #for file copy items, don't keep files in cache to avoid storage issues, just get the original uri
                for i in content.splitlines():
                    uris.append(urlparse(i).path.replace('%20',' '))
                content = '\n'.join(uris)

            elif target == clipboard_manager.image_target: # image/png
                if 'Workspace' in source_app:
                    source = 'screenshot'
                else:
                    source = 'application'
                cache_filetype = '.png'
                temp_cache_uri = os.path.join(self.cache_filedir, temp_filename + cache_filetype)

                # save content to temp file
                content.savev(temp_cache_uri, 'png', [], [])

                # create thumbnail
                # thumbnail = content.scale_simple(content.get_width()//2,content.get_height()//2, GdkPixbuf.InterpType.BILINEAR)

            elif target == clipboard_manager.html_target: # text/html
                source = 'selection'
                cache_filetype = '.html'
                temp_cache_uri = os.path.join(self.cache_filedir, temp_filename + cache_filetype)

                content = content.get_data().decode("utf-8") # decode from bytes to string for html/text targets

            elif target == clipboard_manager.richtext_target: # text/richtext
                source = 'selection'
                cache_filetype = '.rtf'
                temp_cache_uri = os.path.join(self.cache_filedir, temp_filename + cache_filetype)

                content = content.get_data() # for rich text, save the bytes to .rtf file directly
            
            elif target == clipboard_manager.text_target: # text/plain
                source = 'selection'
                cache_filetype = '.txt'
                temp_cache_uri = os.path.join(self.cache_filedir, temp_filename + cache_filetype)

            else:
                print('Clips: Unsupported target type')


            if target != clipboard_manager.image_target: #except for images
                # save content to temp file
                file = open(temp_cache_uri,"w")
                file.write(content)
                file.close()

            checksum = self.get_checksum(open(temp_cache_uri, 'rb').read())
            cache_file = checksum + cache_filetype
            cache_uri = self.cache_filedir + '/' + cache_file
            os.renames(temp_cache_uri, cache_uri)

            record = (str(target), created, source, source_app, source_icon, cache_file)
            self.add_record(record)




# # codes below are only for debugging
# def new_clip(*args):
#     clipboard = locals().get('args')[0]
#     event = locals().get('args')[1]
#     # target, content, source_app, source_icon, created = manager.clipboard_changed(clipboard, event)
#     data = clipboard_manager.clipboard_changed(clipboard, event)
#     datastore.update_cache(data)

# from clipboard_manager import ClipboardManager
# clipboard_manager = ClipboardManager()
# clipboard_manager.clipboard.connect("owner-change", new_clip)
# datastore = CacheManager(clipboard_manager=clipboard_manager)


# GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)
# Gtk.main()
