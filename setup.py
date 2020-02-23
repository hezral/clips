#!/usr/bin/python3

import glob, os 
from distutils.core import setup

install_data = [('share/applications', ['data/com.github.hezral.clips.desktop']),
                ('share/metainfo', ['data/com.github.hezral.clipsappdata.xml']),
                ('share/icons/hicolor/128x128/apps',['data/com.github.hezral.clipssvg']),
                ('bin/clips',['clips/constants.py']),
                ('bin/clips',['clips/headerbar.py']),
                ('bin/clips',['clips/main.py']),
                ('bin/clips',['clips/welcome.py']),
                ('bin/clips',['clips/window.py']),
                ('bin/clips',['clips/__init__.py']),
                ('bin/clips/locale/it_IT/LC_MESSAGES',
                    ['clips/locale/it_IT/LC_MESSAGES/clips.mo']),
                ('bin/clips/locale/it_IT/LC_MESSAGES',
                    ['clips/locale/it_IT/LC_MESSAGES/clips.po'])]

setup(  name='Clips',
        version='0.0.1',
        author='Adi Hezral',
        description='An app to view your clipboard',
        url='https://github.com/hezral/clips',
        license='GNU GPL3',
        scripts=['com.github.hezral.clips'],
        packages=['clips'],
        data_files=install_data)
