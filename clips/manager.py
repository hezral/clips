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
        
        #debug flag
        debugflag = True

        #create clipboard
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        #for debug only
        self.label = Gtk.Label()
        self.label.set_line_wrap(True)
        self.image = Gtk.Image.new_from_icon_name("image-x-generic", Gtk.IconSize.DIALOG)

        #setup supported clip types
        html_target = Gdk.Atom.intern('text/html', False)
        image_target = Gdk.Atom.intern('image/png', False)
        text_target = Gdk.Atom.intern('text/plain', False)
        uri_target = Gdk.Atom.intern('x-special/gnome-copied-files', False)

        def get_contents():
          if self.clipboard.wait_is_target_available(image_target):
            target_type = image_target 
            content = self.clipboard.wait_for_image()
          elif self.clipboard.wait_is_target_available(uri_target):
            target_type = uri_target
            content = self.clipboard.wait_for_contents(uri_target)
          elif self.clipboard.wait_is_target_available(html_target):
            target_type = html_target
            content = self.clipboard.wait_for_contents(html_target).get_data().decode("utf-8") #need to decode from bytes to string for html/text targets
          elif self.clipboard.wait_is_target_available(text_target):
            target_type = text_target
            content = self.clipboard.wait_for_text(text_target).get_data().decode("utf-8") #need to decode from bytes to string for html/text targets
          else:
            target_type = None
            content = None
          return target_type, content

        def debug():
          # debug window to see contents displayed in Gtk.Window
          self.window = Gtk.Window(title="Clips Debug Window")
          self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
          self.window.set_border_width(6)
          self.window.add(self.label)
          self.window.show_all()
          self.window.connect("destroy", Gtk.main_quit)
          # just for debugging at CLI to enable CTRL+C quit
          GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit) 

        def debug_log(clipboard, target, content):
          #print(datetime.now(tz=None))
          #print("Current clipboard offers formats: \n" + str(self.clipboard.wait_for_targets()[1]))
          if content is not None:
            if target == image_target:
              print('1')
              self.image.set_from_pixbuf(content)
            elif target == uri_target:
              print('2')
              self.label.set_text(urlparse(content))
            elif target == html_target:
              print('3')
              self.label.set_text(content)
            elif target == text_target:
              print('4')
              self.label.set_text(content)
            else:
              print('0')
              pass
          else:
            print("No content in the clipboard")
            pass

        def clipboard_changed(clipboard, event):
          target, content = get_contents()
          if debugflag:
            debug_log(clipboard, target, content)

        if debugflag:
          debug()

        # run function everytime clipboard is updated
        self.clipboard.connect("owner-change", clipboard_changed)

clips = ClipsManager()
Gtk.main()