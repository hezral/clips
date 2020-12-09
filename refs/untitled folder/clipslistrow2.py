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
from gi.repository import Gtk, Gdk, Pango

class ClipsListRow2(Gtk.ListBoxRow):
    def __init__(self, data):
        super().__init__()

        #initialize imports

        
        #grid rows
        grid = Gtk.Grid()
        grid.props.column_spacing = 12
        grid.props.row_spacing = 3
        grid.props.margin = 10
        grid.props.margin_bottom = grid.props.margin_top = 10

        item_icon = Gtk.Image.new_from_icon_name("text-html", Gtk.IconSize.DIALOG)
        item_icon.set_size_request(64, 64)
        
        BUTTONS_OVERLAY_CSS = """
        .button-view {
            color: #FFFFFF;
            border: none;
            border-radius: 50%;
            padding: 5px;
            box-shadow: none;
            background-color: rgba(0,0,0,0.2);
        }

        .button-view:hover {
            background: @colorAccentOpaque;
            color: #FFFFFF;
            border: none;
        }

        .transition {
            transition: 200ms;
            transition-timing-function: ease;
        }
        """

        btn_css = Gtk.CssProvider()
        btn_css.load_from_data(bytes(BUTTONS_OVERLAY_CSS.encode()))
        
        btn_view = Gtk.Button().new_from_icon_name("window-maximize-symbolic", Gtk.IconSize.MENU)
        btn_view.get_style_context().add_provider(btn_css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        btn_view.get_style_context().add_class("button-view")
        btn_view.get_style_context().remove_class("button")
        btn_view.get_style_context().add_class("transition")
        btn_view.props.can_focus = False
        #btn_view.props.margin = 8
        btn_view.props.halign = Gtk.Align.CENTER
        btn_view.props.valign = Gtk.Align.CENTER
        btn_view.props.can_default = True
        
        item_content = Gtk.Label(data)
        item_content.get_style_context().add_class("h3")
        item_content.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        item_content.set_lines(1)
        item_content.set_single_line_mode(True)
        item_content.set_max_width_chars(60)

        overlay = Gtk.Overlay()
        overlay.props.can_focus = False
        overlay.props.halign = Gtk.Align.CENTER
        overlay.add(btn_view)
        #overlay.add(item_icon)
        #overlay.add(item_content)
        #overlay.props.width_request = 16
        #overlay.props.height_request = 16
        overlay.show_all()    

        grid.attach(overlay, 2, 0, 1, 1)
        grid.attach(item_icon, 0, 0, 1, 1)
        grid.attach(item_content, 1, 0, 1, 1)
        self.add(grid)
        self.show_all()

