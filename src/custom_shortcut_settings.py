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

# Original code ported from https://github.com/cassidyjames/ideogram/blob/main/src/Settings/CustomShortcutSettings.vala
# Ported to python. 
# Full credits goes to original author.

from gi.repository import Gio

#------------------CLASS-SEPARATOR------------------#

SCHEMA = "org.gnome.settings-daemon.plugins.media-keys"

KEY = "custom-keybinding"
RELOCATABLE_SCHEMA_PATH_TEMLPATE = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom%d/"

MAX_SHORTCUTS = 100

class CustomShortcutSettings():
    def __init__(self, *args, **kwargs):
        # super().__init__(*args, **kwargs)

        self.available = False

        schema_source = Gio.SettingsSchemaSource.get_default()

        schema = schema_source.lookup(SCHEMA, True)

        if schema is None:
            print("Schema is not installed on your system", SCHEMA)
            
        self.gio_settings = Gio.Settings(schema_id=schema.get_id())
        
        if self.gio_settings is not None:
            self.available = True

    # checked
    def get_relocatable_schemas(self):
        return self.gio_settings.get_strv(KEY + "s")

    # checked
    def get_relocatable_schema_path(self, i):
        return RELOCATABLE_SCHEMA_PATH_TEMLPATE % i

    # checked
    def get_relocatable_schema_settings(self, relocatable_schema):
        relocatable_schema_settings = Gio.Settings.new_with_path(SCHEMA + "." + KEY, relocatable_schema)
        return relocatable_schema_settings
    
    # checked
    def create_shortcut(self):
        if self.available:
            for i in range(0, MAX_SHORTCUTS, 1):
                new_relocatable_schema = self.get_relocatable_schema_path(i)

                if self.relocatable_schema_is_used(new_relocatable_schema) == False:
                    self.reset_relocatable_schema(new_relocatable_schema)
                    self.add_relocatable_schema(new_relocatable_schema)
                    return new_relocatable_schema
        else:
            return None

    def relocatable_schema_is_used(self, new_relocatable_schema):
        relocatable_schemas = self.get_relocatable_schemas()
        
        for relocatable_schema in relocatable_schemas:
            if relocatable_schema == new_relocatable_schema:
                return True

        return False
    
    # checked
    def add_relocatable_schema(self, new_relocatable_schema):
        relocatable_schemas = self.get_relocatable_schemas()
        relocatable_schemas.append(new_relocatable_schema)
        self.gio_settings.set_strv(KEY + "s", relocatable_schemas)
        self.apply_settings(self.gio_settings)

    def reset_relocatable_schema(self, relocatable_schema):
        relocatable_settings = self.get_relocatable_schema_settings(relocatable_schema)
        relocatable_settings.reset("name")
        relocatable_settings.reset("command")
        relocatable_settings.reset("binding")
        self.apply_settings(relocatable_settings)

    # checked
    def edit_shortcut(self, relocatable_schema, shortcut):
        if self.available:
            relocatable_settings = self.get_relocatable_schema_settings(relocatable_schema)
            relocatable_settings.set_string("binding", shortcut)
            self.apply_settings(relocatable_settings)
            return True

    # checked
    def edit_command(self, relocatable_schema, command):
        if self.available:
            relocatable_settings = self.get_relocatable_schema_settings(relocatable_schema)
            relocatable_settings.set_string("command", command)
            relocatable_settings.set_string("name", command)
            self.apply_settings(relocatable_settings)
            return True

    # checked
    def list_custom_shortcuts(self):
        if self.available:
            list = []
            for relocatable_schema in self.get_relocatable_schemas():
                list.append(self.create_custom_shortcut_object(relocatable_schema))
            return list

    # checked
    def create_custom_shortcut_object(self, relocatable_schema):
        relocatable_settings = self.get_relocatable_schema_settings(relocatable_schema)
        binding = relocatable_settings.get_string("binding")
        command = relocatable_settings.get_string("command")
        return binding, command, relocatable_schema # returns a tuple

    # checked
    def apply_settings(self, settings):
        settings.apply()
        Gio.Settings.sync()
