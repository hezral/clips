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

from distutils.core import setup
from distutils.command.install import install

import pathlib, os, shutil
from os import path
from subprocess import call


# Base application info
base_rdnn = 'com.github.hezral'
app_name = 'clips'
app_id = base_rdnn + '.' + app_name
app_url = 'https://github.com/hezral/' + app_name
saythanks_url = 'https://www.buymeacoffee.com/hezral'

# Setup file paths for data files
prefix = '/usr'
prefix_data = path.join(prefix, 'share')
install_path = path.join(prefix_data, app_id)
src_path = path.join(install_path, 'src')
data_path = path.join(install_path, 'data')
icon_path = 'icons/hicolor'
icon_sizes = ['16','24','32','48','64','128']
icon_scalable = prefix_data + '/icons/hicolor/scalable/apps'
icon_16 = prefix_data + '/icons/hicolor/16x16/apps'
icon_24 = prefix_data + '/icons/hicolor/24x24/apps'
icon_32 = prefix_data + '/icons/hicolor/32x32/apps'
icon_48 = prefix_data + '/icons/hicolor/48x48/apps'
icon_64 = prefix_data + '/icons/hicolor/64x64/apps'
icon_128 = prefix_data + '/icons/hicolor/128x128/apps'
icon_16_2x = prefix_data + '/icons/hicolor/16x16@2/apps'
icon_24_2x = prefix_data + '/icons/hicolor/24x24@2/apps'
icon_32_2x = prefix_data + '/icons/hicolor/32x32@2/apps'
icon_48_2x = prefix_data + '/icons/hicolor/48x48@2/apps'
icon_64_2x = prefix_data + '/icons/hicolor/64x64@2/apps'
icon_128_2x = prefix_data + '/icons/hicolor/128x128@2/apps'


# Setup install data list
install_data = [(prefix_data + '/metainfo', ['data/' + app_id + '.appdata.xml']),
                (prefix_data + '/applications', ['data/' + app_id + '.desktop']),
                (prefix_data + '/glib-2.0/schemas',['data/' + app_id + '.gschema.xml']),
                (data_path + '/icons',['data/icons/' + app_id + '-info-symbolic.svg']),
                (data_path + '/icons',['data/icons/' + app_id + '-view-symbolic.svg']),
                (data_path,['data/application.css']),
                (src_path,['src' + '/application.py']),
                (src_path,['src' + '/main_window.py']),
                (src_path,['src' + '/utils.py']),
                (src_path + '/services',['src/services' + '/cache_manager.py']),
                (src_path + '/services',['src/services' + '/clipboard_manager.py']),
                (src_path + '/services',['src/services' + '/clips_supported.py']),
                (src_path + '/services',['src/services' + '/custom_shortcut_settings.py']),
                (src_path + '/views',['src/views' + '/clips_view.py']),
                (src_path + '/views',['src/views' + '/settings_view.py']),
                (src_path + '/views',['src/views' + '/info_view.py']),
                (icon_scalable,['data/icons/' + app_id + '.svg']),
                (icon_16,['data/icons/16/' + app_id + '.svg']),
                (icon_16_2x,['data/icons/16/' + app_id + '.svg']),
                (icon_24,['data/icons/24/' + app_id + '.svg']),
                (icon_24_2x,['data/icons/24/' + app_id + '.svg']),
                (icon_32,['data/icons/32/' + app_id + '.svg']),
                (icon_32_2x,['data/icons/32/' + app_id + '.svg']),
                (icon_48,['data/icons/48/' + app_id + '.svg']),
                (icon_48_2x,['data/icons/48/' + app_id + '.svg']),
                (icon_64,['data/icons/64/' + app_id + '.svg']),
                (icon_64_2x,['data/icons/64/' + app_id + '.svg']),
                (icon_128,['data/icons/128/' + app_id + '.svg']),
                (icon_128_2x,['data/icons/128/' + app_id + '.svg'])]

# Post install commands
class PostInstall(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        # print('Updating icon cache...')
        # call(['gtk-update-icon-cache', '-qtf', path.join(prefix_data, 'icons', 'hicolor')])

        # print("Installing new Schemas")
        # call(['glib-compile-schemas', path.join(prefix_data, 'glib-2.0/schemas')])

        # print("Clean-up")
        # import shutil
        # for size in icon_sizes:
        #     shutil.rmtree('data/icons/' + size)
            
setup(
    name=app_name,  # Required
    license='GNU GPL3',
    version='1.0.0',  # Required
    url=app_url,  # Optional
    author='Adi Hezral',  # Optional
    author_email='hezral@gmail.com',  # Optional
    scripts=[app_id],
    data_files=install_data  # Optional
    # cmdclass={
    #     'install': PostInstall,
    # }
)