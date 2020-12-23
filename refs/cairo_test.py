#!/usr/bin/env python
"""Based on cairo-demo/X11/cairo-demo.c"""

import cairo
import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Granite', '1.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf, Gtk, Gdk, Granite

WORKSPACE_WIDTH = 384
WORKSPACE_HEIGHT = 250
WORKSPACE_RADIUS = 4

DOCK_WIDTH = 120
DOCK_HEIGHT = 10
DOCK_RADIUS = 3

PANEL_HEIGHT = 8

OVERLAY_COLOR = Gdk.RGBA(red=0 / 255.0, green=0 / 255.0, blue=0 / 255.0, alpha=0.35)
WORKSPACE_COLOR = Gdk.RGBA(red=33 / 255.0, green=33 / 255.0, blue=33 / 255.0, alpha=1)

file = "/home/adi/.cache/com.github.hezral.clips/cache/4c6dc1c30c998ea530a246d6b028c2d3.png"
width = 190
height = 118

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

class ClipsContainer(Gtk.Grid):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        pixbuf_original = GdkPixbuf.Pixbuf.new_from_file(file)
        pixbuf_scaled = GdkPixbuf.Pixbuf.new_from_file_at_scale(file, width + 20, -1, True)
        dest_pixbuf = GdkPixbuf.Pixbuf.new(pixbuf_original.get_colorspace(), pixbuf_original.get_has_alpha(), pixbuf_original.get_bits_per_sample(), width, height)
        pixbuf_scaled.copy_area(10, 10, width, height, dest_pixbuf, 0, 0)

        drawing_area = Gtk.DrawingArea()
        # drawing_area.set_size_request(190, 118)
        drawing_area.props.expand = True
        #drawing_area.props.halign = self.props.valign = Gtk.Align.FILL
        drawing_area.connect("draw", self.draw, dest_pixbuf)
 
        self.props.halign = self.props.valign = Gtk.Align.FILL
        self.props.name = "clip-container"
        
        self.set_size_request(190, 118)
        self.props.expand = True
        self.props.margin = 20

        box = Gtk.Box()
        box.set_size_request(-1, 32)

        self.attach(drawing_area, 0, 0, 1, 1)
        #self.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), 0, 1, 1, 1)
        #self.attach(box, 0, 2, 1, 1)
        
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

    def draw_rounded(self, area, cr, radius):
        """ draws rectangles with rounded (circular arc) corners """
        from math import pi
        a,b,c,d=area
        cr.arc(a + radius, c + radius, radius, 2*(pi/2), 3*(pi/2))
        cr.arc(b - radius, c + radius, radius, 3*(pi/2), 4*(pi/2))
        cr.arc(b - radius, d - radius, radius, 0*(pi/2), 1*(pi/2))  # ;o)
        cr.arc(a + radius, d - radius, radius, 1*(pi/2), 2*(pi/2))
        cr.close_path()
        cr.stroke()

class MainWindow(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        css = Gtk.CssProvider()
        css.load_from_data(bytes(CSS.encode()))

        clip = ClipsContainer()
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.add(clip)
        #self.set_border_width(20)

        self.set_title("TEST")
        self.resize(250, 250)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()

        
class Example(Gtk.Window):

    def __init__(self):
        super(Example, self).__init__()
        
        self.init_ui()
        self.load_image()
        
        
    def init_ui(self):    

        darea = Gtk.DrawingArea()
        darea.connect("draw", self.on_draw)
        self.add(darea)

        self.set_title("Image")
        self.resize(300, 170)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()
        
        
    def load_image(self):
        
        #self.ims = cairo.ImageSurface.create_from_png("/home/adi/.cache/com.github.hezral.clips/cache/4c6dc1c30c998ea530a246d6b028c2d3.png")

        pixbuf = GdkPixbuf.Pixbuf.new_from_file(file)
        
        cairo_surface = Gdk.cairo_surface_create_from_pixbuf(pixbuf, 1, None)
        self.ims = cairo_surface
            
    def on_draw(self, wid, cr):

        cr.set_source_surface(self.ims, 0, 0)
        cr.paint()
        
    
def main():
    
    #app = Example()
    app = MainWindow()
    Gtk.main()
        
        
if __name__ == "__main__":    
    main()