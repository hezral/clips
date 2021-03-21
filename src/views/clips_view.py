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
from utils import ConvertToRGB
gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, WebKit2, Granite, GdkPixbuf, GLib, Pango, Gdk

import os
from datetime import datetime
import time

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

        #------ scrolled_window ----#
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.props.expand = True
        scrolled_window.props.hscrollbar_policy = Gtk.PolicyType.NEVER
        scrolled_window.add(self.flowbox)
        scrolled_window.connect("edge-reached", self.on_edge_reached)
        
        #------ construct ----#
        self.props.name = "clips-view"
        self.props.expand = True
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
            # new_flowboxchild = [child for child in self.flowbox.get_children() if child.get_children()[0].id == id][0]
            # new_flowboxchild.connect("focus-out-event", self.on_child_focus_out, new_flowboxchild)
            # new_flowboxchild.connect("focus", self.on_child_focus)
            
            if app_startup is False:
                # total_clips = int(main_window.total_clips_label.props.label.split(": ")[1])
                # total_clips = total_clips + 1
                # main_window.total_clips_label.props.label = "Clips: {total}".format(total=total_clips)
                main_window.update_total_clips_label("add")

            self.flowbox.show_all()

        # clean-up and delete from db since cache_file doesn't exist
        elif os.path.exists(cache_file) is False:
            print("cache file doesn't exist")
            app.cache_manager.delete_record(id, cache_file)

    def on_edge_reached(self, scrolledwindow, position):
        if position.value_name == "GTK_POS_BOTTOM":
            print(datetime.now(), "loading next items")

# ----------------------------------------------------------------------------------------------------

