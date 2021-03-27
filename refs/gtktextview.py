#!/usr/bin/env python3
 
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class TextViewWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="TextView Example")

        self.set_default_size(500, 350)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)

        toolbar = Gtk.Toolbar()
        open_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_OPEN)
        open_btn.connect("clicked", self.on_open_clicked)
        toolbar.insert(open_btn, 0)
        save_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_SAVE)
        save_btn.connect("clicked", self.on_save_clicked)
        toolbar.insert(save_btn, 1)
        self.box.pack_start(toolbar, False, True, 0)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        scrolledwindow.add(self.textview)
        self.box.pack_start(scrolledwindow, True, True, 0)

    def on_open_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/richtext")
        # dialog.add_filter(filter_text)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            selected_file = dialog.get_filename()
            with open(selected_file, 'rb') as f:
                data = f.read()
                print(type(data))
                self.textbuffer.set_text(data)
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

        dialog.destroy()

    def on_save_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Save file", self,
        Gtk.FileChooserAction.SAVE,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
         Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            save_file = dialog.get_filename()
            start_iter = self.textbuffer.get_start_iter()
            end_iter = self.textbuffer.get_end_iter()
            text = self.textbuffer.get_text(start_iter, end_iter, True)   
            with open(save_file, 'w') as f:
                f.write(text)
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

        dialog.destroy()

win = TextViewWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()