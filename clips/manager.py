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

class ClipsManager(GObject.GObject):
    def __init__(self):
        super().__init__()
        
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self.html_target = Gdk.Atom.intern('text/html', False)
        self.image_target = Gdk.Atom.intern('image/png', False)
        self.text_target = Gdk.Atom.intern('text/plain', False)
        self.uri_target = Gdk.Atom.intern('x-special/gnome-copied-files', False)

        def target_check():
          #print('targets checked')
          #print("Current clipboard offers formats: \n" + str(self.clipboard.wait_for_targets()[1]))
          #self.clipboard.wait_is_image_available()
          #self.clipboard.wait_is_rich_text_available()
          print(self.clipboard.wait_is_target_available(self.image_target))
          #self.clipboard.wait_is_text_available()
          #self.clipboard.wait_is_uris_available()
          return

        def clipboard_changed(self, event):
          target_check()
          #print(type(event))
          #print(dir(event))
          #print(datetime.now(tz=None))
          #print("Current clipboard offers formats: \n" + str(self.wait_for_targets()[1]))
          #print(self.wait_for_contents(target).get_data().decode("utf-8")) #need to decode from bytes to string for html/text targets

        self.clipboard.connect("owner-change", clipboard_changed)

clips = ClipsManager()
# just for debugging at CLI to enable CTRL+C quit
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit) 
Gtk.main()

# request_contents
# request_image
# request_rich_text
# request_targets
# request_text
# request_uris

# wait_for_contents
# wait_for_image
# wait_for_rich_text
# wait_for_targets
# wait_for_text
# wait_for_uris

