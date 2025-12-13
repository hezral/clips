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
    """
    Get active application info.
    Note: AT-SPI access is restricted in flatpak sandbox, so this currently
    returns "unknown app" on Wayland. Active window detection works on X11 only.
    """
    desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    source_app = "unknown app"
    source_icon = "application-default-icon"

    print(f"[DEBUG] Desktop environment: {desktop_env}")
    print(f"[DEBUG] Active window detection is not available on Wayland (flatpak sandbox restriction)")

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
    """
    Copy content to clipboard using wl-copy on Wayland.

    Note: The caller should set clipboard_manager._skip_clipboard_monitoring flag
    before calling this to prevent the clipboard monitor from capturing the change.
    """
    print(f"[DEBUG] copy_to_clipboard_wayland: target={clipboard_target}, type={type}, file={file}")

    if shutil.which("wl-copy") is not None:
        try:
            if "url" in type:
                with open(file) as _file:
                    data = _file.readlines()[0].rstrip("\n")
                    # Use Popen to avoid blocking - wl-copy needs to stay running in background
                    print(f"[DEBUG] Starting wl-copy for URL (non-blocking)")
                    subprocess.Popen(["wl-copy", data])
            elif "text/plain" in clipboard_target or "text" in type:
                with open(file, 'r') as f:
                    content = f.read()
                    # Use Popen with PIPE for stdin, write asynchronously
                    print(f"[DEBUG] Starting wl-copy for text (non-blocking)")
                    proc = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
                    # Write to stdin and close it, but don't wait for process to complete
                    proc.stdin.write(content.encode('utf-8'))
                    proc.stdin.close()
            else: # for files, images, etc., pipe file content to wl-copy
                # For images and binary files, read and pipe to stdin
                # Use subprocess.run to ensure data is fully written before returning
                print(f"[DEBUG] Starting wl-copy for image/file with type {clipboard_target}")
                with open(file, 'rb') as f:
                    subprocess.run(["wl-copy", "--type", clipboard_target], stdin=f, check=True)
            print(f"[DEBUG] copy_to_clipboard_wayland: Successfully started wl-copy")
            return True
        except (subprocess.CalledProcessError, OSError, BrokenPipeError) as e:
            print(f"[DEBUG] copy_to_clipboard_wayland: Error: {e}")
            return False
    else:
        print(f"[DEBUG] copy_to_clipboard_wayland: wl-copy not found")
        return False

def copy_files_to_clipboard_wayland(uris):
    if shutil.which("wl-copy") is not None:
        try:
            # wl-copy expects URI list via stdin for text/uri-list type
            # The uris parameter is already in the correct format (newline-separated file:// URIs)
            print(f"[DEBUG] Starting wl-copy for files with text/uri-list")
            proc = subprocess.Popen(["wl-copy", "--type", "text/uri-list"], stdin=subprocess.PIPE)
            proc.stdin.write(uris.encode('utf-8'))
            proc.stdin.close()
            # Don't wait for the process - wl-copy needs to stay alive to serve clipboard
            return True
        except (OSError, BrokenPipeError) as e:
            print(f"[DEBUG] copy_files_to_clipboard_wayland: Error: {e}")
            return False
    else:
        return False
