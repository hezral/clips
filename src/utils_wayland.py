# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2023 Your Name <your@email.com>

import os
import shutil
import subprocess
from pydbus import SessionBus
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, GLib

def get_all_apps(app=None):
    ''' Function to get all apps installed on system using desktop files in standard locations for flatpak, snap, native '''
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
    
    for dir in desktop_file_dirs:
        if os.path.exists(dir):
            d = Gio.file_new_for_path(dir)
            files = d.enumerate_children("standard::*", 0)
            for desktop_file in files:
                if ".desktop" in desktop_file.get_name():
                    desktop_file_path = ""
                    
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
                            print("Unable to read {0} application info".format(desktop_file_path))

    if app != None:
        return all_apps[app]
    else:
        return all_apps

def get_active_appinfo_wayland(data=None):
    desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    source_app = None
    source_icon = None

    if "gnome" in desktop_env or "pantheon" in desktop_env:
        try:
            bus = SessionBus()
            shell_proxy = bus.get("org.gnome.Shell")
            focused_app = shell_proxy.get_focus_app()
            if focused_app:
                all_apps = get_all_apps()
                for app_name, app_info in all_apps.items():
                    if focused_app.get_id() in app_info[3]: # app_info[3] is the desktop file path
                        source_app = app_name.split("#")[0]
                        source_icon = app_info[0]
                        break
        except Exception as e:
            print(f"Failed to get active app info from GNOME Shell: {e}")
            
    if source_app is None:
        source_app = "unknown app"
        source_icon = "application-default-icon"
        
    return source_app, source_icon

def paste_from_clipboard_wayland():
    if shutil.which("wtype") is not None:
        try:
            subprocess.run(["wtype", "-M", "ctrl", "-P", "v", "-m", "ctrl"], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    else:
        return False

def copy_to_clipboard_wayland(clipboard_target, file, type=None):
    if shutil.which("wl-copy") is not None:
        try:
            if "url" in type:
                with open(file) as _file:
                    data = _file.readlines()[0].rstrip("\n")
                    subprocess.run(["wl-copy", data], check=True)
            elif "text/plain" in clipboard_target or "text" in type:
                with open(file, 'r') as f:
                    content = f.read()
                    subprocess.run(["wl-copy"], input=content.encode('utf-8'), check=True)
            else: # for files, images, etc., wl-copy directly from file
                subprocess.run(["wl-copy", "--type", clipboard_target, "-f", file], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    else:
        return False

def copy_files_to_clipboard_wayland(uris):
    if shutil.which("wl-copy") is not None:
        try:
            # wl-copy expects file URIs directly
            file_paths = []
            for uri in uris.split('\n'):
                if uri.startswith('file://'):
                    file_paths.append(uri[7:]) # remove "file://"
            
            # wl-copy can take multiple files as arguments
            subprocess.run(["wl-copy", "--type", "text/uri-list"] + [f"file://{p}" for p in file_paths], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    else:
        return False
