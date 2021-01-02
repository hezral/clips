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

from gi.repository import Gdk

# Standard clipboard targets that won't be handled by Clips
excluded_targets = (Gdk.Atom.intern('TIMESTAMP', False), 
                    Gdk.Atom.intern('TARGETS', False), 
                    Gdk.Atom.intern('MULTIPLE', False), 
                    Gdk.Atom.intern('SAVE_TARGETS', False), 
                    Gdk.Atom.intern('STRING', False), 
                    Gdk.Atom.intern('UTF8_STRING', False), 
                    Gdk.Atom.intern('COMPOUND_TEXT', False), 
                    Gdk.Atom.intern('TEXT', False), )


#setup supported clip types
richtext_target = Gdk.Atom.intern('text/richtext', False)
html_target = Gdk.Atom.intern('text/html', False)
image_target = Gdk.Atom.intern('image/png', False)
text_target = Gdk.Atom.intern('text/plain', False)
uri_target = Gdk.Atom.intern('x-special/gnome-copied-files', False)
save_target = Gdk.Atom.intern('SAVE_TARGETS', False)

