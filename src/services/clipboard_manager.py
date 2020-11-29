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
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, GObject, Pango
gi.require_version("Wnck", "3.0")
from gi.repository import Wnck
gi.require_version("Bamf", "3")
from gi.repository import Bamf

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
    html_target = Gdk.Atom.intern('text/html', False)
    image_target = Gdk.Atom.intern('image/png', False)
    text_target = Gdk.Atom.intern('text/plain', False)
    uri_target = Gdk.Atom.intern('x-special/gnome-copied-files', False)

    targets = (uri_target, image_target, html_target, richtext_target, text_target)

    def __init__(self):
        super().__init__()
        
        #create clipboard
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        # #debug flag
        #self.debugflag = debugflag
        # if self.debugflag:
        #     self.debug()
        #     # run function everytime clipboard is updated
        #     self.clipboard.connect("owner-change", self.clipboard_changed)

    def clipboard_changed(self, clipboard, event):
        date_created = datetime.now()
        target, content = self.get_clipboard_contents(clipboard, event)
        app_name, app_icon = self.get_active_app()
        return target, content, app_name, app_icon, date_created

    def get_clipboard_contents(self, clipboard, event):

        if self.clipboard.wait_is_target_available(self.uri_target):
            target_type = self.uri_target
            content = self.clipboard.wait_for_contents(self.uri_target)

        elif self.clipboard.wait_is_target_available(self.image_target):
            target_type = self.image_target 
            content = self.clipboard.wait_for_image()

        elif self.clipboard.wait_is_target_available(self.richtext_target):
            target_type = self.richtext_target
            content = self.clipboard.wait_for_contents(self.richtext_target)

        elif self.clipboard.wait_is_target_available(self.html_target):
            target_type = self.html_target
            content = self.clipboard.wait_for_contents(self.html_target)

        elif self.clipboard.wait_is_target_available(self.text_target):
            target_type = self.text_target
            content = self.clipboard.wait_for_text()

        else:
            target_type = None
            content = None

        return target_type, content

    def get_active_app(self):

        # using Bamf
        matcher = Bamf.Matcher()
        active_win = matcher.get_active_window()
        
        if active_win is not None:
            active_app = matcher.get_application_for_window(active_win)
            app_name = active_app.get_name()
            app_icon = active_app.get_icon()
        else: 
            screen = Wnck.Screen.get_default()
            screen.force_update()
            app_name = screen.get_active_workspace().get_name() # if no active window, fallback to workspace name
            app_icon = 'preferences-desktop-wallpaper' 
    
        return app_name, app_icon

    # def set_clipboard_contents():
    #     pass

    # def debug(self):
    #     self.label = Gtk.Label()
    #     self.label.props.max_width_chars = 100
    #     self.label.props.wrap = True
    #     self.label.props.wrap_mode = Pango.WrapMode.CHAR
    #     self.label.props.lines = 3
    #     #self.label.props.single_line_mode = True
    #     self.label.props.ellipsize = Pango.EllipsizeMode.END
    #     self.image = Gtk.Image.new_from_icon_name("image-x-generic", Gtk.IconSize.DIALOG)
    #     self.window = Gtk.Window(title="Clips Debug Window") #debug window to see contents displayed in Gtk.Window
    #     self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    #     self.box.pack_start(self.image, True, True, 0)
    #     self.box.pack_start(self.label, True, True, 0)
    #     self.window.set_border_width(6)
    #     self.window.add(self.box)
    #     self.window.show_all()
    #     self.window.connect("destroy", Gtk.main_quit)
    #     # just for debugging at CLI to enable CTRL+C quit
    #     GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit) 

    # def debug_log(self, clipboard, target, content):
    #     #print("Current clipboard offers formats: \n" + str(self.clipboard.wait_for_targets()[1]))
    #     if content is not None:
    #         if target == self.image_target:
    #             self.image.set_from_pixbuf(content)
    #         elif target == self.uri_target:
    #             self.label.set_text(content)
    #         elif target == self.html_target:
    #             self.label.set_text(content)
    #         elif target == self.text_target:
    #             self.label.set_text(content)
    #         else:
    #             print('Unsupported target type')
    #     else:
    #         print("No content in the clipboard")

# clips = ClipsManager(debugflag=True)
# Gtk.main()