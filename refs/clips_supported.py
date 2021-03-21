#!/usr/bin/env python3

'''
   Copyright 2018 Adi Hezral (hezral@gmail.com)

   This file is part of Clips.

    Clips is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Clips is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Clips.  If not, see <http://www.gnu.org/licenses/>.
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
word_libreoffice_target = ('application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)"', "odt", "LibreOffice Writer", "office", False)
spreadsheet_libreoffice_target = ('application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)', "ods", "LibreOffice Calc", "office", True)
slides_libreoffice_target = ('application/x-openoffice-drawing;windows_formatname="Drawing Format"', "odp", "LibreOffice Impress", "office", True)

word_wpsoffice_target = ("Kingsoft WPS 9.0 Format", "docx", "WPS Writer", "office", False)
spreadsheet_wpsoffice_target = ("WPS Spreadsheets 6.0 Format", "xlsx", "WPS Spreadsheets", "office", True)
slides_wpsoffice_target = ("WPS Drawing Shape Format", "pptx", "WPS Presentation", "office", True)
slidepage_wpsoffice_target = ("PowerPoint 14.0 Slides Package", "pptx", "WPS Presentation", "office", True)

# html types
html_target = ("text/html", "html", "HTML Formt", "html", False) # chrome, firefox, any app capable of copying html content
# html_webkit_target = ("org.webkitgtk.WebKit.custom-pasteboard-data", "html", "HTML Format for Epiphany", "html", False) # epiphany

# image types
image_png_target = ("image/png", "png", "PNG Format", "image", False)
image_svg_target = ("image/x-inkscape-svg", "svg", "SVG Format", "image", False)

# file manager types
uri_files_target = ("x-special/gnome-copied-files", ".uri", "elementary Files Format", "files", False)
uri_dolphin_target = ("application/x-kde4-urilist", ".uri", "Dolphin Format", "files", False)

# text types
richtext_target = ("text/richtext", "rtf", "Rich Text Format", "richtext", False)
text_target = ("text/plain;charset=utf-8", "txt", "Plain Text Format", "plaintext", False)


supported_targets = (word_libreoffice_target,
                    spreadsheet_libreoffice_target,
                    slides_libreoffice_target,
                    word_wpsoffice_target,
                    spreadsheet_wpsoffice_target,
                    slides_wpsoffice_target, 
                    slidepage_wpsoffice_target, 
                    image_png_target,
                    image_svg_target,
                    html_target,
                    # html_webkit_target,
                    richtext_target,
                    text_target,
                    uri_files_target, 
                    uri_dolphin_target, )


# argumentList = sys.argv[1:]
 
# # Options
# options = "hd:"
 
# # Long options
# long_options = ["help","debug"]

# try:
#     # Parsing argument
#     arguments, values = getopt.getopt(argumentList, options, long_options)
     
#     # checking each argument
#     for currentArgument, currentValue in arguments:
 
#         if currentArgument in ("-h", "--help"):
#             print ("For debug run with -d or --debug flag")
             
#         elif currentArgument in ("-d", "--debug"):
#             print ("Displaying file_name:", sys.argv[0])
             
# except getopt.error as err:
#     # output error, and return with an error code
#     print (str(err))




# Gdk.Atom.intern formats captured for each supported office doc types

# LibreOffice Writer
# Current clipboard offers formats: 15
# 0 application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)" 
# 1 text/rtf 
# 2 text/richtext 
# 3 text/html 
# 4 text/plain;charset=utf-16 
# 5 application/x-openoffice-link;windows_formatname="Link" 
# 6 application/x-openoffice-objectdescriptor-xml;windows_formatname="Star Object Descriptor (XML)";classname="8BC6B165-B1B2-4EDD-aa47-dae2ee689dd6";typename="LibreOffice 7.1 Text Document";viewaspect="1";width="16999";height="2995";posx="0";posy="0" 
# 7 text/plain;charset=utf-8 
# 8 application/x-libreoffice-internal-id-36 

# WPS Writer
# Current clipboard offers formats: 18
# 0 Kingsoft Data Descriptor 
# 1 Kingsoft WPS 9.0 Format 
# 2 Embed Source 
# 3 Object Descriptor 
# 4 Kingsoft Image Data 
# 5 Rich Text Format 
# 6 text/rtf 
# 7 text/richtext 
# 8 text/plain 
# 9 text/html 

# LibreOffice Calc
# Current clipboard offers formats: 24
# 0 application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)" 
# 1 application/x-openoffice-objectdescriptor-xml;windows_formatname="Star Object Descriptor (XML)";classname="47BBB4CB-CE4C-4E80-a591-42d9ae74950f";typename="LibreOffice 7.1 Spreadsheet";viewaspect="1";width="6775";height="4968";posx="0";posy="0" 
# 2 application/x-openoffice-gdimetafile;windows_formatname="GDIMetaFile" 
# 3 application/x-openoffice-emf;windows_formatname="Image EMF" 
# 4 application/x-openoffice-wmf;windows_formatname="Image WMF" 
# 5 image/png 
# 6 application/x-openoffice-bitmap;windows_formatname="Bitmap" 
# 7 image/bmp 
# 8 text/html 
# 9 application/x-openoffice-sylk;windows_formatname="Sylk" 
# 10 application/x-openoffice-link;windows_formatname="Link" 
# 11 application/x-openoffice-dif;windows_formatname="DIF" 
# 12 text/plain;charset=utf-16 
# 13 application/x-libreoffice-tsvc 
# 14 text/rtf 
# 15 text/richtext 
# 16 text/plain;charset=utf-8 
# 17 application/x-libreoffice-internal-id-36 

# WPS Spreadsheets
# Current clipboard offers formats: 19
# 0 image/png 
# 1 WPS Spreadsheets 6.0 Format 
# 2 text/html 
# 3 text/plain 
# 4 Rich Text Format 
# 5 text/richtext 
# 6 text/rtf 
# 7 XML Spreadsheet 
# 8 Link Source 
# 9 Link Source Descriptor 
# 10 Kingsoft Data Descriptor 

# LibreOffice Impress
# Current clipboard offers formats: 14
# 0 application/x-openoffice-objectdescriptor-xml;windows_formatname="Star Object Descriptor (XML)";classname="9176E48A-637A-4D1F-803b-99d9bfac1047";typename="LibreOffice 7.1 Presentation";displayname="file:///home/adi/Downloads/You_Exec_-_Keynote_Presentation_-_Collages.pptx";viewaspect="1";width="55280";height="38100";posx="0";posy="0" 
# 1 application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)" 
# 2 application/x-openoffice-drawing;windows_formatname="Drawing Format" 
# 3 application/x-openoffice-gdimetafile;windows_formatname="GDIMetaFile" 
# 4 application/x-openoffice-emf;windows_formatname="Image EMF" 
# 5 application/x-openoffice-wmf;windows_formatname="Image WMF" 
# 6 image/png 
# 7 application/x-openoffice-bitmap;windows_formatname="Bitmap" 
# 8 image/bmp 
# 9 application/x-libreoffice-internal-id-36 

# WPS Slides
# Current clipboard offers formats: 11
# 0 Art::GVML ClipFormat 
# 1 WPS Drawing Shape Format 
# 2 image/png 
# 3 image/jpeg 
# 4 image/bmp 
# 5 CF_ENHMETAFILE 
# 6 Kingsoft Data Descriptor

