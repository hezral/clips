#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: t; c-basic-offset: 4; tab-width: 4 -*- 

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class FlowBoxWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_border_width(10)
        self.set_default_size(300, 200)

        header = Gtk.HeaderBar(title="Flow Box")
        header.set_subtitle("Flowbox filtering")
        header.props.show_close_button = True

        self.set_titlebar(header)

        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)

        search_entry = Gtk.SearchEntry()
        search_entry.connect('search_changed', self.flowbox_filter)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_min_content_height(200)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(8)

        # Fill flowbox
        text = ['ABC','A','BCD','TCUNF','GNCBC','JFABC','LDNAB',
        'JJVIC','HZACB','BESEI','VEISEI','GJBVV','abcii','fjbci',
        'fsefsi','aabc','fesfoo','fffba','jjfsi'
        ]
        for t in text:
            label = Gtk.Label(t)
            child = Gtk.FlowBoxChild()
            child.set_name(t)
            child.add(label)
            self.flowbox.add(child)

        scrolled.add(self.flowbox)
        box.pack_start(search_entry, False, False, 2)
        box.pack_start(scrolled, False, False, 2)

        self.add(box)

        self.show_all()

    def flowbox_filter(self, search_entry):
        def filter_func(fb_child, text):
            if text in fb_child.get_name():
                return True
            else:
                return False

        text = search_entry.get_text()
        self.flowbox.set_filter_func(filter_func, text)

win = FlowBoxWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
