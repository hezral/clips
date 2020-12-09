#!/usr/bin/env python3  
# section 115  
# Created by xiaosanyu at 16/6/14  
TITLE = "SearchEntry"  
DESCRIPTION = """  
Gtk.SearchEntry is a subclass of Gtk.Entry that has been tailored for use as a search entry.  
SearchEntry' signal  
"""  
#https://www.geek-share.com/detail/2681027539.html
import gi  
  
gi.require_version('Gtk', '3.0')  
from gi.repository import Gtk, GObject  
  
class SearchEntryWindow(Gtk.Window):  
    def __init__(self):  
        Gtk.Window.__init__(self, title="SearchEntry Demo")  
        self.set_size_request(200, 100)  
        grid = Gtk.Grid()  
        se = Gtk.SearchEntry()  
        se.connect("next_match", self.on_next_match)  
        se.connect("previous_match", self.on_previous_match)  
        se.connect("search-changed", self.on_search_changed)  
        se.connect("stop_search", self.on_stop_search)  
        
        self.label = Gtk.Label()  
        #grid.attach(se, 0, 0, 1, 1)  
        grid.attach(self.label, 0, 1, 1, 1) 

        self.set_titlebar(se)

        self.add(grid)  
        
        # Ctrl-g  
    def on_next_match(self, entry):  
        self.label.set_label("value:" + entry.get_text() + "\tsignal name:next_match")  
        print("next_match:", entry.get_text())  
        
        # Ctrl-Shift-g  
    def on_previous_match(self, entry):  
        self.label.set_label("value:" + entry.get_text() + "\tsignal name:previous_match")  
        
        print("previous_match:", entry.get_text())  
        
    def on_search_changed(self, entry):  
        self.label.set_label("value:" + entry.get_text() + "\tsignal name:search_changed")  
        print("search_changed:", entry.get_text())  
        
        # Esc  
    def on_stop_search(self, entry):  
        self.label.set_label("value:" + entry.get_text() + "\tsignal name:stop_search")  
        print("stop_search:", entry.get_text())  
  
def main():  
    win = SearchEntryWindow()  
    win.connect("delete-event", Gtk.main_quit)  
    win.show_all()  
    Gtk.main()  
  
if __name__ == "__main__":  
    main()  