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

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import configparser

class ClipsAttributes():
    application_shortname = "clips"
    application_id = "com.github.hezral.clips"
    application_name = "Clips"
    application_description = "Clipboard Manager"
    application_version ="0.1"
    app_years = "2018-2020"
    main_url = "https://github.com/hezral/clips"
    #bug_url = "https://github.com/hezral/clips/issues/labels/bug"
    #help_url = "https://github.com/hezral/clips/wiki"
    #translate_url = "https://github.com/hezral/clips/blob/master/CONTRIBUTING.md"
    about_authors = "Adi Hezral <hezral@gmail.com>"
    #about_documenters = None
    #about_comments = application_description
    about_license_type = Gtk.License.GPL_3_0

class ClipsConfig():
    def __init__(self):
        super().__init__()

        attributes = ClipsAttributes()

        self.configDir =  os.path.join(GLib.get_user_config_dir(), attributes.application_id)
        self.configFile = os.path.join(self.configDir + "/" + "config.ini")
        self.cacheDir = os.path.join(GLib.get_user_cache_dir(), attributes.application_id)

        if not os.path.exists(self.configDir):
            os.makedirs(self.configDir)

        if not os.path.exists(self.cacheDir):
            os.makedirs(self.cacheDir)

        config = configparser.ConfigParser()
        config['default'] = {}
        config['default']['first_run'] = 'false'
        config['default']['cache_retention_days'] = '5'
        
        if not os.path.isfile(self.configFile):
            with open(self.configFile, 'w') as self.configFile:
                config.write(self.configFile)
    


