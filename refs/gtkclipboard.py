#!/usr/bin/env python3

'''
References
https://stackoverflow.com/questions/2346924/dump-x-clipboard-data-with-gtk-or-pygtk
https://stackoverflow.com/questions/3571179/how-does-x11-clipboard-handle-multiple-data-formats/3571949#3571949
https://github.com/frnsys/nom/blob/master/nom/clipboard.py
https://askubuntu.com/questions/427704/how-can-i-edit-the-source-of-html-in-the-clipboard
'''

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)


#targets = Gdk.Atom.intern('TARGETS', False)

#print(Gdk.Atom.name(targets))

#print(dir(clipboard))
#html_target = Gdk.Atom.intern('text/html', False)
#clipboard.wait_for_contents(html_target).get_data()

#def dump_clipboard_callback(clipboard, selection_data, data=None):
#   print(selection_data.data)

#clipboard.request_contents(html_target , dump_clipboard_callback)



#print(clipboard.wait_is_text_available())

def on(clipboard):
    print("Current clipboard offers formats: " + str(clipboard.wait_for_targets()[1]))
    #print(clipboard.wait_for_contents(html_target).get_data())

#clipboard.connect('owner_change',on)

#Gtk.main()

#print("Current clipboard offers formats: " + str(clipboard.wait_for_targets()[1]))

richtext = Gdk.Atom.intern('text/richtext', False)

for target in clipboard.wait_for_targets()[1]:
    if target == richtext:
        contents = clipboard.wait_for_contents(target)
        if contents:
            print(str(target), type(contents), contents.get_format())
            pixbuf = contents.get_data()
            #print(pixbuf)
            #html = contents.get_data()

            f = open('output.rtf', 'wb')

            f.write(pixbuf)
            f.close()
