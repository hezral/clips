#!/usr/bin/env python3
 
import sys, gi
gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gio, GdkPixbuf, Gdk, Granite
from math import pi


# 画像が沢山あるディレクトリに書き換えしてください
FOLDER = '/home/adi/.cache/com.github.hezral.clips/cache/'
FOLDER = '/home/adi/Downloads/photos'


CSS = """
grid#clip-container {
border-radius: 4px;
box-shadow:
        0 0 0 1px rgba(0,0,0,0.12),
        0 2px 5px  rgba(0,0,0,0.16),
        0 2px 5px  rgba(0,0,0,0.23),
        0 14px 28px  rgba(0,0,0,0);
}

flowboxchild:selected {
opacity: 0.5;
}
"""

class ClipsContainer(Gtk.Grid):
    def __init__(self, filepath, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.props.halign = self.props.valign = Gtk.Align.FILL
        self.props.name = "clip-container"
        self.set_size_request(190, 150)

        imgcontainer = ImageContainer(filepath, filename)

        self.attach(imgcontainer, 0, 0, 1, 1)


class ImageContainer(Gtk.Grid):
    def __init__(self, filepath, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_size_request(190, 150)
        
        # scale = self.get_scale_factor()
        # # width = 190 * scale
        # # height = 118 * scale
        # width = self.get_allocated_width () * scale
        # height = self.get_allocated_height () * scale
        # radius = 5 * scale

        pixbuf_original = GdkPixbuf.Pixbuf.new_from_file(filepath)
        # pixbuf_fitted = GdkPixbuf.Pixbuf.new(pixbuf_original.get_colorspace(), pixbuf_original.get_has_alpha(), pixbuf_original.get_bits_per_sample(), width, height)

        # full_ratio = pixbuf_original.props.height / pixbuf_original.props.width
        
        # print(pixbuf_original.props.height, pixbuf_original.props.width)

        # if int(width * full_ratio) < height:
        #     scaled_pixbuf = pixbuf_original.scale_simple(int(width * (1 / full_ratio)), height, GdkPixbuf.InterpType.BILINEAR)
        # else:
        #     scaled_pixbuf = pixbuf_original.scale_simple(width, int(width * full_ratio), GdkPixbuf.InterpType.BILINEAR)

        # # Find the offset we need to center the source pixbuf on the destination
        # y = abs((height - scaled_pixbuf.props.height) / 2)
        # x = abs((width - scaled_pixbuf.props.width) / 2)

        # #print(x, y)

        # scaled_pixbuf.copy_area (x, y, width, height, pixbuf_fitted, 0, 0)

        # print("full_ratio:", full_ratio, "pixbuf_fitted:", pixbuf_fitted.props.width, pixbuf_fitted.props.height)

        drawing_area = Gtk.DrawingArea()
        drawing_area.props.expand = True
        drawing_area.connect("draw", self.draw, pixbuf_original)
        drawing_area.props.can_focus = False
 
        self.props.halign = self.props.valign = Gtk.Align.FILL
        self.props.name = "image-container"        
        self.set_size_request(190, 120)
        self.props.expand = True
        self.attach(drawing_area, 0, 0, 1, 2)

    def draw(self, drawing_area, cairo_context, pixbuf):

        scale = self.get_scale_factor()
        width = self.get_allocated_width () * scale
        height = self.get_allocated_height () * scale
        radius = 5 * scale

        #pixbuf_original = GdkPixbuf.Pixbuf.new_from_file(filepath)
        pixbuf_original = pixbuf

        full_ratio = pixbuf_original.props.height / pixbuf_original.props.width
        
        pixbuf_fitted = GdkPixbuf.Pixbuf.new(pixbuf_original.get_colorspace(), pixbuf_original.get_has_alpha(), pixbuf_original.get_bits_per_sample(), width, height)
        
        print(full_ratio)

        if int(width * full_ratio) < height:
            scaled_pixbuf = pixbuf_original.scale_simple(int(width * (1 / full_ratio)), height, GdkPixbuf.InterpType.BILINEAR)
        else:
            scaled_pixbuf = pixbuf_original.scale_simple(width, int(width * full_ratio), GdkPixbuf.InterpType.BILINEAR)

        # Find the offset we need to center the source pixbuf on the destination
        y = abs((height - scaled_pixbuf.props.height) / 2)
        x = abs((width - scaled_pixbuf.props.width) / 2)

        print(x, y)

        scaled_pixbuf.copy_area (x, y, width, height, pixbuf_fitted, 0, 0)

        print(pixbuf_fitted.props.width, pixbuf_fitted.props.height)

        cairo_context.save()
        cairo_context.scale (1.0 / scale, 1.0 / scale)
        cairo_context.new_sub_path()
        cairo_context.arc (width - radius, radius, radius, 0-pi/2, 0)
        cairo_context.line_to (width, height)
        cairo_context.line_to (0, height)

        cairo_context.arc (radius, radius, radius, pi, pi + pi/2)
        cairo_context.close_path ()
        Gdk.cairo_set_source_pixbuf (cairo_context, pixbuf_fitted, 0, 0)
        cairo_context.clip ()
        cairo_context.paint ()
        cairo_context.restore ()


        # height_allocated = drawing_area.get_parent().get_allocated_height()
        # width_allocated = drawing_area.get_parent().get_allocated_width()

        # aspect_ratio = pixbuf.props.width / pixbuf.props.height
        # #aspect_ratio = pixbuf.props.height / pixbuf.props.width
        # #aspect_ratio = 190  / 118

        # width = width_allocated
        # height = int(width_allocated * aspect_ratio)
        # #height = height_allocated

        # pixbuf_scaled = pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)

        # print(self.props.name, "w_a", width_allocated, "h_a", height_allocated, "w:", width * aspect_ratio, "h", height, "ratio:", aspect_ratio, "o_w:", pixbuf.props.width, "o_h:", pixbuf.props.height)
        
        # # clip mask
        # Granite.DrawingUtilities.cairo_rounded_rectangle(cairo_context, 0, 0, width, height, 4)
        # cairo_context.clip()

        # cairo_surface = Gdk.cairo_surface_create_from_pixbuf(pixbuf_scaled, 1, None)
        # cairo_context.set_source_surface(cairo_surface, 0, 0)
        # cairo_context.paint()

class Win(Gtk.ApplicationWindow):
    '''
        サムネイルされた後にウインドウのサイズを変更すると動作が解る
        valign の指定は必須だったけど不要になったみたい
    '''
    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app, title='Py')
        # GtkFlowBox
        flowbox = Gtk.FlowBox()
        flowbox.props.valign = Gtk.Align.START
        flowbox.props.halign = Gtk.Align.FILL
        flowbox.props.min_children_per_line = 2
        flowbox.props.max_children_per_line = 50
        flowbox.props.homogeneous = False
        flowbox.props.row_spacing = 10
        flowbox.props.column_spacing = 10
        flowbox.props.margin = 10
        # 指定ディレクトリのファイルを探す
        d = Gio.file_new_for_path(FOLDER)
        enum = d.enumerate_children(Gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE, 0)


        for info in enum:
            fillpath = f'{FOLDER}/{info.get_name()}'

            flowbox.add(ClipsContainer(fillpath, info.get_name()))

            # if content_type == 'image/jpeg' or content_type == 'image/png' or content_type == 'image/gif':
            #     fullpath = f'{FOLDER}/{info.get_name()}'
            #     pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(fullpath, 100, 100, True)
            #     image = Gtk.Image(pixbuf=pixbuf)
            #     flowbox.add(image)

            # if content_type == 'text/html':
            #     fullpath = f'{FOLDER}/{info.get_name()}'
            #     file = open(fullpath, "r")
            #     content = file.read()
            #     webview = WebKit2.WebView()
            #     webview.load_html(content)
            #     flowbox.add(webview)
        scroll = Gtk.ScrolledWindow(child=flowbox)
        # self
        self.add(scroll)
        self.set_size_request(600,600)
        #self.resize(300, 300)
        self.show_all()
 
class App(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)
        css = Gtk.CssProvider()
        css.load_from_data(bytes(CSS.encode()))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # #applicationwindow theme
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", False)
 
    def do_startup(self):
        Gtk.Application.do_startup(self)
        Win(self)
 
    def do_activate(self):
        self.props.active_window.present()
 
app = App()
app.run(sys.argv)