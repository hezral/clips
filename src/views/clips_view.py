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
from datetime import datetime

import os

class ClipsView(Gtk.Grid):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #------ flowbox ----#
        self.flowbox = Gtk.FlowBox()
        self.flowbox.props.name = "flowbox"
        self.flowbox.props.homogeneous = False
        self.flowbox.props.expand = False
        self.flowbox.props.row_spacing = 10
        self.flowbox.props.column_spacing = 10
        self.flowbox.props.min_children_per_line = 2
        self.flowbox.props.valign = Gtk.Align.START
        self.flowbox.props.halign = Gtk.Align.START
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
        self.set_size_request(436, 420)
        self.attach(scrolled_window, 0, 0, 1, 1)



    def update_flowbox(self, clips):

        app = self.get_toplevel().props.application
        
        for clip in clips:
            
            # initialize cachce file with full path        
            cache_file = os.path.join(app.cache_manager.cache_filedir, clip[6])
            # load
            if os.path.exists(cache_file):
                self.flowbox.add(ClipsContainer(clip, app.cache_manager.cache_filedir, app.utils))
            # clean-up and delete from db
            else:
                app.cache_manager.delete_record(clip[0], cache_file)

        self.flowbox.show_all()
        #yield False
        print(datetime.now(), "show_all")

        for child in self.flowbox.get_children():
            child.connect("focus-out-event", self.on_child_focus_out, child)

    def load_from_cache(self):
        print("load_clips")
        
        app = self.get_toplevel().props.application
        
        # print(datetime.now(), "start load_clips")
        clips = app.cache_manager.load_clips()
        # print(datetime.now(), "finish load_clips")
        
        # print(datetime.now(), "loop through clips")
        # for clip in clips:
        #     GLib.idle_add(self.update_flowbox, clip, cache_manager)

        print(datetime.now(), "idle_add")
        GLib.idle_add(self.update_flowbox, clips)
        
        # print(datetime.now(), "loop through clips")
        # for clip in clips:
        #     self.flowbox.add(ClipsContainer(clip, cache_manager.cache_filedir))
        
        # print(datetime.now(), "show_all")
        # self.show_all()

    def new_clip(self, data):
        print("newclip")

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

        self.id = clip[0]
        self.target = clip[1]
        self.created = clip[2]
        self.source = clip[3]
        self.source_app = clip[4]
        self.source_icon = clip[5]
        self.cache_file = clip[6]
        self.type = clip[7]

        # initialize cachce file with full path        
        self.cache_file = os.path.join(cache_filedir, self.cache_file)

        # initialize empty variable
        content = None

        if self.type == "files":
            content = open(self.cache_file, "r")
            self.content_label = str(len(content.read())) + "chars"
            content = Gtk.Label(content.read())

        elif self.type == "image":
            pixbuf_original = GdkPixbuf.Pixbuf.new_from_file(self.cache_file)
            if pixbuf_original.props.width < 192:
                pixbuf = pixbuf_original
            else:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(self.cache_file, 192, -1, True)
            image = Gtk.Image().new_from_pixbuf(pixbuf)
            self.content_label = "{width} x {height} px".format(width=str(pixbuf_original.props.width), height=str(pixbuf_original.props.height))
            content = image
            self.get_style_context().add_class(Granite.STYLE_CLASS_CHECKERBOARD)

        elif self.type == "html":
            content = open(self.cache_file, "r")
            content = content.read()
            self.content_label = str(len(content)) + " chars"

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
            webview.load_html(content)
            webview.props.expand = True
            #webview.props.sensitive = False
            eventbox = Gtk.EventBox()
            eventbox.props.above_child = True
            eventbox.add(webview)
            content = eventbox

        elif self.type == "richtext":
            content = open(self.cache_file, "r")
            self.content_label = str(len(content.read())) + " chars"
            content = Gtk.Label(content.read())

        elif self.type == "plaintext":
            content = open(self.cache_file, "r")
            content = content.read()
            self.content_label = str(len(content)) + " chars"
            content = Gtk.Label(content)
            content.props.wrap_mode = Pango.WrapMode.CHAR
            content.props.max_width_chars = 30
            content.props.wrap = True
            content.props.selectable = False

        elif self.type == "url":
            content = Gtk.Image().new_from_icon_name("internet-web-browser", Gtk.IconSize.DIALOG)
            self.content_label = "Internet URL"

        elif "color" in self.type:
            content = open(self.cache_file, "r")
            content = content.read()
            content = content.strip(" ").strip(";") #strip the ; for processing 
            _content = content.strip(")") #strip the ) for processing 
            #print(self.id, self.type, content)

            if self.type == "color/hex":
                rgb = utils.HexToRGB(content)
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
                h = int(h) / 360
                s = int(s.replace("%","")) / 100
                l = int(l.replace("%)","")) / 100
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

            content = Gtk.Label(content)
            content.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            content.get_style_context().add_class("color-content")

            if str(a) != "1":
                self.get_style_context().add_class(Granite.STYLE_CLASS_CHECKERBOARD) # if there is alpha below 1

            self.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            self.get_style_context().add_class("color-container")

            self.content_label = self.type.split("/")[1].upper()

        else:
            self.content_label = "title"
            content = Gtk.Label("CONTENT")

        #------ clip_content ----#
        content.props.expand = True
        content.props.margin = 6
        clip_content = Gtk.Box()
        clip_content.props.name = "clip-content"
        clip_content.props.halign = Gtk.Align.FILL
        clip_content.props.valign = Gtk.Align.END
        clip_content.props.expand = True
        #clip_content.props.margin = 10
        clip_content.set_size_request(-1, 118)
        clip_content.add(content)

        #------ content label ----#
        self.content_label = Gtk.Label(self.content_label)
        self.content_label.props.name = "clip-content-label"
        self.content_label.props.halign = Gtk.Align.START
        self.content_label.props.valign = Gtk.Align.END
        self.content_label.props.margin_bottom = 8
        self.content_label.props.expand = True

        #------ source_icon / application icon ----#
        if self.source_icon.find("/") != -1:
            source_icon = Gtk.Image().new_from_file(self.source_icon)
            try:
                new_pixbuf = source_icon.props.pixbuf.scale_simple(24, 24, GdkPixbuf.InterpType.BILINEAR)
                source_icon.props.pixbuf = new_pixbuf
            except:
                source_icon = Gtk.Image().new_from_icon_name("image-missing", Gtk.IconSize.LARGE_TOOLBAR)
        else:
            source_icon = Gtk.Image().new_from_icon_name(self.source_icon, Gtk.IconSize.LARGE_TOOLBAR)
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
        clip_info.props.has_tooltip = True
        clip_info.props.tooltip_text = "id: {id}\ntype: {type}\nsource: {source_app}\ncreated: {created}".format(
                                                                                                            id=self.id, 
                                                                                                            type=self.type,
                                                                                                            source=self.source, 
                                                                                                            source_app=self.source_app, 
                                                                                                            created=self.created_short)

        #------ clip_action ----#
        icon_theme = Gtk.IconTheme.get_default()
        print(os.path.join(os.path.dirname(__file__), "..", "..", "..","data", "icons"))
        icon_theme.prepend_search_path(os.path.join(os.path.dirname(__file__), "..", "..", "data", "icons"))

        protect_action = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral.clips-protect-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        protect_action.props.name = "clip-action-button"
        protect_action.props.has_tooltip = True
        protect_action.props.tooltip_text = "Protect clip"
        protect_action.set_size_request(30, 30)
        protect_action.connect("clicked", self.on_clip_action, "protect")
        
        view_action = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral.clips-view-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        view_action.props.name = "clip-action-button"
        view_action.props.has_tooltip = True
        view_action.props.tooltip_text = "View clip"
        view_action.set_size_request(30, 30)
        view_action.connect("clicked", self.on_clip_action, "view")

        copy_action = Gtk.Button(image=Gtk.Image().new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        copy_action.props.name = "clip-action-button"
        copy_action.props.has_tooltip = True
        copy_action.props.tooltip_text = "Copy to clipboard"
        copy_action.set_size_request(30, 30)
        copy_action.connect("clicked", self.on_clip_action, "copy")
        
        delete_action = Gtk.Button(image=Gtk.Image().new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.SMALL_TOOLBAR))
        delete_action.props.name = "clip-action-button"
        delete_action.props.has_tooltip = True
        delete_action.props.tooltip_text = "Delete clip"
        delete_action.set_size_request(30, 30)
        delete_action.connect("clicked", self.on_clip_action, "delete")
        
        clip_action = Gtk.Grid()
        clip_action.props.name = "clip-action"
        clip_action.props.halign = clip_action.props.valign = Gtk.Align.CENTER
        clip_action.props.column_spacing = 8
        clip_action.attach(protect_action, 0, 0, 1, 1)
        clip_action.attach(view_action, 1, 0, 1, 1)
        clip_action.attach(copy_action, 2, 0, 1, 1)
        clip_action.attach(delete_action, 3, 0, 1, 1)

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
        #message_action_revealer.props.transition_duration = 750
        message_action_revealer.props.can_focus = True
        message_action_revealer.connect("focus-out-event", self.on_message_action_hide)
        message_action_revealer.add(message_action)

        #------ id ----#
        clip_id = Gtk.Label(self.id)
        clip_id.props.name = "clip-id"
        clip_id.props.halign = clip_id.props.valign = Gtk.Align.START

        #------ construct ----#
        self.set_size_request(200, 150)
        self.props.name = "clip-container"
        self.props.expand = True
        self.attach(clip_info, 0, 1, 1, 1)
        self.attach(clip_action_revealer, 0, 0, 1, 2)
        self.attach(message_action_revealer, 0, 0, 1, 2)
        self.attach(clip_content, 0, 0, 1, 1)
        
    def on_clip_action(self, button, action):
        print(datetime.now(), action)
        main_window = self.get_toplevel()
        app = main_window.props.application
        utils = app.utils
        message_action_revealer = utils.get_widget_by_name(widget=self, child_name="clip-action-message-revealer", level=0)

        flowboxchild = self.get_parent()

        message_action = utils.get_widget_by_name(widget=self, child_name="clip-action-message", level=0)
        message_action.props.label = action
        message_action_revealer.set_reveal_child(True)
        message_action_revealer.grab_focus()

        if action == "delete":
            flowboxchild.destroy()
            app.cache_manager.delete_record(self.id, self.cache_file)
        elif action == "copy":
            print(action)
            print(self.cache_file)
        elif action == "view":
            print(action)

    def on_message_action_hide(self, revealer, event):
        revealer.set_reveal_child(False)

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







