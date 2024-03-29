# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from datetime import datetime

from . import clips_supported

class ClipboardManager():

    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    events = []
    proceed = True

    def __init__(self, gtk_application=None):
        super().__init__()

        self.app = gtk_application
        self.clips_supported = clips_supported

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
        active_app, active_app_icon = self.app.utils.get_active_appinfo_xlib()

        if active_app != "Clips":
            if active_app not in self.get_settings("excluded-apps"):
                if self.proceed:
                    created = datetime.now()
                    clipboard_contents = self.get_clipboard_contents(clipboard, event, active_app)
                    if clipboard_contents is not None:
                        target, content, thumbnail, file_extension, additional_desc, content_type, alt_content, alt_file_extension = clipboard_contents
                        source_app = active_app
                        source_icon = active_app_icon

                        protected = "no"
                        # print("clipboard_manager.py, line:98:", source_app, self.get_settings("protected-apps"))
                        if self.app.gio_settings.get_value("protected-mode"):
                            if source_app in self.get_settings("protected-apps"):
                                protected = "yes"

                        self.app.logger.debug("clipboard event captured:", self.events, active_app)
                        return target, content, source_app, source_icon, created, protected, thumbnail, file_extension, content_type, alt_content, alt_file_extension, additional_desc
            else:
                self.app.logger.debug("clipboard event ignored:", self.events, event_id, active_app)
                pass

    def get_clipboard_contents(self, clipboard, event, active_app):
        
        clip_saved = False
        alt_target = None
        alt_content = None
        alt_file_extension = None

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

                        if "text/html" in supported_target[0]:
                            alt_target = Gdk.Atom.intern('text/plain', False)
                            alt_file_extension = "txt"

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
                                if content_type == "html":
                                    thumbnail = True
                                else:
                                    thumbnail = clipboard.wait_for_contents(Gdk.Atom.intern('image/png', False))
                            else:
                                thumbnail = None

                            content = clipboard.wait_for_contents(target)

                            if alt_target is not None:
                                alt_content = clipboard.wait_for_contents(alt_target)

                            clip_saved = True

                            return target, content, thumbnail, file_extension, additional_desc, content_type, alt_content, alt_file_extension
