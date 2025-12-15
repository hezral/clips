_apps_cache = None

def get_all_apps(app=None):
    ''' Function to get all apps installed on system using desktop files in standard locations for flatpak, snap, native '''
    import gi, os, logging
    from gi.repository import Gio, GLib
    from datetime import datetime
    from ..constants import APP_ID
    
    global _apps_cache
    if _apps_cache is not None:
        if app is not None:
            return _apps_cache.get(app)
        return _apps_cache

    logger = logging.getLogger(APP_ID)

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
                    
                    # print(desktop_file.get_content_type(), os.path.join(dir, desktop_file.get_name()))

                    if "application/x-desktop" in desktop_file.get_content_type():
                        desktop_file_path = os.path.join(dir, desktop_file.get_name())

                    if "inode/symlink" in desktop_file.get_content_type():
                        if ".local/share/flatpak/exports/share/applications" in dir:
                            desktop_file_path = os.path.join(GLib.get_home_dir(), ".local/share/flatpak", os.path.realpath(desktop_file.get_symlink_target()).replace("/home/", ""))

                    if desktop_file_path != "":

                        try:
                            kf = GLib.KeyFile()
                            if not kf.load_from_file(desktop_file_path, GLib.KeyFileFlags.NONE):
                                continue

                            try:
                                app_name = kf.get_string("Desktop Entry", "Name")
                            except:
                                app_name = "unknown"
                            
                            try:
                                app_icon = kf.get_string("Desktop Entry", "Icon")
                            except:
                                app_icon = "application-default-icon"

                            try:
                                startup_wm_class = kf.get_string("Desktop Entry", "StartupWMClass")
                            except:
                                startup_wm_class = None

                            try:
                                no_display = kf.get_boolean("Desktop Entry", "NoDisplay")
                            except:
                                no_display = False
                            
                            try:
                                app_exec = kf.get_string("Desktop Entry", "Exec")
                            except:
                                app_exec = None
                            
                            try:
                                flatpak_str = kf.get_string("Desktop Entry", "X-Flatpak")
                                flatpak = True if flatpak_str else False
                            except:
                                flatpak = False

                            if app_name in all_apps:
                                duplicate_app += 1
                                app_name = app_name + "#{0}".format(str(duplicate_app))
                            
                            all_apps[app_name] = [app_icon, startup_wm_class, no_display, desktop_file_path, app_exec, flatpak]

                        except Exception as e:
                            logger.error(f"{datetime.now()} Unable to read {desktop_file_path} application info: {e}")
    
    _apps_cache = all_apps

    if app != None:
        return all_apps.get(app)
    else:
        return all_apps

def get_appinfo(app):
    all_apps = get_all_apps()
    try:
        return app, all_apps[app][0]
    except:
        return "not-found", "application-default-icon"
