# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

from datetime import datetime


#-------------------------------------------------------------------------------------------------------
# https://www.blog.pythonlibrary.org/2016/06/09/python-how-to-create-an-exception-logging-decorator/


def init_logger(id, logfile):
    """
    Creates a logging object and returns it
    """
    import sys
    import logging
    
    logger = logging.getLogger(id)
    logger.setLevel(logging.NOTSET)

    file_handler = logging.FileHandler(logfile)
    
    # format_str = "%(levelname)s: %(asctime)s %(pathname)s, %(funcName)s:%(lineno)d: %(message)s"
    format_str = "%(levelname)s: %(asctime)s %(message)s"
    formatter = logging.Formatter(format_str)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter) 

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

def exception_logger(logger):
    """
    A decorator that wraps the passed in function and logs exceptions should one occur
    
    @param logger: a logging object
    """
    
    def decorator(func):
    
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                err = "There was an exception in  "
                err += func.__name__
                logger.exception(err)
            
            # re-raise the exception
            raise
        return wrapper
    return decorator

#-------------------------------------------------------------------------------------------------------

from datetime import timedelta
from functools import wraps
from timeit import default_timer as timer
from typing import Any, Callable, Optional

# def metrics(func: Optional[Callable] = None, name: Optional[str] = None, hms: Optional[bool] = False) -> Any:
def metrics(func=None, name=None, hms=False, logger=None):
    """Decorator to show execution time.

    :param func: Decorated function
    :param name: Metrics name
    :param hms: Show as human-readable string
    """
    assert callable(func) or func is None

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            comment = f"execution time of {name or fn.__name__}:"
            t = timer()
            result = fn(*args, **kwargs)
            te = timer() - t

            # from common import log
            # logger = log.withPrefix('[METRICS]')
            if hms:
                logger.debug(f"{comment} {timedelta(seconds=te)}")
            else:
                logger.debug(f"{comment} {te:>.6f} sec")

            return result
        return wrapper

    return decorator(func) if callable(func) else decorator

#-------------------------------------------------------------------------------------------------------

