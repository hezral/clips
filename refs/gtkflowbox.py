#!/usr/bin/env python3
 
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gio, GdkPixbuf, Gdk, Granite

from math import pi

import os, sys

# 画像が沢山あるディレクトリに書き換えしてください
FOLDER = '/home/adi/.cache/com.github.hezral.clips/cache/'
cache_filedir = FOLDER
#FOLDER = '/home/adi/Downloads/photos'

CSS = """
@keyframes crossfader {
    0% { opacity: 0; } 
    03.33% { opacity: 0; }
    06.66% { opacity: 0; }
    09.99% { opacity: 0; }
    13.33% { opacity: 0; }
    16.65% { opacity: 0.5; }
    100% { opacity: 1; }	
}

grid#clip-container {
    border-style: solid;
    border-width: 1px;
    border-color: rgba(0, 0, 0, 0.22);
    border-radius: 5px;
    animation: crossfader 0.5s ease-in-out forwards;
}

grid#image-container {
    border-radius: 5px;
    background-color: transparent;
}

.clip-container-animated {
    animation: crossfader 0.5s ease-in-out forwards;
}

flowbox {
    padding: 10px;
}

flowboxchild:selected {
    border-radius: 5px;
    box-shadow:
        0 0 0 1px rgba(0,0,0,0.12),
        0 2px 5px  rgba(0,0,0,0.16),
        0 2px 5px  rgba(0,0,0,0.23),
        0 14px 28px  rgba(0,0,0,0);
}

flowboxchild:selected > grid#clip-container {
    border-color: rgba(125, 48, 232, 1);
}

"""

# flowboxchild:selected {
# opacity: 0.5;
# }

# box-shadow:
#         0 0 0 1px rgba(0,0,0,0.12),
#         0 2px 5px  rgba(0,0,0,0.16),
#         0 2px 5px  rgba(0,0,0,0.23),
#         0 14px 28px  rgba(0,0,0,0);
# }

