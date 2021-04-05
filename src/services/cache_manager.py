#!/usr/bin/env python3

'''
    Copyright 2018 Adi Hezral (hezral@gmail.com)
    This file is part of Clips ("Application").
    The Application is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    The Application is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this Application.  If not, see <http://www.gnu.org/licenses/>.
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
            application_id = self.app.props.application_id

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
            id <= ?
            ORDER BY
            created ASC;
            '''
        self.db_cursor.execute(sqlite_with_param, data_param)
        records = self.db_cursor.fetchall()
        
        for record in records:
            id = record[0]
            cache_file = os.path.join(self.cache_filedir,record[6])
            clip_type = record[7]

            # clean-up and delete from db since cache_file doesn't exist
            if os.path.exists(cache_file) is False:
                print("cache file doesn't exist, record removed from db:", id, cache_file, clip_type)
                self.delete_record(id, cache_file, clip_type)
                records.remove(record)

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

        return created_updated

    def delete_record(self, id, cache_file, clip_type):
        data_param = (str(id),) #pass in a sequence ie list
        sqlite_with_param = '''
            DELETE FROM 'ClipsDB'
            WHERE
            id = ?;
            '''
        self.db_cursor.execute(sqlite_with_param, data_param)
        self.db_connection.commit()
        #confirm deleted
        # self.select_record(id)
        self.delete_cache_file(cache_file, clip_type)
        self.check_total_clips()
    
    def delete_all_record(self):
        sqlite_with_param = '''
            DELETE FROM 'ClipsDB'
            '''
        self.db_cursor.execute(sqlite_with_param)
        self.db_connection.commit()
        self.delete_all_cache_file()
        
        count = len(self.app.main_window.clips_view.flowbox.get_children())

        for flowboxchild in self.app.main_window.clips_view.flowbox.get_children():
            flowboxchild.destroy()

        # self.check_total_clips()
        self.main_window.update_total_clips_label("delete", count)

    def auto_housekeeping(self, days, manual_run=False):
        days_param = "-" + str(days) + " " + "day"
        data_param = (days_param,) #pass in a sequence ie list
        sqlite_with_param = '''
            SELECT * FROM 'ClipsDB'
            WHERE
            created <= date('now',?);
            '''
        self.db_cursor.execute(sqlite_with_param, data_param)
        records = self.db_cursor.fetchall()

        count = len(records)

        print(count, "found for auto housekeeping")

        # delete each record that match days criteria
        sqlite_with_param = '''
            DELETE FROM 'ClipsDB'
            WHERE
            id = ?;
            '''
        if count != 0:
            for record in records:
                print("id:", record[0], "cache_file:", record[6], "type:", record[7])
                cache_file = self.cache_filedir + "/" + record[6]
                type = record[7]
                id = record[0]
                self.delete_cache_file(cache_file, type)
                data_param = (str(record[0]),) #pass in a sequence ie list
                self.db_cursor.execute(sqlite_with_param, data_param)
                self.db_connection.commit()
                if manual_run:
                    flowboxchild = [child for child in self.app.main_window.clips_view.flowbox.get_children() if child.get_children()[0].id == id][0]
                    flowboxchild.destroy()

            if manual_run is False:
                self.check_total_clips()
                
            self.main_window.update_total_clips_label("delete", count)
        else:
            print("No records found for auto housekeeping")

        print(datetime.now(), "finish auto-housekeeping")

        last_run = datetime.now()
        last_run_short = datetime.strftime(last_run, '%a, %d %B %Y, %-I:%M:%S %p')
        run_autohousekeeping= self.app.utils.GetWidgetByName(widget=self.main_window.settings_view, child_name="run-housekeeping-now", level=0)
        run_autohousekeeping.sublabel_text.props.label = last_run_short

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

    def search_record(self, data_tuple):
        pass

    def delete_cache_file(self, cache_file, clip_type):

        thumbnail_file = os.path.splitext(cache_file)[0]+'-thumb.png'

        if 'http' in clip_type:
            with open(cache_file) as file:
                content  = file.readlines()[0] # returns a list with 1 item
            checksum = os.path.splitext(cache_file)[0].split("/")[-1]
            domain = self.app.utils.GetDomain(content)
            favicon_file = self.icon_cache_filedir + '/' + domain + '-' + checksum + '.ico'
            try:
                os.remove(favicon_file)
            except OSError:
                return OSError

        try:
            os.remove(cache_file)
            os.remove(thumbnail_file)
            return True
        except OSError:
            return OSError

    def delete_all_cache_file(self):
        for directory in (self.cache_filedir, self.icon_cache_filedir):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

    def get_checksum(self, data):
        checksum = hashlib.md5(data).hexdigest()
        return checksum

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

    def update_cache(self, clipboard, event, clipboard_manager):

        data_tuple = clipboard_manager.clipboard_changed(clipboard, event)

        if data_tuple is not None:
            target, content, source_app, source_icon, created, protected, thumbnail, file_extension, content_type = data_tuple

            temp_filename = next(tempfile._get_candidate_names()) + tempfile.gettempprefix()

            # define type
            type = content_type

            # define filetype/extension
            cache_filetype = file_extension

            # # define temp cache file 
            temp_cache_uri = os.path.join(self.cache_filedir, temp_filename + cache_filetype)
            temp_cache_thumbnail_uri = os.path.join(self.cache_filedir, temp_filename + "-thumb" + ".png")

            # define clip source
            if 'Workspace' in source_app:
                source = 'screenshot'
            elif 'files' in content_type:
                source = 'file-manager'
            else:
                source = 'application'

            # save content in temp
            file = open(temp_cache_uri,"wb")
            file.write(content.get_data())
            file.close()

            # get checksum value
            checksum = self.get_checksum(open(temp_cache_uri, 'rb').read())

            # rename cache file using its checksum value
            cache_file = checksum + "." + cache_filetype      
            cache_uri = self.cache_filedir + '/' + cache_file
            os.renames(temp_cache_uri, cache_uri)

            # save thumbnail if available
            if thumbnail is not None:
                file = open(temp_cache_thumbnail_uri,"wb")
                file.write(thumbnail.get_data())
                file.close()
                cache_thumbnail_file = checksum + "-thumb" + ".png"
                cache_thumbnail_uri = self.cache_filedir + '/' + cache_thumbnail_file
                os.renames(temp_cache_thumbnail_uri, cache_thumbnail_uri)
            
            from datetime import datetime
            if "http" in type:
                # GLib.idle_add(self.app.utils.GetWebpageFavicon, content.get_text(), self.icon_cache_filedir, cache_uri)
                # with open(cache_uri, "a") as file:
                #     file.write("\n"+self.app.utils.GetWebpageTitle(content.get_text()))
                self.app.utils.GetWebpageData(content.get_text(), cache_uri, self.icon_cache_filedir, checksum)
                
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

            clips_view = self.main_window.clips_view

            # print(datetime.now(), "start populating clip content")
        
            # check duplicates using checksum
            if len(self.check_duplicate(checksum)) == 0:
                self.add_record(record) # add to database
                new_record = self.select_record(self.db_cursor.lastrowid)[0] # prepare record for gui
                clips_view.new_clip(new_record) # add to gui

            else:
                self.update_cache_on_recopy(checksum)

            self.check_total_clips()
            
    def update_cache_on_recopy(self, cache_file=None, checksum=None):

        clips_view = self.main_window.clips_view

        if checksum is None:
            checksum = os.path.splitext(cache_file)[0].split("/")[-1]

        # update db with new timestamp and get the timestamp
        created_updated = self.update_record(checksum)
        
        # get the id for the clip that was updated
        clip = self.check_duplicate(checksum)[0]

        id = clip[0]
        target = clip[1]
        created = clip[2]
        source = clip[3]
        source_app = clip[4]
        source_icon = clip[5]
        cache_file = clip[6]
        type = clip[7]
        protected = clip[8]
        created_short = created_updated.strftime('%a, %b %d %Y, %H:%M:%S')

        
        # get the flowboxchild
        flowboxchild_updated = [child for child in clips_view.flowbox.get_children() if child.get_children()[0].id == id][0]

        # update the timestamp
        flowboxchild_updated.get_children()[0].created = created_updated
        flowboxchild_updated.get_children()[0].created_short = created_updated.strftime('%a, %b %d %Y, %H:%M:%S')
        flowboxchild_updated.get_children()[0].props.tooltip_text = "id: {id}\ntype: {type}\nsource: {source_app}\ncreated: {created}".format(
                                                                                                                                            id=id, 
                                                                                                                                            type=type,
                                                                                                                                            source=source, 
                                                                                                                                            source_app=source_app, 
                                                                                                                                            created=created_short)
        
        clips_view.flowbox.invalidate_sort()

    def check_total_clips(self):
        total = len(self.load_clips())

        # total not zero = show clips-view
        # total not zero, info-view is visible = hide info-view, show clips-view
        # total zero, clips-view is visible = show info-view
        # total zero, settings-view is not visible = show info-view
        # total zero, settings-view is visible = do nothing

        if total != 0:
            # print("total clips:", total)
            self.main_window.clips_view.show_all()
            self.main_window.stack.set_visible_child_name("clips-view")
        else:
            # print("total clips:", total)
            if self.main_window.clips_view.is_visible():
                self.main_window.stack.set_visible_child_name("info-view")
            if self.main_window.settings_view.is_visible():
                pass
            if not self.main_window.settings_view.is_visible():
                self.main_window.stack.set_visible_child_name("info-view")

    def load_source_apps(self):
        sqlite_with_param = '''
            SELECT DISTINCT source_app FROM 'ClipsDB'
            '''
        self.db_cursor.execute(sqlite_with_param)
        records = self.db_cursor.fetchall()
        return records

    def get_total_clips(self):
        sqlite_with_param = '''
            SELECT count(id) FROM 'ClipsDB'
            '''
        self.db_cursor.execute(sqlite_with_param)
        records = self.db_cursor.fetchall()
        return records

            
