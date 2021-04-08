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
from utils import to_rgb
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, WebKit2, GdkPixbuf, Pango, Gdk, Gio

import os
from datetime import datetime
import time

class ClipsView(Gtk.Grid):

    current_selected_flowboxchild_index = None

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app

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
        self.flowbox.connect("child-activated", self.on_child_activated)

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

    def flowbox_filter_func(self, search_entry):
        def filter_func(flowboxchild, search_text):
            clips_container = flowboxchild.get_children()[0]

            contents_single_keyword = [str(clips_container.id), clips_container.type.lower(), clips_container.target.lower(), clips_container.source_app.lower(), clips_container.created_short.lower()]
            contents_multi_keyword = ' '.join(contents_single_keyword)

            # check if multi keyword search
            if "," in search_text:
                # check if grouped keyword 
                if '"' in search_text:
                    search_text = search_text.replace('"',"")

                # split into multi keyword list
                search_texts = search_text.split(",")

                # remove any begin/end whitespace
                search_texts = [text.lstrip(' ') for text in search_texts]
                search_texts = [text.rstrip(' ') for text in search_texts]

                # print("multi-keyword-match", search_texts, contents_multi_keyword)
                if all(i in contents_multi_keyword for i in search_texts):
                    return True
                else:
                    return False
            else:
                # print("single-keyword-match", search_text)
                if '"' in search_text:
                    search_text = search_text.replace('"',"")

                if any(search_text in keyword for keyword in contents_single_keyword):
                    return True
                else:
                    return False

        search_text = search_entry.get_text()
        self.flowbox.set_filter_func(filter_func, search_text)

    def sort_flowbox(self, child1, child2):
        date1 = child1.get_children()[0].created
        date2 = child2.get_children()[0].created
        return date1 < date2

    def new_clip(self, clip, app_startup=False):
        app = self.get_toplevel().props.application
        main_window = self.get_toplevel()
        id = clip[0]
        cache_file = os.path.join(app.cache_manager.cache_filedir, clip[6])
        new_flowboxchild = [child for child in self.flowbox.get_children() if child.get_children()[0].id == id]

        # add the new clip if cache_file exists
        if os.path.exists(cache_file) and len(new_flowboxchild) == 0:
            self.flowbox.add(ClipsContainer(self.app, clip, app.cache_manager.cache_filedir, app.utils))
            
            if app_startup is False:
                main_window.update_total_clips_label("add")

            self.flowbox.show_all()

    def on_edge_reached(self, scrolledwindow, position):
        if position.value_name == "GTK_POS_BOTTOM":
            print(datetime.now(), "loading next items")

    def on_child_activated(self, flowbox, flowboxchild):
        # print("activate: current_selected_flowboxchild_index", self.current_selected_flowboxchild_index)
        
        if self.current_selected_flowboxchild_index is not None:
            # print("activate: current_selected_flowboxchild_index is None")
            last_selected_flowboxchild = flowbox.get_child_at_index(self.current_selected_flowboxchild_index)
            last_selected_flowboxchild.get_children()[0].clip_overlay_revealer.set_reveal_child(False)
            last_selected_flowboxchild.get_children()[0].clip_action_notify_revealer.set_reveal_child(False)
        
        self.current_selected_flowboxchild_index = flowboxchild.get_index()
        # self.current_selected_flowboxchild_index = 0
        # print("activate: current_selected_flowboxchild_index", self.current_selected_flowboxchild_index)
        # if flowboxchild.is_selected():
        #     flowboxchild.get_children()[0].clip_overlay_revealer.set_reveal_child(False)
        # else:
        flowboxchild.get_children()[0].clip_overlay_revealer.set_reveal_child(True)
        flowboxchild.grab_focus()
        

# ----------------------------------------------------------------------------------------------------

