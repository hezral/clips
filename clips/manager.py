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

import threading
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject
from threading import Thread

class ClipsManager(GObject.GObject):
    def __init__(self):
        super().__init__()
        
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        def clipboard_changed(self, widget):
            html_target = Gdk.Atom.intern('text/html', False)

            

            print("Current clipboard offers formats: " + str(self.wait_for_targets()[1]))
            print(self.wait_for_contents(html_target).get_data())
            return

        def start():
            self.clipboard.connect("owner-change", clipboard_changed)
            return
        

        self.clipboard.connect("owner-change", clipboard_changed)

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

    # wait_is_image_available
  	# wait_is_rich_text_available
  	# wait_is_target_available
  	# wait_is_text_available
  	# wait_is_uris_available

clips = ClipsManager()
Gtk.main()