class ClipsContainer(Gtk.EventBox):
    def __init__(self, clip, cache_filedir, utils, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # get widget scale factor for redraw event
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

        #------ clip_action ----#
        clip_action_revealer = self.generate_clip_action()

        # initialize cache file with full path        
        self.cache_file = os.path.join(cache_filedir, self.cache_file)

        # initialize empty variable
        self.content = None

        if self.type == "files":
            self.content = open(self.cache_file, "r")
            self.content_label = str(len(self.content.read())) + "chars"
            self.content = Gtk.Label(self.content.read())

        elif self.type == "image":
            self.content = ImageContainer(self.cache_file)

        elif self.type == "html":
            self.content = HtmlContainer(self.cache_file, utils)

        # elif self.type == "richtext":
        #     self.content = open(self.cache_file, "r")
        #     self.content_label = str(len(self.content.read())) + " chars"
        #     self.content = Gtk.Label(self.content.read())

        elif self.type == "plaintext":
            self.content = PlainTextContainer(self.cache_file)

        # elif self.type == "url":
        #     self.content = Gtk.Image().new_from_icon_name("internet-web-browser", Gtk.IconSize.DIALOG)
        #     self.content_label = "Internet URL"

        elif "color" in self.type:
            self.content = ColorContainer(self.cache_file, self.type, utils)
            
        else:
            print(self.cache_file, self.type)
            self.content = DefaultContainer(self.cache_file, self.type, utils)


        #------ clip_content ----#
        #self.content.props.expand = True
        self.content.props.valign = self.content.props.halign = Gtk.Align.FILL
        # self.content.props.name = "clip-contents"
        # self.content.props.margin = 6
        #clip_content = Gtk.Box()
        # clip_content.props.name = "clip-content-box"
        # clip_content.props.halign = Gtk.Align.CENTER
        # clip_content.props.valign = Gtk.Align.CENTER
        # clip_content.props.expand = True
        # clip_content.set_size_request(-1, 118)
        #clip_content.add(self.content)

        #------ clip_info ----#
        if self.content.label is not None:
            self.content_label = Gtk.Label("Clip")
        else:
            self.content_label = Gtk.Label(self.content.label)
        self.content_label.props.name = "clip-content-label"
        self.content_label.props.halign = Gtk.Align.START
        self.content_label.props.valign = Gtk.Align.END
        self.content_label.props.margin_bottom = 10
        self.content_label.props.expand = True

        #------ source_icon / application icon ----#
        source_icon_cache = os.path.join(cache_filedir[:-6],"icon", self.source_app.replace(" ",".").lower() + ".png")
        
        if os.path.exists(source_icon_cache):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(source_icon_cache, 24 * scale, 24 * scale, True)
            source_icon = Gtk.Image().new_from_pixbuf(pixbuf)
        else:
            source_icon = Gtk.Image().new_from_icon_name("image-missing", Gtk.IconSize.LARGE_TOOLBAR)
            source_icon.set_pixel_size(24 * scale)

        source_icon.props.halign = Gtk.Align.START
        source_icon.props.valign = Gtk.Align.END
        source_icon.props.margin = 4
        source_icon.props.has_tooltip = True
        source_icon.props.tooltip_text = self.source_app

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
        self.timestamp.props.margin_bottom = 10
        self.timestamp.props.has_tooltip = True
        self.timestamp.props.tooltip_text = self.created_short

        clip_info = Gtk.Grid()
        clip_info.props.name = "clip-info"
        clip_info.props.halign = Gtk.Align.FILL
        clip_info.props.valign = Gtk.Align.START
        clip_info.props.hexpand = True
        clip_info.props.can_focus = False
        clip_info.props.has_tooltip = True
        clip_info.props.tooltip_text = "id: {id}\ntype: {type}\nsource: {source}".format(id=self.id, type=self.type, source=self.source)
        clip_info.set_size_request(-1, 32)
        clip_info.attach(source_icon, 0, 0, 1, 1)
        clip_info.attach(self.content_label, 1, 0, 1, 1)
        clip_info.attach(self.timestamp, 2, 0, 1, 1)

        clip_info_revealer = Gtk.Revealer()
        clip_info_revealer.props.name = "clip-info-revealer"
        clip_info_revealer.props.halign = Gtk.Align.FILL
        clip_info_revealer.props.valign = Gtk.Align.START
        clip_info_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        clip_info_revealer.add(clip_info)

        #------ message_action ----#
        message_action = Gtk.Label()
        message_action.props.name = "clip-action-message"
        message_action.props.halign = message_action.props.valign = Gtk.Align.CENTER
        message_action_revealer = Gtk.Revealer()
        message_action_revealer.props.name = "clip-action-message-revealer"
        message_action_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        message_action_revealer.add(message_action)

        #------ construct ----#
        
        self.set_size_request(200, 160)
        self.props.name = "clip-container"
        self.props.expand = True
    
        self.container_grid = Gtk.Grid()
        self.container_grid.props.name = "clip-container-grid"
        self.container_grid.attach(clip_info_revealer, 0, 0, 1, 1)
        self.container_grid.attach(clip_action_revealer, 0, 0, 1, 1)
        self.container_grid.attach(message_action_revealer, 0, 0, 1, 1)
        self.container_grid.attach(self.content, 0, 0, 1, 1)

        # self.select_clip = self.generate_action_btn("com.github.hezral.clips-select-symbolic", "Select", "select")
        # self.select_clip.props.halign = self.select_clip.props.valign = Gtk.Align.START
        # self.select_clip.set_size_request(32, 32)

        # overlay = Gtk.Overlay()
        # overlay.add(self.container_grid)
        # overlay.add_overlay(self.select_clip)

        self.add(self.container_grid)
        
        # handle mouse enter/leave events on the flowboxchild
        self.connect("enter-notify-event", self.cursor_entering_clip)
        self.connect("leave-notify-event", self.cursor_leaving_clip)

    def focus_clip(self, clip_action_revealer, eventfocus, type):
        flowboxchild = self.get_parent()
        if type == "out":
            if not flowboxchild.is_selected():
                clip_action_revealer.set_reveal_child(False)
        else:
            clip_action_revealer.set_reveal_child(True)

    def cursor_entering_clip(self, widget, eventcrossing):
        # add css class for hover event
        self.get_parent().get_style_context().add_class("hover")
        
        flowboxchild = self.get_parent()
        main_window = self.get_toplevel()
        app = main_window.props.application
        utils = app.utils

        clip_action_revealer = utils.get_widget_by_name(widget=flowboxchild, child_name="clip-action-revealer", level=0)
        clip_action_revealer.set_reveal_child(True)

        # add zoom effect on hovering an image container
        # content = utils.get_widget_by_name(widget=flowboxchild, child_name="image-container", level=0)
        # if content is not None:
        #     content.hover()

    def cursor_leaving_clip(self, widget, eventcrossing):
        # remove css class for hover event
        self.get_parent().get_style_context().remove_class("hover")

        flowboxchild = self.get_parent()
        main_window = self.get_toplevel()
        app = main_window.props.application
        utils = app.utils

        clip_action_revealer = utils.get_widget_by_name(widget=flowboxchild, child_name="clip-action-revealer", level=0)
        message_action_revealer = utils.get_widget_by_name(widget=flowboxchild, child_name="clip-action-message-revealer", level=0)
        clip_info_revealer = utils.get_widget_by_name(widget=flowboxchild, child_name="clip-info-revealer", level=0)

        if flowboxchild.is_selected():
            clip_action_revealer.set_reveal_child(True)
            clip_action_revealer.grab_focus()
        else: 
            clip_action_revealer.set_reveal_child(False)
        
        if message_action_revealer.get_child_revealed():
            message_action_revealer.set_reveal_child(False)

        if clip_info_revealer.get_child_revealed():
            clip_info_revealer.set_reveal_child(False)

    def generate_action_btn(self, iconname, tooltiptext, actionname):
        button = Gtk.Button(image=Gtk.Image().new_from_icon_name(iconname, Gtk.IconSize.SMALL_TOOLBAR))
        button.props.name = "clip-action-button"
        button.props.hexpand = True
        button.props.has_tooltip = True
        button.props.tooltip_text = tooltiptext
        button.props.can_focus = False
        button.set_size_request(30, 30)
        button.connect("clicked", self.on_clip_action, actionname)        
        return button
    
    def generate_clip_action(self):
        protect_action = self.generate_action_btn("com.github.hezral.clips-protect-symbolic", "Protect", "protect")
        info_action = self.generate_action_btn("com.github.hezral.clips-info-symbolic", "Show Info", "info")
        view_action = self.generate_action_btn("com.github.hezral.clips-view-symbolic", "View", "view")
        copy_action = self.generate_action_btn("edit-copy-symbolic", "Copy to Clipboard", "copy")
        color_action = self.generate_action_btn("com.github.hezral.clips-colorpalette-symbolic", "Change color", "color")
        delete_action = self.generate_action_btn("edit-delete-symbolic", "Delete ", "delete")

        clip_action = Gtk.Grid()
        clip_action.props.name = "clip-action"
        clip_action.props.halign = Gtk.Align.FILL
        clip_action.props.valign = Gtk.Align.END
        clip_action.props.hexpand = True
        clip_action.props.can_focus = False
        clip_action.props.row_spacing = clip_action.props.column_spacing = 4
        
        if "color" in self.type:
            protect_action.props.sensitive = False
            view_action.props.sensitive = False
            protect_action.get_style_context().add_class("clip-action-disabled")
            view_action.get_style_context().add_class("clip-action-disabled")
               
        clip_action.attach(protect_action, 0, 0, 1, 1)
        clip_action.attach(info_action, 1, 0, 1, 1)
        clip_action.attach(view_action, 2, 0, 1, 1)
        clip_action.attach(copy_action, 3, 0, 1, 1)
        # clip_action.attach(color_action, 4, 0, 1, 1)
        clip_action.attach(delete_action, 5, 0, 1, 1)

        clip_action_revealer = Gtk.Revealer()
        clip_action_revealer.props.name = "clip-action-revealer"    
        clip_action_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        clip_action_revealer.add(clip_action)
        clip_action_revealer.props.can_focus = True
        
        # handle mouse focus in/out on the clip action bar
        clip_action_revealer.connect("focus-out-event", self.focus_clip, "out")
        clip_action_revealer.connect("focus-in-event", self.focus_clip, "in")

        return clip_action_revealer
        
    def on_clip_action(self, button=None, action=None):
        print(datetime.now(), action)
        main_window = self.get_toplevel()
        app = main_window.props.application
        utils = app.utils
        message_action_revealer = utils.get_widget_by_name(widget=self, child_name="clip-action-message-revealer", level=0)
        clip_info_revealer = utils.get_widget_by_name(widget=self, child_name="clip-info-revealer", level=0)

        flowboxchild = self.get_parent()
        flowboxchild.do_activate(flowboxchild)

        flowbox = flowboxchild.get_parent()
        flowbox.select_child(flowboxchild)

        message_action = utils.get_widget_by_name(widget=self, child_name="clip-action-message", level=0)
        message_action.props.label = action
        

        if action == "protect":
            message_action_revealer.set_reveal_child(True)
            pass

        elif action == "info":
            print("info", self.props.tooltip_text)
            clip_info_revealer.set_reveal_child(True)

        elif action == "view":
            utils.view_clips(self.cache_file)

        elif action == "copy":
            message_action_revealer.set_reveal_child(True)
            print(action, self.cache_file)

        elif action == "force_delete":
            flowboxchild.destroy()
            app.cache_manager.delete_record(self.id, self.cache_file)
            main_window.update_total_clips_label("delete")

        elif action == "delete":
            dialog = Gtk.Dialog.new()
            dialog.props.title="Confirm delete action"
            dialog.props.transient_for = main_window
            btn_ok = Gtk.Button(label="OK")
            btn_ok.get_style_context().add_class("destructive-action")
            btn_cancel = Gtk.Button(label="Cancel")
            dialog.add_action_widget(btn_ok, Gtk.ResponseType.OK)
            dialog.add_action_widget(btn_cancel, Gtk.ResponseType.CANCEL)
            dialog.set_default_size(150, 100)
            label = Gtk.Label(label="Delete this clip?\n{details}".format(details=self.props.tooltip_text))
            box = dialog.get_content_area()
            box.props.margin = 10
            box.add(label)
            dialog.show_all()
            btn_cancel.grab_focus()
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                flowboxchild.destroy()
                app.cache_manager.delete_record(self.id, self.cache_file)
                main_window.update_total_clips_label("delete")
            dialog.destroy()

        else:
            print(action)
            pass

    def on_message_action_hide(self, message_action_revealer, event):
        message_action_revealer.set_reveal_child(False)
        message_action_revealer.props.can_focus = False

    def on_revealer_focus_out(self, revealer, event):
        revealer.set_reveal_child(False)

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

# ----------------------------------------------------------------------------------------------------

class DefaultContainer(Gtk.Grid):
    def __init__(self, filepath, type, utils, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.content = Gtk.Label(type)
        self.content.props.wrap_mode = Pango.WrapMode.CHAR
        self.content.props.max_width_chars = 23
        self.content.props.wrap = True
        self.content.props.selectable = False
        self.content.props.expand = True
        self.content.props.ellipsize = Pango.EllipsizeMode.END
        
        self.props.margin = 10
        self.props.margin_left = self.props.margin_right = 10
        self.props.name = "plaintext-container"
        self.attach(self.content, 0, 0, 1, 1)

        self.label = str(len(type)) + " chars"
        self.name = "content"
        self.get_style_context().add_class("clip-containers")

# ----------------------------------------------------------------------------------------------------

class ImageContainer(Gtk.Grid):
    def __init__(self, filepath, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pixbuf_original = GdkPixbuf.Pixbuf.new_from_file(filepath)
        self.ratio_h_w = self.pixbuf_original.props.height / self.pixbuf_original.props.width
        self.ratio_w_h = self.pixbuf_original.props.width / self.pixbuf_original.props.height
    
        drawing_area = Gtk.DrawingArea()
        drawing_area.props.expand = True
        drawing_area.connect("draw", self.draw)
        drawing_area.props.can_focus = False
 
        self.props.halign = self.props.valign = Gtk.Align.FILL
        self.props.name = "image-container"
        self.attach(drawing_area, 0, 0, 1, 1)

        if self.pixbuf_original.get_has_alpha():
            # self.get_style_context().add_class(Granite.STYLE_CLASS_CHECKERBOARD)
            self.get_style_context().add_class("checkerboard")
        
        self.label = "{width} x {height} px".format(width=str(self.pixbuf_original.props.width), height=str(self.pixbuf_original.props.height))

        self.name = "content"
        self.get_style_context().add_class("clip-containers")

    def hover(self, *args):
        print(locals())

    def draw(self, drawing_area, cairo_context, hover_scale=1):
        # print("draw")
        # Forked and ported from https://github.com/elementary/greeter/blob/master/src/Widgets/BackgroundImage.vala
        from math import pi

        scale = self.get_scale_factor()
        width = self.get_allocated_width () * scale * hover_scale
        height = self.get_allocated_height () * scale * hover_scale
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

# ----------------------------------------------------------------------------------------------------

class ColorContainer(Gtk.Grid):
    def __init__(self, filepath, type, utils, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.content = open(filepath, "r")
        self.content = self.content.read()

        rgb, a = utils.ConvertToRGB(self.content)

        color_code = "rgba({red},{green},{blue},{alpha})".format(red=str(rgb[0]),green=str(rgb[1]),blue=str(rgb[2]),alpha=str(a))
        
        if utils.isLightOrDark(rgb) == "light":
            font_color = "rgba(0,0,0,0.85)"
        else:
            font_color = "rgba(255,255,255,0.85)"

        color_content_css = ".color-container-bg {background-color: " + color_code + "; color: " + font_color + ";}"
        font_css = ".color-content {letter-spacing: 1px; font-weight: bold; font-size: 120%; opacity: 0.8;}"
        css = color_content_css + "\n" + font_css
        provider = Gtk.CssProvider()
        provider.load_from_data(bytes(css.encode()))

        self.content = Gtk.Label(self.content)
        self.content.props.expand = True
        self.content.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.content.get_style_context().add_class("color-content")

        # add checkerboard background for colors with alpha less than 1
        if str(a) != "1":
            self.get_style_context().add_class("checkerboard")

        self.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.get_style_context().add_class("color-container-bg")

        self.props.halign = self.props.valign = Gtk.Align.FILL
        self.props.name = "color-container"
        self.attach(self.content, 0, 0, 1, 1)

        self.label = type.split("/")[1].upper()
        self.name = "content"
        self.get_style_context().add_class("clip-containers")

# ----------------------------------------------------------------------------------------------------

class PlainTextContainer(Gtk.Grid):
    def __init__(self, filepath, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open(filepath) as f:
            for i, l in enumerate(f):
                pass

        with open(filepath) as myfile:
            firstNlines=myfile.readlines()[0:10] #put here the interval you want
        self.content = ''.join(firstNlines)

        self.content = Gtk.Label(self.content)
        self.content.props.wrap_mode = Pango.WrapMode.CHAR
        self.content.props.max_width_chars = 23
        self.content.props.wrap = True
        self.content.props.selectable = False
        self.content.props.expand = True
        self.content.props.ellipsize = Pango.EllipsizeMode.END
        
        self.props.margin = 10
        self.props.margin_left = self.props.margin_right = 10
        self.props.name = "plaintext-container"
        self.attach(self.content, 0, 0, 1, 1)

        if not i+1 < 10:
            lines = Gtk.Label(str(i+1-10) + " lines more...")
            lines.props.halign = Gtk.Align.END
            self.attach(lines, 0, 1, 1, 1)

        self.label = str(len(self.content.props.label)) + " chars"
        self.name = "content"
        self.get_style_context().add_class("clip-containers")

# ----------------------------------------------------------------------------------------------------

class HtmlContainer(Gtk.Grid):
    def __init__(self, filepath, utils, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.content = open(filepath, "r")
        self.content = self.content.read()

        webview = WebKit2.WebView()
        webview.props.zoom_level = 0.85
        webview.load_html(self.content)
        webview.props.expand = True
        # webview.props.sensitive = False

        css_bg_color = utils.get_css_background_color(self.content)

        if css_bg_color is not None:
            rgb, a = utils.ConvertToRGB(css_bg_color)
            color_code = "rgba({red},{green},{blue},{alpha})".format(red=str(rgb[0]),green=str(rgb[1]),blue=str(rgb[2]),alpha=str(a))
            webview_bg_color = Gdk.RGBA(red=float(rgb[0] / 255), green=float(rgb[1] / 255), blue=float(rgb[2] / 255), alpha=1)
            webview.set_background_color(webview_bg_color)
        else:
            color_code = "@theme_base_color"
            webview_bg_color = Gdk.RGBA(red=1.0000, green=1.0000, blue=1.0000, alpha=1.0000)
            webview.set_background_color(webview_bg_color)

        html_content_css = ".html-container-bg {background-color: " + color_code + ";}"
        provider = Gtk.CssProvider()
        provider.load_from_data(bytes(html_content_css.encode()))

        self.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.get_style_context().add_class("html-container-bg")

        self.props.name = "html-container"
        self.attach(webview, 0, 0, 1, 1)

        self.label = str(len(self.content)) + " chars"
        self.name = "content"
        self.get_style_context().add_class("clip-containers")