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
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, WebKit2, Granite, GdkPixbuf, GLib, Pango, Gdk

import os
from datetime import datetime

class ClipsView(Gtk.Grid):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #------ flowbox ----#
        self.flowbox = Gtk.FlowBox()
        self.flowbox.props.name = "flowbox"
        self.flowbox.props.homogeneous = False
        self.flowbox.props.row_spacing = 10
        self.flowbox.props.column_spacing = 10
        self.flowbox.props.max_children_per_line = 9
        self.flowbox.props.min_children_per_line = 3
        self.flowbox.props.valign = Gtk.Align.START
        self.flowbox.props.halign = Gtk.Align.FILL
        self.flowbox.set_sort_func(self.sort_flowbox)
        self.flowbox.connect("child_activated", self.on_child_activated)

        #------ scrolled_window ----#
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.props.expand = True
        scrolled_window.props.hscrollbar_policy = Gtk.PolicyType.NEVER
        scrolled_window.add(self.flowbox)
        scrolled_window.connect("edge-reached", self.on_edge_reached)
        
        #------ construct ----#
        self.props.name = "clips-view"
        self.props.expand = True
        #self.set_size_request(650, 250)
        self.attach(scrolled_window, 0, 0, 1, 1)

    def filter_flowbox(self, *args):
        print(locals())

    def sort_flowbox(self, child1, child2):
        date1 = child1.get_children()[0].created
        date2 = child2.get_children()[0].created
        return date1 < date2

    def new_clip(self, clip, app_startup=False):
        app = self.get_toplevel().props.application
        main_window = self.get_toplevel()
        id = clip[0]
        cache_file = os.path.join(app.cache_manager.cache_filedir, clip[6])

        # cache_file = os.path.join(cache_filedir, clip[6])
        new_flowboxchild = [child for child in self.flowbox.get_children() if child.get_children()[0].id == id]

        # add the new clip if cache_file exists
        if os.path.exists(cache_file) and len(new_flowboxchild) == 0:
            self.flowbox.add(ClipsContainer(clip, app.cache_manager.cache_filedir, app.utils))
            new_flowboxchild = [child for child in self.flowbox.get_children() if child.get_children()[0].id == id][0]
            new_flowboxchild.connect("focus-out-event", self.on_child_focus_out, new_flowboxchild)

            if app_startup is False:
                # total_clips = int(main_window.total_clips_label.props.label.split(": ")[1])
                # total_clips = total_clips + 1
                # main_window.total_clips_label.props.label = "Clips: {total}".format(total=total_clips)
                main_window.update_total_clips_label("add")

            self.flowbox.show_all()

        # clean-up and delete from db since cache_file doesn't exist
        elif os.path.exists(cache_file) is False:
            print("don't exist")
            app.cache_manager.delete_record(id, cache_file)

    def on_edge_reached(self, scrolledwindow, position):
        if position.value_name == "GTK_POS_BOTTOM":
            print(datetime.now(), "loading next items")

    def on_child_activated(self, flowbox, flowboxchild):
        main_window = self.get_toplevel()
        app = main_window.props.application
        utils = app.utils
        clip_action_revealer = utils.get_widget_by_name(widget=flowboxchild, child_name="clip-action-revealer", level=0)

        if clip_action_revealer.get_child_revealed():
            clip_action_revealer.set_reveal_child(False)
        else:
            clip_action_revealer.set_reveal_child(True)
        
    def on_child_focus_out(self, flowbox, event, flowboxchild):
        main_window = self.get_toplevel()
        app = main_window.props.application
        utils = app.utils
        clip_action_revealer = utils.get_widget_by_name(widget=flowbox, child_name="clip-action-revealer", level=0)
        clip_action_revealer.set_reveal_child(False)


