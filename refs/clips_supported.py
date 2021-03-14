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


# supported clip types

# office types
word_libreoffice_target = (Gdk.Atom.intern('application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)"', False), "odt", "LibreOffice 7.1 Text Document")
word_wpsoffice_target = (Gdk.Atom.intern("Kingsoft WPS 9.0 Format", False), "docx", "WPS Word")
spreadsheet_libreoffice_target = (Gdk.Atom.intern('application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)"', False), "ods", "LibreOffice 7.1 Spreadsheet")
spreadsheet_wpsoffice_target = (Gdk.Atom.intern("WPS Spreadsheets 6.0 Format", False), "xlsx", "WPS Spreadsheet")
slides_libreoffice_target = (Gdk.Atom.intern('application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)"', False), "odp", "LibreOffice 7.1 Presentation")
slides_wpsoffice_target = (Gdk.Atom.intern("WPS Drawing Shape Format", False), "pptx", "WPS Slides")

# html types
html_target = (Gdk.Atom.intern('text/html', False), "html", "HTML Formt") # chrome, firefox, any app capable of copying html content
html_webkit_target = (Gdk.Atom.intern('org.webkitgtk.WebKit.custom-pasteboard-data', False), "html", "HTML Format for Epiphany") # epiphany

# image types
image_png_target = (Gdk.Atom.intern('image/png', False), "png", "PNG Format")
image_svg_target = (Gdk.Atom.intern('image/x-inkscape-svg', False), "svg", "SVG Format")

# text types
richtext_target = (Gdk.Atom.intern("text/richtext", False),"rtf", "Rich Text Format")
text_target = (Gdk.Atom.intern('text/plain;charset=utf-8', False), "txt", "Plain Text Format")

