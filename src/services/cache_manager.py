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
from gi.repository import Gtk, GLib, GdkPixbuf
from urllib.parse import urlparse
from datetime import datetime

class CacheManager():

    main_window = None

    def __init__(self, gtk_application=None, clipboard_manager=None):

        # initiatialize gtk_application and clipboard_manager
        if gtk_application is not None:
            self.app = gtk_application
            application_id = gtk_application.props.application_id

        if clipboard_manager is not None:
            clipboard_manager.clipboard.connect("owner-change", self.update_cache, clipboard_manager)

        # initialize cache directory
        self.cache_dir = os.path.join(GLib.get_user_cache_dir(), application_id)
        self.cache_filedir = os.path.join(self.cache_dir, "cache")
        self.icon_cache_filedir = os.path.join(self.cache_dir, "icon")

        try:
            if not os.path.exists(self.cache_filedir):
                os.makedirs(self.cache_filedir)
            if not os.path.exists(self.icon_cache_filedir):
                os.makedirs(self.icon_cache_filedir)
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
                id              INTEGER     PRIMARY KEY     NOT NULL,
                target          TEXT        NOT NULL,
                created         TEXT        NOT NULL        DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%S.%f', 'NOW', 'localtime')),
                source          TEXT,
                source_app      TEXT,
                source_icon     TEXT,
                cache_file      TEXT,
                type            TEXT,
                protected       TEXT
            );
            ''')
    
    def load_clips(self):
        # get lastrow id
        last_id = self.db_cursor.execute('SELECT max(id) FROM ClipsDB')
        last_id = last_id.fetchone()[0]

        data_param = (str(last_id),) #pass in a sequence ie list

        sqlite_with_param = '''
            SELECT * FROM 'ClipsDB'
            WHERE
            id <= ?;
            '''
        self.db_cursor.execute(sqlite_with_param, data_param)
        records = self.db_cursor.fetchall()
        return records

    def add_record(self, data_tuple):
        sqlite_insert_with_param = '''
            INSERT INTO 'ClipsDB'
            ('target', 'created', 'source', 'source_app', 'source_icon', 'cache_file', 'type', 'protected') 
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?);
            '''
        try:
            self.db_cursor.execute(sqlite_insert_with_param, data_tuple)
            self.db_connection.commit()
            # database_cursor.close()
        except sqlite3.Error as error:
            print("Exception sqlite3.Error: ", error) #add logging
        finally:
            pass
    
    def update_record(self, checksum):
        data_param = (str(checksum + "%"),) #pass in a sequence ie list
        sqlite_with_param = '''
            SELECT created, cache_file FROM 'ClipsDB'
            WHERE
            cache_file LIKE ?;
            '''
        self.db_cursor.execute(sqlite_with_param, data_param)
        records = self.db_cursor.fetchall()

        created_original = datetime.strptime(records[0][0], '%Y-%m-%d %H:%M:%S.%f')
        cache_file = records[0][1]

        created_updated = datetime.now()
        data_param = (created_updated, cache_file, ) #pass in a sequence ie list
        sqlite_with_param = '''
            UPDATE 'ClipsDB'
            SET created = ?
            WHERE
            cache_file = ?;
            '''
        self.db_cursor.execute(sqlite_with_param, data_param)
        self.db_connection.commit()

    def delete_record(self, id, cache_file):
        data_param = (str(id),) #pass in a sequence ie list
        sqlite_with_param = '''
            DELETE FROM 'ClipsDB'
            WHERE
            id = ?;
            '''
        self.db_cursor.execute(sqlite_with_param, data_param)
        self.db_connection.commit()
        #confirm deleted
        self.select_record(id)
        self.delete_cache_file(cache_file)

    def select_record(self, id):
        data_param = (str(id),) #pass in a sequence ie list
        sqlite_with_param = '''
            SELECT * FROM 'ClipsDB'
            WHERE
            id = ?;
            '''
        self.db_cursor.execute(sqlite_with_param, data_param)
        records = self.db_cursor.fetchall()
        # for row in records:
        #     print("db:", type(row), row)
        return records

    def check_duplicate(self, checksum):
        data_param = (checksum + "%",) #pass in a sequence ie list
        sqlite_with_param = '''
            SELECT * FROM 'ClipsDB'
            WHERE
            cache_file LIKE ?;
            '''
        self.db_cursor.execute(sqlite_with_param, data_param)
        records = self.db_cursor.fetchall()
        return records

    def search_record(self, data_tuple):
        pass

    def delete_cache_file(self, cache_file):
        #print(cache_file)
        try:
            os.remove(cache_file)
            return True
        except OSError:
            return OSError

    def get_checksum(self, data):
        checksum = hashlib.md5(data).hexdigest()
        return checksum

    def update_cache(self, clipboard, event, clipboard_manager):

        data_tuple = clipboard_manager.clipboard_changed(clipboard, event)

        if not None in data_tuple:
            target, content, source_app, source_icon, created, protected = data_tuple



            # temp_filename = 'temp-' + tempfile.gettempprefix()
            temp_filename = next(tempfile._get_candidate_names()) + tempfile.gettempprefix()

            if target == clipboard_manager.uri_target: # x-special/gnome-copied-files or uri list
                source = 'file-manager'
                cache_filetype = '.uri'
                type = "files"
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
                type = "image"
                temp_cache_uri = os.path.join(self.cache_filedir, temp_filename + cache_filetype)

                # save content to temp file
                content.savev(temp_cache_uri, 'png', [], [])

            elif target == clipboard_manager.html_target: # text/html
                source = 'selection'
                cache_filetype = '.html'
                type = "html"
                temp_cache_uri = os.path.join(self.cache_filedir, temp_filename + cache_filetype)

                content = content.get_data().decode("utf-8") # decode from bytes to string for html/text targets

            elif target == clipboard_manager.richtext_target: # text/richtext
                source = 'selection'
                cache_filetype = '.rtf'
                type = "richtext"
                temp_cache_uri = os.path.join(self.cache_filedir, temp_filename + cache_filetype)

                content = content.get_data() # for rich text, save the bytes to .rtf file directly
            
            elif target == clipboard_manager.text_target: # text/plain
                source = 'selection'
                cache_filetype = '.txt'
                type = "plaintext"
                temp_cache_uri = os.path.join(self.cache_filedir, temp_filename + cache_filetype)

                # check for other supported types

                # check if hex, rgb, rgba, hsl, hsla color codes, if only a single string contained
                if self.app.utils.isValidColorCode(content):
                    type = "color/" + self.app.utils.isValidColorCode(content)[1]

                # check if string is a URL only if there is one long string of URL
                elif urlparse(content.split(" ")[0]) and len(content.split(" ")) == 1:
                    cache_filetype = '.desktop'
                    type = "url"
                    temp_cache_uri = os.path.join(self.cache_filedir, temp_filename + cache_filetype)

                    _content = "[Desktop Entry]" + "\n"
                    _content = _content + "Encoding=UTF-8" + "\n"
                    _content = _content + "Name={domain}".format(domain=urlparse(content).netloc) + "\n"
                    _content = _content + "Type=Application" + "\n"
                    _content = _content + "Icon=internet-web-browser" + "\n"
                    _content = _content + "MimeType=application/x-mswinurl" + "\n"
                    _content = _content + "Exec=xdg-open {url}".format(url=content) + "\n"

                    content = _content

            else:
                print('Clips: Unsupported target type')


            if target == clipboard_manager.richtext_target: # text/richtext
                file = open(temp_cache_uri,"wb")
                file.write(content)
                file.close()
            elif target != clipboard_manager.image_target: #except for images
                # save content to temp file
                file = open(temp_cache_uri,"w")
                file.write(content)
                file.close()

            checksum = self.get_checksum(open(temp_cache_uri, 'rb').read())
            cache_file = checksum + cache_filetype
            cache_uri = self.cache_filedir + '/' + cache_file
            os.renames(temp_cache_uri, cache_uri)

            # fallback for source_icon
            # save a copy of the icon in case the app is uninstalled and no icon to use
            icon_theme = Gtk.IconTheme.get_default()
            try:
                if source_icon.find("/") != -1:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(source_icon, 48, 48, True) # load from path for non-theme icons
                else:
                    pixbuf = icon_theme.load_icon(source_icon, 48, Gtk.IconLookupFlags.USE_BUILTIN)
            except:
                pixbuf = icon_theme.load_icon("image-missing", 48, Gtk.IconLookupFlags.USE_BUILTIN)

            source_icon_cache = os.path.join(self.icon_cache_filedir, source_app.replace(" ",".").lower() + ".png")
            pixbuf.savev(source_icon_cache, 'png', [], []) # save to icon cache folder

            record = (str(target), created, source, source_app, source_icon, cache_file, type, protected)
            #record = (str(target), created, source, source_app, source_icon, checksum, cache_filetype, type, protected)

            clips_view = self.main_window.utils.get_widget_by_name(widget=self.main_window, child_name="clips-view", level=0)

            # check duplicates using checksum
            if len(self.check_duplicate(checksum)) == 0:
                self.add_record(record) # add to database
                new_record = self.select_record(self.db_cursor.lastrowid)[0] # prepare record for gui
                clips_view.new_clip(self.cache_filedir, new_record) # add to gui
            else:
                # add action if duplicate is found, either updated created date or something
                self.update_record(checksum)
                # clips_view.flowbox.invalidate_sort()
                # clips_view.show_all()








