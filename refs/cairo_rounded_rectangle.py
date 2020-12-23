def draw_rounded(cr, area, radius):
    """ draws rectangles with rounded (circular arc) corners """
    from math import pi
    a,b,c,d=area
    cr.arc(a + radius, c + radius, radius, 2*(pi/2), 3*(pi/2))
    cr.arc(b - radius, c + radius, radius, 3*(pi/2), 4*(pi/2))
    cr.arc(b - radius, d - radius, radius, 0*(pi/2), 1*(pi/2))  # ;o)
    cr.arc(a + radius, d - radius, radius, 1*(pi/2), 2*(pi/2))
    cr.close_path()
    cr.stroke()

################################################################

### EXAMPLE
import cairo, Image

w,h = 800, 600
offset = 100
fig_size = (w,h)

# an area with coordinates of
# (top, bottom, left, right) edges in absolute coordinates:
inside_area = (offset, w-offset, offset, h-offset)

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *fig_size)
cr = cairo.Context(surface)
cr.set_line_width(3)
cr.set_source_rgb(1,1,1)

draw_rounded(cr, inside_area, 150)

file = "/home/adi/.cache/com.github.hezral.clips/cache/4c6dc1c30c998ea530a246d6b028c2d3.png"

im = Image.frombuffer("RGBA",
                       fig_size,
                       surface.get_data(),
                       "raw",
                       "BGRA",
                       0,1)
im.show()