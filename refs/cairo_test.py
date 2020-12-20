#!/usr/bin/env python
"""Based on cairo-demo/X11/cairo-demo.c"""

import cairo
import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Gdk, Granite

class WorkspaceArea(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        drawing_area = Gtk.DrawingArea()
        drawing_area.set_size_request(WORKSPACE_WIDTH, WORKSPACE_HEIGHT)
        drawing_area.props.expand = True
        drawing_area.props.halign = self.props.valign = Gtk.Align.FILL
        drawing_area.connect("draw", self.draw)

        self.props.name = "workspace-area"
        self.add(drawing_area)

        
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
        
        self.ims = cairo.ImageSurface.create_from_png("/home/adi/.cache/com.github.hezral.clips/cache/4c6dc1c30c998ea530a246d6b028c2d3.png")
        
            
    def on_draw(self, wid, cr):

        cr.set_source_surface(self.ims, 0, 0)
        cr.paint()
        
    
def main():
    
    app = Example()
    Gtk.main()
        
        
if __name__ == "__main__":    
    main()