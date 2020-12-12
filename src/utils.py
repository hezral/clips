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

# Function to find widgets using its parent
# https://stackoverflow.com/questions/20461464/how-do-i-iterate-through-all-Gtk-children-in-pyGtk-recursively
# http://cdn.php-Gtk.eu/cdn/farfuture/riUt0TzlozMVQuwGBNNJsaPujRQ4uIYXc8SWdgbgiYY/mtime:1368022411/sites/php-Gtk.eu/files/Gtk-php-get-child-widget-by-name.php__0.txt
# note get_name() vs Gtk.Buildable.get_name(): https://stackoverflow.com/questions/3489520/python-Gtk-widget-name
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def get_widget_by_name(widget, child_name, level, doPrint=False):

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


import re
import math



# function to check valid internet URL
# https://stackoverflow.com/a/60267538/14741406
# https://urlregex.com/
URL = r"^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$"
def isValidURL(str):
    regex = URL
    return validateStr(str, regex)

# function to check valid file manager path
# https://stackoverflow.com/a/38521489/14741406
UNIXPATH = r"^(\/[\w^ ]+)+\/?([\w.])+[^.]$"

def isValidUnixPath(str):
    regex = UNIXPATH
    return validateStr(str, regex)

# function to check email address
EMAIL = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
def isEmaild(str):
    regex = EMAIL
    return validateStr(str, regex)

# Regex Pattern for Rgb, Rgba, Hsl, Hsla color coding
# convert and test regex at https://regex101.com/
# https://www.regexpal.com/97509 this one is better

HEX = ("hex", r"^#([\da-f]{3}|[\dA-F]{3}){1,2};?\s?$")
RGB = ("rgb", r"^[Rr][Gg][Bb]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
RGBA = ("rgba", r"^[Rr][Gg][Bb][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
HSL = ("hsl", r"^[Hh][Ss][Ll]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
HSLA = ("hsla", r"^[Hh][Ss][Ll][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")


color_regex = (HEX, RGB, RGBA, HSL, HSLA)


# function to validate string using regex
def validateStr(str, regex):

    p = re.compile(regex)
 
    # If the string is empty return false
    if(str == None):
        return False
 
    # Return if the string matched the ReGex
    if(re.search(p, str)):
        return True
    else:
        return False

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


# Function to convert HSL to RGB color code
import colorsys
def HSLtoRGB(hslcode):
    h, s, l = hslcode
    r, g, b = colorsys.hls_to_rgb(h, s, l)
    rgb = [int(r*255), int(g*255), int(b*255)]
    return rgb

# Function to convert hexadecimal to RGB color code
# https://stackoverflow.com/a/29643643/14741406
def HexToRGB(hexcode):
    h = hexcode.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return rgb

# Function to determine light or dark color using RGB values
# https://stackoverflow.com/a/58270890/14741406
def isLightOrDark(rgb=[0,0,0]):
    [r,g,b] = rgb
    hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
    if (hsp > 127.5):
        return 'light'
    else:
        return 'dark'

# function to extract background-color from html files
# https://stackoverflow.com/a/4894134/14741406
def get_css_background_color(str):
    regex = r"(?:background-color)\:(.*?)\;"
    result = re.search(regex, str).group(1).strip()

    for regex in color_regex:
        if validateStr(result, regex[1]):
            return result, True
        else:
            return "@theme_base_color", False


# print(isValidUnixPath("/home/adi"))

# print(isValidURL("http://google.com"))




# colors = (
# "#111",
# "#222222",
# "rgb(3,3,3)",
# "rgba(4%,4,4%,0.4)",
# "hsl(5,5,5)",
# "hsla(6,6,6,0.6)",
# "#111;",
# "#222222;",
# "rgb(3,3,3);",
# "rgba(4%,4,4%,0.4);",
# "hsl(5,5,5);",
# "hsla(6,6,6,0.6);",
# "#111; ",
# "#222222; ",
# "rgb(3,3,3)",
# "rgba(4%,4,4%,0.4); ",
# "hsl(5,5,5); ",
# "hsla(6,6,6,0.6); ",
# "#111 ",
# "#222222 ",
# "rgb(3,3,3) ",
# "rgba(4%,4,4%,0.4) ",
# "hsl(5,5,5) ",
# "hsla(6,6,6,0.6) ",
# "#111 junk",
# "#222222 junk",
# "rgb(3,3,3) junk",
# "rgba(4%,4,4%,0.4) junk",
# "hsl(5,5,5) junk",
# "hsla(6,6,6,0.6) junk",
# )

# for color in colors:
#     if isValidColorCode(color) is None:
#         print(color)