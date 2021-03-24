#!/usr/bin/env python3

'''
    Copyright 2018 Adi Hezral (hezral@gmail.com)
    This file is part of Clips ("Application").
    The Application is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    The Application is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this Application.  If not, see <http://www.gnu.org/licenses/>.
'''

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio,  GObject


#------------------CLASS-SEPARATOR------------------#


class SettingsView(Gtk.Grid):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #-- object ----#
        gio_settings = Gio.Settings(schema_id="com.github.hezral.clips")
        gtk_settings = Gtk.Settings().get_default()

        #------ theme switch ----#
        theme_switch = SubSettings(type="switch", name="theme-switch", label="Switch between Dark/Light theme", sublabel=None, separator=True)
        theme_switch.switch.bind_property("active", gtk_settings, "gtk-application-prefer-dark-theme", GObject.BindingFlags.SYNC_CREATE)
        gio_settings.bind("prefer-dark-style", theme_switch.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        #------ persistent mode ----#
        persistent_mode = SubSettings(type="switch", name="persistent-mode", label="Persistent mode", sublabel="Stays open and updates as new clips added",separator=True)
        persistent_mode.switch.connect_after("notify::active", self.on_switch_activated)
        gio_settings.bind("persistent-mode", persistent_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)
        
        #------ sticky mode ----#
        sticky_mode = SubSettings(type="switch", name="sticky-mode", label="Sticky mode", sublabel="Displayed on all workspaces",separator=False)
        sticky_mode.switch.connect_after("notify::active", self.on_switch_activated)
        gio_settings.bind("sticky-mode", sticky_mode.switch, "active", Gio.SettingsBindFlags.DEFAULT)

        display_behaviour_settings = SettingsGroup("Display & Behaviour", (theme_switch, persistent_mode, sticky_mode))

        #-- SettingsView construct--------#
        self.props.name = "settings-view"
        self.get_style_context().add_class(self.props.name)
        self.props.expand = True
        self.props.margin = 20
        self.props.margin_top = 12
        self.props.row_spacing = 6
        self.props.column_spacing = 6
        self.attach(display_behaviour_settings, 0, 1, 1, 1)

    def on_switch_activated(self, switch, gparam):
        name = switch.get_name()

        window = self.get_toplevel()

        if self.is_visible():

            if name == "persistent-mode":
                if switch.get_active():
                    #print('state-flags-on')
                    window.disconnect_by_func(window.on_persistent_mode)
                else:
                    window.connect("state-flags-changed", window.on_persistent_mode)
                    #print('state-flags-off')
            if name == "sticky-mode":
                if switch.get_active():
                    window.stick()
                else:
                    window.unstick()




#------------------CLASS-SEPARATOR------------------#

class SettingsGroup(Gtk.Grid):
    def __init__(self, group_label, subsettings_list, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #-- settings grid --------#
        grid = Gtk.Grid()
        grid.props.margin = 8
        grid.props.hexpand = False
        grid.props.row_spacing = 8
        grid.props.column_spacing = 10

        i = 0
        for subsetting in subsettings_list:
            grid.attach(subsetting, 0, i, 1, 1)
            i += 1

        #-- subsettingsgroup frame --------#
        frame = Gtk.Frame()
        frame.props.name = "settings-group-frame"
        frame.add(grid)

        #-- subsettingsgroup label --------#
        label = Gtk.Label(group_label)
        label.props.name = "settings-group-label"
        label.props.halign = Gtk.Align.START
        label.props.margin_left = 4

        self.props.name = "settings-group"
        self.props.halign = Gtk.Align.CENTER
        self.props.row_spacing = 4
        self.attach(label, 0, 0, 1, 1)
        self.attach(frame, 0, 1, 1, 1)



class SubSettings(Gtk.Grid):
    def __init__(self, type, name, label, sublabel=None, separator=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
        #------ box--------#
        box = Gtk.VBox()
        box.props.spacing = 2
        box.props.hexpand = True

        #------ label--------#
        label = Gtk.Label(label)
        label.props.halign = Gtk.Align.START
        box.add(label)
        
        #------ sublabel--------#
        if sublabel is not None:
            sublabel = Gtk.Label(sublabel)
            sublabel.props.halign = Gtk.Align.START
            sublabel.get_style_context().add_class("settings-sub-label")
            box.add(sublabel)

        #------ switch--------#
        if type == "switch":
            self.switch = Gtk.Switch()
            self.switch.props.name = name
            self.switch.props.halign = Gtk.Align.END
            self.switch.props.valign = Gtk.Align.CENTER
            self.switch.props.hexpand = False

        if type == "spinbutton":
            self.spin_btn = Gtk.SpinButton().new_with_range(min=3, max=25, step=1)

        #------ separator --------#
        if separator:
            row_separator = Gtk.Separator()
            row_separator.props.hexpand = True
            row_separator.props.valign = Gtk.Align.CENTER
            self.attach(row_separator, 0, 2, 2, 1)
        
        #-- SubSettings construct--------#
        self.props.name = name
        self.props.hexpand = True
        self.props.row_spacing = 8
        self.props.column_spacing = 10
        self.attach(box, 0, 0, 1, 2)
        self.attach(self.switch, 1, 0, 1, 2)

    
