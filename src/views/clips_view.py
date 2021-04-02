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

import gi
from utils import ConvertToRGB
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, WebKit2, GdkPixbuf, Pango, Gdk, Gio

import os
from datetime import datetime
import time

class ClipsView(Gtk.Grid):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #------ flowbox ----#
        self.flowbox = Gtk.FlowBox()
        self.flowbox.props.name = "flowbox"
        self.flowbox.props.homogeneous = False
        self.flowbox.props.row_spacing = 10
        self.flowbox.props.column_spacing = 10
        self.flowbox.props.max_children_per_line = 9
        self.flowbox.props.min_children_per_line = app.gio_settings.get_int("min-column-number")
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
        self.scale = self.get_scale_factor()

        self.cache_filedir = cache_filedir
        self.id = clip[0]
        self.target = clip[1]
        self.created = clip[2]
        self.source = clip[3]
        self.source_app = clip[4]
        self.source_icon = clip[5]
        self.cache_file = clip[6]
        self.type = clip[7]
        self.protected = clip[8]

        # initialize cache file with full path        
        self.cache_file = os.path.join(self.cache_filedir, self.cache_file)

        # initialize empty variable
        self.content = None

        #------ container types, refer to clips_supported.py ----#
        if "office/spreadsheet" in self.type:
            self.content = SpreadsheetContainer(self.cache_file, self.type, utils)
        elif "office/presentation" in self.type:
            self.content = PresentationContainer(self.cache_file, self.type, utils)
        elif "office/word" in self.type:
            self.content = WordContainer(self.cache_file, self.type, utils)
        elif "files" in self.type:
            self.content = FilesContainer(self.cache_file, self.type, utils)
        elif "image" in self.type:
            self.content = ImageContainer(self.cache_file, self.type, utils)
        elif "html" in self.type:
            self.content = HtmlContainer(self.cache_file, self.type, utils)
        elif "richtext" in self.type:
            self.content = FilesContainer(self.cache_file, self.type, utils)
        elif "plaintext" in self.type:
            self.content = PlainTextContainer(self.cache_file, self.type, utils)
        elif "color" in self.type:
            self.content = ColorContainer(self.cache_file, self.type, utils)
        elif "url" in self.type:
            self.content = UrlContainer(self.cache_file, self.type, utils, self.cache_filedir)
        else:
            print(self.cache_file, self.type)
            self.content = FallbackContainer(self.cache_file, self.type, utils)


        # print(self.cache_file, self.type)

        #------ clip_info ----#
        clip_info_revealer = self.generate_clip_info()

        #------ clip_action_notify ----#
        clip_action_notify_revealer = self.generate_clip_action_notify()
        
        #------ clip_action ----#
        clip_action_revealer = self.generate_clip_action()

        clip_select_revealer = self.generate_clip_select()

        #------ construct ----#
        # self.container_grid = Gtk.Grid()
        # self.container_grid.props.name = "clip-container-grid"
        # self.container_grid.attach(clip_info_revealer, 0, 0, 1, 1)
        # self.container_grid.attach(clip_action_revealer, 0, 0, 1, 1)
        # self.container_grid.attach(clip_action_notify, 0, 0, 1, 1)
        # self.container_grid.attach(self.content, 0, 0, 1, 1)

        self.container_overlay = Gtk.Overlay()
        self.container_overlay.props.name = "clip-container-overlay"
        self.container_overlay.add(self.content)
        self.container_overlay.add_overlay(clip_action_notify_revealer)
        self.container_overlay.set_overlay_pass_through(clip_action_notify_revealer, True)
        self.container_overlay.add_overlay(clip_action_revealer)
        self.container_overlay.set_overlay_pass_through(clip_action_revealer, True)
        self.container_overlay.add_overlay(clip_info_revealer)
        self.container_overlay.set_overlay_pass_through(clip_info_revealer, True)
        self.container_overlay.add_overlay(clip_select_revealer)

        self.container_grid = Gtk.Grid()
        self.container_grid.props.name = "clip-container-grid"
        self.container_grid.attach(self.container_overlay, 0, 0, 1, 1)

        self.add(self.container_grid)

        self.set_size_request(200, 160)
        self.props.name = "clip-container"
        self.props.expand = True
        
        # handle mouse enter/leave events on the flowboxchild
        self.connect("enter-notify-event", self.on_cursor_entering_clip)
        self.connect("leave-notify-event", self.on_cursor_leaving_clip)

    def generate_clip_select(self):
        clip_select_button = self.generate_action_button("com.github.hezral.clips-select-symbolic", "Select", "select")
        clip_select_button.props.halign = clip_select_button.props.valign = Gtk.Align.CENTER
        clip_select_button.set_size_request(32, 32)

        clip_select_revealer = Gtk.Revealer()
        clip_select_revealer.props.name = "clip-select-revealer"
        clip_select_revealer.props.halign = Gtk.Align.END
        clip_select_revealer.props.valign = Gtk.Align.START
        clip_select_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        # clip_select_revealer.add(clip_select_button)

        return clip_select_revealer

    def generate_action_button(self, iconname, tooltiptext, actionname):
        icon = Gtk.Image().new_from_icon_name(iconname, Gtk.IconSize.SMALL_TOOLBAR)
        button = Gtk.Button(image=icon)
        button.props.name = "clip-action-button"
        button.props.hexpand = True
        button.props.has_tooltip = True
        button.props.tooltip_text = tooltiptext
        button.props.can_focus = False
        button.set_size_request(30, 30)
        button.connect("clicked", self.on_clip_action, actionname)
        return button
    
    def generate_clip_info(self):
        if self.content.label is None:
            self.content_label = Gtk.Label("Clip")
        else:
            self.content_label = Gtk.Label(self.content.label)
        self.content_label.props.name = "clip-content-label"
        self.content_label.props.halign = Gtk.Align.START
        self.content_label.props.valign = Gtk.Align.END
        self.content_label.props.margin_bottom = 9
        self.content_label.props.expand = True

        #------ source_icon / application icon ----#
        source_icon_cache = os.path.join(self.cache_filedir[:-6],"icon", self.source_app.replace(" ",".").lower() + ".png")
        
        if os.path.exists(source_icon_cache):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(source_icon_cache, 24 * self.scale, 24 * self.scale, True)
            source_icon = Gtk.Image().new_from_pixbuf(pixbuf)
            # if self.scale == 2:
            #     source_icon.set_pixel_size(48)
            #     print("scaled")
        else:
            source_icon = Gtk.Image().new_from_icon_name("image-missing", Gtk.IconSize.LARGE_TOOLBAR)
            source_icon.set_pixel_size(24 * self.scale)

        source_icon.props.halign = Gtk.Align.START
        source_icon.props.valign = Gtk.Align.END
        source_icon.props.margin = 4
        source_icon.props.has_tooltip = True
        source_icon.props.tooltip_text = self.source_app

        #------ timestamp ----#
        self.created_short = datetime.strptime(self.created, '%Y-%m-%d %H:%M:%S.%f')
        self.created_short = self.created_short.strftime('%a, %b %d %Y, %H:%M:%S')
        self.created = datetime.strptime(self.created, '%Y-%m-%d %H:%M:%S.%f')
        self.timestamp = self.generate_friendly_timestamp(self.created)
        self.timestamp = Gtk.Label(self.timestamp)
        self.timestamp.props.name = "clip-timestamp"
        self.timestamp.props.halign = self.timestamp.props.valign = Gtk.Align.END
        self.timestamp.props.margin = 4
        self.timestamp.props.margin_right = 6
        self.timestamp.props.margin_bottom = 10
        self.timestamp.props.has_tooltip = True
        self.timestamp.props.tooltip_text = self.created_short

        self.info_text = "id: {id}\ntype: {type}\nsource app: {source}".format(id=self.id, type=self.type, source=self.source_app)
        
        clip_info = Gtk.Grid()
        clip_info.props.name = "clip-info"
        clip_info.props.halign = Gtk.Align.FILL
        clip_info.props.valign = Gtk.Align.START
        clip_info.props.hexpand = True
        clip_info.props.can_focus = False
        clip_info.props.has_tooltip = True
        clip_info.props.tooltip_text = self.info_text
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

        return clip_info_revealer
        
    def generate_clip_action_notify(self):
        action_notify_box = Gtk.Grid()
        action_notify_box.props.name = "clip-action-notify"
        action_notify_box.props.column_spacing = 6
        action_notify_box.props.halign = action_notify_box.props.valign = Gtk.Align.CENTER

        clip_action_notify_revealer = Gtk.Revealer()
        clip_action_notify_revealer.props.name = "clip-action-notify-revealer"
        clip_action_notify_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        clip_action_notify_revealer.add(action_notify_box)
        return clip_action_notify_revealer

    def generate_clip_action(self):
        # protect_action = self.generate_action_button("com.github.hezral.clips-protect-symbolic", "Protect Content", "protect")
        info_action = self.generate_action_button("com.github.hezral.clips-info-symbolic", "Show Info", "info")
        view_action = self.generate_action_button("com.github.hezral.clips-view-symbolic", "View", "view")
        copy_action = self.generate_action_button("edit-copy-symbolic", "Copy to Clipboard", "copy")
        delete_action = self.generate_action_button("edit-delete-symbolic", "Delete", "delete")

        clip_action = Gtk.Grid()
        clip_action.props.name = "clip-action"
        clip_action.props.halign = Gtk.Align.FILL
        clip_action.props.valign = Gtk.Align.END
        clip_action.props.hexpand = True
        clip_action.props.can_focus = False
        clip_action.props.row_spacing = clip_action.props.column_spacing = 4
        
        if "color" in self.type or "spreadsheet" in self.type or "presentation" in self.type:
            # protect_action.props.sensitive = False
            view_action.props.sensitive = False
            # protect_action.get_style_context().add_class("clip-action-disabled")
            view_action.get_style_context().add_class("clip-action-disabled")
               
        # clip_action.attach(protect_action, 0, 0, 1, 1)
        clip_action.attach(info_action, 1, 0, 1, 1)
        clip_action.attach(view_action, 2, 0, 1, 1)
        clip_action.attach(copy_action, 3, 0, 1, 1)
        clip_action.attach(delete_action, 5, 0, 1, 1)

        clip_action_revealer = Gtk.Revealer()
        clip_action_revealer.props.name = "clip-action-revealer"    
        clip_action_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        clip_action_revealer.add(clip_action)
        clip_action_revealer.props.can_focus = True
        
        # handle mouse focus in/out on the clip action bar
        clip_action_revealer.connect("focus-out-event", self.on_clip_focused, "out")
        clip_action_revealer.connect("focus-in-event", self.on_clip_focused, "in")

        return clip_action_revealer

    def on_clip_focused(self, clip_action_revealer, eventfocus, type):
        flowboxchild = self.get_parent()
        main_window = self.get_toplevel()
        app = main_window.props.application
        utils = app.utils
        clip_container_overlay = utils.GetWidgetByName(widget=flowboxchild, child_name="clip-container-overlay", level=0)
        # utils.GetWidgetByName not working for some widget class like Gtk.Overlay
        clip_action_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-action-revealer"][0]
        clip_select_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-select-revealer"][0]
        if type == "out":
            if not flowboxchild.is_selected():
                clip_action_revealer.set_reveal_child(False)
                # clip_select_revealer.set_reveal_child(False)
        else:
            clip_action_revealer.set_reveal_child(True)
            # clip_select_revealer.set_reveal_child(True)

    def on_cursor_entering_clip(self, widget, eventcrossing):
        # add css class for hover event
        self.get_parent().get_style_context().add_class("hover")
        
        flowboxchild = self.get_parent()
        main_window = self.get_toplevel()
        app = main_window.props.application
        utils = app.utils
        clip_container_overlay = utils.GetWidgetByName(widget=flowboxchild, child_name="clip-container-overlay", level=0)
        # utils.GetWidgetByName not working for some widget class like Gtk.Overlay
        clip_action_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-action-revealer"][0]
        clip_select_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-select-revealer"][0]

        clip_action_revealer.set_reveal_child(True)
        clip_select_revealer.set_reveal_child(True)

        # add zoom effect on hovering an image container
        # content = utils.GetWidgetByName(widget=flowboxchild, child_name="image-container", level=0)
        # if content is not None:
        #     content.hover()

    def on_cursor_leaving_clip(self, widget, eventcrossing):
        # remove css class for hover event
        self.get_parent().get_style_context().remove_class("hover")

        flowboxchild = self.get_parent()
        main_window = self.get_toplevel()
        app = main_window.props.application
        utils = app.utils
        clip_container_overlay = utils.GetWidgetByName(widget=flowboxchild, child_name="clip-container-overlay", level=0)
        # utils.GetWidgetByName not working for some widget class like Gtk.Overlay
        clip_action_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-action-revealer"][0]
        clip_action_notify = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-action-notify-revealer"][0]
        clip_info_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-info-revealer"][0]
        clip_select_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-select-revealer"][0]

        if flowboxchild.is_selected():
            clip_action_revealer.set_reveal_child(True)
            clip_action_revealer.grab_focus()
        else: 
            clip_action_revealer.set_reveal_child(False)
        
        if clip_action_notify.get_child_revealed():
            clip_action_notify.set_reveal_child(False)

        if clip_info_revealer.get_child_revealed():
            clip_info_revealer.set_reveal_child(False)

        if clip_select_revealer.get_child_revealed():
            clip_select_revealer.set_reveal_child(False)

    def on_clip_action(self, button=None, action=None):
        main_window = self.get_toplevel()
        app = main_window.props.application
        utils = app.utils
        flowboxchild = self.get_parent()
        flowbox = flowboxchild.get_parent()
        clip_container_overlay = utils.GetWidgetByName(widget=flowboxchild, child_name="clip-container-overlay", level=0)
        # utils.GetWidgetByName not working for some widget class like Gtk.Overlay
        clip_action_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-action-revealer"][0]
        clip_action_notify = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-action-notify-revealer"][0]
        clip_info_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-info-revealer"][0]
        
        flowboxchild.do_activate(flowboxchild)        
        flowbox.select_child(flowboxchild)

        action_notify_box = clip_action_notify.get_children()[0]
        # remove previous widgets
        for child in action_notify_box.get_children():
            child.destroy()
 
        if action == "protect":
            clip_action_notify.set_reveal_child(True)

        elif action == "info":
            clip_info_revealer.set_reveal_child(True)

        elif action == "view":
            if "url" in self.type:
                with open(self.cache_file) as file:
                    utils.ViewFile(file.readlines()[0].replace("\n",""))
            else:
                utils.ViewFile(self.cache_file)

        elif action == "copy":
            icon = Gtk.Image().new_from_icon_name("process-completed", Gtk.IconSize.SMALL_TOOLBAR)
            label = Gtk.Label("Copied to clipboard")
            action_notify_box.attach(icon, 0, 0, 1, 1)
            action_notify_box.attach(label, 1, 0, 1, 1)
            action_notify_box.show_all()

            clip_action_notify.set_reveal_child(True)
            app.clipboard_manager.copy_to_clipboard(self.target, self.cache_file, self.type)
            app.cache_manager.update_cache_on_recopy(self.cache_file)

        elif action == "force_delete":
            flowboxchild.destroy()
            app.cache_manager.delete_record(self.id, self.cache_file, self.type)
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
            label = Gtk.Label(label="Delete this clip?\n\n{details}\n".format(details=self.info_text))
            box = dialog.get_content_area()
            box.props.margin = 10
            box.add(label)
            dialog.show_all()
            btn_cancel.grab_focus()
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                flowboxchild.destroy()
                app.cache_manager.delete_record(self.id, self.cache_file, self.type)
                main_window.update_total_clips_label("delete")
            dialog.destroy()


        else:
            print(action)
            pass

    def on_notify_action_hide(self, clip_action_notify, event):
        clip_action_notify.set_reveal_child(False)
        clip_action_notify.props.can_focus = False

    def on_revealer_focus_out(self, revealer, event):
        revealer.set_reveal_child(False)

    def generate_friendly_timestamp(self, time=False):
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.props.name = "default-container"
        self.props.halign = self.props.valign = Gtk.Align.FILL
        self.props.expand = True
        self.get_style_context().add_class("clip-containers")

