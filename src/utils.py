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
from datetime import datetime

#-------------------------------------------------------------------------------------------------------

def run_async(func):
    '''
    https://github.com/learningequality/ka-lite-gtk/blob/341813092ec7a6665cfbfb890aa293602fb0e92f/kalite_gtk/mainwindow.py
    http://code.activestate.com/recipes/576683-simple-threading-decorator/
        run_async(func)
            function decorator, intended to make "func" run in a separate
            thread (asynchronously).
            Returns the created Thread object
            E.g.:
            @run_async
            def task1():
                do_something
            @run_async
            def task2():
                do_something_too
    '''
    from threading import Thread
    from functools import wraps

    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target=func, args=args, kwargs=kwargs)
        func_hl.start()
        # Never return anything, idle_add will think it should re-run the
        # function because it's a non-False value.
        return None

    return async_func

#-------------------------------------------------------------------------------------------------------

def get_active_app_window():
    import gi
    gi.require_version("Wnck", "3.0")
    gi.require_version("Bamf", "3")
    from gi.repository import Bamf, Wnck

    matcher = Bamf.Matcher()
    screen = Wnck.Screen.get_default()
    screen.force_update()

    # if matcher.get_active_window() is None:
    #     active_win = screen.get_active_window()
    # else:
    #     active_win = matcher.get_active_window()

    active_win = matcher.get_active_window()

    if active_win is not None:
        active_app = matcher.get_application_for_window(active_win)

        # print("get_active_app:", active_app.get_desktop_file())

        # from gi.repository import Gio

        # desktopapp_info = Gio.DesktopAppInfo.new_from_filename(active_app.get_desktop_file())

        # print("get_active_app:", desktopapp_info.get_name())

        if active_app is not None:
            source_app = active_app.get_name().split(" – ")[-1] #some app's name are shown with current document name so we split it and get the last part only
            source_icon = active_app.get_icon()
    else: 
        source_app = screen.get_active_workspace().get_name() # if no active window, fallback to workspace name
        source_icon = 'preferences-desktop-wallpaper' 

    return source_app, source_icon

def get_appinfo(app):
    from gi.repository import Gio
    all_apps = Gio.AppInfo.get_all()
    try:
        appinfo = [child for child in all_apps if app.lower() in child.get_name().lower()][0]
    except:
        appinfo = None
    finally:
        if appinfo is not None:
            icon = appinfo.get_icon()
            if icon is not None:
                icon_name = icon.to_string()   
            app_name = appinfo.get_name()
        else:
            app_name = app
            icon_name = "application-default-icon"
    return app_name, icon_name

def get_widget_by_name(widget, child_name, level, doPrint=False):
    '''
    Function to find widgets using its parent
    https://stackoverflow.com/questions/20461464/how-do-i-iterate-through-all-Gtk-children-in-pyGtk-recursively
    http://cdn.php-Gtk.eu/cdn/farfuture/riUt0TzlozMVQuwGBNNJsaPujRQ4uIYXc8SWdgbgiYY/mtime:1368022411/sites/php-Gtk.eu/files/Gtk-php-get-child-widget-by-name.php__0.txt
    note get_name() vs Gtk.Buildable.get_name(): https://stackoverflow.com/questions/3489520/python-Gtk-widget-name
    '''
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk

    if widget is not None:
        if doPrint: print("-"*level + str(Gtk.Widget.get_name(widget)) + " :: " + str(type(widget).__name__))
    else:
        if doPrint: print("-"*level + "None")
        return None

    #/*** If it is what we are looking for ***/
    if(Gtk.Widget.get_name(widget) == child_name): # not widget.get_name() !
        return widget

    #/*** If this widget has one child only search its child ***/
    if (hasattr(widget, 'get_child') and callable(getattr(widget, 'get_child')) and child_name != ""):
        child = widget.get_child()
        if child is not None:
            return get_widget_by_name(child, child_name, level+1, doPrint)

    # /*** It might have many children, so search them ***/
    elif (hasattr(widget, 'get_children') and callable(getattr(widget, 'get_children')) and child_name !=""):
        children = widget.get_children()
        # /*** For each child ***/
        found = None
        for child in children:
            if child is not None:
                found = get_widget_by_name(child, child_name, level+1, doPrint) # //search the child
                if found: return found

