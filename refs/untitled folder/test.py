#!/usr/bin/env python3

import os

# initialize cache directories
cache_icon_dir = 'cache_icon/tmp/'
cache_dir = 'cache/tmp/'

try:
    if not os.path.exists(cache_icon_dir) or not os.path.exists(cache_dir):
        os.makedirs(cache_icon_dir)
        os.makedirs(cache_dir)
        print('Directory created')
    print('nothing done')
except OSError as error:
    print("Excption: ", error)

print(cache_dir.split('/')[0])