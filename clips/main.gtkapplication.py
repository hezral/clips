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
from gi.repository import Gtk, Gdk, Pango, GdkPixbuf
import infoview


class ClipsListRow(Gtk.ListBoxRow):
    def __init__(self, data):
        super(ClipsListRow, self).__init__()
        
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
        #overlay.show_all()    

        grid.attach(overlay, 2, 0, 1, 1)
        grid.attach(item_icon, 0, 0, 1, 1)
        grid.attach(item_content, 1, 0, 1, 1)
        self.add(grid)


class ClipsListRow2(Gtk.ListBoxRow):
    def __init__(self, data):
        super(ClipsListRow2, self).__init__()

        def generate_delete_button(self, delete_image):
            delete_button = Gtk.EventBox()
            delete_button.add(delete_image)
            delete_button.set_tooltip_text("Remove this clip")
            return delete_button

        thumb_clips_generic = Gtk.Image()
        thumb_clips_generic.props.valign = Gtk.Align.CENTER
        thumb_clips_generic.props.halign = Gtk.Align.CENTER
        thumb_clips_generic.props.pixel_size = 64
        #thumb_clips_generic.props.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size()

        delete_image = Gtk.Image.new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        icon = Gtk.Image.new_from_icon_name("utilities-terminal", Gtk.IconSize.DIALOG)
        vertical_box = Gtk.Box(Gtk.Orientation.VERTICAL, 6)

        delete_button = generate_delete_button(self, delete_image)
        name_label = Gtk.Label(data)

        vertical_box.add(name_label)

        row = Gtk.Box(Gtk.Orientation.HORIZONTAL, 12)
        row.props.margin = 12
        row.add(icon)
        row.add(vertical_box)

        row.pack_end(delete_button, False, False, False)
        self.add(row)
        self.data = data
        
    





class Clips(Gtk.ApplicationWindow):
    def __init__(self):
        #super(Clips, self).__init__(title="Clips", resizable=False, border_width=6)
        Gtk.ApplicationWindow.__init__(self, title="Clips", resizable=False, border_width=0)

        #set icon, window style, size
        self.set_icon_name("com.github.hezral.clips")
        self.get_style_context().add_class("rounded")
        self.set_default_size(400, 480)
        self.set_keep_above(True)
        self.props.window_position = Gtk.WindowPosition.CENTER
        
        #set application theme
        #settings = Gtk.Settings.get_default()
        #settings.set_property("gtk-application-prefer-dark-theme", False)

        #header
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        #headerbar.get_style_context().add_class(Gtk.STYLE_CLASS_FLAT)

        #search field
        search_entry = Gtk.SearchEntry()
        search_entry.props.placeholder_text = "Search Something\u2026"
        search_entry.set_hexpand(True)   
        search_entry.set_halign(Gtk.Align.FILL)
        search_entry.set_size_request(400,32)
        
        SEARCH_ENTRY_CSS = """
        .large-search-entry {
            font-size: 125%;
        }
        """
        search_text_provider = Gtk.CssProvider()
        search_text_provider.load_from_data(bytes(SEARCH_ENTRY_CSS.encode()))
        search_entry.get_style_context().add_provider(search_text_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        search_entry.get_style_context().add_class("large-search-entry")

        #box headerbar
        box = Gtk.HBox(orientation=Gtk.Orientation.HORIZONTAL)
        box.add(search_entry)
        
        #set header
        headerbar.add(box)
        #self.set_titlebar(box)
        self.set_titlebar(headerbar)

        def filter_func(row, data, notify_destroy):
            if(row.get_index() % 2 == 0):
                row.get_style_context().add_class("background")
            else:
                row.get_style_context().add_class("view")
            #return False if row.data == 'Fail' else True
            return True

        def on_row_activated(widget, row):
            print(row.get_index())
            print(row.data)


        #list box
        list_box = Gtk.ListBox()
        list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        list_box.set_activate_on_single_click(False)

        #rows
        items = """
        This is a sorted ListBox Fail
        This is a sorted ListBox Fail
        This is a sorted ListBox Fail
        """.split()
        for item in items:
            #list_box.add(ClipsListRow(item))
            list_box.add(ClipsListRow2(item))
        
        list_box.set_filter_func(filter_func, None, False)
        list_box.connect('row-activated', on_row_activated)

        #list box scrollwindow
        list_box_scrollwin = Gtk.ScrolledWindow()
        list_box_scrollwin.set_vexpand(True)
        list_box_scrollwin.add(list_box)
        list_box_scrollwin.show_all()

        #view for no clipboard items
        info_view = infoview.InfoView("No Clips Found","Start Copying Stuffs", "edit-find-symbolic")
        info_view.show_all()

        stack_view = Gtk.Stack()
        info_view.set_visible(True)
        list_box_scrollwin.set_visible(True)
        stack_view.add_named(list_box_scrollwin, "listbox")
        stack_view.add_named(info_view, "infoview")
        stack_view.set_visible_child_name("infoview")
        stack_view.show_all()

        #self.add(list_box_scrollwin)
        self.add(stack_view)

        self.show_all()


app = Clips()
app.connect("destroy", Gtk.main_quit)
Gtk.main()