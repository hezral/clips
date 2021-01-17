#!/usr/bin/env python3
 
import sys, gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GdkPixbuf, Gdk
 
# 画像が沢山あるディレクトリに書き換えしてください
PICTURES = '/home/adi/.cache/com.github.hezral.clips/cache/'
 
class Win(Gtk.ApplicationWindow):
    '''
        サムネイルされた後にウインドウのサイズを変更すると動作が解る
        valign の指定は必須だったけど不要になったみたい
    '''
    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app, title='Py')
        # GtkFlowBox
        flowbox = Gtk.FlowBox()#valign=Gtk.Align.START)
        # 指定ディレクトリのファイルを探す
        d = Gio.file_new_for_path(PICTURES)
        enum = d.enumerate_children(Gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE, 0)
        for info in enum:
            content_type = info.get_content_type()
            if content_type == 'image/jpeg' or content_type == 'image/png':
                fullpath = f'{PICTURES}/{info.get_name()}'
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(fullpath, 100, 100, True)
                image = Gtk.Image(pixbuf=pixbuf)
                flowbox.add(Child(image, fullpath))
        scroll = Gtk.ScrolledWindow(child=flowbox)
        # self
        self.add(scroll)
        self.resize(400, 300)
        self.show_all()
 
class Child(Gtk.EventBox):
    def __init__(self, image, fullpath, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
        # self.add_events(Gdk.EventMask.LEAVE_NOTIFY_MASK)
        # self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        # self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)

        # box = Gtk.Box()
        # box.add(image)
        self.connect("enter-notify-event", self.entering)
        self.path = fullpath.split("/")[-1]
        self.add(image)
    
    def entering(self, widget, eventcrossing):
        print(self.path)


class App(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)
 
    def do_startup(self):
        Gtk.Application.do_startup(self)
        Win(self)
 
    def do_activate(self):
        self.props.active_window.present()
 
app = App()
app.run(sys.argv)