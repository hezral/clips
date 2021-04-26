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


import gi
gi.require_version('Gtk', '3.0')
gi.require_version("Wnck", "3.0")
gi.require_version("Bamf", "3")
from gi.repository import Gtk, Gdk, Bamf, Wnck

from datetime import datetime

import services.clips_supported

class ClipboardManager():

    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    events = []
    proceed = True

    def __init__(self, gtk_application=None):
        super().__init__()

        self.app = gtk_application
        self.clips_supported = services.clips_supported

    def get_settings(self, gio_settings_keyname):
        return self.app.gio_settings.get_value(gio_settings_keyname).get_strv()

    def clipboard_changed(self, clipboard, event):

        # print("active app:", active_app)
        # print("selection owner:", event.owner)
        # print("reason:", event.reason.value_name)
        # print("event type:", event.type.value_name)

        if event.reason is Gdk.OwnerChange.NEW_OWNER and event.owner is not None:
            event_id = 0

        if event.reason is Gdk.OwnerChange.NEW_OWNER and event.owner is None:
            event_id = 1

        if event.reason is Gdk.OwnerChange.DESTROY and event.owner is None:
            event_id = 1

        if event.reason is Gdk.OwnerChange.CLOSE and event.owner is None:
            event_id = 1

        # print((active_app, event.reason.value_name, event.owner, event_id))

        if len(self.events) == 0 and event_id == 0:
            self.events.append(event_id)
            self.proceed = True
        elif len(self.events) == 1 and self.events[0] == 0 and event_id == 1:
            self.events.append(event_id)
            self.proceed = False
        elif len(self.events) == 2 and self.events[0] == 0 and self.events[1] == 1 and event_id == 0:
            self.events.append(event_id)
            self.proceed = False
        elif len(self.events) == 2 and self.events[0] == 0 and self.events[1] == 1 and event_id == 1:
            self.events.append(event_id)
            self.proceed = False
        elif len(self.events) == 3 and self.events[0] == 0 and self.events[1] == 1 and self.events[2] == 1 and event_id == 0:
            self.events = []
            self.proceed = True
        elif len(self.events) == 3 and self.events[0] == 0 and self.events[1] == 1 and self.events[2] == 0 and event_id == 0:
            self.events = []
            self.proceed = True

        # exclude apps
        active_app, active_app_icon = self.app.utils.get_active_app_window()

        if active_app != "Clips":
            if active_app not in self.get_settings("excluded-apps"):
                if self.proceed:
                    created = datetime.now()
                    clipboard_contents = self.get_clipboard_contents(clipboard, event, active_app)
                    if clipboard_contents is not None:
                        target, content, thumbnail, file_extension, additional_desc, content_type = clipboard_contents
                        source_app = active_app
                        source_icon = active_app_icon

                        print("clipboard_manager.py, line:98:", source_app, self.get_settings("protected-apps"))
                        if source_app not in self.get_settings("protected-apps"):
                            protected = "no"
                        else:
                            protected = "yes"

                        print("clipboard event captured:", self.events, active_app)
                        return target, content, source_app, source_icon, created, protected, thumbnail, file_extension, content_type
            else:
                print("clipboard event ignored:", self.events, event_id, active_app)
                pass

    def get_clipboard_contents(self, clipboard, event, active_app):
        
        clip_saved = False

        for supported_target in self.clips_supported.supported_targets:   
            for target in clipboard.wait_for_targets()[1]:
                if target not in self.clips_supported.excluded_targets and supported_target[0] in str(target) and clip_saved is False:
                    proceed = True

                    content = clipboard.wait_for_contents(target)
                    if content is not None:

                        file_extension = supported_target[1]
                        additional_desc = supported_target[2]
                        content_type = supported_target[3]
                        thumbnail = supported_target[4]

                        # only get the right target for these types
                        if "WPS" in active_app and not "WPS" in supported_target[2]:
                            proceed = False

                        if "Libre" in active_app and not "Libre" in supported_target[2]:
                            proceed = False

                        if "WPS Spreadsheets" in supported_target[2] or "LibreOffice Calc" in supported_target[2]:
                            target = Gdk.Atom.intern('text/html', False)

                        if "WPS Writer" in supported_target[2] or "LibreOffice Writer" in supported_target[2]:
                            target = Gdk.Atom.intern('text/rtf', False)

                        if "LibreOffice Impress" in supported_target[2]:
                            target = Gdk.Atom.intern('application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)"', False)

                        if "text/plain;charset=utf-8" in supported_target[0] and "color" in supported_target[3]:
                            if clipboard.wait_for_contents(target).get_text() is not None:
                                if self.app.utils.is_valid_color_code(clipboard.wait_for_contents(target).get_text().strip()):
                                    content_type = "color/" + self.app.utils.is_valid_color_code(content.get_text().strip())[1]
                                else:
                                    proceed = False

                        if ("text/plain;charset=utf-8" in supported_target[0] or "text/plain" in supported_target[0]) and "url" in supported_target[3]:
                            if clipboard.wait_for_contents(target).get_text() is not None:
                                if self.app.utils.is_valid_url(clipboard.wait_for_contents(target).get_text().strip()):
                                    content_type = "url/" + clipboard.wait_for_contents(target).get_text().split(":")[0]
                                else:
                                    proceed = False

                        if ("text/plain;charset=utf-8" in supported_target[0] or "text/plain" in supported_target[0]) and "mail" in supported_target[3]:
                            if clipboard.wait_for_contents(target).get_text() is not None:
                                if self.app.utils.is_valid_email(clipboard.wait_for_contents(target).get_text().strip()):
                                    content_type = "mail"
                                else:
                                    proceed = False

                        if ("text/plain;charset=utf-8" in supported_target[0] or "text/plain" in supported_target[0]) and "files" in supported_target[3]:
                            if clipboard.wait_for_contents(target).get_text() is not None:
                                if self.app.utils.is_valid_unix_uri(clipboard.wait_for_contents(target).get_text().strip().splitlines()[-1].replace("file://","")):
                                    content_type = "files"
                                else:
                                    proceed = False

                        if proceed:
                            if thumbnail:
                                thumbnail = clipboard.wait_for_contents(Gdk.Atom.intern('image/png', False))
                            else:
                                thumbnail = None

                            content = clipboard.wait_for_contents(target)

                            clip_saved = True

                            return target, content, thumbnail, file_extension, additional_desc, content_type
