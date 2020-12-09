#!/usr/bin/env python3
 
import sys, gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, GtkSource
 
TEXTVIEW_CSS = '''
#MySourceView {
    font: 10pt Monospace;
}'''
 
class Win(Gtk.ApplicationWindow):
    '''
        CSS については別ページにて
    '''
    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app, title='Py')
        # GtkTextView
        view = GtkSource.View(show_line_numbers=True, name='MySourceView')
        # CSS
        provider = Gtk.CssProvider()
        provider.load_from_data(TEXTVIEW_CSS.encode('utf-8'))
        view.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        #
        # Python3 の色分けを割り当て
        #
        lang_man = GtkSource.LanguageManager()
        lang = lang_man.guess_language(None, 'text/html')
        buf = view.get_buffer()
        buf.set_language(lang)
        #
        # このスクリプト自身を読み込む
        with open("/home/adi/.cache/com.github.hezral.clips/cache/2afc3a0fce93f7950a9254c6b2903f36.html") as f:
        # with open(__file__) as f:
            s = f.read()
            buf.set_text(s)
        # GtkScrolledWindow
        sw = Gtk.ScrolledWindow(child=view)
        self.add(sw)
        self.resize(300, 300)
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