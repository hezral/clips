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
gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Granite


class ClipsHeaderBar(Gtk.HeaderBar):
    def __init__(self):
        super().__init__()

        self.set_show_close_button(False)
        self.set_has_subtitle(False)
        self.props.border_width = 0


        #headerbar search field
        search_entry = Gtk.SearchEntry()
        search_entry.props.placeholder_text = "Search Something\u2026"
        search_entry.set_hexpand(True)   
        search_entry.set_halign(Gtk.Align.FILL)
        
        SEARCH_ENTRY_CSS = """
        .large-search-entry {
            font-size: 100%;
        }
        """
        search_text_provider = Gtk.CssProvider()
        search_text_provider.load_from_data(bytes(SEARCH_ENTRY_CSS.encode()))
        search_entry.get_style_context().add_provider(search_text_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        search_entry.get_style_context().add_class("large-search-entry")

        self.settings_icon = Gtk.Button.new_from_icon_name("open-menu", Gtk.IconSize.LARGE_TOOLBAR)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.add(search_entry)

        search_entry.get_style_context().add_class("large-search-entry")

        #------ view switch ----#
        #icon_theme = Gtk.IconTheme.get_default()
        #icon_theme.prepend_search_path(os.path.join(self.modulepath, "..", "data/icons"))
        view_switch = Granite.ModeSwitch.from_icon_name("edit-copy", "preferences-system-symbolic")
        view_switch.props.primary_icon_tooltip_text = "Ghoster"
        view_switch.props.secondary_icon_tooltip_text = "Settings"
        view_switch.props.valign = Gtk.Align.CENTER
        view_switch.props.name = "viewswitch"
        #view_switch.bind_property("active", settings_view, "visible", GObject.BindingFlags.BIDIRECTIONAL)


        #headerbar construct
        self.set_custom_title(box)
        #self.pack_end(view_switch)
        self.show_all()