def get_widget_by_focus_state(widget, focus_state, level, doPrint=False):
    '''
    Function to find widgets using its focus state
    '''
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    if widget is not None:
        if doPrint: print("-"*level + str(Gtk.Widget.get_name(widget)) + " :: " + str(type(widget).__name__) + " :has_focus: " + str(widget.has_focus()))
    else:
        if doPrint: print("-"*level + "None")
        return None

    #/*** If it is what we are looking for ***/
    if(widget.is_focus() == focus_state):
        if doPrint: print("###################################################")
        return widget

    #/*** If this widget has one child only search its child ***/
    if (hasattr(widget, 'get_child') and callable(getattr(widget, 'get_child'))):
        child = widget.get_child()
        if child is not None:
            return get_widget_by_focus_state(child, focus_state, level+1, doPrint)

    # /*** It might have many children, so search them ***/
    elif (hasattr(widget, 'get_children') and callable(getattr(widget, 'get_children'))):
        children = widget.get_children()
        # /*** For each child ***/
        found = None
        for child in children:
            if child is not None:
                found = get_widget_by_focus_state(child, focus_state, level+1, doPrint) # //search the child
                if found: return found

#-------------------------------------------------------------------------------------------------------

# function to validate string using regex
def validate_string_with_regex(str, regex):
    import re
    p = re.compile(regex)
 
    # If the string is empty return false
    if(str == None):
        return False
 
    # Return if the string matched the ReGex
    if(re.search(p, str)):
        return True
    else:
        return False

#-------------------------------------------------------------------------------------------------------
# Color Validation Functions


# Regex Pattern for Rgb, Rgba, Hsl, Hsla color coding
# convert and test regex at https://regex101.com/
# https://www.regexpal.com/97509 this one is better