class ClipsContainer(Gtk.EventBox):
    def __init__(self, app, clip, cache_filedir, utils, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.props.name = "clip-container"

        self.app = app
        # get widget scale factor for redraw event
        self.scale = self.get_scale_factor()

        self.cache_filedir = cache_filedir
        self.id = clip[0]
        self.target = clip[1]
        self.created = datetime.strptime(clip[2], '%Y-%m-%d %H:%M:%S.%f')
        self.created_short = datetime.strptime(clip[2], '%Y-%m-%d %H:%M:%S.%f')
        self.created_short = self.created_short.strftime('%a, %b %d %Y, %H:%M:%S')
        self.fuzzytimestamp = self.app.utils.get_fuzzy_timestamp(self.created)
        self.source = clip[3]
        self.source_app = clip[4]
        self.source_icon = clip[5]
        self.cache_file = clip[6]
        self.type = clip[7]
        self.protected = clip[8]
        self.info_text = "id: {id}\nformat: {format}\ntype: {type}".format(id=self.id, format=self.target, type=self.type)

        # initialize cache file with full path        
        self.cache_file = os.path.join(self.cache_filedir, self.cache_file)

        # initialize empty variable
        self.content = None

        #------ container types, refer to clips_supported.py ----#
        if "office/spreadsheet" in self.type:
            self.content = SpreadsheetContainer(self.cache_file, self.type, app)
        elif "office/presentation" in self.type:
            self.content = PresentationContainer(self.cache_file, self.type, app)
        elif "office/word" in self.type:
            self.content = WordContainer(self.cache_file, self.type, app)
        elif "files" in self.type:
            self.content = FilesContainer(self.cache_file, self.type, app)
        elif "image" in self.type:
            self.content = ImageContainer(self.cache_file, self.type, app)
        elif "html" in self.type:
            self.content = HtmlContainer(self.cache_file, self.type, app)
        elif "richtext" in self.type:
            self.content = FilesContainer(self.cache_file, self.type, app)
        elif "plaintext" in self.type:
            self.content = PlainTextContainer(self.cache_file, self.type, app)
        elif "color" in self.type:
            self.content = ColorContainer(self.cache_file, self.type, app)
        elif "url" in self.type:
            self.content = UrlContainer(self.cache_file, self.type, app, self.cache_filedir)
        elif "mail" in self.type:
            self.content = EmailContainer(self.cache_file, self.type, app, self.cache_filedir)
        else:
            print("clips_view.py:", "FallbackContainer:", self.cache_file, self.type)
            self.content = FallbackContainer(self.cache_file, self.type, app)

        self.extended_info = self.content.label

        # print(self.cache_file, self.type)
        # self.clip_info = self.generate_clip_info(utils)
        self.clip_action_notify_revealer = self.generate_clip_action_notify()
        self.clip_overlay_revealer = self.generate_clip_overlay()
        self.clip_select_revealer = self.generate_clip_select()

        #------ construct ----#
        self.container_overlay = Gtk.Overlay()
        self.container_overlay.props.name = "clip-container-overlay"
        self.container_overlay.add(self.content)
        self.container_overlay.add_overlay(self.clip_action_notify_revealer)
        self.container_overlay.set_overlay_pass_through(self.clip_action_notify_revealer, True)
        self.container_overlay.add_overlay(self.clip_overlay_revealer)
        self.container_overlay.set_overlay_pass_through(self.clip_overlay_revealer, True)
        # self.container_overlay.add_overlay(self.clip_info_revealer)
        # self.container_overlay.set_overlay_pass_through(self.clip_info_revealer, True)
        self.container_overlay.add_overlay(self.clip_select_revealer)

        self.container_grid = Gtk.Grid()
        self.container_grid.props.name = "clip-container-grid"
        self.container_grid.attach(self.container_overlay, 0, 0, 1, 1)

        self.add(self.container_grid)

        self.set_size_request(200, 160)
        
        self.props.expand = True

        # handle mouse enter/leave events on the flowboxchild
        self.connect("enter-notify-event", self.on_cursor_entering_clip)
        self.connect("leave-notify-event", self.on_cursor_leaving_clip)
        self.connect("button-press-event", self.on_double_clicked_clip)

    def on_focus_event(self, *args):
        print(locals())

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
    
    def generate_clip_info(self, utils):
        if self.content.label is None:
            self.content_label = Gtk.Label("Clip")
        else:
            self.content_label = Gtk.Label(self.content.label)
        self.content_label.props.name = "clip-content-label"
        self.content_label.props.halign = Gtk.Align.START
        self.content_label.props.valign = Gtk.Align.END
        self.content_label.props.margin_bottom = 9
        self.content_label.props.expand = True

        # #------ source_icon / application icon ----#
        # try:
        #     source_icon = Gtk.Image().new_from_icon_name(self.source_icon, Gtk.IconSize.LARGE_TOOLBAR)
        #     source_icon.set_pixel_size(24 * self.scale)
        # except:
        #     source_icon_cache = os.path.join(self.cache_filedir[:-6],"icon", self.source_app.replace(" ",".").lower() + ".png")
        #     if os.path.exists(source_icon_cache):
        #         pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(source_icon_cache, 24 * self.scale, 24 * self.scale, True)
        #         source_icon = Gtk.Image().new_from_pixbuf(pixbuf)
        #     else:
        #         source_icon = Gtk.Image().new_from_icon_name("image-missing", Gtk.IconSize.LARGE_TOOLBAR)
        #         source_icon.set_pixel_size(24 * self.scale)

        # source_icon.props.halign = Gtk.Align.START
        # source_icon.props.valign = Gtk.Align.END
        # source_icon.props.margin = 4
        # source_icon.props.has_tooltip = True
        # source_icon.props.tooltip_text = self.source_app

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

        # print("clips_view.py:", type(self.created_short), self.created_short, type(self.created), self.created)

        self.info_text = "id: {id}\nformat: {format}\ntype: {type}".format(id=self.id, format=self.target, type=self.type)
        
        clip_info = Gtk.Grid()
        clip_info.props.name = "clip-info"
        clip_info.props.halign = Gtk.Align.FILL
        clip_info.props.valign = Gtk.Align.START
        clip_info.props.hexpand = True
        clip_info.props.can_focus = False
        # clip_info.props.has_tooltip = True
        # clip_info.props.tooltip_text = self.info_text
        clip_info.set_size_request(-1, 32)
        clip_info.attach(source_icon, 0, 0, 1, 1)
        clip_info.attach(self.content_label, 1, 0, 1, 1)
        clip_info.attach(self.timestamp, 2, 0, 1, 1)

        # clip_info_revealer = Gtk.Revealer()
        # clip_info_revealer.props.name = "clip-info-revealer"
        # clip_info_revealer.props.halign = Gtk.Align.FILL
        # clip_info_revealer.props.valign = Gtk.Align.START
        # clip_info_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        # clip_info_revealer.add(clip_info)

        return clip_info
        
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

    def generate_clip_overlay(self):
        # protect_action = self.generate_action_button("com.github.hezral.clips-protect-symbolic", "Protect Content", "protect")
        reveal_action = self.generate_action_button("document-open-symbolic", "Reveal files", "reveal")
        # info_action = self.generate_action_button("com.github.hezral.clips-info-symbolic", "Show Info", "info")
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

        icon = self.generate_source_icon_overlay()

        self.fuzzytimestamp_label = self.generate_fuzzytimestamp_label()

        # clip_action.attach(protect_action, 0, 0, 1, 1)
        clip_action.attach(reveal_action, 0, 0, 1, 1)
        # clip_action.attach(info_action, 1, 0, 1, 1)
        clip_action.attach(view_action, 2, 0, 1, 1)
        clip_action.attach(copy_action, 3, 0, 1, 1)
        clip_action.attach(delete_action, 5, 0, 1, 1)
        clip_action.attach(self.fuzzytimestamp_label, 6, 0, 1, 1)

        grid = Gtk.Grid()
        grid.props.expand = True
        grid.props.halign = grid.props.valign = Gtk.Align.FILL
        grid.attach(icon, 0, 0, 1, 1)
        # grid.attach(self.fuzzytimestamp_label, 1, 0, 1, 1)
        grid.attach(clip_action, 0, 1, 2, 1)

        clip_overlay_revealer = Gtk.Revealer()
        clip_overlay_revealer.props.name = "clip-action-revealer"    
        clip_overlay_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        clip_overlay_revealer.add(grid)
        clip_overlay_revealer.props.can_focus = False # this breaks keyboard navigation!, disable it
        
        return clip_overlay_revealer

    def generate_fuzzytimestamp_label(self):
        fuzzytimestamp_label = Gtk.Label(self.fuzzytimestamp)
        fuzzytimestamp_label.props.halign = Gtk.Align.END
        fuzzytimestamp_label.props.valign = Gtk.Align.START
        fuzzytimestamp_label.props.hexpand = True
        fuzzytimestamp_label.props.margin = 12
        fuzzytimestamp_label.props.margin_right = 8
        fuzzytimestamp_label.props.name = "clips-fuzzytimestamp"
        return fuzzytimestamp_label

    def generate_source_icon_overlay(self):
        app_name, app_icon = self.app.utils.get_appinfo(self.source_app)
        icon_size = 32 * self.scale
        if app_icon == "application-default-icon":
            source_icon_cache = os.path.join(self.cache_filedir[:-6],"icon", self.source_app.replace(" ",".").lower() + ".png")
            try:
                if os.path.exists(source_icon_cache):
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(source_icon_cache, icon_size, icon_size, True)
                    icon = Gtk.Image().new_from_pixbuf(pixbuf)
            except:
                icon = Gtk.Image().new_from_icon_name("application-default-icon", Gtk.IconSize.LARGE_TOOLBAR)
        else:
            icon = Gtk.Image().new_from_icon_name(app_icon, Gtk.IconSize.LARGE_TOOLBAR)
        
        icon.set_pixel_size(icon_size)
        icon.props.halign = Gtk.Align.START
        icon.props.valign = Gtk.Align.START
        icon.props.expand = True
        icon.props.margin = 6
        icon.props.name = "clip-source-app-icon-overlay"
        icon.props.has_tooltip = True
        icon.connect("query-tooltip", self.on_tooltip)

        return icon

    def on_double_clicked_clip(self, widget, eventbutton):
        if eventbutton.type.value_name == "GDK_2BUTTON_PRESS":
            self.on_clip_action(button=None, action="copy")        

    def on_cursor_entering_clip(self, widget, eventcrossing):
        # add css class for hover event
        self.get_parent().get_style_context().add_class("hover")
        
        flowboxchild = self.get_parent()
        main_window = self.get_toplevel()
        app = main_window.props.application
        utils = app.utils
        clip_container_overlay = utils.get_widget_by_name(widget=flowboxchild, child_name="clip-container-overlay", level=0)
        # utils.get_widget_by_name not working for some widget class like Gtk.Overlay
        clip_overlay_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-action-revealer"][0]
        clip_select_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-select-revealer"][0]

        clip_overlay_revealer.set_reveal_child(True)
        clip_select_revealer.set_reveal_child(True)

        # add zoom effect on hovering an image container
        # content = utils.get_widget_by_name(widget=flowboxchild, child_name="image-container", level=0)
        # if content is not None:
        #     content.hover()

    def on_cursor_leaving_clip(self, widget, eventcrossing):
        # remove css class for hover event
        self.get_parent().get_style_context().remove_class("hover")

        flowboxchild = self.get_parent()
        main_window = self.get_toplevel()
        app = main_window.props.application
        utils = app.utils
        clip_container_overlay = utils.get_widget_by_name(widget=flowboxchild, child_name="clip-container-overlay", level=0)
        # utils.get_widget_by_name not working for some widget class like Gtk.Overlay
        clip_overlay_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-action-revealer"][0]
        clip_action_notify_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-action-notify-revealer"][0]
        # clip_info_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-info-revealer"][0]
        # clip_select_revealer = [child for child in clip_container_overlay.get_children() if child.props.name == "clip-select-revealer"][0]

        if flowboxchild.is_selected():
            clip_overlay_revealer.set_reveal_child(True)
            clip_overlay_revealer.grab_focus()
        else: 
            clip_overlay_revealer.set_reveal_child(False)
        
        if clip_action_notify_revealer.get_child_revealed():
            clip_action_notify_revealer.set_reveal_child(False)

        # if clip_info_revealer.get_child_revealed():
        #     clip_info_revealer.set_reveal_child(False)

        # if clip_select_revealer.get_child_revealed():
        #     clip_select_revealer.set_reveal_child(False)

        flowboxchild_selected = main_window.clips_view.flowbox.get_selected_children()

        if len(flowboxchild_selected) != 0:
            if flowboxchild_selected[0].get_children()[0].clip_action_notify_revealer.get_child_revealed():
                flowboxchild_selected[0].get_children()[0].clip_action_notify_revealer.set_reveal_child(False)

    def on_clip_action(self, button=None, action=None):
        flowboxchild = self.get_parent()
        flowbox = flowboxchild.get_parent()
    
        flowbox.select_child(flowboxchild)

        action_notify_box = self.clip_action_notify_revealer.get_children()[0]

        # remove previous widgets
        for child in action_notify_box.get_children():
            child.destroy()
 
        if action == "protect":
            self.clip_action_notify_revealer.set_reveal_child(True)

        elif action == "reveal":
            self.app.utils.reveal_file_gio(self.cache_file)
            
        elif action == "info":
            self.clip_info_revealer.set_reveal_child(True)

        elif action == "view":
            if "url" in self.type:
                with open(self.cache_file) as file:
                    lines = file.readlines()
                self.app.utils.open_url_gtk(lines[0].replace('\n',''))
            if "files" in self.type:
                with open(self.cache_file) as file:
                    lines = file.readlines()
                    # .replace("copyfile://", ""))
                print(lines)
                self.app.utils.open_file_gio(self.cache_file)
            else:
                self.app.utils.open_file_gio(self.cache_file)

        elif action == "copy":
            icon = Gtk.Image().new_from_icon_name("process-completed", Gtk.IconSize.SMALL_TOOLBAR)
            label = Gtk.Label("Copied to clipboard")
            action_notify_box.attach(icon, 0, 0, 1, 1)
            action_notify_box.attach(label, 1, 0, 1, 1)
            action_notify_box.show_all()

            self.clip_action_notify_revealer.set_reveal_child(True)
            self.app.utils.copy_to_clipboard(self.target, self.cache_file, self.type)
            self.app.cache_manager.update_cache_on_recopy(self.cache_file)
            
        elif action == "force_delete":
            flowboxchild.destroy()
            self.app.cache_manager.delete_record(self.id, self.cache_file, self.type)
            self.app.main_window.update_total_clips_label("delete")

        elif action == "delete":
            dialog = Gtk.Dialog.new()
            dialog.props.title="Confirm delete action"
            dialog.props.transient_for = self.app.main_window
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
                self.app.cache_manager.delete_record(self.id, self.cache_file, self.type)
                self.app.main_window.update_total_clips_label("delete")
            dialog.destroy()

        else:
            print(action)
            pass

    def update_timestamp_on_clips(self, datetime):
        self.created = datetime
        self.created_short = datetime.strftime('%a, %b %d %Y, %H:%M:%S')
        self.fuzzytimestamp = self.app.utils.get_fuzzy_timestamp(datetime)
        self.fuzzytimestamp_label.props.label = self.fuzzytimestamp

    def on_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        app_name, app_icon = self.app.utils.get_appinfo(self.source_app)

        id = Gtk.Label(self.id)
        id.props.hexpand = True
        id.props.halign = Gtk.Align.START
        id_icon = Gtk.Image().new_from_icon_name("com.github.hezral.clips", Gtk.IconSize.LARGE_TOOLBAR)

        source_app = Gtk.Label(self.source_app)
        source_app.props.hexpand = True
        source_app.props.halign = Gtk.Align.START
        source_app_icon = Gtk.Image().new_from_icon_name("application-default-icon", Gtk.IconSize.LARGE_TOOLBAR)

        created = Gtk.Label(self.created_short)
        created.props.hexpand = True
        created.props.halign = Gtk.Align.START        
        created_icon = Gtk.Image().new_from_icon_name("preferences-system-time", Gtk.IconSize.LARGE_TOOLBAR)

        type = Gtk.Label(self.type)
        type.props.hexpand = True
        type.props.halign = Gtk.Align.START          
        type_icon = Gtk.Image().new_from_icon_name("mail-sent", Gtk.IconSize.LARGE_TOOLBAR)

        extended_info = Gtk.Label(self.extended_info)
        extended_info.props.hexpand = True
        extended_info.props.halign = Gtk.Align.START    
        extended_icon = Gtk.Image().new_from_icon_name("tag", Gtk.IconSize.LARGE_TOOLBAR)

        grid = Gtk.Grid()
        grid.props.margin = 6
        grid.props.row_spacing = 6
        grid.props.column_spacing = 6

        grid.attach(id_icon, 0, 0, 1, 1)
        grid.attach(id, 1, 0, 1, 1)
        grid.attach(source_app_icon, 0, 1, 1, 1)
        grid.attach(source_app, 1, 1, 1, 1)
        grid.attach(created_icon, 0, 2, 1, 1)
        grid.attach(created, 1, 2, 1, 1)
        grid.attach(type_icon, 0, 3, 1, 1)
        grid.attach(type, 1, 3, 1, 1)
        grid.attach(extended_icon, 0, 4, 1, 1)
        grid.attach(extended_info, 1, 4, 1, 1)
        grid.show_all()

        tooltip.set_custom(None)
        tooltip.set_custom(grid)
        
        return True

    def on_notify_action_hide(self, clip_action_notify, event):
        clip_action_notify.set_reveal_child(False)
        clip_action_notify.props.can_focus = False

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
    def __init__(self, filepath, type, app, *args, **kwargs):
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
        self.props.name = "default-container"
        self.attach(self.content, 0, 0, 1, 1)

        self.label = str(len(type)) + " chars"

# ----------------------------------------------------------------------------------------------------

class ImageContainer(DefaultContainer):
    def __init__(self, filepath, type, app, *args, **kwargs):
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
    def __init__(self, filepath, type, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.content = open(filepath, "r")
        self.content = self.content.read()

        rgb, a = app.utils.to_rgb(self.content)

        color_code = "rgba({red},{green},{blue},{alpha})".format(red=str(rgb[0]),green=str(rgb[1]),blue=str(rgb[2]),alpha=str(a))

        if app.utils.is_light_color(rgb) == "light":
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
    def __init__(self, filepath, type, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # print("parent", parent_container)

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
        # self.content.props.justify = Gtk.Justification.LEFT
        # self.content.props.halign = Gtk.Align.FILL

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
    def __init__(self, filepath, type, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.content = open(filepath, "r")
        self.content = self.content.read()

        webview = WebKit2.WebView()
        webview.props.zoom_level = 0.85
        webview.load_html(self.content)
        webview.props.expand = True
        webview.props.can_focus = False
        # webview.props.sensitive = False

        css_bg_color = app.utils.get_css_background_color(self.content)

        if css_bg_color is not None:
            rgb, a = app.utils.to_rgb(css_bg_color)
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
    def __init__(self, filepath, type, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        scale = self.get_scale_factor()
        self.icon_size = 48 * scale
        self.icon_theme = Gtk.IconTheme.get_default()
        icon = None

        self.flowbox = Gtk.FlowBox()
        self.flowbox.props.expand = True
        self.flowbox.props.homogeneous = True
        self.flowbox.props.row_spacing = 4
        self.flowbox.props.column_spacing = 4
        self.flowbox.props.max_children_per_line = 4
        self.flowbox.props.min_children_per_line = 2
        self.flowbox.props.valign = Gtk.Align.CENTER
        self.flowbox.props.halign = Gtk.Align.CENTER

        with open(filepath) as file:
            file_content = file.readlines()

        file_count = len(file_content)

        with open(filepath) as file:
            i = 0
            for line_number, line_content in enumerate(file):
                line_content = line_content.replace("copy","").replace("file://","").strip().replace("%20", " ")
                if os.path.exists(line_content):
                    if os.path.isdir(line_content):  
                        mime_type = "inode/directory"
                    elif os.path.isfile(line_content):  
                        mime_type, val = Gio.content_type_guess(line_content, data=None)
                    else:
                        print(line_content, ": special file (socket, FIFO, device file)" )
                        pass
                else:
                    mime_type = "application/octet-stream"
                                
                icons = Gio.content_type_get_icon(mime_type)
                
                for icon_name in icons.to_string().split():
                    if icon_name != "." and icon_name != "GThemedIcon":
                        try:
                            if i == 7:
                                more_label = Gtk.Label("+" + str(file_count - 7))
                                more_label.props.name = "files-container-more"
                                more_label.props.valign = Gtk.Align.END
                                more_label.props.margin_bottom = 4
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
    def __init__(self, filepath, type, app, *args, **kwargs):
        thumbnail = os.path.splitext(filepath)[0]+'-thumb.png'
        super().__init__(thumbnail, type, app)

        self.props.name = "spreadsheet-container"

        self.label = "Spreadsheet"

# ----------------------------------------------------------------------------------------------------

class PresentationContainer(ImageContainer):
    def __init__(self, filepath, type, app, *args, **kwargs):
        thumbnail = os.path.splitext(filepath)[0]+'-thumb.png'
        super().__init__(thumbnail, type, app)

        self.props.name = "presentation-container"

        self.label = "Presentation"

# ----------------------------------------------------------------------------------------------------

class WordContainer(DefaultContainer):
    def __init__(self, filepath, type, app, *args, **kwargs):
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

        label = Gtk.Label("Preview with View action")
        label.props.margin_top = 10
        self.attach(label, 0, 1, 1, 1)

        self.props.name = "word-container"
        self.props.halign = self.props.valign = Gtk.Align.CENTER

        self.label = "Word Document"

# ----------------------------------------------------------------------------------------------------

class UrlContainer(DefaultContainer):
    def __init__(self, filepath, type, app, cache_filedir, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open(filepath) as file:
            self.content  = file.readlines()

        domain = app.utils.get_domain(self.content[0].replace("\n",""))
        checksum = os.path.splitext(filepath)[0].split("/")[-1]
        
        icon_size = 48 * self.get_scale_factor()
        favicon_file = os.path.join(cache_filedir[:-6],"icon", domain + "-" + checksum + ".ico")
        
        try:
            favicon = Gtk.Image()
            favicon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(favicon_file, icon_size, icon_size)
            favicon.props.pixbuf = favicon_pixbuf
        except:
            favicon = Gtk.Image().new_from_icon_name("applications-internet", Gtk.IconSize.LARGE_TOOLBAR)
            favicon.set_pixel_size(icon_size)
            
        favicon.props.margin_bottom = 10

        self.title = self.content[1]

        title = Gtk.Label(self.title)
        title.props.name = "url-container-title"
        title.props.wrap_mode = Pango.WrapMode.WORD
        title.props.max_width_chars = 40
        title.props.wrap = True
        title.props.hexpand = True
        title.props.justify = Gtk.Justification.CENTER
        title.props.lines = 3
        title.props.ellipsize = Pango.EllipsizeMode.END
        
        domain = Gtk.Label(domain)

        self.props.margin = 10
        self.props.name = "url-container"

        self.attach(favicon, 0, 0, 1, 1)
        self.attach(title, 0, 1, 1, 1)
        self.attach(domain, 0, 2, 1, 1)

        self.props.valign = Gtk.Align.CENTER
        self.props.halign = Gtk.Align.FILL
        self.props.name = "url-container"

        self.label = "Internet URL"

# ----------------------------------------------------------------------------------------------------

class EmailContainer(DefaultContainer):
    def __init__(self, filepath, type, app, cache_filedir, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.props.name = "email-container"

        self.label = "Email"

        with open(filepath) as file:
            self.content  = file.readlines()

        domain = self.content[0].split("@")[-1]
        checksum = os.path.splitext(filepath)[0].split("/")[-1]
        
        icon_size = 48 * self.get_scale_factor()
        favicon_file = os.path.join(cache_filedir[:-6],"icon", domain + "-" + checksum + ".ico")
        
        try:
            favicon = Gtk.Image()
            favicon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(favicon_file, icon_size, icon_size)
            favicon.props.pixbuf = favicon_pixbuf
        except:
            favicon = Gtk.Image().new_from_icon_name("applications-internet", Gtk.IconSize.LARGE_TOOLBAR)
            favicon.set_pixel_size(icon_size)
            
        favicon.props.margin_bottom = 10

        self.title = self.content[0].split(":")[-1].replace("\n","")

        title = Gtk.Label(self.title)
        title.props.name = "mail-container-title"
        title.props.wrap_mode = Pango.WrapMode.WORD
        title.props.max_width_chars = 30
        title.props.wrap = True
        title.props.justify = Gtk.Justification.CENTER
        title.props.lines = 3
        title.props.ellipsize = Pango.EllipsizeMode.END
        title.props.valign = Gtk.Align.CENTER

        domain = Gtk.Label(domain)

        self.props.margin = 10
        self.props.name = "mail-container"

        self.attach(favicon, 0, 0, 1, 1)
        self.attach(title, 0, 1, 1, 1)
        self.attach(domain, 0, 2, 1, 1)

        self.props.valign = Gtk.Align.CENTER
        self.props.halign = Gtk.Align.FILL

# ----------------------------------------------------------------------------------------------------
