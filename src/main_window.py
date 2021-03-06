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
import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Granite, GObject, Gdk
from views.info_view import InfoView
from views.clips_view import ClipsView
from views.settings_view import SettingsView

class ClipsWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.utils = self.props.application.utils

        #------ views ----#
        self.clips_view = ClipsView()
        self.info_view = InfoView("No Clips Found","Start Copying Stuffs", "system-os-installer")
        self.settings_view = SettingsView()
        self.settings_view.connect("notify::visible", self.on_view_visible)

        #------ stack ----#
        stack = Gtk.Stack()
        stack.props.name = "main-stack"
        stack.props.transition_type = Gtk.StackTransitionType.CROSSFADE
        stack.props.transition_duration = 150
        stack.add_named(self.clips_view, self.clips_view.get_name())
        stack.add_named(self.settings_view, self.settings_view.get_name())
        stack.add_named(self.info_view, self.info_view.get_name())

        #------ headerbar ----#
        self.set_titlebar(self.generate_headerbar())

        #------ main_view ----#
        main_view = Gtk.Grid()
        main_view.props.name = "main-view"
        main_view.attach(stack, 0, 0, 1, 1)
        main_view.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), 0, 1, 1, 1)
        # main_view.attach(self.generate_actionbar(), 0, 2, 1, 1)
        main_view.attach(self.generate_statusbar(), 0, 2, 1, 1)
        main_view.attach(self.generate_viewswitch(settings_view_obj=self.settings_view), 0, 2, 1, 1)

        #------ construct ----#
        self.props.title = "Clips"
        self.props.name = "main-window"
        self.props.border_width = 0
        self.props.window_position = Gtk.WindowPosition.CENTER
        self.get_style_context().add_class("rounded")
        #self.set_default_size(958, 450)
        self.set_size_request(880, 450)
        # self.set_size_request(640, 450)
        self.resize(958, 450)
        geometry = Gdk.Geometry()
        # setattr(geometry, 'base_height', 450)
        # setattr(geometry, 'base_width', 800)
        # self.set_geometry_hints(None, geometry, Gdk.WindowHints.BASE_SIZE)
        setattr(geometry, 'min_height', 450)
        setattr(geometry, 'min_width', 880)
        self.set_geometry_hints(None, geometry, Gdk.WindowHints.MIN_SIZE)
        # setattr(geometry, 'max_height', 1080)
        # setattr(geometry, 'max_width', 1888)
        # self.set_geometry_hints(None, geometry, Gdk.WindowHints.MAX_SIZE)
        # setattr(geometry, 'height_inc', 100)
        # setattr(geometry, 'width_inc', 100)
        # self.set_geometry_hints(None, geometry, Gdk.WindowHints.RESIZE_INC)
        #self.connect("window-state-event", self.on_maximized)
        #self.connect("notify::is-maximized", self.on_max)

        #self.set_keep_above(True)
        self.add(main_view)
        self.show_all()

        # this is for tracking window state flags for persistent mode
        self.state_flags_changed_count = 0
        self.active_state_flags = ['GTK_STATE_FLAG_NORMAL', 'GTK_STATE_FLAG_DIR_LTR']

    def generate_headerbar(self):
        #------ self.searchentry ----#
        self.searchentry = Gtk.SearchEntry()
        self.searchentry.props.placeholder_text = "Search Clips" #"Search Clips\u2026"
        self.searchentry.props.hexpand = True
        self.searchentry.props.name = "search-entry"

        self.searchentry.connect("focus-in-event", self.on_searchbar_activate, "in")
        self.searchentry.connect("focus-out-event", self.on_searchbar_activate, "out")
        # self.searchentry.connect_after("delete-text", self.on_delete_text, "delete")
        self.searchentry.connect("icon-press", self.on_quicksearch_activate)
        
        self.searchentry.connect("search-changed", self.on_search_changed)

        quicksearchbar = Gtk.Grid()
        quicksearchbar.props.name = "search-quick"
        quicksearchbar.props.margin_top = 8
        quicksearchbar.props.column_spacing = 2
        quicksearchbar.props.row_spacing = 2
        quicksearchbar.props.hexpand = True

        images = Gtk.Button(label="images")
        images.connect("clicked", self.on_quicksearch)
        texts = Gtk.Button(label="texts")
        texts.connect("clicked", self.on_quicksearch)

        quicksearchbar.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), 0, 0, 1, 1)
        quicksearchbar.attach(images, 0, 1, 1, 1)
        quicksearchbar.attach(texts, 1, 1, 1, 1)

        revealer = Gtk.Revealer()
        revealer.props.name = "search-revealer"
        revealer.add(quicksearchbar)

        #------ searchbar ----#
        searchbar = Gtk.Grid()
        searchbar.props.name = "search-bar"
        searchbar.attach(self.searchentry, 0, 0, 1, 1)
        # searchbar.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), 0, 1, 1, 1)
        searchbar.attach(revealer, 0, 1, 1, 1)

        headerbar = Gtk.HeaderBar()
        headerbar.props.show_close_button = False
        headerbar.props.has_subtitle = False
        headerbar.props.custom_title = searchbar
        #headerbar.add(searchbar)
        return headerbar

    def generate_statusbar(self):

        self.total_clips_label = Gtk.Label("Clips: {total}".format(total=self.props.application.total_clips))

        infobar = Gtk.Grid()
        infobar.props.name = "app-statusbar"
        infobar.props.halign = Gtk.Align.START
        infobar.props.valign = Gtk.Align.CENTER
        infobar.props.margin_left = 3
        infobar.attach(self.total_clips_label, 0, 0, 1, 1)
        return infobar

    def generate_actionbar(self):
        clipstoggle_action = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral.clips-enabled-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        clipstoggle_action.props.name = "app-action-enable"
        clipstoggle_action.props.has_tooltip = True
        clipstoggle_action.props.tooltip_text = "Clipboard Monitoring: Enabled"
        clipstoggle_action.state = "enabled"
        clipstoggle_action.get_style_context().add_class("app-action-enabled")
        clipstoggle_action.connect("clicked", self.on_clips_action, "enable")
        
        protecttoggle_action = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral.clips-protect-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        protecttoggle_action.props.name = "app-action-protect"
        protecttoggle_action.props.has_tooltip = True
        protecttoggle_action.props.tooltip_text = "Password Display/Monitoring: Enabled"
        protecttoggle_action.state = "enabled"
        protecttoggle_action.get_style_context().add_class("clips-action-enabled")
        protecttoggle_action.connect("clicked", self.on_clips_action, "protect")

        actionbar = Gtk.Grid()
        actionbar.props.name = "app-actionbar"
        actionbar.props.halign = Gtk.Align.START
        actionbar.props.valign = Gtk.Align.CENTER
        actionbar.props.margin_left = 3
        actionbar.attach(clipstoggle_action, 0, 0, 1, 1)
        actionbar.attach(protecttoggle_action, 1, 0, 1, 1)
        return actionbar

    def generate_viewswitch(self, settings_view_obj):
        view_switch = Granite.ModeSwitch.from_icon_name("com.github.hezral.clips-symbolic", "com.github.hezral.clips-settings-symbolic")
        # view_switch.props.primary_icon_tooltip_text = "Ghoster"
        # view_switch.props.secondary_icon_tooltip_text = "Settings"
        view_switch.props.valign = Gtk.Align.CENTER
        view_switch.props.halign = Gtk.Align.END
        view_switch.props.margin = 4
        view_switch.props.name = "view-switch"
        view_switch.bind_property("active", settings_view_obj, "visible", GObject.BindingFlags.BIDIRECTIONAL)

        
        # switch = [child for child in view_switch.get_children() if isinstance(child, Gtk.Switch)][0]
        # print("mode-switch", switch)
        # switch.set_size_request(-1, 32)
        # print(switch.get_allocated_height(), switch.get_allocated_width())
        return view_switch

    def on_country_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            country = model[tree_iter][0]
            print("Selected: country=%s" % country)

    def on_delete_text(self, searchentry, int1, int2, type):
        # searchbar = self.searchentry.get_parent()

        # revealer = utils.get_widget_by_name(widget=searchbar, child_name="search-revealer", level=0)
        # if revealer.get_child_revealed():
        #     revealer.set_reveal_child(False)

        # else:
        #     revealer.set_reveal_child(True)
        pass

    def on_quicksearch_activate(self, searchentry, iconposition, eventbutton):
        print(locals())
        searchbar = self.searchentry.get_parent()
        revealer = self.utils.get_widget_by_name(widget=searchbar, child_name="search-revealer", level=0)
        if revealer.get_child_revealed():
            revealer.set_reveal_child(False)
        else:
            revealer.set_reveal_child(True)

    def on_date_select(self, button):
        # searchbar = [child for child in self.get_children() if child.get_name() == "search-bar"][0]
        # calendar_dialog = utils.get_widget_by_name(widget=searchbar, child_name="search-calendar-dialog", level=0)
        # print(calendar_dialog)

        calendar_dialog = Gtk.Window(type=Gtk.WindowType.POPUP)
        calendar_dialog.props.name = "search-calendar-dialog"
        calendar_dialog.set_modal(True)
        calendar_dialog.set_transient_for(self)
        calendar_dialog.set_attached_to(button)
        calendar_dialog.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        
        calendar = Gtk.Calendar()
        calendar_dialog.add(calendar)
        calendar_dialog.show_all()

    def on_quicksearch(self, button):
        
        searchbar = [child for child in self.get_children() if child.get_name() == "search-bar"][0]
        self.searchentry = self.utils.get_widget_by_name(widget=searchbar, child_name="search-entry", level=0)

        if self.searchentry.props.text == "":
            self.searchentry.props.text = button.props.label
        else:
            self.searchentry.props.text = self.searchentry.props.text + ", " + button.props.label

    def on_searchbar_activate(self, searchentry, event, type):

        searchbar = self.searchentry.get_parent()
        revealer = self.utils.get_widget_by_name(widget=searchbar, child_name="search-revealer", level=0)

        if type == "in" and revealer.get_child_revealed() is False:
            self.searchentry.props.primary_icon_name = "quick-search"
            self.searchentry.props.primary_icon_tooltip_text = "Use quick search tags"
            self.searchentry.props.name = "search-entry-active"
            self.searchentry.props.primary_icon_activatable = True
            self.searchentry.props.primary_icon_sensitive = True
            # searchbar.props.has_tooltip = True
            # searchbar.props.tooltip_text = "Try these quick search tags"
        elif type == "out":
            self.searchentry.props.primary_icon_name = "system-search-symbolic"
            self.searchentry.props.name = "search-entry"

        # if revealer.get_child_revealed():
        #     revealer.set_reveal_child(False)
        #     #searchbar.props.has_tooltip = False

        # elif revealer.get_child_revealed() and type == "search":
        #     revealer.set_reveal_child(False)
        #     #searchbar.props.has_tooltip = False
        # else:
        #     revealer.set_reveal_child(True)
        #     #searchbar.props.has_tooltip = True
        #     #searchbar.props.tooltip_text = "Try these quick search tags"

    def on_search_changed(self, searchentry):
        self.searchentry.props.primary_icon_name = "system-search-symbolic"
        #print(locals())

    def on_view_visible(self, view, gparam=None, runlookup=None, word=None):
        
        stack = self.utils.get_widget_by_name(widget=self, child_name="main-stack", level=0)
        main_view = self.utils.get_widget_by_name(widget=self, child_name="main-view", level=0)

        if view.is_visible():
            self.current_view = "settings-view"
            print("on:settings")

        else:
            view.hide()
            self.current_view = "clips-view"
            print("on:settings-view > clips-view")

        # toggle css styling
        if self.current_view == "settings-view":
            stack.get_style_context().add_class("stack-settings")
            main_view.get_style_context().add_class("main_view-settings")
        else:
            stack.get_style_context().remove_class("stack-settings")
            main_view.get_style_context().remove_class("main_view-settings")

        stack.set_visible_child_name(self.current_view)

    def on_persistent_mode(self, widget, event):
        
        # state flags for window active state
        self.state_flags = self.get_state_flags().value_names
        # print(self.state_flags)
        if not self.state_flags == self.active_state_flags and self.state_flags_changed_count > 1:
            self.destroy()
        else:
            self.state_flags_changed_count += 1
            # print('state-flags-changed', self.state_flags_changed_count)

    def on_clips_action(self, button, action):
        
        app = self.props.application
        
        if action == "enable":

            if button.state == "enabled":
                button.props.tooltip_text = "Clipboard Monitoring: Disabled"
                app.clipboard_manager.clipboard.disconnect_by_func(app.cache_manager.update_cache)
            else:
                button.props.tooltip_text = "Clipboard Monitoring: Enabled"
                app.clipboard_manager.clipboard.connect("owner-change", app.cache_manager.update_cache, app.clipboard_manager)
        
        elif action == "protect":

            if button.state == "enabled":
                button.props.tooltip_text = "Password Display/Monitoring: Disabled"
            else:
                button.props.tooltip_text = "Password Display/Monitoring: Enabled"
            
        else:
            pass

        if button.state == "enabled":
            button.state = "disabled"
            button.get_style_context().add_class("clips-action-disabled")
            button.get_style_context().remove_class("clips-action-enabled")

        else:
            button.state = "enabled"
            button.get_style_context().add_class("clips-action-enabled")
            button.get_style_context().remove_class("clips-action-disabled")

    def update_total_clips_label(self, event):
        total_clips = int(self.total_clips_label.props.label.split(": ")[1])
        if event == "add":
            total_clips = total_clips + 1
        elif event == "delete":
            total_clips = total_clips - 1
        self.total_clips_label.props.label = "Clips: {total}".format(total=total_clips)
        





    def on_max(self, window, bool):
        if window.is_maximized():
            print("max")
        else:
            print("normal")
            # rectangle1 = Gdk.Rectangle()
            # setattr(rectangle1, 'height', 20)
            # setattr(rectangle1, 'width', 20)
            # self.clips_view.flowbox.size_allocate(rectangle1)
            # rectangle2 = Gdk.Rectangle()
            # setattr(rectangle2, 'height', 32)
            # setattr(rectangle2, 'width', 37)
            # self.size_allocate(rectangle2)
            # print(self.clips_view.flowbox.get_allocation())
            # self.clips_view.scrolled_window.set_size_request(1, 1)
            # self.clips_view.flowbox.set_size_request(580, -1)
            # self.clips_view.set_size_request(1, 1)
            # self.resize(900, 600)
            # self.resize(100,100)
            # for size in self.get_preferred_size():
            #     print(size.width, size.height)
            # self.clips_view.flowbox.set_size_request(648, 500)
            # self.clips_
            self.resize(800, 450)

    def on_maximized(self, window, eventwindowstate):
        
        if "GDK_WINDOW_STATE_MAXIMIZED" in eventwindowstate.changed_mask.value_names and len(eventwindowstate.changed_mask.value_names) == 1:
            print(eventwindowstate.changed_mask.value_names)
            self.resize(1, 1)

    def generate_searchbar(self):
        #------ self.searchentry ----#
        self.searchentry = Gtk.SearchEntry()
        self.searchentry.props.placeholder_text = "Search Clips" #"Search Clips\u2026"
        self.searchentry.props.hexpand = True
        self.searchentry.props.name = "search-entry"
        self.searchentry.props.primary_icon_activatable = True
        self.searchentry.props.primary_icon_sensitive = True

        self.searchentry.connect("focus-in-event", self.on_searchbar_activate, "in")
        self.searchentry.connect_after("delete-text", self.on_delete_text, "delete")
        self.searchentry.connect("icon-press", self.on_quicksearch_activate)
        self.searchentry.connect("focus-out-event", self.on_searchbar_activate, "out")

        #------ quicksearchbar ----#
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        country_store = Gtk.ListStore(str)
        countries = [
            "Austria",
            "Brazil",
            "Belgium",
            "France",
            "Germany",
            "Switzerland",
            "United Kingdom",
            "United States of America",
            "Uruguay",
        ]
        for country in countries:
            country_store.append([country])

        country_combo = Gtk.ComboBox.new_with_model(country_store)
        country_combo.connect("changed", self.on_country_combo_changed)
        renderer_text = Gtk.CellRendererText()
        country_combo.pack_start(renderer_text, True)
        country_combo.add_attribute(renderer_text, "text", 0)
        vbox.pack_start(country_combo, False, False, True)

        quicksearchbar = Gtk.Grid()
        quicksearchbar.props.name = "search-quick"
        quicksearchbar.props.column_spacing = 2
        quicksearchbar.props.margin_top = 3
        images = Gtk.Button(label="images")
        images.connect("clicked", self.on_quicksearch)
        texts = Gtk.Button(label="texts")
        texts.connect("clicked", self.on_quicksearch)

        calendar_btn = Gtk.Button(label="Date")
        calendar_btn.connect("clicked", self.on_date_select)

        quicksearchbar.attach(images, 0, 0, 1, 1)
        quicksearchbar.attach(texts, 1, 0, 1, 1)
        # quicksearchbar.attach(calendar_btn, 2, 0, 1, 1)

        #------ revealer ----#
        revealer = Gtk.Revealer()
        revealer.props.name = "search-revealer"
        revealer.add(quicksearchbar)

        #------ searchbar ----#
        searchbar = Gtk.Grid()
        searchbar.props.name = "search-bar"
        searchbar.attach(self.searchentry, 0, 0, 1, 1)
        searchbar.attach(revealer, 0, 1, 1, 1)

        return searchbar