# file manager types
uri_files_target = (Gdk.Atom.intern('x-special/gnome-copied-files', False), ".uri", "elementary Files Format")
uri_dolphin_target = (Gdk.Atom.intern('application/x-kde4-urilist, False), ".uri", "Dolphin Format")

# # office types
# richtext_target = Gdk.Atom.intern("text/richtext", False)
# word_libreoffice_target = Gdk.Atom.intern("application/x-openoffice-embed-source-xml", False)
# word_wpsoffice_target = Gdk.Atom.intern("Kingsoft WPS 9.0 Format", False)
# spreadsheet_libreoffice_target = Gdk.Atom.intern("application/x-openoffice-embed-source-xml", False)
# spreadsheet_wpsoffice_target = Gdk.Atom.intern("WPS Spreadsheets 6.0 Format", False)
# slides_libreoffice_target = Gdk.Atom.intern("application/x-openoffice-embed-source-xml", False)
# slides_wpsoffice_target = Gdk.Atom.intern("WPS Drawing Shape Format", False)
# html_target = Gdk.Atom.intern('text/html', False) # chrome, firefox, any app capable of copying html content
# html_webkit_target = Gdk.Atom.intern('org.webkitgtk.WebKit.custom-pasteboard-data', False) # epiphany
# image_target = Gdk.Atom.intern('image/png', False)
# text_target = Gdk.Atom.intern('text/plain;charset=utf-8', False)
# uri_target = Gdk.Atom.intern('x-special/gnome-copied-files', False)


supported_targets = (word_libreoffice_target,
                    word_wpsoffice_target,
                    spreadsheet_libreoffice_target,
                    spreadsheet_wpsoffice_target,
                    slides_libreoffice_target,
                    slides_wpsoffice_target,
                    html_target,
                    html_webkit_target,
                    image_png_target,
                    image_svg_target,
                    richtext_target,
                    text_target,
                    uri_files_target, 
                    uri_dolphin_target, )

# LibreOffice Writer
# Current clipboard offers formats:  15
# 0 application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)" <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x155ba80)>
# 1 text/rtf <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x155bac0)>
# 2 text/richtext <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x155bb00)>
# 3 text/html <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x155bb40)>
# 4 text/plain;charset=utf-16 <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x155bb80)>
# 5 application/x-openoffice-link;windows_formatname="Link" <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1c00)>
# 6 application/x-openoffice-objectdescriptor-xml;windows_formatname="Star Object Descriptor (XML)";classname="8BC6B165-B1B2-4EDD-aa47-dae2ee689dd6";typename="LibreOffice 7.1 Text Document";viewaspect="1";width="16999";height="2995";posx="0";posy="0" <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1c40)>
# 7 text/plain;charset=utf-8 <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1c80)>
# 8 application/x-libreoffice-internal-id-36 <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1cc0)>

# WPS Writer
# Current clipboard offers formats:  18
# 0 Kingsoft Data Descriptor <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1e00)>
# 1 Kingsoft WPS 9.0 Format <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1e40)>
# 2 Embed Source <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1e00)>
# 3 Object Descriptor <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1dc0)>
# 4 Kingsoft Image Data <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1d80)>
# 5 Rich Text Format <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1d40)>
# 6 text/rtf <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1d00)>
# 7 text/richtext <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1cc0)>
# 8 text/plain <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1c80)>
# 9 text/html <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1c40)>

# LibreOffice Calc
# Current clipboard offers formats:  24
# 0 application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)" <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1c80)>
# 1 application/x-openoffice-objectdescriptor-xml;windows_formatname="Star Object Descriptor (XML)";classname="47BBB4CB-CE4C-4E80-a591-42d9ae74950f";typename="LibreOffice 7.1 Spreadsheet";viewaspect="1";width="6775";height="4968";posx="0";posy="0" <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1cc0)>
# 2 application/x-openoffice-gdimetafile;windows_formatname="GDIMetaFile" <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1d00)>
# 3 application/x-openoffice-emf;windows_formatname="Image EMF" <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1d40)>
# 4 application/x-openoffice-wmf;windows_formatname="Image WMF" <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1d80)>
# 5 image/png <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1dc0)>
# 6 application/x-openoffice-bitmap;windows_formatname="Bitmap" <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1e00)>
# 7 image/bmp <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1e40)>
# 8 text/html <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1e00)>
# 9 application/x-openoffice-sylk;windows_formatname="Sylk" <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1dc0)>
# 10 application/x-openoffice-link;windows_formatname="Link" <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1d80)>
# 11 application/x-openoffice-dif;windows_formatname="DIF" <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1d40)>
# 12 text/plain;charset=utf-16 <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1d00)>
# 13 application/x-libreoffice-tsvc <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1cc0)>
# 14 text/rtf <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1c80)>
# 15 text/richtext <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1c40)>
# 16 text/plain;charset=utf-8 <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1c00)>
# 17 application/x-libreoffice-internal-id-36 <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x155bb80)>

# WPS Spreadsheets
# Current clipboard offers formats:  19
# 0 image/png <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1d00)>
# 1 WPS Spreadsheets 6.0 Format <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1d40)>
# 2 text/html <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1d80)>
# 3 text/plain <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1dc0)>
# 4 Rich Text Format <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1e00)>
# 5 text/richtext <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1e40)>
# 6 text/rtf <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1e00)>
# 7 XML Spreadsheet <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1dc0)>
# 8 Link Source <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1d80)>
# 9 Link Source Descriptor <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1d40)>
# 10 Kingsoft Data Descriptor <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1d00)>

# LibreOffice Impress
# Current clipboard offers formats:  14
# 0 application/x-openoffice-objectdescriptor-xml;windows_formatname="Star Object Descriptor (XML)";classname="9176E48A-637A-4D1F-803b-99d9bfac1047";typename="LibreOffice 7.1 Presentation";displayname="file:///home/adi/Downloads/You_Exec_-_Keynote_Presentation_-_Collages.pptx";viewaspect="1";width="55280";height="38100";posx="0";posy="0" <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1cc0)>
# 1 application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)" <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x155bb80)>
# 2 application/x-openoffice-drawing;windows_formatname="Drawing Format" <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1c80)>
# 3 application/x-openoffice-gdimetafile;windows_formatname="GDIMetaFile" <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1d00)>
# 4 application/x-openoffice-emf;windows_formatname="Image EMF" <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1d40)>
# 5 application/x-openoffice-wmf;windows_formatname="Image WMF" <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1d80)>
# 6 image/png <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1dc0)>
# 7 application/x-openoffice-bitmap;windows_formatname="Bitmap" <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1e00)>
# 8 image/bmp <Gtk.SelectionData object at 0xffffaa5b49a0 (GtkSelectionData at 0x16b1e40)>
# 9 application/x-libreoffice-internal-id-36 <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1e00)>

# WPS Slides
# Current clipboard offers formats:  11
# 0 Art::GVML ClipFormat <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1c80)>
# 1 WPS Drawing Shape Format <Gtk.SelectionData object at 0xffffa9a72a00 (GtkSelectionData at 0x155bb80)>
# 2 image/png <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1cc0)>
# 3 image/jpeg <Gtk.SelectionData object at 0xffffa9a72a00 (GtkSelectionData at 0x16b1c00)>
# 4 image/bmp <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x16b1c40)>
# 5 CF_ENHMETAFILE <Gtk.SelectionData object at 0xffffa9a72a00 (GtkSelectionData at 0x155bac0)>
# 6 Kingsoft Data Descriptor <Gtk.SelectionData object at 0xffffaa5b4d00 (GtkSelectionData at 0x155bb40)>
