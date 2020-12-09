import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')

from gi.repository import Gtk, WebKit2, Gdk
import urllib.parse


uri = "/home/adi/.cache/com.github.hezral.clips/cache/ece26450ebf51d94044dc0bd390582ef.html"
file = open(uri, "r")
content = file.read()
print(type)

window = Gtk.Window()
window.connect("destroy", Gtk.main_quit)
window.set_size_request(800, 500)



scrolled_window = Gtk.ScrolledWindow()
scrolled_window.props.expand = True

webview = WebKit2.WebView()
#webview.load_uri("https://google.cl")
webview.props.zoom_level = 0.8
webview.load_html(content)
#webview.set_background_color(Gdk.RGBA(255,255,255,0))
webview.props.expand = True


image = Gtk.Image().new_from_icon_name("preferences-desktop-wallpaper", Gtk.IconSize.DND)


grid = Gtk.Grid()
grid.props.expand = True
grid.props.row_spacing = 10
grid.attach(image, 0, 0, 1, 1)
grid.attach(webview, 0, 1, 1, 1)



def get_snapshot(webview, result, callback, *args):
    """
        Set snapshot on main image
        @param webview as WebKit2.WebView
        @param result as Gio.AsyncResult
        @return cairo.Surface
    """
    ART_RATIO = 1.5  # ArtSize.START_WIDTH / ArtSize.START_HEIGHT
    try:
        snapshot = webview.get_snapshot_finish(result)
        # Set start image scale factor
        ratio = snapshot.get_width() / snapshot.get_height()
        if ratio > ART_RATIO:
            factor = ArtSize.START_HEIGHT / snapshot.get_height()
        else:
            factor = ArtSize.START_WIDTH / snapshot.get_width()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                     ArtSize.START_WIDTH,
                                     ArtSize.START_HEIGHT)
        context = cairo.Context(surface)
        context.scale(factor, factor)
        context.set_source_surface(snapshot, factor, 0)
        context.paint()
        callback(surface, *args)
    except Exception as e:
        print("get_snapshot():", e)
        callback(None, *args)


def on_snapshot(self, pixbuf):
        """
            Set snapshot
            @param surface as cairo.Surface
        """
        #self.__image.set_from_surface(surface)
        print(pixbuf)


window.add(grid)
window.show_all()
print(webview.get_allocated_width(), webview.get_allocated_height())
window.resize(webview.get_allocated_width(), webview.get_allocated_height())

# webview.get_snapshot(
#                     WebKit2.SnapshotRegion.FULL_DOCUMENT,
#                     WebKit2.SnapshotOptions.TRANSPARENT_BACKGROUND,
#                     None,
#                     get_snapshot,
#                     on_snapshot)






Gtk.main()