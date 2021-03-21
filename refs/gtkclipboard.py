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

def get_clipboard_contents(clipboard, event):
    i = 0
    clip_saved = False
    
    # print("Active App:", get_active_app())
    # print("Current clipboard offers formats: ", len(clipboard.wait_for_targets()[1]))

    for supported_target in clips_supported.supported_targets:       
        for target in clipboard.wait_for_targets()[1]:
            if target not in clips_supported.excluded_targets and supported_target[0] in str(target) and clip_saved is False:
                proceed = True

                # only get the right target for these types
                if "WPS" in get_active_app()[0] and not "WPS" in supported_target[2]:
                    proceed = False

                # if "Libre" in get_active_app()[0] and not "Libre" in supported_target[2]:
                #     proceed = False

                if "WPS Spreadsheets" in supported_target[2] or "LibreOffice Calc" in supported_target[2]:
                    target = Gdk.Atom.intern('text/html', False)

                if "WPS Writer" in supported_target[2] or "LibreOffice Writer" in supported_target[2]:
                    target = Gdk.Atom.intern('text/richtext', False)

                if "LibreOffice Impress" in supported_target[2]:
                    target = Gdk.Atom.intern('application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)"', False)

                if proceed:
                    content = clipboard.wait_for_contents(target)
                    if content is not None:
                        file_extension = supported_target[1]
                        additional_desc = supported_target[2]
                        content_type = supported_target[3]
                        thumbnail = supported_target[4]
    
                        data = content.get_data()

                        file = open("{filename}.{ext}".format(filename="file-"+str(i), ext=file_extension),"wb")
                        file.write(data)
                        file.close()

                        if thumbnail:
                            thumbnail = clipboard.wait_for_contents(Gdk.Atom.intern('image/png', False))
                            data = thumbnail.get_data()
                            file = open("{filename}.{ext}".format(filename="file-"+str(i)+"-thumb", ext="png"),"wb")
                            file.write(data)
                            file.close()

                        clip_saved = True
                
                        print(i, target, supported_target, get_active_app())
                        i += 1

    # for debugging
    # i=0
    # for target in clipboard.wait_for_targets()[1]:
    #     if target not in clips_supported.excluded_targets:
    #         # content = clipboard.wait_for_contents(target)
    #         # if content is not None:

    #         #     ext = str(target).split("/")
    #         #     if len(ext) == 1:
    #         #         ext = ext[0]
    #         #     else:
    #         #         ext = ext[1]

    #         #     data = content.get_data()
    #         #     file = open("{filename}.{ext}".format(filename="file-"+str(i), ext=ext),"wb")
    #         #     file.write(data)
    #         #     file.close()

    #         print(i, target)
    #         i += 1


clipboard.connect('owner_change', get_clipboard_contents)

Gtk.main()