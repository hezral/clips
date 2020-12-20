#!/usr/bin/env python3
 
import sys, gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, Gio, GdkPixbuf, WebKit2
 
# 画像が沢山あるディレクトリに書き換えしてください
FOLDER = '/home/adi/.cache/com.github.hezral.clips/cache/'
 
class Win(Gtk.ApplicationWindow):
    '''
        サムネイルされた後にウインドウのサイズを変更すると動作が解る
        valign の指定は必須だったけど不要になったみたい
    '''
    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app, title='Py')
        # GtkFlowBox
        flowbox = Gtk.FlowBox()
        flowbox.props.valign = flowbox.props.halign = Gtk.Align.START
        flowbox.props.min_children_per_line = 2
        flowbox.props.max_children_per_line = 10
        flowbox.set_homogeneous(False)
        # 指定ディレクトリのファイルを探す
        d = Gio.file_new_for_path(FOLDER)
        enum = d.enumerate_children(Gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE, 0)
        for info in enum:
            content_type = info.get_content_type()
            if content_type == 'image/jpeg' or content_type == 'image/png' or content_type == 'image/gif':
                fullpath = f'{FOLDER}/{info.get_name()}'
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(fullpath, 100, 100, True)
                image = Gtk.Image(pixbuf=pixbuf)
                flowbox.add(image)
            if content_type == 'text/html':
                fullpath = f'{FOLDER}/{info.get_name()}'
                file = open(fullpath, "r")
                content = file.read()
                webview = WebKit2.WebView()
                webview.load_html(content)
                flowbox.add(webview)
        #scroll = Gtk.ScrolledWindow(child=flowbox)
        # self
        self.add(flowbox)
        #self.set_size_request(600,300)
        #self.resize(300, 300)
        self.show_all()
 
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