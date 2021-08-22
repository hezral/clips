#!/usr/bin/env python3

'''
    Copyright 2018 Adi Hezral (hezral@gmail.com)
    This file is part of Clips ("Application").
    The Application is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    The Application is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this Application.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys, getopt

import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

# Standard clipboard targets that won't be handled by Clips
excluded_targets = (Gdk.Atom.intern('TIMESTAMP', False), 
                    Gdk.Atom.intern('TARGETS', False), 
                    Gdk.Atom.intern('MULTIPLE', False), 
                    Gdk.Atom.intern('SAVE_TARGETS', False), 
                    Gdk.Atom.intern('STRING', False), 
                    Gdk.Atom.intern('UTF8_STRING', False), 
                    Gdk.Atom.intern('COMPOUND_TEXT', False), 
                    Gdk.Atom.intern('TEXT', False), )


# supported clipboard targets
# definition for clip types in list format following the schema
# schema: (Gdk.Atom.intern name(str), file_extension(str), additional_desc(str), content_type(str), thumbnail(bool))
# order the variable definitions by 1st detected

# office types
word_libreoffice_target = ('application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)"', "odt", "LibreOffice Writer", "office/word", False)
spreadsheet_libreoffice_target = ('application/x-openoffice-sylk;windows_formatname="Sylk"', "ods", "LibreOffice Calc", "office/spreadsheet", False) # use this to differentiate since all libreoffice target using same Gdk.Atom target
slides_libreoffice_target = ('application/x-openoffice-drawing;windows_formatname="Drawing Format"', "odp", "LibreOffice Impress", "office/presentation", True) # use this to differentiate since all libreoffice target using same Gdk.Atom target

word_wpsoffice_target = ("Kingsoft WPS 9.0 Format", "rtf", "WPS Writer", "office/word", False)
spreadsheet_wpsoffice_target = ("WPS Spreadsheets 6.0 Format", "xlsx", "WPS Spreadsheets", "office/spreadsheet", False)
slides_wpsoffice_target = ("WPS Drawing Shape Format", "pptx", "WPS Presentation", "office/presentation", True)
slidepage_wpsoffice_target = ("PowerPoint 14.0 Slides Package", "pptx", "WPS Presentation", "office/presentation", True)

# html types
html_target = ("text/html", "html", "HTML Formt", "html", False) # chrome, firefox, any app capable of copying html content
# html_webkit_target = ("org.webkitgtk.WebKit.custom-pasteboard-data", "html", "HTML Format for Epiphany", "html", False) # epiphany

# image types
image_png_target = ("image/png", "png", "PNG Format", "image", False)
image_svg_target = ("image/x-inkscape-svg", "svg", "SVG Format", "image", False)

# file manager types
uri_files_target = ("x-special/gnome-copied-files", "uri", "elementary Files Format", "files", False)
uri_nautilus_target = ("text/plain;charset=utf-8", "uri", "Nautilus Format", "files", False)
uri_dolphin_target = ("text/uri-list", "uri", "Dolphin Format", "files", False)

# text types
richtext_target = ("text/richtext", "rtf", "Rich Text Format", "richtext", False)
utf8text_target = ("text/plain;charset=utf-8", "txt", "Plain Text Format", "plaintext", False)
plaintext_target = ("text/plain", "txt", "Plain Text Format", "plaintext", False)

# custom types, not a real clipboard data type
url1_target = ("text/plain;charset=utf-8", "txt", "Internet URL", "url", False)
url2_target = ("text/plain", "txt", "Internet URL", "url", False)
mail1_target = ("text/plain;charset=utf-8", "txt", "Email", "mail", False)
mail2_target = ("text/plain", "txt", "email", "mail", False)
color_target = ("text/plain;charset=utf-8", "txt", "Color Codes", "color", False)

supported_targets = (spreadsheet_libreoffice_target,
                    slides_libreoffice_target,
                    word_libreoffice_target,
                    spreadsheet_wpsoffice_target,
                    slides_wpsoffice_target, 
                    word_wpsoffice_target,
                    slidepage_wpsoffice_target, 
                    uri_files_target, 
                    uri_nautilus_target,
                    uri_dolphin_target,
                    image_svg_target,
                    image_png_target,
                    html_target,
                    # html_webkit_target,
                    richtext_target,
                    color_target,
                    url1_target,
                    url2_target,
                    mail1_target,
                    mail2_target,
                    utf8text_target, 
                    plaintext_target, )

def get_clipboard_contents(clipboard, event, save_files):
    from . import utils
    print("Active App:", utils.get_active_appinfo_xlib())
    print("Current clipboard offers formats: ", len(clipboard.wait_for_targets()[1]))
    i=0
    for target in clipboard.wait_for_targets()[1]:
        if target not in excluded_targets:

            if save_files:
                content = clipboard.wait_for_contents(target)
                if content is not None:

                    ext = str(target).split("/")
                    if len(ext) == 1:
                        ext = ext[0]
                    else:
                        ext = ext[1]

                    data = content.get_data()
                    file = open("{filename}.{ext}".format(filename="file-"+str(i), ext=ext),"wb")
                    file.write(data)
                    file.close()

            print(i, target)
            i += 1

def debug():
    # for debugging
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GLib

    # setup commandline quit
    import signal
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit) 
    
    # create clipboard and connect to event
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    clipboard.connect('owner_change', get_clipboard_contents, False)

    print("running in debug mode")
    print("waiting for clipboard event")

    # run
    Gtk.main()

argumentList = sys.argv[1:]
 
# Options
options = "hd"
 
# Long options
long_options = ["help","debug"]

try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)
     
    # checking each argument
    for currentArgument, currentValue in arguments:
 
        if currentArgument in ("-h", "--help"):
            print ("For debug run with -d or --debug flag")
             
        elif currentArgument in ("-d", "--debug"):
            # print ("Displaying file_name:", sys.argv[0])
            debug()
             
except getopt.error as err:
    # output error, and return with an error code
    print (str(err))

