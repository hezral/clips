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


import gi
gi.require_version('Gtk', '3.0')
gi.require_version("Wnck", "3.0")
gi.require_version("Bamf", "3")
from gi.repository import Gtk, Gdk, Bamf, Wnck, Gio

from datetime import datetime
import signal
import sys
import os



# list of excluded apps by default
exclude_list = ('Wingpanel',
                'Plank',)

class ClipboardManager():

    #setup supported clip types
    richtext_target = Gdk.Atom.intern('text/richtext', False)
    rtf_target = Gdk.Atom.intern('text/rtf', False)
    html_target = Gdk.Atom.intern('text/html', False)
    image_target = Gdk.Atom.intern('image/png', False)
    text_target = Gdk.Atom.intern('text/plain', False)
    uri_target = Gdk.Atom.intern('x-special/gnome-copied-files', False)
    internet_target = "uri/internet"
    file_target = "uri/filemanager"
    hexcolor_target = "color/hex"

    #targets = (uri_target, image_target, html_target, richtext_target, text_target, internet_target, file_target, hexcolor_target)

    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    def __init__(self, gtk_application=None):
        super().__init__()

        self.app = gtk_application
        self.blacklist_apps = self.app.gio_settings.get_value("blacklist-apps").get_strv()

    def clipboard_changed(self, clipboard, event):
        date_created = datetime.now()
        target, content = self.get_clipboard_contents(clipboard, event)
        source_app, source_icon, protected = self.get_active_app()
        return target, content, source_app, source_icon, date_created, protected

    def get_clipboard_contents(self, clipboard, event):

        if self.clipboard.wait_is_target_available(self.uri_target):
            target_type = self.uri_target
            content = self.clipboard.wait_for_contents(self.uri_target)

        elif self.clipboard.wait_is_target_available(self.image_target):
            target_type = self.image_target 
            content = self.clipboard.wait_for_image()

        elif self.clipboard.wait_is_target_available(self.html_target) or self.clipboard.wait_is_target_available(self.html_target) and self.clipboard.wait_is_target_available(self.image_target):
            target_type = self.html_target
            content = self.clipboard.wait_for_contents(self.html_target)

        elif self.clipboard.wait_is_target_available(self.richtext_target):
            target_type = self.richtext_target
            content = self.clipboard.wait_for_contents(self.richtext_target)

        elif self.clipboard.wait_is_target_available(self.text_target):
            target_type = self.text_target
            content = self.clipboard.wait_for_text().strip() #strip any whitespace in start/end of text

        else:
            target_type = None
            content = None

        return target_type, content

    def get_active_app(self):

        # using Bamf
        matcher = Bamf.Matcher()
        active_win = matcher.get_active_window()
        screen = Wnck.Screen.get_default()
        screen.force_update()

        if active_win is not None:
            active_app = matcher.get_application_for_window(active_win)
            if active_app is not None:
                source_app = active_app.get_name().split(" – ")[-1] #some app's name are shown with current document name so we split it and get the last part only
                source_icon = active_app.get_icon()

        else: 
            source_app = screen.get_active_workspace().get_name() # if no active window, fallback to workspace name
            source_icon = 'preferences-desktop-wallpaper' 
    
        protected = "no"

        
        print(__file__.split("/")[-1], "blacklist_apps", self.blacklist_apps)

        return source_app, source_icon, protected

    def clip_to_clipboard(self):
        pass
