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
gi.require_version("Wnck", "3.0")
gi.require_version("Bamf", "3")
from gi.repository import Gtk, Gdk, Bamf, Wnck, Gio

import signal
from gi.repository import GLib
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit) 

import clips_supported

clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

def get_active_app():

    # using Bamf
    matcher = Bamf.Matcher()
    screen = Wnck.Screen.get_default()
    screen.force_update()

    # if matcher.get_active_window() is None:
    #     active_win = screen.get_active_window()
    # else:
    #     active_win = matcher.get_active_window()

    active_win = matcher.get_active_window()
    if active_win is not None:
        active_app = matcher.get_application_for_window(active_win)
        if active_app is not None:
            source_app = active_app.get_name().split(" – ")[-1] #some app's name are shown with current document name so we split it and get the last part only
            source_icon = active_app.get_icon()

    else: 
        source_app = screen.get_active_workspace().get_name() # if no active window, fallback to workspace name
        source_icon = 'preferences-desktop-wallpaper' 

    protected = "no"

    return source_app, source_icon, protected

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

    print(get_active_app())

    for target in clipboard.wait_for_targets()[1]:
        if target not in clips_supported.excluded_targets:

            print(i, target)
            i += 1

            # if target in clips_supported.supported_targets:
            # for supported_target in clips_supported.supported_targets:
            #     if target == supported_target[0]:
                    
            #         # content = clipboard.wait_for_contents(target)

            #         # if content is not None:
                        
            #         if supported_target[2].find("Libre") != -1:
            #             print("libre")

            #         # if i == 0:
                    
                    
                    
            #         print(i, target)
                        
            #         i += 1

                    # if str(target).find("WPS Drawing Shape Format") != -1:
                    #     bytes = content.get_data()
                    #     file = open("file.pptx","wb")
                    #     # file = open("{i}.{ext}".format(i=str(target).split("/")[0], ext=str(target).split("/")[1]),"wb")
                    #     file.write(bytes)
                    #     file.close()
                    # if str(target).find("application/x-openoffice-embed-source-xml") != -1: #LibreOffice format compatible with Office XLSX, PPTX, DOCX
                    #     bytes = content.get_data()
                    #     file = open("file.odp","wb") #change based on string: typename="LibreOffice 7.0 Spreadsheet", typename="LibreOffice 7.0 Presentation", typename="LibreOffice 7.0 Text Document"
                    #     # file = open("{i}.{ext}".format(i=str(target).split("/")[0], ext=str(target).split("/")[1]),"wb")
                    #     file.write(bytes)
                    #     file.close()
                    # if str(target).find("application/ico") != -1:
                    #     print("application/ico")
                    #     bytes = content.get_data()
                    #     file = open("file.ico","wb")
                    #     # file = open("{i}.{ext}".format(i=str(target).split("/")[0], ext=str(target).split("/")[1]),"wb")
                    #     file.write(bytes)
                    #     file.close()
                    # if str(target).find("text/plain;charset=utf-8") != -1:
                    #     print(content.get_data().decode("utf-8"))
                    # if str(target).find("text/html") != -1:
                    #     bytes = content.get_data()
                    #     file = open("file.html","wb")
                    #     file.write(bytes)
                    #     file.close()
                    # if str(target).find("text/richtext") != -1:
                    #     bytes = content.get_data()
                    #     file = open("file.rtf","wb")
                    #     file.write(bytes)
                    #     file.close()




clipboard.connect('owner_change',on)

Gtk.main()