class ClipsContainer(Gtk.Grid):
    def __init__(self, filepath, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.props.halign = self.props.valign = Gtk.Align.FILL
        self.props.name = "clip-container"
        self.set_size_request(190, 150)

        self.imgcontainer = ImageContainer(filepath, filename)
        self.clipinfo = ClipsInfo(filepath, filename)
        #self.attach(self.clipinfo, 0, 0, 1, 1)
        self.attach(self.imgcontainer, 0, 0, 1, 1)


class ClipsInfo(Gtk.EventBox):
    def __init__(self, filepath, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)

        scale = self.get_scale_factor()

        source_icon_cache = os.path.join(cache_filedir.replace("cache","icon"), "web.png")
        icon_size = 24 * scale
        source_icon = Gtk.Image().new_from_icon_name(source_icon_cache, Gtk.IconSize.LARGE_TOOLBAR)
        source_icon.set_pixel_size(icon_size)
        source_icon.props.halign = Gtk.Align.START
        source_icon.props.valign = Gtk.Align.END
        source_icon.props.margin = 4

        label = Gtk.Label()
        label.props.label = "Web"

        grid = Gtk.Grid()
        grid.props.halign = Gtk.Align.CENTER
        grid.props.valign = Gtk.Align.END
        grid.attach(source_icon, 0, 0, 1, 1)
        grid.attach(label, 0, 1, 1, 1)

        revealer = Gtk.Revealer()
        revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        revealer.add(grid)

        self.set_above_child(False)
        self.props.name = "clip-info"
        self.add(revealer)



        # if os.path.exists(source_icon_cache):
        #     pass
        # else:
        #     pass

        # if self.source_icon.find("/") != -1:
        #     source_icon = Gtk.Image().new_from_file(self.source_icon)
        #     try:
        #         new_pixbuf = source_icon.props.pixbuf.scale_simple(24, 24, GdkPixbuf.InterpType.BILINEAR)
        #         source_icon.props.pixbuf = new_pixbuf
        #     except:
        #         source_icon = Gtk.Image().new_from_icon_name("image-missing", Gtk.IconSize.LARGE_TOOLBAR)
        # else:
        #     source_icon = Gtk.Image().new_from_icon_name(self.source_icon, Gtk.IconSize.LARGE_TOOLBAR)


class ImageContainer(Gtk.Grid):
    def __init__(self, filepath, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # width = 190
        # height = 150

        # self.set_size_request(width, height)

        self.pixbuf_original = GdkPixbuf.Pixbuf.new_from_file(filepath)
        self.ratio_h_w = self.pixbuf_original.props.height / self.pixbuf_original.props.width
        self.ratio_w_h = self.pixbuf_original.props.width / self.pixbuf_original.props.height

        self.name = filename
        self.props.has_tooltip = True
        self.props.tooltip_text = "file: " + self.name + "\nwidth: " + str(self.pixbuf_original.props.width) + "\nheight: " + str(self.pixbuf_original.props.height) + "\nratio_h_w: " + str(self.ratio_h_w)
        
        drawing_area = Gtk.DrawingArea()
        drawing_area.props.expand = True
        drawing_area.connect("draw", self.draw)
        drawing_area.props.can_focus = False
 
        self.props.halign = self.props.valign = Gtk.Align.FILL
        self.props.name = "image-container"        
        self.set_size_request(190, 120)
        self.props.expand = True
        self.attach(drawing_area, 0, 0, 1, 2)

        if self.pixbuf_original.get_has_alpha():
            self.get_style_context().add_class(Granite.STYLE_CLASS_CHECKERBOARD)

    def draw(self, drawing_area, cairo_context):
        # Forked and ported from https://github.com/elementary/greeter/blob/master/src/Widgets/BackgroundImage.vala

        scale = self.get_scale_factor()
        width = self.get_allocated_width () * scale
        height = self.get_allocated_height () * scale
        radius = 4 * scale #Off-by-one to prevent light bleed

        pixbuf_fitted = GdkPixbuf.Pixbuf.new(self.pixbuf_original.get_colorspace(), self.pixbuf_original.get_has_alpha(), self.pixbuf_original.get_bits_per_sample(), width, height)

        if int(width * self.ratio_h_w) < height:
            scaled_pixbuf = self.pixbuf_original.scale_simple(int(height * self.ratio_w_h), height, GdkPixbuf.InterpType.BILINEAR)
        else:
            scaled_pixbuf = self.pixbuf_original.scale_simple(width, int(width * self.ratio_h_w), GdkPixbuf.InterpType.BILINEAR)

        if self.pixbuf_original.props.width * self.pixbuf_original.props.height < width * height:
            # Find the offset we need to center the source pixbuf on the destination since its smaller
            y = abs((height - self.pixbuf_original.props.height) / 2)
            x = abs((width - self.pixbuf_original.props.width) / 2)
            final_pixbuf = self.pixbuf_original
        else:
            # Find the offset we need to center the source pixbuf on the destination
            y = abs((height - scaled_pixbuf.props.height) / 2)
            x = abs((width - scaled_pixbuf.props.width) / 2)
            scaled_pixbuf.copy_area(x, y, width, height, pixbuf_fitted, 0, 0)
            # Set coordinates for cairo surface since this has been fitted, it should be (0, 0) coordinate
            y = 0
            x = 0
            final_pixbuf = pixbuf_fitted

        cairo_context.save()
        cairo_context.scale(1.0 / scale, 1.0 / scale)
        cairo_context.new_sub_path()

        # draws top only rounded rectangle
        # cairo_context.arc(width - radius, radius, radius, 0-pi/2, 0) # top-right-corner
        # #cairo_context.line_to(width, height)
        # #cairo_context.line_to(0, height)
        # cairo_context.arc(radius, radius, radius, pi, pi + pi/2) # top-left-corner
    
        # draws rounded rectangle
        cairo_context.arc(width - radius, radius, radius, 0-pi/2, 0) # top-right-corner
        cairo_context.arc(width - radius, height - radius, radius, 0, pi/2) # bottom-right-corner
        cairo_context.arc(radius, height - radius, radius, pi/2, pi) # bottom-left-corner
        cairo_context.arc(radius, radius, radius, pi, pi + pi/2) # top-left-corner
    
        cairo_context.close_path()

        Gdk.cairo_set_source_pixbuf(cairo_context, final_pixbuf, x, y)

        cairo_context.clip()
        cairo_context.paint()
        cairo_context.restore()



# --------------------------------------------------------------------------------------------------------------------------------------------     

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
        flowbox.props.min_children_per_line = 1
        flowbox.props.max_children_per_line = 50
        flowbox.props.homogeneous = False
        flowbox.props.row_spacing = 10
        flowbox.props.column_spacing = 10
        #flowbox.props.margin = 10
        # 指定ディレクトリのファイルを探す
        d = Gio.file_new_for_path(FOLDER)
        enum = d.enumerate_children(Gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE, 0)

        for info in enum:
            fillpath = f'{FOLDER}/{info.get_name()}'
            flowbox.add(ClipsContainer(fillpath, info.get_name()))

        for child in flowbox.get_children():
            child.connect("button-press-event", self.on_child_focus_in, child, "press")
            child.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
            child.get_children()[0].connect("enter-notify-event", self.on_child_focus_in, child, "enter")
            child.get_children()[0].connect("leave-notify-event", self.on_child_focus_in, child, "leave")
        
        scroll = Gtk.ScrolledWindow(child=flowbox)
        scroll.props.hscrollbar_policy = Gtk.PolicyType.NEVER
        # self
        self.add(scroll)
        self.set_size_request(330,480)
        #self.resize(300, 300)
        self.show_all()

    def on_child_focus_in(self, flowbox, eventfocus, flowboxchild, type):

        print(type)

        # if flowboxchild.get_children()[0].clipinfo.get_child_revealed():
        #     flowboxchild.get_children()[0].clipinfo.set_reveal_child(False)
        # else:
        #     flowboxchild.get_children()[0].clipinfo.set_reveal_child(True)
 
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