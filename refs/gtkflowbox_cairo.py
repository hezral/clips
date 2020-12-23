#!/usr/bin/env python3
 
import sys, gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, Gio, GdkPixbuf, WebKit2, Gdk
 
# 画像が沢山あるディレクトリに書き換えしてください
FOLDER = '/home/adi/.cache/com.github.hezral.clips/cache/'

CSS = """
grid#clip-container {
border-radius: 4px;
box-shadow:
        0 0 0 1px rgba(0,0,0,0.12),
        0 2px 5px  rgba(0,0,0,0.16),
        0 2px 5px  rgba(0,0,0,0.23),
        0 14px 28px  rgba(0,0,0,0);
}
"""


class Win(Gtk.ApplicationWindow):
    '''
        サムネイルされた後にウインドウのサイズを変更すると動作が解る
        valign の指定は必須だったけど不要になったみたい
    '''
    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app, title='Py')
        # GtkFlowBox
        flowbox = Gtk.FlowBox()
        flowbox.props.valign = flowbox.props.halign = Gtk.Align.START
        flowbox.props.min_children_per_line = 2
        flowbox.props.max_children_per_line = 10
        flowbox.set_homogeneous(False)
        # 指定ディレクトリのファイルを探す
        d = Gio.file_new_for_path(FOLDER)
        enum = d.enumerate_children(Gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE, 0)
        for info in enum:
            content_type = info.get_content_type()
            if content_type == 'image/jpeg' or content_type == 'image/png' or content_type == 'image/gif':
                fullpath = f'{FOLDER}/{info.get_name()}'
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(fullpath, 100, 100, True)
                image = Gtk.Image(pixbuf=pixbuf)
                flowbox.add(image)

        scroll = Gtk.ScrolledWindow(child=flowbox)
        self.add(scroll)
        self.set_size_request(600, 200)

        self.show_all()

class ClipsContainer(Gtk.Grid):
    def __init__(self, file, *args, **kwargs):
        super().__init__(*args, **kwargs)

        pixbuf_original = GdkPixbuf.Pixbuf.new_from_file(file)
        pixbuf_scaled = GdkPixbuf.Pixbuf.new_from_file_at_scale(file, width + 20, -1, True)
        dest_pixbuf = GdkPixbuf.Pixbuf.new(pixbuf_original.get_colorspace(), pixbuf_original.get_has_alpha(), pixbuf_original.get_bits_per_sample(), width, height)
        pixbuf_scaled.copy_area(10, 10, width, height, dest_pixbuf, 0, 0)

        drawing_area = Gtk.DrawingArea()
        # drawing_area.set_size_request(190, 118)
        drawing_area.props.expand = True
        drawing_area.props.halign = self.props.valign = Gtk.Align.FILL
        drawing_area.connect("draw", self.draw, dest_pixbuf)

    def draw(self, drawing_area, cairo_context, pixbuf):

        #print(drawing_area)
        height_allocated = drawing_area.get_parent().get_allocated_height()
        width_allocated = drawing_area.get_parent().get_allocated_width()

        print(self.draw.__name__, width_allocated, height_allocated)

        # clip mask
        Granite.DrawingUtilities.cairo_rounded_rectangle(cairo_context, 0, 0, width_allocated, height_allocated, WORKSPACE_RADIUS)
        cairo_context.clip()

        cairo_surface = Gdk.cairo_surface_create_from_pixbuf(pixbuf, 1, None)
        cairo_context.set_source_surface(cairo_surface, 0, 0)
        cairo_context.paint()

        # # border highlights
        # COLOR = OVERLAY_COLOR
        # cairo_context.set_source_rgba(COLOR.red, COLOR.green, COLOR.blue, 0.5)
        # cairo_context.set_line_width(1)
        # Granite.DrawingUtilities.cairo_rounded_rectangle(cairo_context, 0, 0, width, height, WORKSPACE_RADIUS)
        # cairo_context.stroke()
 
class App(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)
        css = Gtk.CssProvider()
        css.load_from_data(bytes(CSS.encode()))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

 
    def do_startup(self):
        Gtk.Application.do_startup(self)
        Win(self)
 
    def do_activate(self):
        self.props.active_window.present()
 
app = App()
app.run(sys.argv)