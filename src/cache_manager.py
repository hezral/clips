# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

import time
import os
import hashlib
import sqlite3
import tempfile
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib, GdkPixbuf
from urllib.parse import urlparse
from datetime import datetime

import chardet

class CacheManager():

    main_window = None
    clipboard_monitoring = False
    queue = []

    def __init__(self, gtk_application=None, clipboard_manager=None):

        # initiatialize gtk_application and clipboard_manager
        if gtk_application is not None:
            self.app = gtk_application
            application_id = self.app.props.application_id

        if clipboard_manager is not None:
            clipboard_manager.clipboard.connect("owner-change", self.update_cache, clipboard_manager)
            self.clipboard_monitoring = True

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
        print(datetime.now(), "open_db")
        print("Found ClipsDB", curr_table)
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

    def update_record_on_recopy(self, checksum):
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

        self.check_total_clips()
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
        run_autohousekeeping= self.app.utils.get_widget_by_name(widget=self.main_window.settings_view, child_name="run-housekeeping-now", level=0)
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

    def get_id_by_checksum(self, checksum):
        data_param = (checksum + "%",) #pass in a sequence ie list
        sqlite_with_param = '''
            SELECT id FROM 'ClipsDB'
            WHERE
            cache_file LIKE ?;
            '''
        self.db_cursor.execute(sqlite_with_param, data_param)
        records = self.db_cursor.fetchall()
        return records[0][0]

    def delete_cache_file(self, cache_file, clip_type):

        thumbnail_file = os.path.splitext(cache_file)[0]+'-thumb.png'
        alt_cache_file = cache_file.replace("html", "txt")

        if 'http' in clip_type:
            with open(cache_file) as file:
                content  = file.readlines()[0] # returns a list with 1 item
            checksum = os.path.splitext(cache_file)[0].split("/")[-1]
            domain = self.app.utils.get_domain(content)
            favicon_file = self.icon_cache_filedir + '/' + domain + '-' + checksum + '.ico'
            try:
                os.remove(favicon_file)
            except OSError:
                return OSError

        try:
            os.remove(cache_file)
            if "html" in clip_type:
                os.remove(alt_cache_file)
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
            target, content, source_app, source_icon, created, protected, thumbnail, file_extension, content_type, alt_content, alt_file_extension, additional_desc = data_tuple

            temp_filename = next(tempfile._get_candidate_names()) + tempfile.gettempprefix()
            type = content_type
            cache_filetype = file_extension
            temp_cache_uri = os.path.join(self.cache_filedir, temp_filename + cache_filetype)
            temp_cache_thumbnail_uri = os.path.join(self.cache_filedir, temp_filename + "-thumb" + ".png")
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
 
            # condition if certain keywords is excluded from copy events
            excluded_keywords_list_values = self.app.gio_settings.get_value("keywords").get_strv()
            keyword_match = [source_app.lower(), content.get_data().decode("utf-8").lower(), file_extension.lower(), content_type.lower(), additional_desc.lower()]
            keyword_match_joined = ' '.join(keyword_match)
            if any(i.lower() in keyword_match_joined for i in excluded_keywords_list_values):
                return

            # condition if certain file types is excluded from copy events
            if 'files' in content_type:
                lines = []
                excluded_file_types_list_values = self.app.gio_settings.get_value("file-types").get_strv()
                file_read = open(temp_cache_uri, "r")
                line_content = file_read.readlines()

                if len(line_content) == 1:
                    line = line_content[0].replace("copy","").replace("file://","").strip().replace("%20", " ")
                    if os.path.exists(line):
                        mime_type, val = Gio.content_type_guess(line, data=None)
                        if mime_type in excluded_file_types_list_values:
                            return
                else:
                    for line in line_content:
                            line = line.replace("copy","").replace("file://","").strip().replace("%20", " ")
                            if os.path.exists(line):
                                mime_type, val = Gio.content_type_guess(line, data=None)
                                if mime_type not in excluded_file_types_list_values:
                                    lines.append(line)
                file_read.close()

                if len(lines) != 0:
                    file_write = open(temp_cache_uri, "w")
                    i = 0
                    for line in lines:
                        if i == 0:
                            line = "copyfile://{0}".format(line)
                        else:
                            line = "\nfile://{0}".format(line)
                        file_write.write(line)
                        i += 1

                    file_write.close()

            # save alt_content in temp for html
            if alt_content is not None:
                temp_alt_cache_uri = os.path.join(self.cache_filedir, temp_filename + alt_file_extension)
                file = open(temp_alt_cache_uri,"wb")
                file.write(alt_content.get_data())
                file.close()

                # condition for html content where bg and text is same color
                # file_read = open(temp_cache_uri, "r")
                # content = file_read.read()
                # css_bg_color = self.app.utils.get_css_background_color(content)
                # css_txt_color = self.app.utils.get_css_text_color(content)
                # if css_bg_color == css_txt_color:
                #     new_content = content.replace("background-color: {0}".format(css_bg_color), "background-color: rgb(255,255,255)")
                #     new_content = new_content.replace("color: {0}".format(css_txt_color), "color: none")
                #     file_read.close()
                #     file_write = open(temp_cache_uri,"w")
                #     file_write.write(new_content)
                #     file_write.close()

            # get checksum value
            checksum = self.get_checksum(open(temp_cache_uri, 'rb').read())

            # rename cache file using its checksum value
            cache_file = checksum + "." + cache_filetype
            cache_uri = self.cache_filedir + '/' + cache_file
            os.renames(temp_cache_uri, cache_uri)
            if alt_content is not None:
                alt_cache_file = checksum + "." + alt_file_extension
                alt_cache_uri = self.cache_filedir + '/' + alt_cache_file
                os.renames(temp_alt_cache_uri, alt_cache_uri)

            if "yes" in protected and type == "plaintext":
                cache_file = self.encrypt_file(cache_uri)

            # save thumbnail if available
            if thumbnail is not None:
                cache_thumbnail_file = checksum + "-thumb" + ".png"
                cache_thumbnail_uri = self.cache_filedir + '/' + cache_thumbnail_file
                if content_type == "html":
                    self.app.utils.do_webview_screenshot(uri=cache_uri, out_file_path=cache_thumbnail_uri)
                    # GLib.timeout_add(250, os.renames, temp_cache_thumbnail_uri, cache_thumbnail_uri) #add timeout for it to catchup and now the temp file is there
                else:
                    file = open(cache_thumbnail_uri,"wb")
                    file.write(thumbnail.get_data())
                    file.close()
            
            from datetime import datetime
            if "http" in type:
                # GLib.idle_add(self.app.utils.get_web_favicon, content.get_text(), self.icon_cache_filedir, cache_uri)
                # with open(cache_uri, "a") as file:
                #     file.write("\n"+self.app.utils.get_web_title(content.get_text()))
                url = content.get_text()
                self.app.utils.get_web_data(url, cache_uri, self.icon_cache_filedir, checksum)

            if "mail" in type:
                url = "https://" + content.get_text().split("@")[-1]
                self.app.utils.get_web_data(url, cache_uri, self.icon_cache_filedir, checksum)

            # fallback for source_icon
            # save a copy of the icon in case the app is uninstalled and no icon to use
            icon_theme = self.app.icon_theme
            try:
                if source_icon.find("/") != -1:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(source_icon, 64, 64, True) # load from path for non-theme icons
                else:
                    pixbuf = icon_theme.load_icon(source_icon, 64, Gtk.IconLookupFlags.USE_BUILTIN)
            except:
                pixbuf = icon_theme.load_icon("image-missing", 64, Gtk.IconLookupFlags.USE_BUILTIN)

            source_icon_cache = os.path.join(self.icon_cache_filedir, source_app.replace(" ",".").lower() + ".png")
            pixbuf.savev(source_icon_cache, 'png', [], []) # save to icon cache folder

            record = (str(target), created, source, source_app, source_icon, cache_file, type, protected)
            clips_view = self.main_window.clips_view

            # check duplicates using checksum
            if len(self.check_duplicate(checksum)) == 0:
                self.add_record(record) # add to database
                
                new_record = self.select_record(self.db_cursor.lastrowid)[0] # prepare record for gui

                # self.queue_update_cache(new_record)
                # clips_view.new_clip(new_record) # add to gui
                GLib.timeout_add(750, clips_view.new_clip, new_record) # add to gui
            else:
                self.update_cache_on_recopy(checksum)
            
            self.check_total_clips()


    def queue_update_cache(self, record):
        print(record)
        id = record[0]
        self.main_window.clips_view.new_clip(record)

        try:
            print("success")
            self.main_window.clips_view.new_clip(record)
        except:
            flowboxchild = [child for child in self.main_window.clips_view.flowbox.get_children() if child.get_children()[0].id == id]
            print(flowboxchild)
            if flowboxchild is None:
                print("failed")
                return self.queue_update_cache(record)

        self.check_total_clips()
        # if len(self.queue) != 0:
        #     for item in self.queue:
        #         try:
        #             id = item[0]
        #             record = item[1]
        #             self.main_window.clips_view.new_clip(record)
        #             self.queue.pop(item)
        #         except:
        #             self.queue.append((id, record))
        #             return self.queue_update_cache
        # else:
        #     try:
        #         self.main_window.clips_view.new_clip(record)
        #     except:
        #         self.queue.append((id, record))
        #         return self.queue_update_cache
        
    def update_cache_on_recopy(self, cache_file=None, checksum=None):
        if checksum is None:
            checksum = os.path.splitext(cache_file)[0].split("/")[-1]

        # update db with new timestamp and get the timestamp
        created_updated = self.update_record_on_recopy(checksum)
        
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
        
        # update timestamp
        flowboxchild_updated = [child for child in self.main_window.clips_view.flowbox.get_children() if child.get_children()[0].id == id][0]
        clips_container = flowboxchild_updated.get_children()[0]
        clips_container.update_timestamp_on_clips(created_updated)
        
        self.main_window.clips_view.flowbox.invalidate_sort()

    def update_cache_on_newdata(self, cache_file=None, checksum=None):
        
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
        created_short = clip[9]
        
        # update timestamp
        flowboxchild_updated = [child for child in self.main_window.clips_view.flowbox.get_children() if child.get_children()[0].id == id][0]
        clips_container = flowboxchild_updated.get_children()[0]

        self.main_window.clips_view.flowbox.invalidate_sort()

    def check_total_clips(self):
        self.main_window.on_view_visible()

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

    def get_total_clips_by_type(self):
        sqlite_with_param = '''
            SELECT type, count(id) FROM 'ClipsDB' group by type
            '''
        self.db_cursor.execute(sqlite_with_param)
        records = self.db_cursor.fetchall()
        return records

    def get_data_for_liststore(self):
        sqlite_with_param = '''
            SELECT distinct type FROM 'ClipsDB'
            '''
        self.db_cursor.execute(sqlite_with_param)
        records = self.db_cursor.fetchall()
        return records

    def encrypt_file(self, cache_uri, reencrypt=False, passphrase=None):
        do_authenticate, authenticate_data = self.app.utils.do_authentication("get")
        if do_authenticate:
            if reencrypt:
                decrypt, decrypted_data = self.app.utils.do_encryption("decrypt", passphrase, cache_uri)
                if decrypt:
                    import tempfile, shutil
                    temp_filename = next(tempfile._get_candidate_names()) + tempfile.gettempprefix()
                    temp_file_uri = os.path.join(tempfile.gettempdir(), temp_filename)
                    with open(temp_file_uri, 'wb') as file:
                        file.write(decrypted_data)
                        file.close()
                    os.remove(cache_uri)
                    shutil.move(temp_file_uri, cache_uri)
                    # os.renames(temp_file_uri, cache_uri)
                    self.encrypt_file(cache_uri)
            else:
                encrypt, encrypted_file = self.app.utils.do_encryption("encrypt", authenticate_data, cache_uri)
                if encrypt:
                    os.remove(cache_uri)
                    cache_file = encrypted_file.replace("_enc__enc_","_enc_")
                    os.renames(encrypted_file, cache_file)
                    return os.path.split(cache_file)[1]

    def reset_protected_clips(self, password):
        protected = "yes"
        data_param = (protected, )
        sqlite_with_param = '''
            SELECT id, cache_file FROM 'ClipsDB'
            WHERE
            protected = ?;
            '''
        try:
            self.db_cursor.execute(sqlite_with_param, data_param)
            rows = self.db_cursor.fetchall()
            if rows is not None:
                # print(rows)
                for row in rows:
                    id = row[0]
                    cache_file_uri = os.path.join(self.cache_filedir,row[1])
                    self.encrypt_file(cache_file_uri, reencrypt=True, passphrase=password)
        except sqlite3.Error as error:
            return False, str(error)