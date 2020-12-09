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
from gi.repository import Gtk, Gdk

class ClipboardRowData(Gtk.ListBoxRow):
    def __init__(self, data):
        super(ClipboardRowData, self).__init__()
        self.data = data
        self.add(Gtk.Label(data))

class Clips(Gtk.ApplicationWindow):

    def __init__(self):
        Gtk.ApplicationWindow.__init__(self, title="Clips", resizable=False, border_width=6)
        
        #set window style, size
        self.get_style_context().add_class("rounded")
        self.set_default_size(640, 480)

        #set theme to light only
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", False)

        #set titlebar
        self.titlebar = Gtk.HeaderBar()
        self.titlebar.set_size_request(-1,-1)
        self.titlebar.props.title = "Clips"
        self.titlebar.set_show_close_button(True)
        #self.titlebar.has_subtitle = False
        self.titlebar_style_context = self.titlebar.get_style_context()
        self.titlebar_style_context.add_class(Gtk.STYLE_CLASS_FLAT)
        #self.titlebar_style_context.add_class("default-decoration")
        self.set_titlebar(self.titlebar)

        #table = Gtk.Table(3, 2)

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.entry = Gtk.Entry()
        self.image = Gtk.Image.new_from_icon_name("process-stop", Gtk.IconSize.MENU)

        box_outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(box_outer)

        listbox_2 = Gtk.ListBox()
        items = 'This is a sorted ListBox Fail'.split()

        for item in items:
            listbox_2.add(ClipboardRowData(item))

        def sort_func(row_1, row_2, data, notify_destroy):
            return row_1.data.lower() > row_2.data.lower()

        def filter_func(row, data, notify_destroy):
            return False if row.data == 'Fail' else True

        listbox_2.set_sort_func(sort_func, None, False)
        listbox_2.set_filter_func(filter_func, None, False)

        listbox_2.connect('row-activated', self.on_row_activated)

        box_outer.pack_start(listbox_2, True, True, 0)
        listbox_2.show_all()


    def on_row_activated(self, listbox_widget, row):
        print(row.data)

    def copy_text(self, widget):
        self.clipboard.set_text(self.entry.get_text(), -1)

    def paste_text(self, widget):
        text = self.clipboard.wait_for_text()
        if text is not None:
            self.entry.set_text(text)
        else:
            print("No text on the clipboard.")

    def copy_image(self, widget):
        if self.image.get_storage_type() == Gtk.ImageType.PIXBUF:
            self.clipboard.set_image(self.image.get_pixbuf())
        else:
            print("No image has been pasted yet.")

    def paste_image(self, widget):
        image = self.clipboard.wait_for_image()
        if image is not None:
            self.image.set_from_pixbuf(image)

win = Clips()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()