HEX = ("hex", r"^#([\da-f]{3}|[\dA-F]{3}){1,2};?\s?$")
RGB = ("rgb", r"^[Rr][Gg][Bb]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
RGBA = ("rgba", r"^[Rr][Gg][Bb][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
HSL = ("hsl", r"^[Hh][Ss][Ll]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
HSLA = ("hsla", r"^[Hh][Ss][Ll][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
color_regex = (HEX, RGB, RGBA, HSL, HSLA)

# Function validate hexadecimal color code
# https://www.geeksforgeeks.org/how-to-validate-hexadecimal-color-code-using-regular-expression/

# Function validate is any of the HEX, RGB, RGBA, HSL, HSLA color code
def is_valid_color_code(str):
    #clean whitespaces 
    #str_ = str.replace(" ", "")
    for regex in color_regex:
        # #print(regex)
        if validate_string_with_regex(str, regex[1]):
            return True, regex[0]
        else:
            pass

# Function to convert hsl string to RGB color code
import colorsys
def hsl_to_rgb(hslcode):
    h, s, l = hslcode
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    rgb = (int(r*255), int(g*255), int(b*255))
    return rgb

# Function to convert hexadecimal string to RGB color code
# https://stackoverflow.com/a/29643643/14741406
def hex_to_rgb(hexcode):
    h = hexcode.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return rgb

# Function to determine light or dark color using RGB values
# https://stackoverflow.com/a/58270890/14741406
def is_light_color(rgb=[0,0,0]):
    import math
    [r,g,b] = rgb
    hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
    if (hsp > 127.5):
        return 'light'
    else:
        return 'dark'

# function to extract background-color from html files
# https://stackoverflow.com/a/4894134/14741406
def get_css_background_color(str):
    import re
    regex = r"(?:background-color)\:(.*?)\;"
    result = re.search(regex, str)
    
    if result is not None:
        css_background_color = re.search(regex, str).group(1).strip()

        for regex in color_regex:
            if validate_string_with_regex(css_background_color, regex[1]):
                return css_background_color

def to_rgb(color_string):
    color_string = color_string.strip(" ").strip(";").strip(")") #strip "space ; )" chars    
    color_string = color_string.replace(" ","") #replace space chars

    color_string = color_string.split("(")
    
    if "#" in color_string[0]:
        a = 1
        rgb = hex_to_rgb(color_string[0])

    elif "rgb" in color_string[0]:
        r, g, b = color_string[1].split(",")[0:3]
        r = int(int(r.strip("%"))/100*255) if r.find("%") != -1 else int(r)
        g = int(int(g.strip("%"))/100*255) if g.find("%") != -1 else int(g)
        b = int(int(b.strip("%"))/100*255) if b.find("%") != -1 else int(b)
        a = 1
        rgb = (r, g, b)

    elif "rgba" in color_string[0]:
        r, g, b, a = color_string[1].split(",")
        r = int(int(r.strip("%"))/100*255) if r.find("%") != -1 else int(r)
        g = int(int(g.strip("%"))/100*255) if g.find("%") != -1 else int(g)
        b = int(int(b.strip("%"))/100*255) if b.find("%") != -1 else int(b)
        a = float(a.split(")")[0])
        rgb = (r, g, b)

    elif "hsl" in color_string[0]:
        h, s, l = color_string[1].split(",")[0:3]
        h = float(h) / 360
        s = float(s.replace("%","")) / 100
        l = float(l.replace("%","")) / 100
        a = 1
        rgb = hsl_to_rgb((h, s, l))

    elif "hsla" in color_string[0]:
        h, s, l, a = color_string[1].split(",") 
        h = int(h) / 360
        s = int(s.replace("%","")) / 100
        l = int(l.replace("%","")) / 100
        a = float(a.split(")")[0])
        rgb = hsl_to_rgb((h, s, l))
    
    else:
        rgb = None
        a = None
    
    # print(type(rgb), type(float(a)))

    return rgb, float(a)

#-------------------------------------------------------------------------------------------------------

# function to view file using default application
def open_file_xdg(filepath):
    import subprocess
    try:
        subprocess.Popen(['xdg-open', filepath])
    except:
        print("Unable to launch {filepath}".format(filepath=filepath))
        pass

def open_url_gtk(url):
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk
    try:
        Gtk.show_uri_on_window(None, url, Gdk.CURRENT_TIME)
    except:
        print("Unable to launch {url}".format(url=url))
        pass

def open_file_gio(filepath):
    from gi.repository import Gio
    view_file = Gio.File.new_for_path(filepath)
    if view_file.query_exists():
        try:
            Gio.AppInfo.launch_default_for_uri(uri=view_file.get_uri(), context=None)
        except:
            print("Unable to launch {file}".format(file=view_file))
            pass

def open_url_email(uri):
    from gi.repository import Gio
    try:
        Gio.AppInfo.launch_default_for_uri(uri, None)
    except:
        print("Unable to launch {uri}".format(uri=uri))
        pass

def reveal_file_gio(files):
    from gi.repository import Gio, GLib, Gdk
    app_info = Gio.AppInfo.get_default_for_type("inode/directory", True)
    # add check if file or files
    if isinstance(files, list):
        try:
            app_info.launch_uris(files, None)
        except:
            print("Unable to reveal {files}".format(files=files))
            pass
    else:
        view_file = Gio.File.new_for_path(files)
        files_list = [view_file, ]
        app_info.launch(files_list, None)

# file1 = "/home/adi/Work/clips/colors.txt"
# file2 = "/home/adi/Work/clips/setup.py"
# files = [file1, file2]
# reveal_file_gio(files)
# reveal_file_gio(file1)

#-------------------------------------------------------------------------------------------------------

# function to check distro since platform.linux_distribution() is deprecated since 3.7
# https://majornetwork.net/2019/11/get-linux-distribution-name-and-version-with-python/

def GetOsDistroName():
    import csv

    RELEASE_DATA = {}
    with open("/etc/os-release") as f:
        reader = csv.reader(f, delimiter="=")
        for row in reader:
            if row:
                RELEASE_DATA[row[0]] = row[1]

    if RELEASE_DATA["ID"] in ["debian", "raspbian"]:
        with open("/etc/debian_version") as f:
            DEBIAN_VERSION = f.readline().strip()
        major_version = DEBIAN_VERSION.split(".")[0]
        version_split = RELEASE_DATA["VERSION"].split(" ", maxsplit=1)
        if version_split[0] == major_version:
            # Just major version shown, replace it with the full version
            RELEASE_DATA["VERSION"] = " ".join([DEBIAN_VERSION] + version_split[1:])

    print("{} {}".format(RELEASE_DATA["NAME"], RELEASE_DATA["VERSION"]))

    return RELEASE_DATA["NAME"], RELEASE_DATA["VERSION"]

#-------------------------------------------------------------------------------------------------------

# function to get domain from url
def get_domain(url):
    from urllib.parse import urlparse
    result = urlparse(url).netloc
    if len(result.split('.')) == 3:
        domain = '.'.join(result.split('.')[1:])
    else:
        domain = '.'.join(result.split('.'))
    return domain

def get_web_contents(url):
    import requests
    # print(datetime.now(), "start get webpage contents", url)
    try:
        contents = requests.get(url).text
        return contents
    except:
        return None
    # finally:
        # print(datetime.now(), "finish get webpage contents", url)

# function to get web page title from url    
def get_web_title(contents, url):
    from urllib.parse import urlparse
    # print(datetime.now(), "start get webpage title", url)
    if contents is not None:
        title_tag_open = "<title>"
        title_tag_close = "</title>"
        title = str(contents[contents.find(title_tag_open) + len(title_tag_open) : contents.find(title_tag_close)])
    else:
        title = urlparse(url).netloc
    # print(datetime.now(), "start get webpage title", url)
    return title

# function to get web page favicon from a url
def get_web_favicon(contents, url, download_path='./', checksum='na'):
    LFAVICON = r"<link\srel\=\"(apple-touch-icon-precomposed|apple-touch-icon)\"\s(.*(\/.*)+?|href)\=\".*(\/.*)+?\""
    SFAVICON = r"<link\srel\=\"(icon|shortcut icon)\"\s(.*(\/.*)+?|href)\=\".*(\/.*)+?\""
    
    import re
    import requests
    from urllib.parse import urlparse

    # print(datetime.now(), "start downloading favicon", url)

    domain = get_domain(url)
    icon_name = download_path + '/' + domain + '-' + checksum + '.ico'    

    regex_result1 = re.search(LFAVICON, contents)
    regex_result2 = re.search(SFAVICON, contents)

    if regex_result1 is not None:
        regex_result = regex_result1
    else:
        regex_result = regex_result2

    if regex_result is not None:
        favicon_url = regex_result.group(0).split('href="')[1].split('"')[0].strip(">").strip("/")
        if "http" not in favicon_url:
            favicon_url = urlparse(url).scheme + '://' + domain + '/' + favicon_url
    else:
        favicon_url = urlparse(url).scheme + '://' + domain + '/' + 'favicon.ico'
    
    r = None
    # print(datetime.now(), "favicon", favicon_url)
    try:
        r = requests.get(favicon_url, allow_redirects=True)
    except:
        pass

    if r is not None:
        open(icon_name, 'wb').write(r.content)
        # print(datetime.now(), "finish downloading favicon", url)
        return icon_name

def get_web_data(url, file_path=None, download_path='./', checksum='na'):
    # print(datetime.now(), "start get webpage data", url)
    
    contents = get_web_contents(url)
    title = get_web_title(contents, url)
    icon_name = get_web_favicon(contents, url, download_path, checksum)

    if file_path is not None:
        with open(file_path, "a") as file:
            file.write("\n"+title)
            file.close

    # print(datetime.now(), "finish get webpage data", url)
    print(get_fuzzy_timestamp(datetime.now()))
    return title, icon_name

# def GetWebpageThread(url, file_path, download_path='./'):
#     import concurrent.futures
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         future = executor.submit(get_web_data, url, file_path, download_path)
#         return_value = future.result()
#         # print(return_value)
#         print(get_fuzzy_timestamp(datetime.now()))

# print("Testing GetWebpageThread...")
# url = "https://netflix.com"
# # GetWebpageThread(url, "./")
# get_web_data(url)
# print("Finish  GetWebpageThread...")

#-------------------------------------------------------------------------------------------------------

def is_valid_url(str):
    # https://stackoverflow.com/a/60267538/14741406
    # https://urlregex.com/
    URL = r"(^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$)"
    regex = URL
    return validate_string_with_regex(str, regex)

#-------------------------------------------------------------------------------------------------------

def is_valid_unix_uri(str):
    # https://stackoverflow.com/a/38521489/14741406
    UNIXPATH = r"^(\/[\w^ ]+)+\/?([\w.])+[^.]$"
    regex = UNIXPATH
    return validate_string_with_regex(str, regex)

#-------------------------------------------------------------------------------------------------------

def is_valid_email(str):
    EMAIL = r"(^(mailto\:)?[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    regex = EMAIL
    return validate_string_with_regex(str, regex)

#-------------------------------------------------------------------------------------------------------

def copy_to_clipboard(clipboard_target, file, type=None):
    from subprocess import Popen, PIPE

    if "url" in type:
        with open(file) as _file:
            data = Popen(['echo', _file.readlines()[0].rstrip("\n").rstrip("\n")], stdout=PIPE)
            Popen(['xclip', '-selection', 'clipboard', '-target', clipboard_target], stdin=data.stdout)
    # elif "html" in type:
    #     try:
    #         Popen(['xclip', '-selection', 'clipboard', '-target', 'text/plain;charset=utf-8', '-i', file])
    #     except:
    #         Popen(['xclip', '-selection', 'clipboard', '-target', 'text/plain', '-i', file])
    else:
        Popen(['xclip', '-selection', 'clipboard', '-target', clipboard_target, '-i', file])

#-------------------------------------------------------------------------------------------------------

def get_fuzzy_timestamp(time=False):
    """
    Get a datetime object or a int() Epoch self.timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromself.timestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now

    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + "s ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(round(second_diff / 60)) + "m ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(round(second_diff / 3600)) + "hrs ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(round(day_diff, 1)) + " days ago"
    if day_diff < 31:
        return str(round(day_diff / 7, 1)) + " weeks ago"
    if day_diff < 365:
        return str(round(day_diff / 30, 1)) + " months ago!"
    return str(round(day_diff / 365, 1)) + " years ago!!"