def run_async(func):
    '''
    https://github.com/learningequality/ka-lite-gtk/blob/341813092ec7a6665cfbfb890aa293602fb0e92f/kalite_gtk/mainwindow.py
    http://code.activestate.com/recipes/576683-simple-threading-decorator/
    run_async(func): 
    function decorator, intended to make "func" run in a separate thread (asynchronously).
    Returns the created Thread object
    Example:
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

def validate_string_with_regex(str, regex):
    '''function to validate string using regex'''
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

def get_fuzzy_timestamp(time=False):
    '''
    Get a datetime object or a int() Epoch self.timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago', 'just now', etc
    '''
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
            return str(second_diff) + " s ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(round(second_diff / 60)) + " m ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(round(second_diff / 3600)) + " hrs ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(round(day_diff, 1)) + " days"
    if day_diff < 31:
        weeks = day_diff / 7
        if weeks.is_integer():
            weeks = int(weeks)
        else:
            weeks = round(weeks, 1)
        if weeks == 1:
            return str(weeks) + " week"
        else:
            return str(weeks) + " weeks"
    if day_diff < 365:
        months = day_diff / 30
        if months.is_integer():
            months = int(months)
        else:
            months = round(months, 1)
        if months == 1:
            return str(months) + " month"
        else:
            return str(months) + " months"
    
    return str(round(day_diff / 365, 1)) + " years!!"

def get_os_distribution_name():
    '''
    Function to check distro since platform.linux_distribution() is deprecated since 3.7
    https://majornetwork.net/2019/11/get-linux-distribution-name-and-version-with-python/
    '''
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

    # print("{} {}".format(RELEASE_DATA["NAME"], RELEASE_DATA["VERSION"]))

    return RELEASE_DATA["NAME"], RELEASE_DATA["VERSION"]

#-------------------------------------------------------------------------------------------------------

def get_mimetype_icon(mimetype):
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gio, Gtk
    icon_name = None
    icon_theme = Gtk.IconTheme.get_default()
    icon = Gio.content_type_get_icon(mimetype)
    for entry in icon.to_string().split():
        if entry != "." and entry != "GThemedIcon":
            try:
                icon_theme.lookup_icon(entry,32,0).get_filename()
                icon_name = entry
                break
            except:
                icon_name = "application-octet-stream"
    # print("Mimetype {0} can use icon file {1}".format(mimetype,icon_name))
    return icon_name

def get_all_apps(app=None):
    ''' Function to get all apps installed on system using desktop files in standard locations for flatpak, snap, native '''
    import gi, os, re
    from gi.repository import Gio, GLib

    all_apps = {}
    app_name = None
    app_icon = None
    startup_wm_class = None
    no_display = None
    app_exec = None
    duplicate_app = 0

    flatpak_system_app_dirs = "/run/host/usr/share/applications"
    native_system_app_dirs = "/usr/share/applications"
    native_system_app_alt_dirs = "/usr/local/share/applications"
    native_system_flatpak_app_dirs = "/var/lib/flatpak/exports/share/applications"
    native_snap_app_dirs = "/var/lib/snapd/desktop"
    native_user_flatpak_app_dirs = os.path.join(GLib.get_home_dir(), ".local/share/flatpak/exports/share/applications")
    native_user_app_dirs = os.path.join(GLib.get_home_dir(), ".local/share/applications")
    desktop_file_dirs = [native_system_app_dirs, native_system_app_alt_dirs, flatpak_system_app_dirs, native_system_flatpak_app_dirs, native_snap_app_dirs, native_user_flatpak_app_dirs, native_user_app_dirs]

    # system_app_dirs = "/run/host/usr/share/applications"
    # # system_app_alt_dirs = "/usr/local/share/applications"
    # snap_app_dirs = "/var/lib/snapd/desktop"
    # system_flatpak_app_dirs = "/var/lib/flatpak/exports/share/applications"
    # user_flatpak_app_dirs = os.path.join(GLib.get_home_dir(), ".local/share/flatpak/exports/share/applications")
    # user_app_dirs = os.path.join(GLib.get_home_dir(), ".local/share/applications")
    # desktop_file_dirs = [system_app_dirs, system_flatpak_app_dirs, snap_app_dirs, user_app_dirs, user_flatpak_app_dirs]

    for dir in desktop_file_dirs:
        if os.path.exists(dir):
            d = Gio.file_new_for_path(dir)
            files = d.enumerate_children("standard::*", 0)
            for desktop_file in files:
                if ".desktop" in desktop_file.get_name():
                    desktop_file_path = ""
                    
                    # print(desktop_file.get_content_type(), os.path.join(dir, desktop_file.get_name()))

                    if "application/x-desktop" in desktop_file.get_content_type():
                        desktop_file_path = os.path.join(dir, desktop_file.get_name())

                    if "inode/symlink" in desktop_file.get_content_type():
                        if ".local/share/flatpak/exports/share/applications" in dir:
                            desktop_file_path = os.path.join(GLib.get_home_dir(), ".local/share/flatpak", os.path.realpath(desktop_file.get_symlink_target()).replace("/home/", ""))

                    if desktop_file_path != "":
                        try:
                            with open(desktop_file_path) as file:
                                lines = file.readlines()
                            contents = ''.join(lines)

                            app_name = re.search("Name=(?P<name>.+)*", contents)
                            app_icon = re.search("Icon=(?P<name>.+)*", contents)
                            startup_wm_class = re.search("StartupWMClass=(?P<name>.+)*", contents)
                            no_display = re.search("NoDisplay=(?P<name>.+)*", contents)
                            app_exec = re.search("Exec=(?P<name>.+)*", contents)
                            flatpak = re.search("X-Flatpak=(?P<name>.+)*", contents)

                            if app_name != None:
                                app_name = app_name.group(1)
                            else:
                                app_name = "unknown"
                            
                            if app_icon != None:
                                app_icon = app_icon.group(1)
                            else:
                                app_icon = "application-default-icon"

                            if startup_wm_class != None:
                                startup_wm_class = startup_wm_class.group(1)

                            if no_display != None:
                                no_display = no_display.group(1)
                                if 'true' in no_display:
                                    no_display = True
                                else:
                                    no_display = False

                            if app_exec != None:
                                app_exec = app_exec.group(1)

                            if flatpak != None:
                                flatpak = True
                            else:
                                flatpak = False

                            if app_name != None and app_icon != None:
                                if no_display is None or no_display is False:
                                    if app_name in all_apps:
                                        duplicate_app += 1
                                        app_name = app_name + "#{0}".format(str(duplicate_app))
                                        all_apps[app_name] = [app_icon, startup_wm_class, no_display, desktop_file_path, app_exec, flatpak]
                                    else:
                                        all_apps[app_name] = [app_icon, startup_wm_class, no_display, desktop_file_path, app_exec, flatpak]
                        except:
                            print(datetime.now(), "Unable to read {0} application info".format(desktop_file_path))

    if app != None:
        return all_apps[app]
    else:
        return all_apps

def get_active_appinfo_xlib(data=None):
    source_app = None
    source_icon = None
    all_apps = get_all_apps()

    import os
    import Xlib
    import Xlib.display

    display = Xlib.display.Display()
    root = display.screen().root

    NET_CLIENT_LIST = display.intern_atom('_NET_CLIENT_LIST')
    NET_DESKTOP_NAMES = display.intern_atom('_NET_DESKTOP_NAMES')
    NET_ACTIVE_WINDOW = display.intern_atom('_NET_ACTIVE_WINDOW')
    GTK_APPLICATION_ID = display.intern_atom('_GTK_APPLICATION_ID')
    WM_NAME = display.intern_atom('WM_NAME')
    WM_CLASS = display.intern_atom('WM_CLASS')
    BAMF_DESKTOP_FILE = display.intern_atom('_BAMF_DESKTOP_FILE')

    try:
        window_id = root.get_full_property(NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType).value[0]
        window = display.create_resource_object('window', window_id)
        
        for key in sorted(all_apps.keys()):

            app_name = key.split("#")[0].lower()
            app_icon = all_apps[key][0].lower()
            if all_apps[key][1] is not None:
                startup_wm_class = all_apps[key][1].lower()
            else:
                startup_wm_class = None
            desktop_file_path = all_apps[key][3].lower()

            if window.get_full_property(BAMF_DESKTOP_FILE, 0):
                bamf_desktop_file = window.get_full_property(BAMF_DESKTOP_FILE, 0).value.replace(b'\x00',b' ').decode("utf-8").lower()
                # print("utils.py: os.path.basename(bamf_desktop_file) == os.path.basename(desktop_file_path): {0}, xlib: {1}, all_apps: {2}".format(os.path.basename(bamf_desktop_file) == os.path.basename(desktop_file_path), os.path.basename(bamf_desktop_file), os.path.basename(desktop_file_path)))
                if os.path.basename(bamf_desktop_file) == os.path.basename(desktop_file_path):
                    if "#" in key:
                        source_app = key.split("#")[0]
                    else:
                        source_app = key
                    source_icon = all_apps[key][0]
                    break_point = "bamf_desktop_file"
                    break

            elif window.get_full_property(GTK_APPLICATION_ID, 0):
                gtk_application_id = window.get_full_property(GTK_APPLICATION_ID, 0).value.replace(b'\x00',b' ').decode("utf-8").lower()
                # print("utils.py: gtk_application_id == app_icon", gtk_application_id == app_icon, gtk_application_id, app_icon)
                if gtk_application_id == app_icon:
                    if "#" in key:
                        source_app = key.split("#")[0]
                    else:
                        source_app = key
                    source_icon = all_apps[key][0]
                    break_point = "gtk_application_id"
                    break

            elif window.get_full_property(WM_CLASS, 0):
                wm_class = window.get_full_property(WM_CLASS, 0).value.replace(b'\x00',b',').decode("utf-8")
                wm_class_keys = wm_class.split(",")
                for wm_class_key in wm_class_keys:
                    if wm_class_key != '':
                        # if wm_class_key.lower() == app_name or wm_class_key.lower() == startup_wm_class or wm_class_key.lower() in app_icon:
                        if wm_class_key.lower() in app_icon:
                            # print("utils.py: key: {0}, all_apps[key]: {1}".format(key, all_apps[key]))
                            # print("utils.py: wm_class_key.lower() == app_name: {0}, wm_class_key: {1}, app_name: {2}".format(wm_class_key.lower() == app_name, wm_class_key, app_name))
                            # print("utils.py: wm_class_key.lower() == startup_wm_class: {0}, wm_class_key: {1}, startup_wm_class: {2}".format(wm_class_key.lower() == startup_wm_class, wm_class_key, startup_wm_class))
                            # print("utils.py: wm_class_key.lower() in app_icon: {0}, wm_class_key: {1}, app_icon: {2}".format(wm_class_key.lower() in app_icon, wm_class_key, app_icon))
                            # print("\n")
                            if "#" in key:
                                source_app = key.split("#")[0]
                            else:
                                source_app = key
                            source_icon = all_apps[key][0]
                            break_point = "wm_class_key, {0}".format(all_apps[key])
                            break
                        elif "-" in wm_class_key:
                            # print("utils.py: wm_class_key.split("-")", wm_class_key.split("-"))
                            for wm_class_subkey in wm_class_key.split("-"):
                                if wm_class_subkey.lower() == app_name or wm_class_subkey.lower() == startup_wm_class or wm_class_subkey.lower() in app_icon:
                                    # print("utils.py: wm_class_subkey", wm_class_subkey)
                                    # print("utils.py: key, all_apps[key]", key, all_apps[key])
                                    # print("utils.py: wm_class_subkey.lower() == app_name", wm_class_subkey.lower() == app_name, wm_class_subkey)
                                    # print("utils.py: wm_class_subkey.lower() == startup_wm_class", wm_class_subkey.lower() == startup_wm_class, wm_class_subkey)
                                    # print("utils.py: wm_class_subkey.lower() in app_icon", wm_class_subkey.lower() in app_icon, wm_class_subkey)
                                    if "#" in key:
                                        source_app = key.split("#")[0]
                                    else:
                                        source_app = key
                                    source_icon = all_apps[key][0]
                                    break_point = "wm_class_subkey, {0}".format(all_apps[key])
                                    break

            elif window.get_full_property(WM_NAME, 0):
                wm_name = window.get_full_property(WM_NAME, 0).value.decode("utf-8").lower()
                if " - " in wm_name:
                    wm_name = wm_name.split(" - ")[-1]
                if startup_wm_class != None:
                    if wm_name == app_name or wm_name == startup_wm_class or wm_name in app_icon:
                        # print("utils.py: key, all_apps[key]", key, all_apps[key])
                        # print("utils.py: wm_name == app_name", wm_name == app_name, wm_name)
                        # print("utils.py: wm_name == startup_wm_class", wm_name == startup_wm_class, wm_name)
                        # print("utils.py: wm_name in app_icon", wm_name in app_icon, wm_name)
                        if "#" in key:
                            source_app = key.split("#")[0]
                        else:
                            source_app = key
                        source_icon = all_apps[key][0]
                        break_point = "wm_name, {0}".format(all_apps[key])
                        break
            
        if source_app is None and source_icon is None:
            workspace = root.get_full_property(NET_DESKTOP_NAMES, Xlib.X.AnyPropertyType).value.replace(b'\x00',b'').decode("utf-8")
            source_app = workspace + ": unknown app" # if no active window, fallback to workspace name
            source_icon = "application-default-icon"

    except Xlib.error.XError: #simplify dealing with BadWindow
        source_app = None
        source_icon = None

    return source_app, source_icon

def get_appinfo(app):
    all_apps = get_all_apps()
    try:
        return app, all_apps[app][0]
    except:
        return "not-found", "application-default-icon"

def get_appinfo_gio(app):
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

def get_active_window_xlib():
    ''' Function to get active window '''
    import Xlib
    import Xlib.display

    display = Xlib.display.Display()
    root = display.screen().root

    NET_ACTIVE_WINDOW = display.intern_atom('_NET_ACTIVE_WINDOW')

    root.change_attributes(event_mask=Xlib.X.FocusChangeMask)
    try:
        window_id = root.get_full_property(NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType).value[0]
        window = display.create_resource_object('window', window_id)
    except Xlib.error.XError: #simplify dealing with BadWindow
        window = None

    return window

def set_active_window_by_xwindow(window):
    ''' Function to set window as active based on x window '''
    import Xlib
    from Xlib.display import Display
    from Xlib import X

    display = Display()

    window.circulate(X.RaiseLowest)
    window.set_input_focus(X.RevertToParent, X.CurrentTime)
    window.configure(stack_mode=X.Above)
    display.flush()
    display.sync()

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

def is_valid_color_code(str):
    '''
    Function validate is any of the HEX, RGB, RGBA, HSL, HSLA color code
    Function validate hexadecimal color code
    https://www.geeksforgeeks.org/how-to-validate-hexadecimal-color-code-using-regular-expression/
    '''
    HEX = ("hex", r"^#([\da-f]{3}|[\dA-F]{3}){1,2};?\s?$")
    RGB = ("rgb", r"^[Rr][Gg][Bb]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
    RGBA = ("rgba", r"^[Rr][Gg][Bb][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
    HSL = ("hsl", r"^[Hh][Ss][Ll]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
    HSLA = ("hsla", r"^[Hh][Ss][Ll][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
    color_regex = (HEX, RGB, RGBA, HSL, HSLA)

    for regex in color_regex:
        if validate_string_with_regex(str, regex[1]):
            return True, regex[0]
        else:
            pass

def hsl_to_rgb(hslcode):
    ''' Function to convert hsl string to RGB color code '''

    import colorsys
    h, s, l = hslcode
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    rgb = (int(r*255), int(g*255), int(b*255))
    return rgb

def hex_to_rgb(hexcode):
    '''
    Function to convert hexadecimal string to RGB color code
    https://stackoverflow.com/a/29643643/14741406
    '''
    h = hexcode.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return rgb

def is_light_color(rgb=[0,0,0]):
    '''
    Function to determine light or dark color using RGB values
    https://stackoverflow.com/a/58270890/14741406
    '''
    import math
    [r,g,b] = rgb
    hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
    if (hsp > 127.5):
        return 'light'
    else:
        return 'dark'

def get_css_background_color(str):
    '''
    function to extract background-color from html files
    https://stackoverflow.com/a/4894134/14741406
    '''
    HEX = ("hex", r"^#([\da-f]{3}|[\dA-F]{3}){1,2};?\s?$")
    RGB = ("rgb", r"^[Rr][Gg][Bb]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
    RGBA = ("rgba", r"^[Rr][Gg][Bb][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
    HSL = ("hsl", r"^[Hh][Ss][Ll]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
    HSLA = ("hsla", r"^[Hh][Ss][Ll][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
    color_regex = (HEX, RGB, RGBA, HSL, HSLA)
    
    import re
    regex = r"(?:background-color)\:(.*?)\;"
    result = re.search(regex, str)

    if result is not None:
        css_background_color = re.search(regex, str).group(1).strip()

        for regex in color_regex:
            if validate_string_with_regex(css_background_color, regex[1]):
                return css_background_color

def get_css_text_color(str):
    '''
    function to extract background-color from html files
    https://stackoverflow.com/a/4894134/14741406
    '''
    HEX = ("hex", r"^#([\da-f]{3}|[\dA-F]{3}){1,2};?\s?$")
    RGB = ("rgb", r"^[Rr][Gg][Bb]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
    RGBA = ("rgba", r"^[Rr][Gg][Bb][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
    HSL = ("hsl", r"^[Hh][Ss][Ll]\(\d{1,3}%?(,\s?\d{1,3}%?){2}\);?\s?$")
    HSLA = ("hsla", r"^[Hh][Ss][Ll][Aa]\((\d{1,3}%?,\s?){3}(1|0?\.\d+)\);?\s?$")
    color_regex = (HEX, RGB, RGBA, HSL, HSLA)
    
    import re
    regex = r"(?:[^\-]color)\:(.*?)\;"
    result = re.search(regex, str)

    if result is not None:
        css_text_color = re.search(regex, str).group(1).strip()

        for regex in color_regex:
            if validate_string_with_regex(css_text_color, regex[1]):
                return css_text_color

def to_rgb(color_string):
    '''
    Function to convert color codes to string by stripping other caharcters and returning rgba codes in tuple format
    '''
    color_string = color_string.strip(" ").strip(";").strip(")") #strip "space ; )" chars    
    color_string = color_string.replace(" ","") #replace space chars
    color_string = color_string.split("(")
    
    if "#" in color_string[0]:
        a = 1
        rgb = hex_to_rgb(color_string[0])

    elif "rgb" in color_string[0] and not "rgba" in color_string[0]:
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

    elif "hsl" in color_string[0] and not "hsla" in color_string[0]:
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
    
    if a == 1.0:
        a = 1
        return rgb, a
    else:
        return rgb, float(a)

#-------------------------------------------------------------------------------------------------------

def get_domain(url):
    ''' Function to get domain from url '''
    from urllib.parse import urlparse
    result = urlparse(url).netloc
    if len(result.split('.')) == 3:
        domain = '.'.join(result.split('.')[1:])
    else:
        domain = '.'.join(result.split('.'))
    return domain

def get_web_contents(url):
    ''' Function to get web contents '''
    import requests
    try:
        contents = requests.get(url).text
        return contents
    except:
        return None

def get_web_title(contents, url):
    ''' Function to get web page title from url'''
    from urllib.parse import urlparse
    if contents is not None:
        title_tag_open = "<title>"
        title_tag_close = "</title>"
        title = str(contents[contents.find(title_tag_open) + len(title_tag_open) : contents.find(title_tag_close)])
    else:
        title = urlparse(url).netloc
    return title

def get_web_favicon(contents, url, download_path='./', checksum='na'):
    ''' Function to get web page favicon from a url '''
    LARGE_FAVICON = r"<link\srel\=\"(apple-touch-icon-precomposed|apple-touch-icon)\"\s(.*(\/.*)+?|href)\=\".*(\/.*)+?\""
    SMALL_FAVICON = r"<link\srel\=\"(icon|shortcut icon)\"\s(.*(\/.*)+?|href)\=\".*(\/.*)+?\""
    
    import re
    import requests
    from urllib.parse import urlparse

    domain = get_domain(url)
    icon_name = download_path + '/' + domain + '-' + checksum + '.ico'

    regex_result1 = re.search(LARGE_FAVICON, contents)
    regex_result2 = re.search(SMALL_FAVICON, contents)

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
    try:
        r = requests.get(favicon_url, allow_redirects=True)
    except:
        pass

    if r is not None:
        open(icon_name, 'wb').write(r.content)
        return icon_name

def get_web_data(url, file_path=None, download_path='./', checksum='na'):
    ''' Function to get web data '''
    contents = get_web_contents(url)
    title = get_web_title(contents, url)
    icon_name = get_web_favicon(contents, url, download_path, checksum)

    if file_path is not None:
        with open(file_path, "a") as file:
            file.write("\n"+title)
            file.close
    return title, icon_name

def get_web_data_threaded(url, file_path, download_path='./'):
    ''' Function to get web data threaded '''
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(get_web_data, url, file_path, download_path)
        return_value = future.result()
        # print(return_value)
        print(get_fuzzy_timestamp(datetime.now()))

#-------------------------------------------------------------------------------------------------------

def is_valid_url(str):
    '''
    Function to validate if a string is a url
    https://stackoverflow.com/a/60267538/14741406
    https://urlregex.com/
    '''
    URL = r"(^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$)"
    regex = URL
    return validate_string_with_regex(str, regex)

def is_valid_unix_uri(str):
    '''
    Function to validate if a string is a unix url
    https://stackoverflow.com/a/38521489/14741406
    '''
    UNIXPATH = r"^(\/[\w^ ]+)+\/?([\w.])+[^.]$"
    regex = UNIXPATH
    return validate_string_with_regex(str, regex)

def is_valid_email(str):
    '''
    Function to validate if a string is an email url
    '''
    EMAIL = r"(^(mailto\:)?[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    regex = EMAIL
    return validate_string_with_regex(str, regex)

#-------------------------------------------------------------------------------------------------------

def copy_to_clipboard(clipboard_target, file, type=None):
    ''' Function to copy files to clipboard '''
    from subprocess import Popen, PIPE

    try:
        if "url" in type:
            with open(file) as _file:
                data = Popen(['echo', _file.readlines()[0].rstrip("\n").rstrip("\n")], stdout=PIPE)
                Popen(['xclip', '-selection', 'clipboard', '-target', clipboard_target], stdin=data.stdout)
        else:
            Popen(['xclip', '-selection', 'clipboard', '-target', clipboard_target, '-i', file])
        return True
    except:
        return False

def copy_files_to_clipboard(uris):
    ''' Function to copy files to clipboard from a string of uris in file:// format '''
    from subprocess import Popen, PIPE
    try:
        copyfiles = Popen(['xclip', '-selection', 'clipboard', '-target', 'x-special/gnome-copied-files'], stdin=PIPE)
        copyfiles.communicate(str.encode(uris))
        return True
    except:
        return False

