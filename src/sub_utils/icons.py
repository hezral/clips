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
