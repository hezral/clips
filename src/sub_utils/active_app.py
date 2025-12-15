from .app_data import get_all_apps
from .session import is_wayland_session
from .wayland_utils import get_active_appinfo_wayland
import os

def get_active_appinfo(data=None, app=None):
    """
    Get active application info using the unified AT-SPI window manager.
    Falls back to legacy X11 method if window manager not available.
    """
    # Use window_manager if available (works on both X11 and Wayland with AT-SPI)
    if app and hasattr(app, 'window_manager') and app.window_manager:
        app_name = None
        app_name = app.window_manager.last_seen.get('title')

        if hasattr(app, 'logger'):
            app.logger.debug(f"get_active_appinfo: window_manager available, app_name: {app_name}")
        if app_name:
            all_apps = get_all_apps()
            # all_apps is a dict where keys are app names (strings) and values are lists:
            # [app_icon, startup_wm_class, no_display, desktop_file_path, app_exec, flatpak]

            # First try: exact match on display name
            for app_key, app_info in all_apps.items():
                if app_key.lower() == app_name.lower():
                    app_icon = app_info[0]
                    if hasattr(app, 'logger'):
                        app.logger.debug(f"get_active_appinfo: Found matching app by name: {app_key}")
                    return app_key, app_icon

            # Second try: match against desktop file name (app ID)
            # AT-SPI often returns app ID like "io.elementary.terminal" which matches the .desktop filename
            for app_key, app_info in all_apps.items():
                desktop_file_path = app_info[3]  # Index 3 is desktop_file_path
                if desktop_file_path:
                    # Extract filename without .desktop extension
                    desktop_filename = os.path.basename(desktop_file_path)
                    if desktop_filename.endswith('.desktop'):
                        app_id = desktop_filename[:-8]  # Remove .desktop
                        if app_id.lower() == app_name.lower():
                            app_icon = app_info[0]
                            if hasattr(app, 'logger'):
                                app.logger.debug(f"get_active_appinfo: Found matching app by desktop ID: {app_key} (from {app_id})")
                            return app_key, app_icon

            # App name found but not in installed apps list
            if hasattr(app, 'logger'):
                app.logger.debug(f"get_active_appinfo: App name '{app_name}' not in installed apps, using default icon")
            return app_name, 'application-default-icon'
    elif app and hasattr(app, 'logger'):
        app.logger.debug(f"get_active_appinfo: window_manager not available or not initialized")

    # Fall back to legacy methods
    if is_wayland_session():
        if app and hasattr(app, 'logger'):
            app.logger.debug("get_active_appinfo: Falling back to Wayland method")
        return get_active_appinfo_wayland(data)
    else:
        if app and hasattr(app, 'logger'):
            app.logger.debug("get_active_appinfo: Falling back to X11 method")
        return _get_active_appinfo_xlib(data)

def _get_active_appinfo_xlib(data=None):
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
