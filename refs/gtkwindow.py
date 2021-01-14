import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def reveal(*args):
    if revealer.get_child_revealed():
        revealer.set_reveal_child(False)
        revealer1.set_reveal_child(False)
        revealer2.set_reveal_child(True)
    else:
        revealer.set_reveal_child(True)
        revealer1.set_reveal_child(True)
        revealer2.set_reveal_child(False)

header = Gtk.HeaderBar()
header.props.show_close_button = True
header.props.title = "GtkWindow"

label1 = Gtk.Label("Revealer1")
label1.props.expand = True
label2 = Gtk.Label("Revealer2")
label2.props.expand = True

revealer1 = Gtk.Revealer()
revealer1.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
revealer1.add(label1)

revealer2 = Gtk.Revealer()
revealer2.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
revealer2.add(label2)

grid2 = Gtk.Grid()
grid2.props.expand = True
grid2.attach(revealer1, 0, 0, 1, 1)
grid2.attach(revealer2, 0, 1, 1, 1)

revealer = Gtk.Revealer()
revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
revealer.add(grid2)
#revealer.set_reveal_child(True)

button = Gtk.Button(label="Reveal")
button.props.expand = True
button.connect("clicked", reveal)

grid = Gtk.Grid()
grid.props.expand = True
grid.attach(revealer, 0, 0, 1, 1)
grid.attach(button, 0, 1, 1, 1)

win = Gtk.Window()
win.set_size_request(300,250)
win.get_style_context().add_class("rounded")
win.set_titlebar(header)
win.add(grid)

win.show_all()
win.connect("destroy", Gtk.main_quit)



Gtk.main()