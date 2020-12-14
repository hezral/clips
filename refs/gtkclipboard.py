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

import signal
from gi.repository import GLib
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit) 
clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
#targets = Gdk.Atom.intern('TARGETS', False)

#print(Gdk.Atom.name(targets))

#print(dir(clipboard))
#html_target = Gdk.Atom.intern('text/html', False)
#clipboard.wait_for_contents(html_target).get_data()

#def dump_clipboard_callback(clipboard, selection_data, data=None):
#   print(selection_data.data)

#clipboard.request_contents(html_target , dump_clipboard_callback)


#setup supported clip types
richtext_target = Gdk.Atom.intern('text/richtext', False)
html_target = Gdk.Atom.intern('text/html', False)
image_target = Gdk.Atom.intern('image/png', False)
text_target = Gdk.Atom.intern('text/plain', False)
uri_target = Gdk.Atom.intern('x-special/gnome-copied-files', False)
save_target = Gdk.Atom.intern('SAVE_TARGETS', False)
#print(clipboard.wait_is_text_available())

global event_time
event_time = 0

def on(clipboard, event, event_time):
    #print(locals())
    #print(dir(event))
    #global event_time
    # print(event_time)
    # print(event.time - event_time)
    # if event.time - event_time != 1:
        #print(event.time, event.selection_time, event.handler_set)
    print("Current clipboard offers formats: ")
    #print(type(clipboard.wait_for_targets()))
    i = 0
    for target in clipboard.wait_for_targets()[1]:
        content = clipboard.wait_for_contents(target)
        # if content is not None and str(target).find("WPS Drawing Shape Format") != -1:
        #     bytes = content.get_data()
        #     file = open("file.pptx","wb")
        #     # file = open("{i}.{ext}".format(i=str(target).split("/")[0], ext=str(target).split("/")[1]),"wb")
        #     file.write(bytes)
        #     file.close()
        #     i += 1
        print(target, content)
    #print(clipboard.wait_for_contents(html_target).get_data())
    #content = clipboard.wait_for_contents(image_target)
        # event_time = event.time
    # print(event_time)
    
    #print(type(content))

    # for target in clipboard.wait_for_targets()[1]:
    #     contents = clipboard.wait_for_contents(target)
    #     # if target == image_target:
    #     #     print("image")
    #     #     contents.get_pixbuf().savev("/home/adi/Work/clips/refs/file.png", 'png', [], [])
    #     print(target, type(contents))
    
    #content.savev("file.png", 'png', [], [])
    # pixbuf = contents.get_pixbuf()
    # f = open('output.png', 'wb')

    # f.write(pixbuf)
    # f.close()

clipboard.connect('owner_change',on, event_time)

Gtk.main()

#print("Current clipboard offers formats: " + str(clipboard.wait_for_targets()[1]))

# richtext = Gdk.Atom.intern('text/richtext', False)

# for target in clipboard.wait_for_targets()[1]:
#     if target == richtext:
#         contents = clipboard.wait_for_contents(target)
#         if contents:
#             print(str(target), type(contents), contents.get_format())
#             pixbuf = contents.get_data()
#             #print(pixbuf)
#             #html = contents.get_data()

#             f = open('output.rtf', 'wb')

#             f.write(pixbuf)
#             f.close()


Gtk.main()