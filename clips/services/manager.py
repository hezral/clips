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
import hashlib
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject, GdkPixbuf, Pango
from datetime import datetime
from urllib.parse import urlparse

class ClipsManager():
    def __init__(self):
        super().__init__()
        
        #debug flag
        debugflag = False
        if debugflag:
            self.debug()

        #create clipboard
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        #setup supported clip types
        self.html_target = Gdk.Atom.intern('text/html', False)
        self.image_target = Gdk.Atom.intern('image/png', False)
        self.text_target = Gdk.Atom.intern('text/plain', False)
        self.uri_target = Gdk.Atom.intern('x-special/gnome-copied-files', False)

        # run function everytime clipboard is updated
        #self.clipboard.connect("owner-change", self.clipboard_changed)

    def clipboard_changed(self, clipboard, event):
        target, content = self.get_clipboard_contents()
        print('copy')
        if debugflag:
            self.debug_log(clipboard, target, content)
        return target, content

    def get_clipboard_contents(self, clipboard, event):
        if self.clipboard.wait_is_target_available(self.image_target):
            target_type = self.image_target 
            content = self.clipboard.wait_for_image() #original image
            content.savev('/home/adi/Downloads/content.png', 'png', [], []) #save file
            thumbnail = content.scale_simple(content.get_width()//2,content.get_height()//2, GdkPixbuf.InterpType.BILINEAR) #create thumbnail
            content = thumbnail
        elif self.clipboard.wait_is_target_available(self.uri_target):
            target_type = self.uri_target
            content = self.clipboard.wait_for_contents(self.uri_target).get_data().decode("utf-8") #need to decode from bytes to string
            new_content=[]
            for i in content.splitlines():
                new_content.append(urlparse(i).path.replace('%20',' '))
            content = '\n'.join(new_content)
        elif self.clipboard.wait_is_target_available(self.html_target):
            target_type = self.html_target
            content = self.clipboard.wait_for_contents(self.html_target).get_data().decode("utf-8") #need to decode from bytes to string for html/text targets
            content = self.clipboard.wait_for_contents(self.text_target).get_data().decode("utf-8") #need to decode from bytes to string for html/text targets
        elif self.clipboard.wait_is_target_available(self.text_target):
            target_type = self.text_target
            content = self.clipboard.wait_for_text()
        else:
            target_type = None
            content = None
        return target_type, content

    def debug(self):
        self.label = Gtk.Label()
        self.label.props.max_width_chars = 100
        self.label.props.wrap = True
        self.label.props.wrap_mode = Pango.WrapMode.CHAR
        self.label.props.lines = 3
        #self.label.props.single_line_mode = True
        self.label.props.ellipsize = Pango.EllipsizeMode.END
        self.image = Gtk.Image.new_from_icon_name("image-x-generic", Gtk.IconSize.DIALOG)
        self.window = Gtk.Window(title="Clips Debug Window") #debug window to see contents displayed in Gtk.Window
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.box.pack_start(self.image, True, True, 0)
        self.box.pack_start(self.label, True, True, 0)
        self.window.set_border_width(6)
        self.window.add(self.box)
        self.window.show_all()
        self.window.connect("destroy", Gtk.main_quit)
        # just for debugging at CLI to enable CTRL+C quit
        GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit) 

    def debug_log(self, clipboard, target, content):
        #print(type(content))
        #print(type(content.splitlines()))
        #print(content.splitlines())
        self.content_checksum = get_checksum(content)
        print(self.content_checksum)
        print("Current clipboard offers formats: \n" + str(self.clipboard.wait_for_targets()[1]))
        if content is not None:
            if target == self.image_target:
                self.image.set_from_pixbuf(content)
            elif target == self.uri_target:
                self.label.set_text(content)
            elif target == self.html_target:
                self.label.set_text(content)
            elif target == self.text_target:
                self.label.set_text(content)
            else:
                print('Unsupported target type')
        else:
            print("No content in the clipboard")

    def get_checksum(self, data):
        md5sum = hashlib.md5()
        md5sum.update(data)
        checksum = md5sum.hexdigest()
        return checksum
        
    def set_clipboard_contents():
        pass

#clips = ClipsManager()
#Gtk.main()