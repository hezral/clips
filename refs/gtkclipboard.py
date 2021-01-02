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
# TIMESTAMP
# TARGETS
# MULTIPLE
# SAVE_TARGETS
#print(Gdk.Atom.name(targets))

#print(dir(clipboard))
#html_target = Gdk.Atom.intern('text/html', False)
#clipboard.wait_for_contents(html_target).get_data()

#def dump_clipboard_callback(clipboard, selection_data, data=None):
#   print(selection_data.data)

#clipboard.request_contents(html_target , dump_clipboard_callback)the 

# excluded_targets = (Gdk.Atom.intern('TIMESTAMP', False), 
#                     Gdk.Atom.intern('TARGETS', False), 
#                     Gdk.Atom.intern('MULTIPLE', False), 
#                     Gdk.Atom.intern('SAVE_TARGETS', False), 
#                     Gdk.Atom.intern('STRING', False), 
#                     Gdk.Atom.intern('UTF8_STRING', False), 
#                     Gdk.Atom.intern('TEXT', False), )


# #setup supported clip types
# richtext_target = Gdk.Atom.intern('text/richtext', False)
# html_target = Gdk.Atom.intern('text/html', False)
# image_target = Gdk.Atom.intern('image/png', False)
# text_target = Gdk.Atom.intern('text/plain', False)
# uri_target = Gdk.Atom.intern('x-special/gnome-copied-files', False)
# save_target = Gdk.Atom.intern('SAVE_TARGETS', False)
# #print(clipboard.wait_is_text_available())

# global event_time
# event_time = 0

import clips_supported

#print(clips_supported.excluded_targets)

def on(clipboard, event):

#     targets = clipboard.wait_for_targets()[1]
#     for i in range(0, len(targets)): 
#         targets[i] = str(targets[i])

#     #print(targets)

#     libreoffice = [i for i in targets if "application/x-openoffice-embed-source-xml" in i]
#     libreoffice_xlsx = [i for i in targets if "LibreOffice 7.0 Spreadsheet" in i]
#     image_png = [i for i in targets if "image/png" in i]
    
#     if len(libreoffice) == 1 and len(libreoffice_xlsx) == 1 and len(image_png) == 1:
#         print(libreoffice, "\n", libreoffice_xlsx, "\n", image_png)

#     inkscape_svg = [i for i in targets if "image/x-inkscape-svg" in i]
#     image_png = [i for i in targets if "image/png" in i]
    
#     print(inkscape_svg, image_png)

#     if len(inkscape_svg) > 0 and len(image_png) == 1:
# #        print(inkscape_svg, "\n", image_png)

#         content = clipboard.wait_for_contents(Gdk.Atom.intern(inkscape_svg[0], False))
#         bytes = content.get_data()
#         file = open("file.svg","wb")
#         file.write(bytes)
#         file.close()

#         content = clipboard.wait_for_contents(Gdk.Atom.intern(image_png[0], False))
#         bytes = content.get_data()
#         file = open("file.png","wb")
#         file.write(bytes)
#         file.close()


    print("\nCurrent clipboard offers formats: ", len(clipboard.wait_for_targets()[1]))

    i = 0
    for target in clipboard.wait_for_targets()[1]:
        if target not in clips_supported.excluded_targets:
            content = clipboard.wait_for_contents(target)

            if content is not None:

            #     if str(target).find("WPS Drawing Shape Format") != -1:
            #         bytes = content.get_data()
            #         file = open("file.pptx","wb")
            #         # file = open("{i}.{ext}".format(i=str(target).split("/")[0], ext=str(target).split("/")[1]),"wb")
            #         file.write(bytes)
            #         file.close()
            #     if str(target).find("application/x-openoffice-embed-source-xml") != -1: #LibreOffice format compatible with Office XLSX, PPTX, DOCX
            #         bytes = content.get_data()
            #         file = open("file.odp","wb") #change based on string: typename="LibreOffice 7.0 Spreadsheet", typename="LibreOffice 7.0 Presentation", typename="LibreOffice 7.0 Text Document"
            #         # file = open("{i}.{ext}".format(i=str(target).split("/")[0], ext=str(target).split("/")[1]),"wb")
            #         file.write(bytes)
            #         file.close()
                # if str(target).find("application/ico") != -1:
                #     print("application/ico")
                #     bytes = content.get_data()
                #     file = open("file.ico","wb")
                #     # file = open("{i}.{ext}".format(i=str(target).split("/")[0], ext=str(target).split("/")[1]),"wb")
                #     file.write(bytes)
                #     file.close()

            print(i, target, content)
            i += 1


clipboard.connect('owner_change',on)

Gtk.main()