# ----------------------------------------------------------------------------------------------------

class FallbackContainer(DefaultContainer):
    def __init__(self, filepath, type, utils, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # print(os.path.splitext(filepath)[0]+'-thumb.png')

        self.content = Gtk.Label(type)
        self.content.props.wrap_mode = Pango.WrapMode.CHAR
        self.content.props.max_width_chars = 23
        self.content.props.wrap = True
        self.content.props.selectable = False
        self.content.props.expand = True
        self.content.props.ellipsize = Pango.EllipsizeMode.END
        
        self.props.margin = 10
        self.props.margin_left = self.props.margin_right = 10
        self.props.name = "default-container"
        self.attach(self.content, 0, 0, 1, 1)

        self.label = str(len(type)) + " chars"
        # self.name = "content"

# ----------------------------------------------------------------------------------------------------

class ImageContainer(DefaultContainer):
    def __init__(self, filepath, type, utils, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pixbuf_original = GdkPixbuf.Pixbuf.new_from_file(filepath)
        self.ratio_h_w = self.pixbuf_original.props.height / self.pixbuf_original.props.width
        self.ratio_w_h = self.pixbuf_original.props.width / self.pixbuf_original.props.height
    
        drawing_area = Gtk.DrawingArea()
        drawing_area.props.expand = True
        drawing_area.connect("draw", self.draw)
        drawing_area.props.can_focus = False
 
        self.props.name = "image-container"
        self.attach(drawing_area, 0, 0, 1, 1)

        if self.pixbuf_original.get_has_alpha():
            self.get_style_context().add_class("checkerboard")
        
        self.label = "{width} x {height} px".format(width=str(self.pixbuf_original.props.width), height=str(self.pixbuf_original.props.height))

    def hover(self, *args):
        '''
        Function to implement cool hover > zoom image effect
        '''
        print(locals())

    def draw(self, drawing_area, cairo_context, hover_scale=1):
        '''
        Forked and ported from https://github.com/elementary/greeter/blob/master/src/Widgets/BackgroundImage.vala
        '''
        from math import pi

        scale = self.get_scale_factor()
        width = self.get_allocated_width() * scale * hover_scale
        height = self.get_allocated_height() * scale * hover_scale
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

class ColorContainer(DefaultContainer):
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
        # font_css = ".color-content {letter-spacing: 1px; font-weight: bold; font-size: 120%; opacity: 0.8;}"
        css = color_content_css
        provider = Gtk.CssProvider()
        provider.load_from_data(bytes(css.encode()))

        self.content = Gtk.Label(self.content)
        self.content.props.expand = True
        self.content.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.content.props.name = "color-container-content"

        # add checkerboard background for colors with alpha less than 1
        if str(a) != "1":
            self.get_style_context().add_class("checkerboard")

        self.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.get_style_context().add_class("color-container-bg")

        self.props.name = "color-container"
        self.attach(self.content, 0, 0, 1, 1)

        self.label = type.split("/")[1].upper()

# ----------------------------------------------------------------------------------------------------

class PlainTextContainer(DefaultContainer):
    def __init__(self, filepath, type, utils, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open(filepath) as file:
            firstNlines = file.readlines()[0:10] #put here the interval you want
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

        with open(filepath) as file:
            for i, l in enumerate(file):
                pass

        if not i+1 < 10:
            lines = Gtk.Label(str(i+1-10) + " lines more...")
            lines.props.halign = Gtk.Align.END
            self.attach(lines, 0, 1, 1, 1)

        self.label = str(len(self.content.props.label)) + " chars"

# ----------------------------------------------------------------------------------------------------

class HtmlContainer(DefaultContainer):
    def __init__(self, filepath, type, utils, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.content = open(filepath, "r")
        self.content = self.content.read()

        webview = WebKit2.WebView()
        webview.props.zoom_level = 0.85
        webview.load_html(self.content)
        webview.props.expand = True
        # webview.props.sensitive = False

        css_bg_color = utils.GetCssBackgroundColor(self.content)

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

# ----------------------------------------------------------------------------------------------------

class FilesContainer(DefaultContainer):
    def __init__(self, filepath, type, utils, *args, **kwargs):
        super().__init__(*args, **kwargs)

        scale = self.get_scale_factor()
        self.icon_size = 48 * scale
        self.icon_theme = Gtk.IconTheme.get_default()
        icon = None

        self.flowbox = Gtk.FlowBox()
        self.flowbox.props.expand = True
        self.flowbox.props.homogeneous = True
        self.flowbox.props.row_spacing = 4
        self.flowbox.props.column_spacing = 2
        self.flowbox.props.max_children_per_line = 4
        self.flowbox.props.min_children_per_line = 2
        self.flowbox.props.valign = Gtk.Align.CENTER
        self.flowbox.props.halign = Gtk.Align.CENTER

        with open(filepath) as file:
            file_content = file.readlines()

        with open(filepath) as file:
            i = 0
            for line_number, line_content in enumerate(file):
                line_content = line_content.replace("copy","").replace("file://","").strip()
                if os.path.isdir(line_content):  
                    mime_type = "inode/directory"
                elif os.path.isfile(line_content):  
                    mime_type, val = Gio.content_type_guess(line_content, data=None)
                elif not os.path.exists(line_content):
                    pass
                else:
                    print(line_content, ": special file (socket, FIFO, device file)" )
                    pass
                                
                icons = Gio.content_type_get_icon(mime_type)
                
                for icon_name in icons.to_string().split():
                    if icon_name != "." and icon_name != "GThemedIcon":
                        try:
                            if i == 7:
                                more_label = Gtk.Label("+" + str(file_count - 7))
                                more_label.props.name = "files-container-more-label"
                                self.flowbox.add(more_label)
                            elif i > 7 :
                                pass
                            else:
                                icon_pixbuf = self.icon_theme.load_icon(icon_name, self.icon_size, 0)
                                icon = Gtk.Image().new_from_pixbuf(icon_pixbuf)
                                # icon.props.has_tooltip = True
                                # icon.props.tooltip_text = line_content
                                self.flowbox.add(icon)
                            i += 1
                            break
                        except:
                            pass # file not exist for this entry

                        
            # file_count = line_number + 1
            if len(file_content) < 4:
                self.flowbox.props.max_children_per_line = len(file_content)
        
        # disable focus on flowboxchild items
        for child in self.flowbox.get_children():
            child.props.can_focus = False

        self.props.name = "files-container"
        self.attach(self.flowbox, 0, 0, 1, 1)

        self.label = str(len(file_content)) + " files"

# ----------------------------------------------------------------------------------------------------

class SpreadsheetContainer(ImageContainer):
    def __init__(self, filepath, type, utils, *args, **kwargs):
        thumbnail = os.path.splitext(filepath)[0]+'-thumb.png'
        super().__init__(thumbnail, type, utils)

        self.props.name = "spreadsheet-container"

        self.label = "Spreadsheet"

# ----------------------------------------------------------------------------------------------------

class PresentationContainer(ImageContainer):
    def __init__(self, filepath, type, utils, *args, **kwargs):
        thumbnail = os.path.splitext(filepath)[0]+'-thumb.png'
        super().__init__(thumbnail, type, utils)

        self.props.name = "presentation-container"

        self.label = "Presentation"

# ----------------------------------------------------------------------------------------------------

class WordContainer(DefaultContainer):
    def __init__(self, filepath, type, utils, *args, **kwargs):
        super().__init__(*args, **kwargs)

        scale = self.get_scale_factor()
        self.icon_size = 64 * scale
        self.icon_theme = Gtk.IconTheme.get_default()
        icon = None

        if os.path.isdir(filepath):  
            mime_type = "inode/directory"
        elif os.path.isfile(filepath):  
            mime_type, val = Gio.content_type_guess(filepath, data=None)
        elif not os.path.exists(filepath):
            pass
        else:
            print(filepath, ": special file (socket, FIFO, device file)" )
            pass
                        
        icons = Gio.content_type_get_icon(mime_type)
        
        for icon_name in icons.to_string().split():
            if icon_name != "." and icon_name != "GThemedIcon":
                try:
                    icon_pixbuf = self.icon_theme.load_icon(icon_name, self.icon_size, 0)
                    icon = Gtk.Image().new_from_pixbuf(icon_pixbuf)
                    self.attach(icon, 0, 0, 1, 1)
                    break
                except:
                    pass # file not exist for this entry

        label = Gtk.Label("Preview Unavailable")
        label.props.margin_top = 10
        self.attach(label, 0, 1, 1, 1)

        self.props.name = "word-container"
        self.props.halign = self.props.valign = Gtk.Align.CENTER

        self.label = "Word Document"

# ----------------------------------------------------------------------------------------------------

class UrlContainer(DefaultContainer):
    def __init__(self, filepath, type, utils, cache_filedir, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open(filepath) as file:
            self.content  = file.readlines()

        domain = utils.GetDomain(self.content[0].replace("\n",""))
        
        icon_size = 48 * self.get_scale_factor()
        favicon_file = os.path.join(cache_filedir[:-6],"icon", domain + ".ico")
        
        try:
            favicon = Gtk.Image()
            favicon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(favicon_file, icon_size, icon_size)
            favicon.props.pixbuf = favicon_pixbuf
        except:
            favicon = Gtk.Image().new_from_icon_name("applications-internet", Gtk.IconSize.LARGE_TOOLBAR)
            favicon.set_pixel_size(icon_size)
            
        favicon.props.margin_bottom = 10

        title = Gtk.Label(self.content[1])
        title.props.name = "url-container-title"
        title.props.wrap_mode = Pango.WrapMode.WORD
        title.props.max_width_chars = 20
        title.props.wrap = True
        title.props.justify = Gtk.Justification.CENTER
        title.props.lines = 3
        title.props.ellipsize = Pango.EllipsizeMode.END


        domain = Gtk.Label(self.content[0].replace("\n","").split("/")[2])

        self.props.margin = 10
        self.props.name = "url-container"

        self.attach(favicon, 0, 0, 1, 1)
        self.attach(title, 0, 1, 1, 1)
        self.attach(domain, 0, 2, 1, 1)

        self.props.halign = self.props.valign = Gtk.Align.CENTER
        self.props.name = "url-container"

        self.label = "Internet URL"

# ----------------------------------------------------------------------------------------------------
