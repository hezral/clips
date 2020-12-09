#!/usr/bin/python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GObject
GObject.threads_init()
 
class CalDialog(Gtk.Dialog):
    '''
    Calendar Dialog
    '''
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Select Date", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))
 
        self.set_default_size(300, 200)
 
        self.value = None
 
        box = self.get_content_area()
 
        calendar = Gtk.Calendar()
        #calendar.set_detail_height_rows(1)
        #calendar.set_property("show-details",True)
        calendar.set_detail_func(self.cal_entry)
 
        box.add(calendar)
 
        self.show_all()
 
    def cal_entry(self, calendar, year, month, date):
        #print(year, month, date)
        self.value = calendar.get_date()
 
class FlowBoxWindow(Gtk.Window):
    '''
    Flowbox example mixed with HeaderBar from
    https://python-gtk-3-tutorial.readthedocs.io/en/latest/introduction.html
    '''
    def __init__(self):
        Gtk.Window.__init__(self, title="Calendar Demo")
        self.flowbox = None
        self.set_border_width(10)
        self.set_default_size(400, 250)
 
        header = Gtk.HeaderBar(title="Calendar Demo")
        header.props.show_close_button = True
 
        # Add button to header to display calendar dialog.
        cal_button = Gtk.Button()
        icon_cal = Gio.ThemedIcon(name="gnome-calendar")
        image_cal = Gtk.Image.new_from_gicon(icon_cal, Gtk.IconSize.BUTTON)
        cal_button.add(image_cal)
        cal_button.set_tooltip_text("Pick date")
        cal_button.connect("clicked", self.on_cal_clicked)
        header.pack_start(cal_button)
 
        # Button to exit main window.
        exit_button = Gtk.Button()
        icon_exit = Gio.ThemedIcon(name="exit")
        image_exit = Gtk.Image.new_from_gicon(icon_exit, Gtk.IconSize.BUTTON)
        exit_button.add(image_exit)
        exit_button.set_tooltip_text("Exit")
        exit_button.connect("clicked", self.on_exit_clicked)
        header.pack_start(exit_button)
 
        self.set_titlebar(header)
 
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(30)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_property("vexpand", False)
 
        self.show_all()
 
    def on_cal_clicked(self, widget):
        # Open calender and get user selection,
        dialog = CalDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print(dialog.value) # See terminal.
        # Close calendar.
        dialog.destroy()
 
    def on_exit_clicked(self, widget):
        self.destroy()
 
win = FlowBoxWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()