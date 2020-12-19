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
import utils


class ClipsWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.utils = self.props.application.utils

        #------ views ----#
        clips_view = ClipsView()
        info_view = InfoView("No Clips Found","Start Copying Stuffs", "system-os-installer")
        settings_view = SettingsView()
        settings_view.connect("notify::visible", self.on_view_visible)

        #------ stack ----#
        stack = Gtk.Stack()
        stack.props.name = "main-stack"
        stack.props.transition_type = Gtk.StackTransitionType.CROSSFADE
        stack.props.transition_duration = 150
        stack.add_named(clips_view, clips_view.get_name())
        stack.add_named(settings_view, settings_view.get_name())
        stack.add_named(info_view, info_view.get_name())

        #------ headerbar ----#
        #self.set_titlebar(self.generate_searchbar())
        self.set_titlebar(self.generate_headerbar())

        #------ main_view ----#
        main_view = Gtk.Grid()
        main_view.props.name = "main-view"
        main_view.attach(stack, 0, 0, 1, 1)
        main_view.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), 0, 1, 1, 1)
        main_view.attach(self.generate_actionbar(), 0, 2, 1, 1)
        main_view.attach(self.generate_viewswitch(settings_view_obj=settings_view), 0, 2, 1, 1)

        #------ construct ----#
        self.props.title = "Clips"
        self.props.name = "main-window"
        #self.props.resizable = False
        self.props.border_width = 0
        self.props.window_position = Gtk.WindowPosition.CENTER
        self.get_style_context().add_class("rounded")
        #self.set_default_size(600, 652)
        #self.set_size_request(600, 652)
        self.set_keep_above(True)
        self.add(main_view)
        self.show_all()

       # clips_view.hide_toolbar_buttons()

        # this is for tracking window state flags for persistent mode
        self.state_flags_changed_count = 0
        self.active_state_flags = ['GTK_STATE_FLAG_NORMAL', 'GTK_STATE_FLAG_DIR_LTR']

    def generate_searchbar(self):
        #------ searchentry ----#
        searchentry = Gtk.SearchEntry()
        searchentry.props.placeholder_text = "Search Clips" #"Search Clips\u2026"
        searchentry.props.hexpand = True
        searchentry.props.name = "search-entry"
        searchentry.props.primary_icon_activatable = True
        searchentry.props.primary_icon_sensitive = True

        searchentry.connect("focus-in-event", self.on_search_activate, "in")
        searchentry.connect_after("delete-text", self.on_delete_text, "delete")
        searchentry.connect("icon-press", self.on_quicksearch_activate)
        searchentry.connect("focus-out-event", self.on_search_activate, "out")

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
        searchbar.attach(searchentry, 0, 0, 1, 1)
        searchbar.attach(revealer, 0, 1, 1, 1)

        return searchbar

    def generate_headerbar(self):
        #------ searchentry ----#
        searchentry = Gtk.SearchEntry()
        searchentry.props.placeholder_text = "Search Clips" #"Search Clips\u2026"
        searchentry.props.hexpand = True
        searchentry.props.name = "search-entry"
        searchentry.props.primary_icon_activatable = True
        searchentry.props.primary_icon_sensitive = True

        searchentry.connect("focus-in-event", self.on_search_activate, "in")
        searchentry.connect("focus-out-event", self.on_search_activate, "out")
        # searchentry.connect_after("delete-text", self.on_delete_text, "delete")
        # searchentry.connect("icon-press", self.on_quicksearch_activate)
        
        searchentry.connect("search-changed", self.on_search_changed)

        quicksearchbar = Gtk.Grid()
        quicksearchbar.props.name = "search-quick"
        quicksearchbar.props.column_spacing = 2
        quicksearchbar.props.margin_top = 3
        images = Gtk.Button(label="images")
        images.connect("clicked", self.on_quicksearch)
        texts = Gtk.Button(label="texts")
        texts.connect("clicked", self.on_quicksearch)

        quicksearchbar.attach(images, 0, 0, 1, 1)
        quicksearchbar.attach(texts, 1, 0, 1, 1)

        #------ revealer ----#
        revealer = Gtk.Revealer()
        revealer.props.name = "search-revealer"
        revealer.add(quicksearchbar)

        #------ searchbar ----#
        searchbar = Gtk.Grid()
        searchbar.props.name = "search-bar"
        searchbar.attach(searchentry, 0, 0, 1, 1)
        searchbar.attach(revealer, 0, 1, 1, 1)

        headerbar = Gtk.HeaderBar()
        headerbar.props.show_close_button = False
        headerbar.props.has_subtitle = False
        headerbar.props.custom_title = searchbar
        return headerbar

    def generate_actionbar(self):
        icon_theme = Gtk.IconTheme.get_default()
        icon_theme.prepend_search_path(os.path.join(os.path.dirname(__file__), "..", "data", "icons"))

        clipstoggle_action = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral.clips-enabled-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        clipstoggle_action.props.name = "clips-action-enable"
        clipstoggle_action.props.has_tooltip = True
        clipstoggle_action.props.tooltip_text = "Clipboard Monitoring: Enabled"
        clipstoggle_action.state = "enabled"
        clipstoggle_action.get_style_context().add_class("clips-action-enabled")
        clipstoggle_action.connect("clicked", self.on_clips_action, "enable")
        
        protecttoggle_action = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral.clips-protect-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        protecttoggle_action.props.name = "clips-action-protect"
        protecttoggle_action.props.has_tooltip = True
        protecttoggle_action.props.tooltip_text = "Password Display/Monitoring: Enabled"
        protecttoggle_action.state = "enabled"
        protecttoggle_action.get_style_context().add_class("clips-action-enabled")
        protecttoggle_action.connect("clicked", self.on_clips_action, "protect")

        actionbar = Gtk.Grid()
        actionbar.props.name = "clips-actionbar"
        actionbar.props.halign = Gtk.Align.START
        actionbar.props.valign = Gtk.Align.CENTER
        actionbar.props.margin_left = 3
        actionbar.attach(clipstoggle_action, 0, 0, 1, 1)
        actionbar.attach(protecttoggle_action, 1, 0, 1, 1)
        return actionbar


    def generate_viewswitch(self, settings_view_obj):
        icon_theme = Gtk.IconTheme.get_default()
        icon_theme.prepend_search_path(os.path.join(os.path.dirname(__file__), "..", "data", "icons"))
        view_switch = Granite.ModeSwitch.from_icon_name("com.github.hezral.clips-symbolic", "preferences-system-symbolic")
        # view_switch.props.primary_icon_tooltip_text = "Ghoster"
        # view_switch.props.secondary_icon_tooltip_text = "Settings"
        view_switch.props.valign = Gtk.Align.CENTER
        view_switch.props.halign = Gtk.Align.END
        view_switch.props.margin = 4
        view_switch.props.name = "view-switch"
        view_switch.bind_property("active", settings_view_obj, "visible", GObject.BindingFlags.BIDIRECTIONAL)
        return view_switch

    def on_country_combo_changed(self, combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            country = model[tree_iter][0]
            print("Selected: country=%s" % country)

    def on_delete_text(self, searchentry, int1, int2, type):
        # searchbar = searchentry.get_parent()

        # revealer = utils.get_widget_by_name(widget=searchbar, child_name="search-revealer", level=0)
        # if revealer.get_child_revealed():
        #     revealer.set_reveal_child(False)

        # else:
        #     revealer.set_reveal_child(True)
        pass

    def on_quicksearch_activate(self, searchentry, iconposition, eventbutton):
        print(locals())
        searchbar = searchentry.get_parent()
        revealer = utils.get_widget_by_name(widget=searchbar, child_name="search-revealer", level=0)
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
        searchentry = utils.get_widget_by_name(widget=searchbar, child_name="search-entry", level=0)

        if searchentry.props.text == "":
            searchentry.props.text = button.props.label
        else:
            searchentry.props.text = searchentry.props.text + ", " + button.props.label

    def on_search_activate(self, searchentry, event, type):

        searchbar = searchentry.get_parent()
        revealer = utils.get_widget_by_name(widget=searchbar, child_name="search-revealer", level=0)

        if type == "in" and revealer.get_child_revealed() is False:
            searchentry.props.primary_icon_name = "preferences-system-power-symbolic"
            searchentry.props.primary_icon_tooltip_text = "Use quick search tags"
            searchentry.props.name = "search-entry-active"
            # searchbar.props.has_tooltip = True
            # searchbar.props.tooltip_text = "Try these quick search tags"
        elif type == "out":
            searchentry.props.primary_icon_name = "system-search-symbolic"
            searchentry.props.name = "search-entry"

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
        searchentry.props.primary_icon_name = "system-search-symbolic"
        #print(locals())

    def on_view_visible(self, view, gparam=None, runlookup=None, word=None):
        
        stack = utils.get_widget_by_name(widget=self, child_name="main-stack", level=0)
        main_view = utils.get_widget_by_name(widget=self, child_name="main-view", level=0)

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

        