def paste_from_clipboard():
    '''
    Function to paste from clipboard based on where the mouse pointer is hovering
    '''
    # ported from Clipped: https://github.com/davidmhewitt/clipped/blob/edac68890c2a78357910f05bf44060c2aba5958e/src/ClipboardManager.vala
    import time

    def perform_key_event(accelerator, press, delay):
        import Xlib
        from Xlib import X
        from Xlib.display import Display
        from Xlib.ext.xtest import fake_input
        from Xlib.protocol.event import KeyPress, KeyRelease
        import time

        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, Gdk, GdkX11

        keysym, modifiers = Gtk.accelerator_parse(accelerator)
        display = Display()
        # root = display.screen().root
        # window = root.query_pointer().child
        # window.set_input_focus(X.RevertToParent, X.CurrentTime)
        # window.configure(stack_mode=X.Above)
        # display.sync()

        keycode = display.keysym_to_keycode(keysym)

        if press:
            event_type = X.KeyPress
        else:
            event_type = X.KeyRelease

        if keycode != 0:
            if 'GDK_CONTROL_MASK' in modifiers.value_names:
                modcode = display.keysym_to_keycode(Gdk.KEY_Control_L)
                fake_input(display, event_type, modcode, delay)

            if 'GDK_SHIFT_MASK' in modifiers.value_names:
                modcode = display.keysym_to_keycode(Gdk.KEY_Shift_L)
                fake_input(display, event_type, modcode, delay)

            fake_input(display, event_type, keycode, delay)
            display.sync()

    perform_key_event("<Control>v", True, 100)
    perform_key_event("<Control>v", False, 0)

