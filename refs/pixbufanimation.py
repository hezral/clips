#!/usr/bin/env python
"""Based on cairo-demo/X11/cairo-demo.c"""

import cairo
import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Granite', '1.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf, Gtk, Gdk, GLib
import cairo

filepath = "/home/adi/Downloads/giphy.gif"

class Example(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.pixbuf_original = GdkPixbuf.PixbufAnimation.new_from_file(filepath)
        self.pixbuf_original_height = self.pixbuf_original.get_height()
        self.pixbuf_original_width = self.pixbuf_original.get_width()
        self.ratio_h_w = self.pixbuf_original_height / self.pixbuf_original_width
        self.ratio_w_h = self.pixbuf_original_width / self.pixbuf_original_height

        self.iter = self.pixbuf_original.get_iter()

        self.timer_func()

        drawing_area = Gtk.DrawingArea()
        drawing_area.props.expand = True
        drawing_area.connect("draw", self.draw)
        drawing_area.props.can_focus = False
 
        self.add(drawing_area)
        self.resize(700, 400)
        self.set_border_width(10)
        self.set_keep_above(True)
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()

    def timer_func(self, *args):
        self.iter.advance()
        GLib.timeout_add(self.iter.get_delay_time(), self.timer_func, None)
        self.queue_draw()
   
    def draw(self, drawing_area, cairo_context):
        from math import pi

        scale = self.get_scale_factor()
        width = self.get_allocated_width() * scale
        height = self.get_allocated_height() * scale
        radius = 6 * scale #Off-by-one to prevent light bleed

        pixbuf = GdkPixbuf.PixbufAnimationIter.get_pixbuf(self.iter)
        pixbuf_fitted = GdkPixbuf.Pixbuf.new(pixbuf.get_colorspace(), pixbuf.get_has_alpha(), pixbuf.get_bits_per_sample(), width, height)

        if int(width * self.ratio_h_w) < height:
            scaled_pixbuf = pixbuf.scale_simple(int(height * self.ratio_w_h), height, GdkPixbuf.InterpType.BILINEAR)
        else:
            scaled_pixbuf = pixbuf.scale_simple(width, int(width * self.ratio_h_w), GdkPixbuf.InterpType.BILINEAR)

        if self.pixbuf_original_width * self.pixbuf_original_height < width * height:
            # Find the offset we need to center the source pixbuf on the destination since its smaller
            y = abs((height - self.pixbuf_original_height) / 2)
            x = abs((width - self.pixbuf_original_width) / 2)
            final_pixbuf = self.pixbuf_original
        else:
            # Find the offset we need to center the source pixbuf on the destination
            y = abs((height - scaled_pixbuf.props.height) / 2)
            x = abs((width - scaled_pixbuf.props.width) / 2)
            scaled_pixbuf.copy_area(x, y, width, height, pixbuf_fitted, 0, 0)
            # Set coordinates for cairo surface since this has been fitted, it should be (0, 0) coordinate
            x = y = 0
            final_pixbuf = pixbuf_fitted

        cairo_context.set_operator(cairo.Operator.SOURCE)

        Gdk.cairo_set_source_pixbuf(cairo_context, final_pixbuf, x, y)
        # cairo_context.paint()

        cairo_context.save()
        cairo_context.scale(1.0 / scale, 1.0 / scale)
        cairo_context.new_sub_path()

        # draws rounded rectangle
        cairo_context.arc(width - radius, radius, radius, 0-pi/2, 0) # top-right-corner
        cairo_context.arc(width - radius, height - radius, radius, 0, pi/2) # bottom-right-corner
        cairo_context.arc(radius, height - radius, radius, pi/2, pi) # bottom-left-corner
        cairo_context.arc(radius, radius, radius, pi, pi + pi/2) # top-left-corner
    
        cairo_context.close_path()
        cairo_context.clip()
        cairo_context.paint()
        cairo_context.restore()
    
def main():
    app = Example()
    Gtk.main()
        
if __name__ == "__main__":    
    main()