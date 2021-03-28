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

###################################################################################################################

def RunAsync(func):
    '''
    https://github.com/learningequality/ka-lite-gtk/blob/341813092ec7a6665cfbfb890aa293602fb0e92f/kalite_gtk/mainwindow.py
    http://code.activestate.com/recipes/576683-simple-threading-decorator/
        RunAsync(func)
            function decorator, intended to make "func" run in a separate
            thread (asynchronously).
            Returns the created Thread object
            E.g.:
            @RunAsync
            def task1():
                do_something
            @RunAsync
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

###################################################################################################################

def GetWidgetByName(widget, child_name, level, doPrint=False):
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
            return GetWidgetByName(child, child_name, level+1, doPrint)

    # /*** It might have many children, so search them ***/
    elif (hasattr(widget, 'get_children') and callable(getattr(widget, 'get_children')) and child_name !=""):
        children = widget.get_children()
        # /*** For each child ***/
        found = None
        for child in children:
            if child is not None:
                found = GetWidgetByName(child, child_name, level+1, doPrint) # //search the child
                if found: return found

def GetWidgetByFocusState(widget, focus_state, level, doPrint=False):
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
            return GetWidgetByFocusState(child, focus_state, level+1, doPrint)

    # /*** It might have many children, so search them ***/
    elif (hasattr(widget, 'get_children') and callable(getattr(widget, 'get_children'))):
        children = widget.get_children()
        # /*** For each child ***/
        found = None
        for child in children:
            if child is not None:
                found = GetWidgetByFocusState(child, focus_state, level+1, doPrint) # //search the child
                if found: return found

###################################################################################################################

# function to validate string using regex
def validateStr(str, regex):
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

###################################################################################################################
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
def isValidColorCode(str):
    #clean whitespaces 
    #str_ = str.replace(" ", "")
    for regex in color_regex:
        # #print(regex)
        if validateStr(str, regex[1]):
            return True, regex[0]
        else:
            pass

# Function to convert hsl string to RGB color code
import colorsys
def HSLtoRGB(hslcode):
    h, s, l = hslcode
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    rgb = (int(r*255), int(g*255), int(b*255))
    return rgb

# Function to convert hexadecimal string to RGB color code
# https://stackoverflow.com/a/29643643/14741406
def HexToRGB(hexcode):
    h = hexcode.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return rgb

# Function to determine light or dark color using RGB values
# https://stackoverflow.com/a/58270890/14741406
def isLightOrDark(rgb=[0,0,0]):
    import math
    [r,g,b] = rgb
    hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
    if (hsp > 127.5):
        return 'light'
    else:
        return 'dark'

# function to extract background-color from html files
# https://stackoverflow.com/a/4894134/14741406
def GetCssBackgroundColor(str):
    import re
    regex = r"(?:background-color)\:(.*?)\;"
    result = re.search(regex, str)
    
    if result is not None:
        css_background_color = re.search(regex, str).group(1).strip()

        for regex in color_regex:
            if validateStr(css_background_color, regex[1]):
                return css_background_color

def ConvertToRGB(color_string):
    color_string = color_string.strip(" ").strip(";").strip(")") #strip "space ; )" chars    
    color_string = color_string.replace(" ","") #replace space chars

    color_string = color_string.split("(")
    
    if "#" in color_string[0]:
        a = 1
        rgb = HexToRGB(color_string[0])

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
        rgb = HSLtoRGB((h, s, l))

    elif "hsla" in color_string[0]:
        h, s, l, a = color_string[1].split(",") 
        h = int(h) / 360
        s = int(s.replace("%","")) / 100
        l = int(l.replace("%","")) / 100
        a = float(a.split(")")[0])
        rgb = HSLtoRGB((h, s, l))
    
    else:
        rgb = None
        a = None
    
    return rgb, a

###################################################################################################################

# function to view file using default application
def ViewFile(file):
    import subprocess
    subprocess.Popen(['xdg-open', file])

###################################################################################################################

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

###################################################################################################################

# function to get domain from url
def GetDomain(url):
    from urllib.parse import urlparse
    result = urlparse(url).netloc
    if len(result.split('.')) == 3:
        domain = '.'.join(result.split('.')[1:])
    else:
        domain = '.'.join(result.split('.'))
    return domain

# function to get web page title from url
def GetWebpageTitle(url):
    import requests
    from urllib.parse import urlparse
    try:
        response = requests.get(url)
        contents = response.text
        title_tag_open = "<title>"
        title_tag_close = "</title>"
        title = str(contents[contents.find(title_tag_open) + len(title_tag_open) : contents.find(title_tag_close)])
    except:
        title = urlparse(url).netloc
    return title

# function to get web page favicon form a url
def GetWebpageFavicon(url, download_path='./'):
    FAVICON = r"<link\srel\=\"(shortcut icon|icon)\"\s(.*(\/.*)+?|href)\=\".*(\/.*)+?\>"
    import re
    import requests
    from urllib.parse import urlparse

    domain = GetDomain(url)
    icon_name = download_path + '/' + domain + '.ico'
    
    response = requests.get(url)
    contents = response.text
    regex_result = re.search(FAVICON, contents)

    if regex_result is not None:
        favicon_url = regex_result.group(0).split('href=')[1].replace('"',"").replace(">","")
        if "http" not in favicon_url:
            favicon_url = urlparse(url).scheme + '://' + domain + '/' + favicon_url
    else:
        favicon_url = urlparse(url).scheme + '://' + domain + '/' + 'favicon.ico'

    r = None
    try:
        r = requests.get(favicon_url, allow_redirects=True)
    except:
        pass
    if r is not None:
        open(icon_name, 'wb').write(r.content)
    
###################################################################################################################

# function to check valid internet URL
# https://stackoverflow.com/a/60267538/14741406
# https://urlregex.com/
URL = r"^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$"
def isValidURL(str):
    regex = URL
    return validateStr(str, regex)

###################################################################################################################

# function to check valid file manager path
# https://stackoverflow.com/a/38521489/14741406
UNIXPATH = r"^(\/[\w^ ]+)+\/?([\w.])+[^.]$"
def isValidUnixPath(str):
    regex = UNIXPATH
    return validateStr(str, regex)

###################################################################################################################

# function to check email address
EMAIL = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
def isEmaild(str):
    regex = EMAIL
    return validateStr(str, regex)

###################################################################################################################

# print(GetWebpageTitle('https://apple.com'))
# GetWebpageFavicon('https://apple.com')

# print(GetWebpageTitle('https://keep.google.com/?pli=1#home'))
# GetWebpageFavicon('https://keep.google.com/?pli=1#home')

# print(GetWebpageTitle('https://appcenter.elementary.io/com.github.devalien.workspaces/e'))
# GetWebpageFavicon('https://appcenter.elementary.io/com.github.devalien.workspaces/e')

# print(GetWebpageTitle('https://getpasta.com/faq.html'))
# GetWebpageFavicon('https://getpasta.com/faq.html')

# print(GetWebpageTitle('https://stackoverflow.com/questions/55828169/how-to-filter-gtk-flowbox-children-with-gtk-entrysearch'))
# GetWebpageFavicon('https://stackoverflow.com/questions/55828169/how-to-filter-gtk-flowbox-children-with-gtk-entrysearch')


# get_distro()

# print(ConvertToRGB("rgb(255, 242, 0)")[0][0])
# print(ConvertToRGB("hsl(133, 100%, 50%)"))
# print(ConvertToRGB("#ff005d"))
# print(ConvertToRGB("rgba(25, 0, 255, 0.75)"))
# print(ConvertToRGB("hsla(124, 100%, 50%, 0.45)"))

# print(isValidUnixPath("/home/adi"))
# print(isValidURL("http://google.com"))
# print(isEmaild("hezral@gmail.com"))