#-------------------------------------------------------------------------------------------------------
# functions to encrypt or decrypt files
def do_encryption(action, passphrase, filepath):
    import cryptography
    from cryptography.fernet import Fernet
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from hashlib import sha1
    import base64
    import os

    def key_func(action, passphrase, filepath):
        password = passphrase.encode()
        if action == "encrypt":
            salt = os.urandom(16)
        else:
            with open(filepath, 'rb') as file:
                salt = file.read(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key, salt

    def encrypt(key, salt, filepath):
        fernet = Fernet(key)
        file, ext = os.path.splitext(filepath)
        file = file.split('\\' or '/')[-1]
        encrypted_file = file + "_enc_" + ext

        with open(filepath, 'rb') as file:
            original = file.read()

        try:
            data = fernet.encrypt(original)
            with open(encrypted_file, 'wb') as file:
                file.write(salt)
                file.write(data)
            return True, encrypted_file
        except:
            return False, "encryption failed"
        
    def decrypt(key, filepath):
        fernet = Fernet(key)
        file, ext = os.path.splitext(filepath)
        file = file.split('\\' or '/')[-1]

        with open(filepath, 'rb') as file:
            data = file.read()
        data = data[16:]

        try:
            return True, fernet.decrypt(data)
        except cryptography.fernet.InvalidToken as error:
            return False, "decryption failed {errormsg}".format(errormsg=error)

    encryption_key, salt = key_func(action, passphrase, filepath)
    
    if action == "encrypt":
        return encrypt(encryption_key, salt, filepath)

    if action == "decrypt":
        return decrypt(encryption_key, filepath)

def do_authentication(action, password=None):

    def set_password(password):
        import keyring
        try:
            return True, keyring.set_password("com.github.hezral.clips", "clips", password)
        except:
            return False, keyring.errors

    def get_password():
        import keyring
        try:
            return True, keyring.get_password("com.github.hezral.clips", "clips")
        except:
            return False, keyring.errors

    if action == "get":
        return get_password()
    elif action == "set":
        return set_password(password)
    elif action == "reset":
        return get_password(), set_password(password)

#-------------------------------------------------------------------------------------------------------

def do_webview_screenshot(uri, out_file_path):
    """
    function to load html/url in webview and save snapshot of the full page in png
    uri: can be local uri like a html file, or internet url
    out_file_path: full path to the png file export
    """
    import os
    import chardet
    import gi
    gi.require_version('Gtk', '3.0')
    gi.require_version('WebKit2', '4.0')
    from gi.repository import Gtk, WebKit2, GLib

    def get_snapshot(webview, result, callback, *args):
        snapshot = webview.get_snapshot_finish(result)
        snapshot.write_to_png(out_file_path)
        GLib.idle_add(self_destroy, (webview, offscreen_window))

    def loaded_handler(webview, event, offscreen_window):
        if event.value_name == "WEBKIT_LOAD_FINISHED":
            try:
                webview.get_snapshot(WebKit2.SnapshotRegion.FULL_DOCUMENT, WebKit2.SnapshotOptions.TRANSPARENT_BACKGROUND, None, get_snapshot, None)
            except:
                import traceback
                traceback.print_exc()
                pass

    def self_destroy(data):
        webview = data[0]
        offscreen_window = data[1]
        webview.try_close()
        webview.destroy()
        webview = None
        # del webview
        # print(webview)
        offscreen_window.destroy()
        offscreen_window = None
        # del offscreen_window
        # print(offscreen_window)
        # file.close()
    
    webview = WebKit2.WebView()
    webview.props.zoom_level = 1
    webview.props.expand = True

    file = open(uri, "rb")
    encoding_name = chardet.detect(file.read())["encoding"]
    file.close()

    with open(uri, encoding=encoding_name) as file:
        content  = file.read()

    # file = open(uri, "r", encoding=encoding_name)
    # content = file.read()
    webview.load_html(content)

    alt_file_uri = uri.replace("html", "txt")
    if os.path.exists(alt_file_uri):

        alt_file = open(alt_file_uri, "rb")
        encoding_name = chardet.detect(alt_file.read())["encoding"]
        alt_file.close()

        with open(alt_file_uri, encoding=encoding_name) as alt_file:
            lines  = alt_file.readlines()

        # alt_file = open(uri.replace("html", "txt"), "r", encoding=encoding_name)
        # lines = alt_file.readlines()

        line_char_counts = []
        for line in lines:
            line_chars = line.split(' ')
            line_char_counts.append(len(' '.join(line_chars)))
        
        if max(line_char_counts) < 50:
            snapshot_width = 256
        elif max(line_char_counts) < 100:
            snapshot_width = 512
        else:
            snapshot_width = 1024
    else:
        snapshot_width = 256

    offscreen_window = Gtk.OffscreenWindow()
    offscreen_window.set_size_request(snapshot_width, 160)
    offscreen_window.add(webview)
    offscreen_window.show_all()

    webview.connect("load-changed", loaded_handler, offscreen_window)

#-------------------------------------------------------------------------------------------------------

def open_url_gtk(url):
    ''' Function to view file using default application via Gtk'''
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk
    try:
        Gtk.show_uri_on_window(None, url, Gdk.CURRENT_TIME)
    except:
        print("Unable to launch {url}".format(url=url))
        pass

def open_file_gio(filepath):
    ''' Function to view file using default application via Gio'''
    import gi
    from gi.repository import Gio
    view_file = Gio.File.new_for_path(filepath)
    if view_file.query_exists():
        try:
            Gio.AppInfo.launch_default_for_uri(uri=view_file.get_uri(), context=None)
        except:
            print("Unable to launch {file}".format(file=view_file))
            pass