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

    skip_event = 0

    def __init__(self, gtk_application=None):
        super().__init__()

        self.app = gtk_application
        self.clips_supported = services.clips_supported

    def get_settings(self, gio_settings_keyname):
        return self.app.gio_settings.get_value(gio_settings_keyname).get_strv()

    def clipboard_changed(self, clipboard, event):

        print("\n")
        print("skip_event:", self.skip_event)
        print("active app:", self.get_active_app()[0])
        print("selection owner:", event.owner)
        print("reason:", event.reason.value_name)
        print("event type:", event.type.value_name)
        print("receiving window:", event.window)
        print("selection_time:", event.selection_time)
        print("timestamp:", event.time)
        print("send_event:", event.send_event)

        if self.skip_event >= 1:
            self.skip_event = 0

        if self.skip_event == 0 and event.owner is not None and event.reason == Gdk.OwnerChange.NEW_OWNER and self.get_active_app()[0] not in self.get_settings("blacklist-apps"):
            created = datetime.now()
            clipboard_contents = self.get_clipboard_contents(clipboard, event)
            if clipboard_contents is not None:
                target, content, thumbnail, file_extension, additional_desc, content_type = clipboard_contents
                source_app, source_icon = self.get_active_app()
                if source_app not in self.get_settings("protected-apps"):
                    protected = "no"
                else:
                    protected = "yes"
                # reset skip_event state to false for next event    
                self.skip_event = 0
                return target, content, source_app, source_icon, created, protected, thumbnail, file_extension, content_type
        else:
            # set skip_event state to true for next event is new_owner_change event when clipboard is taken over by another app
            self.skip_event += 1
            print("clipboard event ignored:", self.skip_event)


    def get_clipboard_contents(self, clipboard, event):
        
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
                        if "WPS" in self.get_active_app()[0] and not "WPS" in supported_target[2]:
                            proceed = False

                        if "Libre" in self.get_active_app()[0] and not "Libre" in supported_target[2]:
                            proceed = False

                        if "WPS Spreadsheets" in supported_target[2] or "LibreOffice Calc" in supported_target[2]:
                            target = Gdk.Atom.intern('text/html', False)

                        if "WPS Writer" in supported_target[2] or "LibreOffice Writer" in supported_target[2]:
                            target = Gdk.Atom.intern('text/richtext', False)

                        if "LibreOffice Impress" in supported_target[2]:
                            target = Gdk.Atom.intern('application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)"', False)

                        if "text/plain;charset=utf-8" in supported_target[0] and "color" in supported_target[3]:
                            if self.app.utils.isValidColorCode(content.get_text().strip()):
                                content_type = "color/" + self.app.utils.isValidColorCode(content.get_text().strip())[1]
                            else:
                                proceed = False

                        if "text/plain;charset=utf-8" in supported_target[0] and "url" in supported_target[3]:
                            if self.app.utils.isValidURL(content.get_text().strip()):
                                content_type = "url/" + content.get_text().split(":")[0]
                            else:
                                proceed = False

                        # if "image/png" in supported_target[0] and "files" in supported_target[3]:
                        #     if len(content.get_text().split("\n")) > 1:
                        #         proceed = False

                        if proceed:
                            if thumbnail:
                                thumbnail = clipboard.wait_for_contents(Gdk.Atom.intern('image/png', False))
                            else:
                                thumbnail = None

                            clip_saved = True

                            return target, content, thumbnail, file_extension, additional_desc, content_type

    def get_active_app(self):
        matcher = Bamf.Matcher()
        screen = Wnck.Screen.get_default()
        screen.force_update()

        # if matcher.get_active_window() is None:
        #     active_win = screen.get_active_window()
        # else:
        #     active_win = matcher.get_active_window()

        active_win = matcher.get_active_window()
        if active_win is not None:
            active_app = matcher.get_application_for_window(active_win)
            if active_app is not None:
                source_app = active_app.get_name().split(" – ")[-1] #some app's name are shown with current document name so we split it and get the last part only
                source_icon = active_app.get_icon()
        else: 
            source_app = screen.get_active_workspace().get_name() # if no active window, fallback to workspace name
            source_icon = 'preferences-desktop-wallpaper' 

        return source_app, source_icon

    def clip_to_clipboard(self, clipboard_target, file):
        import subprocess
        subprocess.Popen(['xclip', '-selection', 'clipboard', '-target', clipboard_target, '-i', file])