class ClipsContainer(Gtk.Grid):
    def __init__(self, clip, cache_filedir, utils, *args, **kwargs):
        super().__init__(*args, **kwargs)

        scale = self.get_scale_factor()

        self.id = clip[0]
        self.target = clip[1]
        self.created = clip[2]
        self.source = clip[3]
        self.source_app = clip[4]
        self.source_icon = clip[5]
        self.cache_file = clip[6]
        self.type = clip[7]
        self.protected = clip[8]


        # initialize cachce file with full path        
        self.cache_file = os.path.join(cache_filedir, self.cache_file)

        # initialize empty variable
        self.content = None

        if self.type == "files":
            self.content = open(self.cache_file, "r")
            self.content_label = str(len(self.content.read())) + "chars"
            self.content = Gtk.Label(self.content.read())

        elif self.type == "image":

            #original code
            image_size = 200
            #margin = 0
            pixbuf_original = GdkPixbuf.Pixbuf.new_from_file(self.cache_file)
            # dest_pixbuf = GdkPixbuf.Pixbuf.new(pixbuf_original.get_colorspace(), pixbuf_original.get_has_alpha(), pixbuf_original.get_bits_per_sample(), 168, 118)
            # pixbuf_original.copy_area(0, 0, 181, 174, dest_pixbuf, 0, 0)
            # print(dest_pixbuf)
            #pixbuf = dest_pixbuf

            if pixbuf_original.props.width < image_size:
                pixbuf = pixbuf_original

            else:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.cache_file, image_size, -1, True)

            image = Gtk.Image().new_from_pixbuf(pixbuf)

            self.content_label = "{width} x {height} px".format(width=str(pixbuf_original.props.width), height=str(pixbuf_original.props.height))
            self.content = image
            if pixbuf.get_has_alpha():
                self.get_style_context().add_class(Granite.STYLE_CLASS_CHECKERBOARD)
            else:
                self.content.get_style_context().add_class(Granite.STYLE_CLASS_CARD)

        elif self.type == "html":
            self.content = open(self.cache_file, "r")
            self.content = self.content.read()
            self.content_label = str(len(self.content)) + " chars"

            # background_color, valid = utils.get_css_background_color(content)

            # if valid:
            #     if utils.isLightOrDark(utils.HexToRGB(background_color)) == "light":
            #         font_color = "black"
            #     else:
            #         font_color = "white"
            # else:
            #     font_color = "@theme_text_color"

            # background_css = ".webview-container {background-color: " + background_color + "; color: " + font_color + ";}"
            # provider = Gtk.CssProvider()
            # provider.load_from_data(bytes(background_css.encode()))

            # self.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            # self.get_style_context().add_class("webview-container")

            webview = WebKit2.WebView()
            
            # if valid: 
            #     [r,g,b] = utils.HexToRGB(background_color)
            #     self.props.app_paintable = True

            #     webview.set_background_color(Gdk.RGBA(r,g,b,1))
            webview.props.zoom_level = 0.8
            webview.load_html(self.content)
            webview.props.expand = True
            #webview.props.sensitive = False
            eventbox = Gtk.EventBox()
            eventbox.props.above_child = True
            eventbox.add(webview)
            self.content = eventbox

        elif self.type == "richtext":
            self.content = open(self.cache_file, "r")
            self.content_label = str(len(self.content.read())) + " chars"
            self.content = Gtk.Label(self.content.read())

        elif self.type == "plaintext":
            self.content = open(self.cache_file, "r")
            self.content = self.content.read()
            self.content_label = str(len(self.content)) + " chars"
            self.content = Gtk.Label(self.content)
            self.content.props.wrap_mode = Pango.WrapMode.CHAR
            self.content.props.max_width_chars = 30
            self.content.props.wrap = True
            self.content.props.selectable = False

        elif self.type == "url":
            self.content = Gtk.Image().new_from_icon_name("internet-web-browser", Gtk.IconSize.DIALOG)
            self.content_label = "Internet URL"

        elif "color" in self.type:
            self.content = open(self.cache_file, "r")
            self.content = self.content.read()
            self.content = self.content.strip(" ").strip(";") #strip the ; for processing 
            _content = self.content.strip(")") #strip the ) for processing 
            #print(self.id, self.type, content)

            if self.type == "color/hex":
                rgb = utils.HexToRGB(_content)
                a = 1

            elif self.type == "color/rgb":
                r, g, b = _content.split("(")[1].split(",")[0:3]
                r = int(int(r.strip("%"))/100*255) if r.find("%") != -1 else int(r)
                g = int(int(g.strip("%"))/100*255) if g.find("%") != -1 else int(g)
                b = int(int(b.strip("%"))/100*255) if b.find("%") != -1 else int(b)
                rgb = [r, g, b] 
                a = 1

            elif self.type == "color/rgba":
                r, g, b, a = _content.split("(")[1].split(",")
                r = int(int(r.strip("%"))/100*255) if r.find("%") != -1 else int(r)
                g = int(int(g.strip("%"))/100*255) if g.find("%") != -1 else int(g)
                b = int(int(b.strip("%"))/100*255) if b.find("%") != -1 else int(b)
                rgb = [r, g, b] 
                a = float(a.split(")")[0])

            elif self.type == "color/hsl":
                h, s, l = _content.split("(")[1].split(",")[0:3]
                print(h, s, l)
                h = int(h) / 360
                s = int(s.replace("%","")) / 100
                l = int(l.replace("%","")) / 100
                a = 1
                rgb = utils.HSLtoRGB((h, s, l))

            elif self.type == "color/hsla":
                h, s, l, a = _content.split("(")[1].split(",") 
                h = int(h) / 360
                s = int(s.replace("%","")) / 100
                l = int(l.replace("%","")) / 100
                a = float(a.split(")")[0])
                rgb = utils.HSLtoRGB((h, s, l))

            color_code = "rgba(" + str(rgb[0]) + "," + str(rgb[1]) + "," + str(rgb[2]) + "," + str(1) + ")"
            
            if utils.isLightOrDark(rgb) == "light":
                font_color = "rgba(0,0,0,0.85)"
            else:
                font_color = "rgba(255,255,255,0.85)"

            color_content_css = ".color-container {background-color: " + color_code + "; color: " + font_color + ";}"
            font_css = ".color-content {letter-spacing: 1px; font-weight: bold; font-size: 125%;}"
            css = color_content_css + "\n" + font_css
            provider = Gtk.CssProvider()
            provider.load_from_data(bytes(css.encode()))

            self.content = Gtk.Label(self.content)
            self.content.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            self.content.get_style_context().add_class("color-content")

            if str(a) != "1":
                self.get_style_context().add_class(Granite.STYLE_CLASS_CHECKERBOARD) # if there is alpha below 1

            self.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            self.get_style_context().add_class("color-container")

            self.content_label = self.type.split("/")[1].upper()

        else:
            self.content_label = "title"
            self.content = Gtk.Label("CONTENT")

        #------ clip_content ----#
        #self.content.props.expand = True
        self.content.props.valign = self.content.props.halign = Gtk.Align.CENTER
        self.content.props.name = "clip-contents"
        self.content.props.margin = 6
        clip_content = Gtk.Box()
        clip_content.props.name = "clip-content-box"
        clip_content.props.halign = Gtk.Align.CENTER
        clip_content.props.valign = Gtk.Align.END
        clip_content.props.expand = True
        clip_content.set_size_request(-1, 118)
        clip_content.add(self.content)

        #------ content label ----#
        self.content_label = Gtk.Label(self.content_label)
        self.content_label.props.name = "clip-content-label"
        self.content_label.props.halign = Gtk.Align.START
        self.content_label.props.valign = Gtk.Align.END
        self.content_label.props.margin_bottom = 8
        self.content_label.props.expand = True

        #------ source_icon / application icon ----#
        try:
            pass
        except:
            pass

        source_icon_cache = os.path.join(cache_filedir.replace("cache","icon"), self.source_app.replace(" ",".").lower() + ".png")
        #print(source_icon_cache)

        

        if os.path.exists(source_icon_cache):
            pass
        else:
            pass

        if self.source_icon.find("/") != -1:
            source_icon = Gtk.Image().new_from_file(self.source_icon)
            try:
                new_pixbuf = source_icon.props.pixbuf.scale_simple(24, 24, GdkPixbuf.InterpType.BILINEAR)
                source_icon.props.pixbuf = new_pixbuf
            except:
                source_icon = Gtk.Image().new_from_icon_name("image-missing", Gtk.IconSize.LARGE_TOOLBAR)
        else:
            source_icon = Gtk.Image().new_from_icon_name(self.source_icon, Gtk.IconSize.LARGE_TOOLBAR)
        source_icon.set_pixel_size(24)
        source_icon.props.halign = Gtk.Align.START
        source_icon.props.valign = Gtk.Align.END
        source_icon.props.margin = 4

        #------ timestamp ----#
        self.created_short = datetime.strptime(self.created, '%Y-%m-%d %H:%M:%S.%f')
        self.created_short = self.created_short.strftime('%a, %b %d %Y, %H:%M:%S')
        self.created = datetime.strptime(self.created, '%Y-%m-%d %H:%M:%S.%f')
        self.timestamp = self.friendly_timestamp(self.created)
        self.timestamp = Gtk.Label(self.timestamp)
        self.timestamp.props.name = "clip-timestamp"
        self.timestamp.props.halign = self.timestamp.props.valign = Gtk.Align.END
        self.timestamp.props.margin = 4
        self.timestamp.props.margin_right = 6
        self.timestamp.props.margin_bottom = 8

        #------ clip_info ----#
        clip_info = Gtk.Grid()
        clip_info.props.name = "clip-info"
        clip_info.props.halign = Gtk.Align.FILL
        clip_info.props.valign = Gtk.Align.END
        clip_info.props.expand = True
        clip_info.set_size_request(-1, 32)
        clip_info.attach(source_icon, 0, 0, 1, 1)
        clip_info.attach(self.content_label, 1, 0, 1, 1)
        clip_info.attach(self.timestamp, 3, 0, 1, 1)

        #------ clip_action ----#
        icon_theme = Gtk.IconTheme.get_default()
        icon_theme.prepend_search_path(os.path.join(os.path.dirname(__file__), "..", "..", "data", "icons"))

        protect_action = Gtk.Button().new_with_mnemonic(label="_Protect")
        protect_action.props.image = Gtk.Image().new_from_icon_name("com.github.hezral.clips-protect-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        protect_action.props.always_show_image = True
        protect_action.props.use_underline = True
        # protect_action = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral.clips-protect-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        protect_action.props.name = "clip-action-button"
        protect_action.props.has_tooltip = True
        protect_action.props.tooltip_text = "Protect clip"
        protect_action.props.sensitive = False
        protect_action.set_size_request(30, 30)
        protect_action.connect("clicked", self.on_clip_action, "protect")
        # if "color" in self.type:
        #     protect_action.props.sensitive = False
        #     protect_action.props.has_tooltip = False
        
        view_action = Gtk.Button().new_with_mnemonic(label="_View")
        view_action.props.image = Gtk.Image().new_from_icon_name("com.github.hezral.clips-view-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        view_action.props.always_show_image = True
        view_action.props.use_underline = True
        #view_action = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral.clips-view-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        view_action.props.name = "clip-action-button"
        view_action.props.has_tooltip = True
        view_action.props.tooltip_text = "View clip"
        view_action.set_size_request(30, 32)
        view_action.connect("clicked", self.on_clip_action, "view")
        if "color" in self.type:
            view_action.props.sensitive = False
            view_action.props.has_tooltip = False

        copy_action = Gtk.Button().new_with_mnemonic(label="_Copy")
        copy_action.props.image = Gtk.Image().new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        copy_action.props.always_show_image = True
        copy_action.props.use_underline = True
        # copy_action = Gtk.Button(image=Gtk.Image().new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        copy_action.props.name = "clip-action-button"
        copy_action.props.has_tooltip = True
        copy_action.props.tooltip_text = "Copy to clipboard"
        copy_action.set_size_request(30, 30)
        copy_action.connect("clicked", self.on_clip_action, "copy")
        
        delete_action = Gtk.Button().new_with_mnemonic(label="_Delete")
        delete_action.props.image = Gtk.Image().new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        delete_action.props.always_show_image = True
        delete_action.props.use_underline = True
        # delete_action = Gtk.Button(image=Gtk.Image().new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        delete_action.props.name = "clip-action-button"
        delete_action.props.has_tooltip = True
        delete_action.props.tooltip_text = "Delete clip"
        #delete_action.props.halign = Gtk.Align.START
        delete_action.set_size_request(30, 30)
        delete_action.connect("clicked", self.on_clip_action, "delete")
        
        clip_action = Gtk.Grid()
        clip_action.props.name = "clip-action"
        clip_action.props.halign = clip_action.props.valign = Gtk.Align.CENTER
        clip_action.props.row_spacing = clip_action.props.column_spacing = 4
        # if self.protected == "yes": # add if clip is protected
        #     protect_action.props.
        clip_action.attach(protect_action, 0, 0, 1, 1)
        clip_action.attach(view_action, 1, 0, 1, 1)
        clip_action.attach(copy_action, 0, 1, 1, 1)
        clip_action.attach(delete_action, 1, 1, 1, 1)
        # if self.protected == "yes": # add if clip is protected
        #     clip_action.attach(protect_action, 0, 0, 1, 1)
        # clip_action.attach(view_action, 1, 0, 1, 1)
        # clip_action.attach(copy_action, 2, 0, 1, 1)
        # clip_action.attach(delete_action, 3, 0, 1, 1)

        clip_action_revealer = Gtk.Revealer()
        clip_action_revealer.props.name = "clip-action-revealer"
        clip_action_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        clip_action_revealer.add(clip_action)

        #------ message_action ----#
        message_action = Gtk.Label()
        message_action.props.name = "clip-action-message"
        message_action.props.halign = message_action.props.valign = Gtk.Align.CENTER
        message_action_revealer = Gtk.Revealer()
        message_action_revealer.props.name = "clip-action-message-revealer"
        message_action_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
       
        message_action_revealer.connect("focus-out-event", self.on_message_action_hide)
        message_action_revealer.add(message_action)

        #------ construct ----#
        self.set_size_request(190, 150)
        self.props.name = "clip-container"
        self.props.expand = True
        self.props.has_tooltip = True
        self.props.tooltip_text = "id: {id}\ntype: {type}\nsource: {source_app}\ncreated: {created}".format(
                                                                                                            id=self.id, 
                                                                                                            type=self.type,
                                                                                                            source=self.source, 
                                                                                                            source_app=self.source_app, 
                                                                                                            created=self.created_short)
        self.attach(clip_info, 0, 1, 1, 1)
        self.attach(clip_action_revealer, 0, 0, 1, 2)
        self.attach(message_action_revealer, 0, 0, 1, 2)
        self.attach(clip_content, 0, 0, 1, 1)

        #self.connect("draw", self.draw)

    def draw(self, clips_container, cairo_context):
        #print(locals())
        print(clips_container.get_allocated_width(), clips_container.get_allocated_height())
        
    def on_clip_action(self, button=None, action=None):
        print(datetime.now(), action)
        main_window = self.get_toplevel()
        app = main_window.props.application
        utils = app.utils
        message_action_revealer = utils.get_widget_by_name(widget=self, child_name="clip-action-message-revealer", level=0)

        flowboxchild = self.get_parent()

        message_action = utils.get_widget_by_name(widget=self, child_name="clip-action-message", level=0)
        message_action.props.label = action
        
        message_action_revealer.set_reveal_child(True)
        message_action_revealer.props.can_focus = True
        message_action_revealer.grab_focus()

        if action == "protect":
            pass

        elif action == "view":
            utils.view_clips(self.cache_file)

        elif action == "copy":
            print(action, self.cache_file)

        elif action == "delete":
            flowboxchild.destroy()
            app.cache_manager.delete_record(self.id, self.cache_file)
            main_window.update_total_clips_label("delete")

        # elif action == "updated":
        #     message_action_revealer.grab_focus()

        else:
            pass

    def on_message_action_hide(self, message_action_revealer, event):
        message_action_revealer.set_reveal_child(False)
        message_action_revealer.props.can_focus = False

    def friendly_timestamp(self, time=False):
        """
        Get a datetime object or a int() Epoch self.timestamp and return a
        pretty string like 'an hour ago', 'Yesterday', '3 months ago',
        'just now', etc
        """
        now = datetime.now()
        if type(time) is int:
            diff = now - datetime.fromself.timestamp(time)
        elif isinstance(time,datetime):
            diff = now - time
        elif not time:
            diff = now - now

        second_diff = diff.seconds
        day_diff = diff.days

        if day_diff < 0:
            return ''

        if day_diff == 0:
            if second_diff < 10:
                return "just now"
            if second_diff < 60:
                return str(second_diff) + " seconds ago"
            if second_diff < 120:
                return "a minute ago"
            if second_diff < 3600:
                return str(round(second_diff / 60)) + " minutes ago"
            if second_diff < 7200:
                return "an hour ago"
            if second_diff < 86400:
                return str(round(second_diff / 3600)) + " hours ago"
        if day_diff == 1:
            return "Yesterday"
        if day_diff < 7:
            return str(round(day_diff, 1)) + " days ago"
        if day_diff < 31:
            return str(round(day_diff / 7, 1)) + " weeks ago"
        if day_diff < 365:
            return str(round(day_diff / 30, 1)) + " months ago"
        return str(round(day_diff / 365, 1)) + " years ago (wow!)"


class ImageContainer(Gtk.Grid):
    def __init__(self, filepath, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # width = 190
        # height = 150
        # self.set_size_request(width, height)

        self.pixbuf_original = GdkPixbuf.Pixbuf.new_from_file(filepath)

        self.content_label = "{width} x {height} px".format(width=str(self.pixbuf_original.props.width), height=str(self.pixbuf_original.props.height))

        self.ratio_h_w = self.pixbuf_original.props.height / self.pixbuf_original.props.width
        self.ratio_w_h = self.pixbuf_original.props.width / self.pixbuf_original.props.height
    
        drawing_area = Gtk.DrawingArea()
        drawing_area.props.expand = True
        drawing_area.connect("draw", self.draw)
        drawing_area.props.can_focus = False
 
        self.props.halign = self.props.valign = Gtk.Align.FILL
        self.props.name = "image-container"        
        self.set_size_request(190, 120)
        self.props.expand = True
        self.attach(drawing_area, 0, 0, 1, 2)

        if self.pixbuf_original.get_has_alpha():
            self.get_style_context().add_class(Granite.STYLE_CLASS_CHECKERBOARD)

    def draw(self, drawing_area, cairo_context):
        # Forked and ported from https://github.com/elementary/greeter/blob/master/src/Widgets/BackgroundImage.vala
        from math import pi

        scale = self.get_scale_factor()
        width = self.get_allocated_width () * scale
        height = self.get_allocated_height () * scale
        radius = 4 * scale #Off-by-one to prevent light bleed

        pixbuf_fitted = GdkPixbuf.Pixbuf.new(self.pixbuf_original.get_colorspace(), self.pixbuf_original.get_has_alpha(), self.pixbuf_original.get_bits_per_sample(), width, height)

        if int(width * self.ratio_h_w) < height:
            scaled_pixbuf = self.pixbuf_original.scale_simple(int(height * self.ratio_w_h), height, GdkPixbuf.InterpType.BILINEAR)
        else:
            scaled_pixbuf = self.pixbuf_original.scale_simple(width, int(width * self.ratio_h_w), GdkPixbuf.InterpType.BILINEAR)

        if self.pixbuf_original.props.width * self.pixbuf_original.props.height < width * height:
            # Find the offset we need to center the source pixbuf on the destination since its smaller
            y = abs((height - self.pixbuf_original.props.height) / 2)
            x = abs((width - self.pixbuf_original.props.width) / 2)
            final_pixbuf = self.pixbuf_original
        else:
            # Find the offset we need to center the source pixbuf on the destination
            y = abs((height - scaled_pixbuf.props.height) / 2)
            x = abs((width - scaled_pixbuf.props.width) / 2)
            scaled_pixbuf.copy_area(x, y, width, height, pixbuf_fitted, 0, 0)
            # Set coordinates for cairo surface since this has been fitted, it should be (0, 0) coordinate
            x = y = 0
            final_pixbuf = pixbuf_fitted

        cairo_context.save()
        cairo_context.scale(1.0 / scale, 1.0 / scale)
        cairo_context.new_sub_path()

        # draws rounded rectangle
        cairo_context.arc(width - radius, radius, radius, 0-pi/2, 0) # top-right-corner
        cairo_context.arc(width - radius, height - radius, radius, 0, pi/2) # bottom-right-corner
        cairo_context.arc(radius, height - radius, radius, pi/2, pi) # bottom-left-corner
        cairo_context.arc(radius, radius, radius, pi, pi + pi/2) # top-left-corner
    
        cairo_context.close_path()

        Gdk.cairo_set_source_pixbuf(cairo_context, final_pixbuf, x, y)

        cairo_context.clip()
        cairo_context.paint()
        cairo_context.restore()


    # def on_resize(self, clipscontainer, cairocontext):
    #     #print(locals())
        
    #     #print(self.get_parent())
    #     flowbox = self.get_parent().get_parent()
    #     print(flowbox)
    #     base_size = flowbox.get_allocated_width() + 20
    #     print(base_size)
    #     width = height = base_size / 3.2
    #     print(width)

    #     self.set_size_request(width, height)

    #     print(self.get_allocated_width())
    #     pass

    # def update_flowbox(self, clips):
    #     app = self.get_toplevel().props.application
    #     for clip in clips:
    #         # initialize cachce file with full path        
    #         cache_file = os.path.join(app.cache_manager.cache_filedir, clip[6])
    #         # load
    #         if os.path.exists(cache_file):
    #             self.flowbox.add(ClipsContainer(clip, app.cache_manager.cache_filedir, app.utils))
    #         # clean-up and delete from db
    #         else:
    #             app.cache_manager.delete_record(clip[0], cache_file)    #     self.flowbox.show_all()
    #     #yield False
    #     print(datetime.now(), "show_all")

    #     for child in self.flowbox.get_children():
    #         child.connect("focus-out-event", self.on_child_focus_out, child)
    #     first_child = self.flowbox.get_child_at_index(0)
    #     #self.flowbox.select_child(first_child)
    #     first_child.grab_focus()

    # def load_from_cache(self):
    #     print("load_clips")
    #     app = self.get_toplevel().props.application
    #     # print(datetime.now(), "start load_clips")
    #     clips = app.cache_manager.load_clips()
    #     # print(datetime.now(), "finish load_clips")
    #     # print(datetime.now(), "loop through clips")
    #     # for clip in clips:
    #     #     GLib.idle_add(self.update_flowbox, clip, cache_manager)
    #     print(datetime.now(), "idle_add")
    #     GLib.idle_add(self.update_flowbox, clips)
    #     # print(datetime.now(), "loop through clips")
    #     # for clip in clips:
    #     #     self.flowbox.add(ClipsContainer(clip, cache_manager.cache_filedir))
    #     # print(datetime.now(), "show_all")
    #     # self.show_all()