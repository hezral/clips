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
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject
from datetime import datetime
from urllib.parse import urlparse

class ClipsManager(GObject.GObject):
    def __init__(self):
        super().__init__()
        
        #create clipboard
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        #for debug only
        self.label = Gtk.Label()
        self.image = Gtk.Image.new_from_icon_name("image-x-generic", Gtk.IconSize.DIALOG)

        #setup supported clip types
        html_target = Gdk.Atom.intern('text/html', False)
        image_target = Gdk.Atom.intern('image/png', False)
        text_target = Gdk.Atom.intern('text/plain', False)
        uri_target = Gdk.Atom.intern('x-special/gnome-copied-files', False)

        def target_check():
          if self.clipboard.wait_is_target_available(image_target):
            image = self.clipboard.wait_for_image()
            if image is not None:
              self.image.set_from_pixbuf(image)
          elif self.clipboard.wait_is_target_available(uri_target):
            uri = self.clipboard.wait_for_contents(uri_target)
            if uri is not None:
              pass
          elif self.clipboard.wait_is_target_available(html_target):
            target_type = html_target
          elif self.clipboard.wait_is_target_available(text_target):
            target_type = text_target
            text = self.clipboard.wait_for_text()
            if text is not None:
                self.label.set_text(text)
            else:
                print("No text on the clipboard.")
          else:
            pass
          #for debug only
          print("Current clipboard offers formats: \n" + str(self.clipboard.wait_for_targets()[1]))
          return target_type

        def clipboard_changed(clipboard, event):
          target = target_check()
          print(datetime.now(tz=None))
          print(target)
          print(clipboard.wait_for_contents(target).get_data().decode("utf-8")) #need to decode from bytes to string for html/text targets

        # run function everytime a clipboard is changed
        self.clipboard.connect("owner-change", clipboard_changed)

        self.window = Gtk.Window()
        self.window.set_border_width(6)
        #self.window.add(self.label)
        self.window.add(self.image)
        self.window.show_all()
        self.window.connect("destroy", Gtk.main_quit)
        

clips = ClipsManager()
# just for debugging at CLI to enable CTRL+C quit
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit) 
Gtk.main()



