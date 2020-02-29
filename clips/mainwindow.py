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
from gi.repository import Gtk
from widgets.headerbar import ClipsHeaderBar
from widgets.listboxrow import ClipsListRow
from widgets.infoview import ClipsInfoView
from widgets.listbox import ClipsListBox
from widgets.clipsview import ClipsView


class ClipsWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #applicationwindow construct
        self.props.title = "Clips"
        self.props.resizable = False
        self.props.border_width = 0
        self.set_icon_name("com.github.hezral.clips")
        self.get_style_context().add_class("rounded")
        self.set_default_size(360, 480)
        self.set_keep_above(True)
        self.props.window_position = Gtk.WindowPosition.CENTER
        
        #applicationwindow theme
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)

        listbox_view = ClipsListBox()
        #initial launch add some rows
        welcome_text = "Welcome to Clips"
        welcome_image = Gtk.Image.new_from_icon_name("system-os-installer", Gtk.IconSize.MENU)
        welcome_image.set_pixel_size(96)
        listbox_view.add(ClipsListRow(welcome_image))
        listbox_view.add(ClipsListRow(welcome_text))
        listbox_view.add(ClipsListRow(welcome_image))
        
        # clips_view
        self.clips_view = ClipsView(listbox_view)

        #welcome_view
        info_view = ClipsInfoView("No Clips Found","Start Copying Stuffs", "system-os-installer")
        
        #search_view
        #settings_view

        #stack_view
        stack_view = Gtk.Stack()
        stack_view.add_named(self.clips_view, "clips_view")
        stack_view.add_named(info_view, "info_view")
        stack_view.set_visible_child_name("clips_view")

        def toggle_stack(self):
            if stack_view.get_visible_child_name() == 'clips_view':
                stack_view.set_visible_child_full("info_view",Gtk.StackTransitionType.CROSSFADE)
            else:
                stack_view.set_visible_child_full("clips_view",Gtk.StackTransitionType.CROSSFADE)

        #headerbar construct
        header_bar = ClipsHeaderBar()        
        header_bar.settings_icon.connect('clicked',toggle_stack)

        self.set_titlebar(header_bar)

        self.add(stack_view)
        self.show()
        self.show_all()

        # hide toolbar buttons on all rows by iterating through all the child objects in listbox
        listbox_view.foreach(lambda child, data: child.hide_buttons(), None)
        #print(len(listbox_view))

    def check(self, widget, event):
        print(type(self.clips_view))

# app = ClipsWindow()
# app.connect("destroy", Gtk.main_quit)
# Gtk.main()