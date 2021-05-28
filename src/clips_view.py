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

from os.path import basename
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, WebKit2, GdkPixbuf, Pango, Gdk, Gio, GLib
import cairo
from . import custom_widgets

import os
from datetime import datetime
import time

global stop_threads

class ClipsView(Gtk.Grid):

    current_selected_flowboxchild_index = 0
    multi_select_mode = False
    filter_count = 0

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app

        self.flowbox = Gtk.FlowBox()
        self.flowbox.props.name = "flowbox"
        self.flowbox.props.homogeneous = False
        self.flowbox.props.row_spacing = 10
        self.flowbox.props.column_spacing = 10
        self.flowbox.props.max_children_per_line = 8
        self.flowbox.props.min_children_per_line = app.gio_settings.get_int("min-column-number")
        self.flowbox.props.valign = Gtk.Align.START
        self.flowbox.props.halign = Gtk.Align.FILL
        self.flowbox.set_sort_func(self.sort_flowbox)
        self.flowbox.connect("child-activated", self.on_child_activated)
        
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.props.expand = True
        scrolled_window.props.hscrollbar_policy = Gtk.PolicyType.NEVER
        scrolled_window.add(self.flowbox)
        # scrolled_window.connect("edge-reached", self.on_edge_reached)

        self.multi_delete_revealer = self.generate_multi_delete_revealer()

        self.clips_view_overlay = Gtk.Overlay()
        self.clips_view_overlay.add(scrolled_window)
        self.clips_view_overlay.add_overlay(self.multi_delete_revealer)
        self.clips_view_overlay.set_overlay_pass_through(self.multi_delete_revealer, True)

        self.props.name = "clips-view"
        self.props.expand = True
        self.attach(self.clips_view_overlay, 0, 0, 1, 1)

    def generate_multi_delete_revealer(self):
        self.select_all_button = Gtk.Button(label="Select All")
        self.select_all_button.props.halign = Gtk.Align.START
        self.select_all_button.props.hexpand = True
        self.select_all_button.props.name = "select-all-off"
        self.select_all_button.connect("clicked", self.on_select_all)

        self.delete_selected_button = Gtk.Button(label="Delete", image=Gtk.Image().new_from_icon_name("dialog-warning", Gtk.IconSize.SMALL_TOOLBAR))
        self.delete_selected_button.props.always_show_image = True
        self.delete_selected_button.get_style_context().add_class("destructive-action")
        label = [child for child in self.delete_selected_button.get_children()[0].get_child() if isinstance(child, Gtk.Label)][0]
        label.props.valign = Gtk.Align.CENTER
        self.delete_selected_button.connect("clicked", self.on_delete_selected)

        cancel_multi_delete_button = Gtk.Button(label="Cancel")
        cancel_multi_delete_button.connect("clicked", self.on_cancel_multi_delete)

        button_grid = Gtk.Grid()
        button_grid.props.halign = Gtk.Align.END
        button_grid.props.hexpand = True
        button_grid.props.margin = 6
        button_grid.props.row_spacing = button_grid.props.column_spacing = 6
        button_grid.attach(self.delete_selected_button, 0, 0, 1, 1)
        button_grid.attach(self.select_all_button, 1, 0, 1, 1)
        button_grid.attach(cancel_multi_delete_button, 2, 0, 1, 1)

        grid_multi_delete = Gtk.Grid()
        grid_multi_delete.props.name = "clips-multi-delete"
        grid_multi_delete.props.hexpand = True
        grid_multi_delete.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), 0, 0, 1, 1)
        grid_multi_delete.attach(button_grid, 0, 1, 1, 1)

        multi_delete_revealer = Gtk.Revealer()
        multi_delete_revealer.props.halign = Gtk.Align.FILL
        multi_delete_revealer.props.valign = Gtk.Align.END
        multi_delete_revealer.props.hexpand = True
        multi_delete_revealer.props.can_focus = False
        multi_delete_revealer.add(grid_multi_delete)
        return multi_delete_revealer

    def flowbox_filter_func(self, search_entry):
        def filter_func(flowboxchild, search_text):
            clips_container = flowboxchild.get_children()[0]

            if clips_container.type in ("plaintext", "html", "url/https", "url/http", "mail", "files"):
                with open(clips_container.cache_file) as file:
                    lines = file.readlines()
                contents = ''.join(lines)
                contents_single_keyword = [str(clips_container.id), clips_container.type.lower(), clips_container.target.lower(), clips_container.source_app.lower(), clips_container.created_short.lower(), clips_container.extended_info.lower(), contents.lower()]
                contents_multi_keyword = ' '.join(contents_single_keyword)
            else:
                contents_single_keyword = [str(clips_container.id), clips_container.type.lower(), clips_container.target.lower(), clips_container.source_app.lower(), clips_container.created_short.lower(), clips_container.extended_info.lower()]
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

    def new_clip(self, clip):
        app = self.get_toplevel().props.application
        main_window = self.get_toplevel()
        id = clip[0]
        cache_file = os.path.join(app.cache_manager.cache_filedir, clip[6])
        new_flowboxchild = [child for child in self.flowbox.get_children() if child.get_children()[0].id == id]

        # add the new clip if cache_file exists
        if os.path.exists(cache_file) and len(new_flowboxchild) == 0:
            self.flowbox.add(ClipsContainer(self.app, clip, app.cache_manager.cache_filedir, app.utils))
            
            # if app_startup is False:
            main_window.update_total_clips_label("add")

            self.flowbox.show_all()

    def on_edge_reached(self, scrolledwindow, position):
        if position.value_name == "GTK_POS_BOTTOM":
            print(datetime.now(), "loading next items")

    def on_child_activated(self, flowbox, flowboxchild):
        selected = len(flowbox.get_selected_children())

        if selected == 1:
            if self.current_selected_flowboxchild_index is not None:
                last_selected_flowboxchild = flowbox.get_child_at_index(self.current_selected_flowboxchild_index)
                if last_selected_flowboxchild is not None:
                    last_selected_flowboxchild.get_children()[0].clip_overlay_revealer.set_reveal_child(False)
                    last_selected_flowboxchild.get_children()[0].clip_action_notify_revealer.set_reveal_child(False)

                    if self.current_selected_flowboxchild_index != flowboxchild.get_index():
                        flowbox.unselect_child(last_selected_flowboxchild)

            self.current_selected_flowboxchild_index = flowboxchild.get_index()
            flowboxchild.get_children()[0].clip_overlay_revealer.set_reveal_child(True)
            flowboxchild.get_children()[0].clip_action_revealer.set_reveal_child(True)
            flowboxchild.get_children()[0].source_icon_revealer.set_reveal_child(True)
            flowboxchild.grab_focus()

    def on_child_multi_selected(self, flowbox, flowboxchild):
        for flowboxchild in self.flowbox.get_selected_children():
            clips_container = flowboxchild.get_children()[0]
            clips_container.clip_overlay_revealer.set_reveal_child(True)
            clips_container.clip_action_revealer.set_reveal_child(False)
            clips_container.source_icon_revealer.set_reveal_child(False)
            clips_container.select_button.get_style_context().add_class("clip-selected")

        self.delete_selected_button.props.label = "Delete ({count})".format(count=str(len(self.flowbox.get_selected_children()))) 

    def on_child_multi_unselected(self, clips_container):
        clips_container.clip_overlay_revealer.set_reveal_child(False)
        self.app.main_window.clips_view.flowbox.unselect_child(clips_container.get_parent())
        self.delete_selected_button.props.label = "Delete ({count})".format(count=str(len(self.flowbox.get_selected_children())))
        if len(self.flowbox.get_selected_children()) == 0:
            self.off_multi_select()

    def on_selected_children_changed(self, flowbox):
        selected = len(flowbox.get_selected_children())

        if selected == 0:
            pass
        if selected == 1:
            pass
        if selected > 1:
            self.multi_delete_revealer.set_reveal_child(True)
            flowbox.handler_block(flowbox.on_child_activated_handler_id)
            
            for child in flowbox.get_children():
                clips_container = child.get_children()[0]
                clips_container.handler_block(clips_container.on_cursor_entering_clip_handler_id)
                clips_container.handler_block(clips_container.on_cursor_leaving_clip_handler_id)
                clips_container.handler_block(clips_container.on_double_clicked_clip_handler_id)
                clips_container.clip_action_notify_revealer.set_reveal_child(False)
                clips_container.clip_overlay_revealer.set_reveal_child(False)

    def on_select_all(self, button):
        if button.props.name == "select-all-off":
            self.flowbox.select_all()
            for flowboxchild in self.flowbox.get_selected_children():
                self.on_child_multi_selected(self.flowbox, flowboxchild)
            self.select_all_button.props.name = "select-all-on"
            self.select_all_button.props.label = "Unselect All ({count})".format(count=str(len(self.flowbox.get_selected_children())))
        else:
            for flowboxchild in self.flowbox.get_selected_children():
                flowboxchild.get_children()[0].clip_overlay_revealer.set_reveal_child(False)
            self.flowbox.unselect_all()
            self.select_all_button.props.name = "select-all-off"
            self.select_all_button.props.label = "Select All"
            self.delete_selected_button.props.label = "Delete ({count})".format(count=str(len(self.flowbox.get_selected_children())))

    def on_delete_selected(self, button):
        selected = self.flowbox.get_selected_children()
        for flowboxchild in self.flowbox.get_selected_children():
            clips_container = flowboxchild.get_children()[0]
            clips_container.on_clip_action(action="multi-delete")
            flowboxchild.destroy()
        self.off_multi_select()

    def on_cancel_multi_delete(self, button):
        self.off_multi_select()
        self.flowbox.unselect_all()
        self.select_all_button.props.name = "select-all-off"
        self.select_all_button.props.label = "Select All"
        self.delete_selected_button.props.label = "Delete ({count})".format(count=str(len(self.flowbox.get_selected_children())))
        
    
    def on_multi_select(self):
        self.flowbox.connect("child-activated", self.on_child_multi_selected)
        self.multi_delete_revealer.set_reveal_child(True)
        self.flowbox.props.selection_mode = Gtk.SelectionMode.MULTIPLE
        self.flowbox.disconnect_by_func(self.on_child_activated)
        
        for flowboxchild in self.app.main_window.clips_view.flowbox.get_children():
            clips_container = flowboxchild.get_children()[0]
            clips_container.disconnect_by_func(clips_container.on_cursor_entering_clip)
            clips_container.disconnect_by_func(clips_container.on_cursor_leaving_clip)
            clips_container.disconnect_by_func(clips_container.on_double_clicked_clip)
        
        self.delete_selected_button.props.label = "Delete ({count})".format(count=str(len(self.flowbox.get_selected_children())))
        self.multi_select_mode = True

    def off_multi_select(self):
        self.flowbox.disconnect_by_func(self.on_child_multi_selected)
        self.multi_delete_revealer.set_reveal_child(False)
        self.flowbox.props.selection_mode = Gtk.SelectionMode.SINGLE
        self.flowbox.connect("child-activated", self.on_child_activated)
        
        for flowboxchild in self.app.main_window.clips_view.flowbox.get_children():
            clips_container = flowboxchild.get_children()[0]
            clips_container.connect("enter-notify-event", clips_container.on_cursor_entering_clip)
            clips_container.connect("leave-notify-event", clips_container.on_cursor_leaving_clip)
            clips_container.connect("button-press-event", clips_container.on_double_clicked_clip)
            clips_container.select_button.get_style_context().remove_class("clip-selected")
            clips_container.select_button.get_style_context().add_class("clip-select")
            clips_container.clip_overlay_revealer.set_reveal_child(False)

        self.delete_selected_button.props.label = "Delete ({count})".format(count=str(0)) 
        self.multi_select_mode = False
        if self.flowbox.get_child_at_index(self.current_selected_flowboxchild_index) is not None:
            self.flowbox.select_child(self.flowbox.get_child_at_index(self.current_selected_flowboxchild_index))

# ----------------------------------------------------------------------------------------------------

class ClipsContainer(Gtk.EventBox):

    def __init__(self, app, clip, cache_filedir, utils, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.props.name = "clip-container"

        self.app = app
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
        # self.info_text = "id: {id}\nformat: {format}\ntype: {type}".format(id=self.id, format=self.target, type=self.type)
        self.cache_file = os.path.join(self.cache_filedir, self.cache_file)
        self.content = None

        #------ container types, refer to clips_supported.py ----#
        if "office/spreadsheet" in self.type:
            self.content = SpreadsheetContainer(self.cache_file, self.type, app)
        elif "office/presentation" in self.type:
            self.content = PresentationContainer(self.cache_file, self.type, app)
        elif "office/word" in self.type:
            self.content = WordContainer(self.cache_file, self.type, app)
        elif "files" in self.type:
            is_files = True
            with open(self.cache_file) as file:
                file_content = file.readlines()
            file_count = len(file_content)
            if file_count == 1:
                file_content = file_content[0].replace("copy","").replace("file://","").strip().replace("%20", " ").replace("\n","")
                if os.path.exists(file_content):
                    mime_type, val = Gio.content_type_guess(file_content, data=None)
                    if "image" in mime_type and not "webp" in mime_type:
                        self.content = ImageContainer(file_content, mime_type, app)
                        is_files = False
            if is_files:
                self.content = FilesContainer(self.cache_file, self.type, app)
        elif "image" in self.type:
            self.content = ImageContainer(self.cache_file, self.type, app)
        elif "html" in self.type:
            self.content = HtmlContainer(self.cache_file, self.type, app)
        # elif "html" in self.type and self.protected == "yes":
        #     self.content = ProtectedContainer(self.cache_file, self.type, app)
        elif "richtext" in self.type:
            self.content = FilesContainer(self.cache_file, self.type, app)
        elif "plaintext" in self.type and self.protected == "no":
            self.content = PlainTextContainer(self.cache_file, self.type, app)
        elif "plaintext" in self.type and self.protected == "yes":
            self.content = ProtectedContainer(self.cache_file, self.type, app)
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

        self.clip_action_notify_revealer = self.generate_clip_action_notify()
        self.clip_overlay_revealer = self.generate_clip_overlay()

        #------ construct ----#
        self.container_overlay = Gtk.Overlay()
        self.container_overlay.props.name = "clip-container-overlay"
        self.container_overlay.add(self.content)
        self.container_overlay.add_overlay(self.clip_action_notify_revealer)
        self.container_overlay.set_overlay_pass_through(self.clip_action_notify_revealer, True)
        self.container_overlay.add_overlay(self.clip_overlay_revealer)
        self.container_overlay.set_overlay_pass_through(self.clip_overlay_revealer, True)

        self.container_grid = Gtk.Grid()
        self.container_grid.props.name = "clip-container-grid"
        self.container_grid.attach(self.container_overlay, 0, 0, 1, 1)

        self.add(self.container_grid)
        self.set_size_request(200, 160)
        self.props.expand = True

        # handle mouse enter/leave events on the flowboxchild
        self.on_cursor_entering_clip_handler_id = self.connect("enter-notify-event", self.on_cursor_entering_clip)
        self.on_cursor_leaving_clip_handler_id = self.connect("leave-notify-event", self.on_cursor_leaving_clip)
        self.on_double_clicked_clip_handler_id = self.connect("button-press-event", self.on_double_clicked_clip)

    def generate_clip_select_button(self):
        button = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral.clips-select", Gtk.IconSize.SMALL_TOOLBAR))
        button.set_size_request(30, 30)
        button.props.name = "clip-select"
        button.props.halign = Gtk.Align.END
        button.props.valign = Gtk.Align.START
        button.props.can_focus = False
        button.props.margin_right = 3
        button.connect("clicked", self.on_clip_select)
        button.get_style_context().add_class("clip-select")
        return button
           
    def generate_action_button(self, iconname, tooltiptext, actionname):
        icon = Gtk.Image().new_from_icon_name(iconname, Gtk.IconSize.SMALL_TOOLBAR)
        button = Gtk.Button(image=icon)
        button.props.name = "clip-action-button"
        button.props.hexpand = False
        button.props.has_tooltip = True
        button.props.tooltip_text = tooltiptext
        button.props.can_focus = False
        button.set_size_request(30, 30)
        button.connect("clicked", self.on_clip_action, actionname)
        return button
    
    def generate_clip_info(self):
        id = Gtk.Label("ID: " + str(self.id))
        id.props.hexpand = True
        id.props.halign = Gtk.Align.START
        id_icon = Gtk.Image().new_from_icon_name("com.github.hezral.clips", Gtk.IconSize.LARGE_TOOLBAR)

        cache_file = Gtk.Label("Cache: " + os.path.basename(self.cache_file))
        cache_file.props.hexpand = True
        cache_file.props.halign = Gtk.Align.START

        source_app = Gtk.Label("Source: " + self.source_app)
        source_app.props.hexpand = True
        source_app.props.halign = Gtk.Align.START
        source_app_icon = Gtk.Image().new_from_icon_name("application-default-icon", Gtk.IconSize.LARGE_TOOLBAR)

        created = Gtk.Label("Created: " + self.created_short)
        created.props.hexpand = True
        created.props.halign = Gtk.Align.START        
        created_icon = Gtk.Image().new_from_icon_name("preferences-system-time", Gtk.IconSize.LARGE_TOOLBAR)

        type = Gtk.Label()
        type.props.label = "Type (Format): {type} ({target})".format(type=self.type, target=self.target)
        type.props.hexpand = True
        type.props.halign = Gtk.Align.START
        if "office/spreadsheet" in self.type:
            type_icon = "x-office-spreadsheet"
        elif "office/presentation" in self.type:
            type_icon = "x-office-presentation"
        elif "office/word" in self.type:
            type_icon = "x-office-document"
        elif "files" in self.type:
            type_icon = "folder-documents"
        elif "image" in self.type:
            type_icon = "image-x-generic"
        elif "html" in self.type:
            type_icon = "text-html"
        elif "richtext" in self.type:
            type_icon = "x-office-document"
        elif "plaintext" in self.type:
            type_icon = "text-x-generic"
        elif "color" in self.type:
            type_icon = "preferences-color"
        elif "url" in self.type:
            type_icon = "applications-internet"
        elif "mail" in self.type:
            type_icon = "mail-sent"
        else:
            type_icon = "application-octet-stream"
        type_icon = Gtk.Image().new_from_icon_name(type_icon, Gtk.IconSize.LARGE_TOOLBAR)

        extended_info = Gtk.Label("Extended Info: " + self.extended_info)
        extended_info.props.hexpand = True
        extended_info.props.halign = Gtk.Align.START    
        extended_icon = Gtk.Image().new_from_icon_name("tag", Gtk.IconSize.LARGE_TOOLBAR)

        grid = Gtk.Grid()
        grid.props.margin = 6
        grid.props.row_spacing = 6
        grid.props.column_spacing = 6

        grid.attach(id_icon, 0, 0, 1, 1)
        grid.attach(id, 1, 0, 1, 1)
        grid.attach(cache_file, 1, 1, 1, 1)
        grid.attach(source_app_icon, 0, 2, 1, 1)
        grid.attach(source_app, 1, 2, 1, 1)
        grid.attach(created_icon, 0, 3, 1, 1)
        grid.attach(created, 1, 3, 1, 1)
        grid.attach(type_icon, 0, 4, 1, 1)
        grid.attach(type, 1, 4, 1, 1)
        grid.attach(extended_icon, 0, 5, 1, 1)
        grid.attach(extended_info, 1, 5, 1, 1)
        grid.show_all()

        return grid

    def generate_clip_action_notify(self):
        action_notify_box = Gtk.Grid()
        action_notify_box.props.name = "clip-action-notify"
        action_notify_box.props.column_spacing = 6
        action_notify_box.props.halign = action_notify_box.props.valign = Gtk.Align.CENTER

        clip_action_notify_revealer = Gtk.Revealer()
        clip_action_notify_revealer.props.name = "clip-action-notify-revealer"
        clip_action_notify_revealer.props.can_focus = False
        clip_action_notify_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        clip_action_notify_revealer.add(action_notify_box)
        return clip_action_notify_revealer

    def generate_clip_overlay(self):
        protect_action = self.generate_action_button("com.github.hezral.clips-unprotect-symbolic", "Unprotect", "protect")
        reveal_action = self.generate_action_button("document-open-symbolic", "Reveal Cache File", "reveal")
        view_action = self.generate_action_button("com.github.hezral.clips-view-symbolic", "View", "view")
        copy_action = self.generate_action_button("edit-copy-symbolic", "Copy to Clipboard", "copy")
        delete_action = self.generate_action_button("edit-delete-symbolic", "Delete", "delete")

        clip_action = Gtk.Grid()
        clip_action.props.name = "clip-action"
        clip_action.props.halign = Gtk.Align.FILL
        clip_action.props.valign = Gtk.Align.END
        clip_action.props.hexpand = True
        clip_action.props.can_focus = False
        clip_action.props.row_spacing = clip_action.props.column_spacing = 2

        self.clip_action_revealer = Gtk.Revealer()
        self.clip_action_revealer.props.name = "clip-action-revealer"    
        self.clip_action_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        self.clip_action_revealer.add(clip_action)
        self.clip_action_revealer.props.can_focus = False
        
        icon = self.generate_source_icon()
        self.source_icon_revealer = Gtk.Revealer()
        self.source_icon_revealer.add(icon)
        self.source_icon_revealer.props.can_focus = False

        self.select_button = self.generate_clip_select_button()
        self.fuzzytimestamp_label = self.generate_fuzzytimestamp_label()

        clip_action.attach(reveal_action, 0, 0, 1, 1)
        clip_action.attach(view_action, 1, 0, 1, 1)
        clip_action.attach(copy_action, 2, 0, 1, 1)
        clip_action.attach(delete_action, 3, 0, 1, 1)
        clip_action.attach(self.fuzzytimestamp_label, 5, 0, 1, 1)

        if "color" in self.type or "spreadsheet" in self.type or "presentation" in self.type:
            view_action.props.sensitive = False
            view_action.get_style_context().add_class("clip-action-disabled")

        if "yes" in self.protected:
            # protect_action.props.sensitive = False
            # protect_action.get_style_context().add_class("clip-action-disabled")
            clip_action.attach(protect_action, 4, 0, 1, 1)

        grid = Gtk.Grid()
        grid.props.expand = True
        grid.props.halign = grid.props.valign = Gtk.Align.FILL
        grid.attach(self.source_icon_revealer, 0, 0, 1, 1)
        grid.attach(self.select_button, 1, 0, 1, 1)
        grid.attach(self.clip_action_revealer, 0, 1, 2, 1)

        clip_overlay_revealer = Gtk.Revealer()
        clip_overlay_revealer.props.name = "clip-action-revealer"    
        clip_overlay_revealer.props.transition_type = Gtk.RevealerTransitionType.CROSSFADE
        clip_overlay_revealer.add(grid)
        clip_overlay_revealer.props.can_focus = False # this breaks keyboard navigation!, disable it
        
        return clip_overlay_revealer

    def generate_fuzzytimestamp_label(self):
        fuzzytimestamp_label = Gtk.Label(self.fuzzytimestamp)
        fuzzytimestamp_label.props.halign = Gtk.Align.END
        fuzzytimestamp_label.props.valign = Gtk.Align.CENTER
        fuzzytimestamp_label.props.hexpand = True
        fuzzytimestamp_label.props.margin_right = 8
        fuzzytimestamp_label.props.margin_left = 8
        fuzzytimestamp_label.props.name = "clips-fuzzytimestamp"
        return fuzzytimestamp_label

    def generate_source_icon(self):
        icon_size = 32 * self.scale
        
        try: 
            icon_pixbuf = self.app.icon_theme.load_icon(self.source_icon, icon_size, 0)
            pixbuf = icon_pixbuf.scale_simple(icon_size, icon_size, True)
            icon = Gtk.Image().new_from_pixbuf(pixbuf)
        except:
            app_name, app_icon = self.app.utils.get_appinfo(self.source_app)
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

    def on_clip_select(self, button):
        if self.app.main_window.clips_view.multi_select_mode:
            button.get_style_context().remove_class("clip-selected")
            button.get_style_context().add_class("clip-select")
            self.app.main_window.clips_view.on_child_multi_unselected(self)
        else:
            button.get_style_context().remove_class("clip-select")
            button.get_style_context().add_class("clip-selected")
            self.clip_action_revealer.set_reveal_child(False)
            self.source_icon_revealer.set_reveal_child(False)
            self.app.main_window.clips_view.on_multi_select()

    def on_double_clicked_clip(self, widget, eventbutton):
        if eventbutton.type.value_name == "GDK_2BUTTON_PRESS":
            # if self.app.main_window.clips_view.multi_select_mode:
            #     self.app.main_window.clips_view.flowbox.unselect_child(self.get_parent())
            # else:
            self.on_clip_action(button=None, action="copy")

    def on_cursor_entering_clip(self, widget, eventcrossing):
        self.get_parent().get_style_context().add_class("hover")
        
        self.clip_overlay_revealer.set_reveal_child(True)
        self.clip_action_revealer.set_reveal_child(True)
        self.source_icon_revealer.set_reveal_child(True)

        image_container = self.app.utils.get_widget_by_name(widget=self, child_name="image-container", level=0)
        if image_container is not None:
            if "gif" in image_container.type:
                # image_container.animation_func()
                image_container.stop_threads = False
                import threading
                image_container.play_gif_thread = threading.Thread(target=image_container.animation_func)
                image_container.play_gif_thread.start()
                
        # add zoom effect on hovering an image container
        # content = utils.get_widget_by_name(widget=flowboxchild, child_name="image-container", level=0)
        # if content is not None:
        #     content.hover()

    def on_cursor_leaving_clip(self, widget, eventcrossing):
        self.get_parent().get_style_context().remove_class("hover")
        flowboxchild = self.get_parent()

        if flowboxchild.is_selected():
            self.clip_overlay_revealer.set_reveal_child(True)
            self.clip_overlay_revealer.grab_focus()
        else: 
            self.clip_overlay_revealer.set_reveal_child(False)
        
        if self.clip_action_notify_revealer.get_child_revealed():
            self.clip_action_notify_revealer.set_reveal_child(False)

        flowboxchild_selected = self.app.main_window.clips_view.flowbox.get_selected_children()

        if len(flowboxchild_selected) != 0:
            if flowboxchild_selected[0].get_children()[0].clip_action_notify_revealer.get_child_revealed():
                flowboxchild_selected[0].get_children()[0].clip_action_notify_revealer.set_reveal_child(False)
        
        image_container = self.app.utils.get_widget_by_name(widget=self, child_name="image-container", level=0)
        if image_container is not None:
            if "gif" in image_container.type:
                if image_container.play_gif_thread is not None:
                    image_container.stop_threads = True
                    image_container.play_gif_thread.join()
                    image_container.play_gif_thread = None

    def on_clip_action(self, button=None, action=None, validated=False, data=None):
        flowboxchild = self.get_parent()
        flowbox = self.app.main_window.clips_view.flowbox
        flowbox.select_child(flowboxchild)

        action_notify_box = self.clip_action_notify_revealer.get_children()[0]

        # remove previous widgets
        for child in action_notify_box.get_children():
            child.destroy()
 
        if action == "protect":
            if "yes" in self.protected:
                protected_container = self.app.utils.get_widget_by_name(self, "protected-container", 0, doPrint=False)
                content = protected_container.content
                title = "Reveal Content"
                callback = self.on_button_clicked
                if validated:
                    decrypt, decrypted_data = self.app.utils.do_encryption("decrypt", data, self.cache_file)
                    if decrypt:
                        self.on_revealcontent_timeout(content, decrypted_data.decode("utf-8"))
                else:
                    self.authenticate_dialog = self.on_authenticate(title, action, callback, content)

        elif action == "reveal":
            self.app.utils.reveal_file_gio(self.app.main_window, self.cache_file)

        elif action == "info":
            self.clip_info_revealer.set_reveal_child(True)

        elif action == "view":
            if "url" in self.type:
                with open(self.cache_file) as file:
                    lines = file.readlines()
                self.app.utils.open_url_gtk(lines[0].replace('\n',''))
            elif "files" in self.type:
                with open(self.cache_file) as file:
                    file_content = file.readlines()
                if len(file_content) == 1:
                    file_path = file_content[0].replace("copy","").replace("file://","").strip().replace("%20", " ")
                    self.app.utils.reveal_file_gio(file_path)
                else:
                    files_popover = FilesContainerPopover(self.cache_file, self.type, self.app, button)
                    files_popover.popup()
            else:
                self.app.utils.open_file_gio(self.cache_file)

        elif action == "copy":
            icon = Gtk.Image().new_from_icon_name("process-completed", Gtk.IconSize.SMALL_TOOLBAR)
            label = Gtk.Label("Copied to clipboard")
            action_notify_box.attach(icon, 0, 0, 1, 1)
            action_notify_box.attach(label, 1, 0, 1, 1)
            copy_result = False
            temp_file_uri = ""
            title = "Copy Content"
            callback = self.on_button_clicked
            
            if "yes" in self.protected:
                if validated:
                    decrypt, decrypted_data = self.app.utils.do_encryption("decrypt", data, self.cache_file)
                    if decrypt:
                        import tempfile
                        temp_filename = next(tempfile._get_candidate_names()) + tempfile.gettempprefix()
                        temp_file_uri = os.path.join(tempfile.gettempdir(), temp_filename)
                        print(temp_file_uri)
                        with open(temp_file_uri, 'wb') as file:
                            file.write(decrypted_data)
                            file.close()
                        copy_result = self.app.utils.copy_to_clipboard(self.target, temp_file_uri, self.type)
                        
                else:
                    self.authenticate_dialog = self.on_authenticate(title, action, callback)
            else:
               copy_result = self.app.utils.copy_to_clipboard(self.target, self.cache_file, self.type)

            if copy_result:
                action_notify_box.show_all()
                self.clip_action_notify_revealer.set_reveal_child(True)
                self.app.cache_manager.update_cache_on_recopy(self.cache_file)
                if "yes" in self.protected:
                    os.remove(temp_file_uri)

            if validated is False and copy_result is False and button is None:
                label = Gtk.Label("Authentication failed")
                action_notify_box.show_all()
                self.clip_action_notify_revealer.set_reveal_child(True)
            
        elif action == "force_delete" or action[0] == "force_delete":
            current_flowbox_index = flowboxchild.get_index() - 1
            self.app.cache_manager.delete_record(self.id, self.cache_file, self.type)
            self.app.main_window.update_total_clips_label("delete")
            if len(flowbox.get_children()) - 1 != 0 and current_flowbox_index >= 0:
                pass
            elif len(flowbox.get_children()) == 1:
                current_flowbox_index = 0
            else:
                current_flowbox_index = 1
            if len(flowbox.get_children()) > 0:
                flowbox.select_child(flowbox.get_child_at_index(current_flowbox_index))
                flowbox.get_child_at_index(current_flowbox_index).grab_focus()
                self.app.main_window.clips_view.on_child_activated(flowbox, flowbox.get_child_at_index(current_flowbox_index))
            flowboxchild.destroy()
            try:
                self.delete_clip_dialog.destroy()
            except:
                pass

        elif action == "delete":
            self.delete_clip_dialog = custom_widgets.CustomDialog(
                dialog_parent_widget=self,
                dialog_title="Delete Action",
                dialog_content_widget=self.generate_clip_info(),
                action_button_label="Delete",
                action_button_name="delete",
                action_callback=self.on_clip_action,
                action_type="destructive",
                size=[250, -1],
                data="force_delete"
                )

        elif action == "multi-delete":
            flowboxchild.destroy()
            self.app.cache_manager.delete_record(self.id, self.cache_file, self.type)
            self.app.main_window.update_total_clips_label("delete")

        else:
            print(action[0])
            print(action[1])
            pass

    def update_timestamp_on_clips(self, datetime):
        self.created = datetime
        self.created_short = datetime.strftime('%a, %b %d %Y, %H:%M:%S')
        self.fuzzytimestamp = self.app.utils.get_fuzzy_timestamp(datetime)
        self.fuzzytimestamp_label.props.label = self.fuzzytimestamp

    def on_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        tooltip.set_custom(None)
        tooltip.set_custom(self.generate_clip_info())
        return True

    def on_notify_action_hide(self, clip_action_notify, event):
        clip_action_notify.set_reveal_child(False)
        clip_action_notify.props.can_focus = False

    def on_authenticate(self, title, action, callback, data=None):
        password_editor = custom_widgets.PasswordEditor(
            main_label="Password required to reveal content", 
            gtk_application=self.app,
            type="authenticate",
            auth_callback=self.on_revealcontent)
        
        authenticate_dialog = custom_widgets.CustomDialog(
            dialog_parent_widget=self,
            dialog_title=title,
            dialog_content_widget=password_editor,
            action_button_label="Authenticate",
            action_button_name="authenticate",
            action_callback=callback,
            action_type="suggested",
            size=[250,-1],
            data=(
                password_editor.password_authentication,
                )
            )
        return authenticate_dialog

    def on_button_clicked(self, button=None, data=None):
        if button.props.name == "authenticate":
            password_authentication_callback = data[0][0]
            if password_authentication_callback:
                self.on_reveal_content()

    def on_revealcontent(self, *args):
        do_authenticate, authenticated_data = self.app.utils.do_authentication("get")
        if do_authenticate:
            self.on_clip_action(button=None, action="protect", validated=True, data=authenticated_data)
            try:
                self.authenticate_dialog.destroy()
            except:
                pass

    def on_revealcontent_timeout(self, label, content):

        def update_label(timeout):
            label.props.label = "{message} ({i})\n".format(message=content,i=timeout)

        @self.app.utils.run_async
        def timeout_label(self, label):
            
            import time
            for i in reversed(range(1, self.app.gio_settings.get_int(key="unprotect-timeout"), 1)):
                GLib.idle_add(update_label, (i))
                time.sleep(1)
            label.props.label = "*********"

        timeout_label(self, label)

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

    stop_threads = False
    play_gif_thread = None
    alpha = False

    def __init__(self, filepath, type, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.type = type
        if "gif" in self.type:
            self.pixbuf_original = GdkPixbuf.PixbufAnimation.new_from_file(filepath)
            self.pixbuf_original_height = self.pixbuf_original.get_height()
            self.pixbuf_original_width = self.pixbuf_original.get_width()
            self.iter = self.pixbuf_original.get_iter()
            if self.iter.get_pixbuf().get_has_alpha():
                self.alpha = True
        else:
            self.pixbuf_original = GdkPixbuf.Pixbuf.new_from_file(filepath)
            self.pixbuf_original_height = self.pixbuf_original.props.height
            self.pixbuf_original_width = self.pixbuf_original.props.width
            if self.pixbuf_original.get_has_alpha():
                self.alpha = True

        if self.alpha:
            self.get_style_context().add_class("checkerboard")

        self.ratio_h_w = self.pixbuf_original_height / self.pixbuf_original_width
        self.ratio_w_h = self.pixbuf_original_width / self.pixbuf_original_height
    
        drawing_area = Gtk.DrawingArea()
        drawing_area.props.expand = True
        drawing_area.connect("draw", self.draw)
        drawing_area.props.can_focus = False
 
        self.props.name = "image-container"
        self.attach(drawing_area, 0, 0, 1, 1)

        self.label = "{width} x {height} px".format(width=str(self.pixbuf_original_width), height=str(self.pixbuf_original_height))

    def animation_loop_func(self, *args):
        self.iter.advance()
        GLib.timeout_add(self.iter.get_delay_time(), self.animation_func, None)
        self.queue_draw()

    def animation_func(self, *args):
        import time
        while True:
            self.iter.advance()
            self.queue_draw()
            time.sleep(self.iter.get_delay_time()/1000)
            if self.stop_threads:
                break

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

        if "gif" in self.type:
            pixbuf = GdkPixbuf.PixbufAnimationIter.get_pixbuf(self.iter)
            pixbuf_fitted = GdkPixbuf.Pixbuf.new(pixbuf.get_colorspace(), pixbuf.get_has_alpha(), pixbuf.get_bits_per_sample(), width, height)
        else:
            pixbuf = self.pixbuf_original
            pixbuf_fitted = GdkPixbuf.Pixbuf.new(pixbuf.get_colorspace(), pixbuf.get_has_alpha(), pixbuf.get_bits_per_sample(), width, height)

        if int(width * self.ratio_h_w) < height:
            scaled_pixbuf = pixbuf.scale_simple(int(height * self.ratio_w_h), height, GdkPixbuf.InterpType.BILINEAR)
        else:
            scaled_pixbuf = pixbuf.scale_simple(width, int(width * self.ratio_h_w), GdkPixbuf.InterpType.BILINEAR)

        if self.pixbuf_original_width * self.pixbuf_original_height < width * height:
            # Find the offset we need to center the source pixbuf on the destination since its smaller
            y = abs((height - self.pixbuf_original_height) / 2)
            x = abs((width - self.pixbuf_original_width) / 2)
            final_pixbuf = self.pixbuf_original
        else:
            # Find the offset we need to center the source pixbuf on the destination
            y = abs((height - scaled_pixbuf.props.height) / 2)
            x = abs((width - scaled_pixbuf.props.width) / 2)
            scaled_pixbuf.copy_area(x, y, width, height, pixbuf_fitted, 0, 0)
            # Set coordinates for cairo surface since this has been fitted, it should be (0, 0) coordinate
            x = y = 0
            final_pixbuf = pixbuf_fitted

        # cairo_context.set_operator(cairo.Operator.SOURCE)

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

        if app.utils.is_light_color(rgb) == "light" and a >= 0.5:
            font_color = "rgba(0,0,0,0.85)"
        elif app.utils.is_light_color(rgb) == "dark" and a >= 0.5:
            font_color = "rgba(255,255,255,0.85)"
        if app.utils.is_light_color(rgb) == "light" and a <= 0.5:
            font_color = "rgba(0,0,0,0.85)"
        elif app.utils.is_light_color(rgb) == "dark" and a <= 0.5:
            font_color = "rgba(0,0,0,0.85)"

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
    def __init__(self, filepath, type, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.content = open(filepath, "r")
        self.content = self.content.read()

        webview = WebKit2.WebView()
        webview.props.zoom_level = 0.85
        webview.load_html(self.content)
        webview.props.expand = True
        webview.props.can_focus = False
        # webview.props.sensitive = True

        # print(webview.get_child())
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

        self.app = app
        scale = self.get_scale_factor()
        self.icon_size = 72 * scale
        self.iconstack_offset = 0

        self.iconstack_overlay = Gtk.Overlay()
        self.iconstack_overlay.props.expand = True
        self.iconstack_overlay.props.valign = Gtk.Align.FILL
        self.iconstack_overlay.props.halign = Gtk.Align.FILL
        
        with open(filepath) as file:
            file_content = file.readlines()

        file_count = len(file_content)

        mime_type = None
        with open(filepath) as file:
            for line_number, line_content in enumerate(file):
                if "file://" in line_content:
                    line_content = line_content.replace("copy","").replace("file://","").strip().replace("%20", " ")
                    if os.path.exists(line_content):
                        if os.path.isdir(line_content):  
                            mime_type = "inode/directory"
                        elif os.path.isfile(line_content):  
                            mime_type, val = Gio.content_type_guess(line_content, data=None)
                        
                        self.update_stack(line_content, mime_type)

        self.props.name = "files-container"
        self.attach(self.iconstack_overlay, 0, 0, 1, 1)

        self.label = str(len(file_content)) + " files"

    def update_stack(self, path, mime_type):
        icon = self.generate_default_icon(path, mime_type)
        if "image" in mime_type and not "gif" in mime_type:
            try:
                icon = self.generate_image_icon(path)
            except:
                pass
        if "gif" in mime_type:
            icon = self.generate_gif_icon(path)

        icon.props.halign = icon.props.valign = Gtk.Align.CENTER

        import random
        if len(self.iconstack_overlay.get_children()) != 1:
            margin = random.randint(24,64) + self.iconstack_offset
            set_margins = [icon.set_margin_bottom, icon.set_margin_top, icon.set_margin_left, icon.set_margin_right]
            random.choice(set_margins)(margin)
            random.choice(set_margins)(self.iconstack_offset + random.randint(10,1000) % 2)

        self.iconstack_overlay.add_overlay(icon)

        if self.iconstack_offset >= 30:
            self.iconstack_offset = 0
        else:
            self.iconstack_offset += 2

    def generate_default_icon(self, path, mime_type):
        icon = Gtk.Image()
        icons = Gio.content_type_get_icon(mime_type)
        for icon_name in icons.to_string().split():
            if icon_name != "." and icon_name != "GThemedIcon":
                try:
                    icon_pixbuf = self.app.icon_theme.load_icon(icon_name, self.icon_size, 0)
                    break
                except:
                    pass
            if "generic" in icon_name:
                try:
                    icon_pixbuf = self.app.icon_theme.load_icon(icon_name, self.icon_size, 0)
                    break
                except:
                    icon_pixbuf = self.app.icon_theme.load_icon("application-octet-stream", self.icon_size, 0)
        icon.props.pixbuf = icon_pixbuf
        return icon

    def generate_image_icon(self, path):
        icon = Gtk.Image()
        icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, self.icon_size, self.icon_size)
        icon.props.pixbuf = icon_pixbuf
        return icon

    def generate_gif_icon(self, path):
        icon = Gtk.Image()
        
        pixbuf_original = GdkPixbuf.PixbufAnimation.new_from_file(path)
        pixbuf_original_height = pixbuf_original.get_height()
        pixbuf_original_width = pixbuf_original.get_width()
        iter = pixbuf_original.get_iter()
        for i in range(0, 250):
            timeval = GLib.TimeVal()
            timeval.tv_sec = int(str(GLib.get_real_time())[:-3])
            iter.advance(timeval)
            self.queue_draw()

        ratio_h_w = pixbuf_original_height / pixbuf_original_width
        ratio_w_h = pixbuf_original_width / pixbuf_original_height

        if ratio_w_h > 1:
            width = self.icon_size
            height = int((10/16)*self.icon_size) + 1
        else:
            width = height = self.icon_size

        pixbuf = GdkPixbuf.PixbufAnimationIter.get_pixbuf(iter)
        pixbuf_fitted = GdkPixbuf.Pixbuf.new(pixbuf.get_colorspace(), pixbuf.get_has_alpha(), pixbuf.get_bits_per_sample(), width, height)

        if int(width * ratio_h_w) < height:
            scaled_pixbuf = pixbuf.scale_simple(int(height * ratio_w_h), height, GdkPixbuf.InterpType.BILINEAR)
        else:
            scaled_pixbuf = pixbuf.scale_simple(width, int(width * ratio_h_w), GdkPixbuf.InterpType.BILINEAR)
        icon.props.pixbuf = scaled_pixbuf
        return icon

# ----------------------------------------------------------------------------------------------------

class FilesContainerPopover(Gtk.Popover):
    def __init__(self, filepath, type, app, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app
        scale = self.get_scale_factor()
        self.icon_size = 48 * scale
        self.iconstack_offset = 0

        self.flowbox = Gtk.FlowBox()
        self.flowbox.props.name = "files-popover-flowbox"
        self.flowbox.props.expand = True
        self.flowbox.props.homogeneous = False
        self.flowbox.props.row_spacing = 8
        self.flowbox.props.column_spacing = 4
        self.flowbox.props.max_children_per_line = 3
        self.flowbox.props.min_children_per_line = 3
        self.flowbox.props.valign = self.flowbox.props.halign = Gtk.Align.FILL
        self.flowbox.connect("child-activated", self.on_files_activated)

        mime_type = None
        with open(filepath) as file:
            for line_number, line_content in enumerate(file):
                if "file://" in line_content:
                    line_content = line_content.replace("copy","").replace("file://","").strip().replace("%20", " ")
                    if os.path.exists(line_content):
                        if os.path.isdir(line_content):  
                            mime_type = "inode/directory"
                        elif os.path.isfile(line_content):  
                            mime_type, val = Gio.content_type_guess(line_content, data=None)
                        
                        self.update_stack(line_content, mime_type)

        # disable focus on flowboxchild items
        for child in self.flowbox.get_children():
            child.props.can_focus = False

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.props.name = "files-popover-scrolledwindow"
        scrolled_window.props.expand = True
        scrolled_window.add(self.flowbox)

        grid = Gtk.Grid()
        grid.props.expand = True
        grid.props.name = "files-popover-main-grid"
        grid.props.margin = 4
        grid.attach(scrolled_window, 0, 0, 1, 1)
        
        self.props.name = "files-popover"
        self.props.position = Gtk.PositionType.BOTTOM
        self.props.relative_to = parent

        if len(self.flowbox.get_children()) > 3:
            self.set_size_request(320, 240)
        else:
            self.set_size_request(320, 160)
        
        self.add(grid)
        self.connect("closed", self.on_closed)
        self.show_all()

    def on_closed(self, *args):
        self.destroy()

    def on_files_activated(self, flowbox, flowboxchild):
        flowboxchild.grab_focus()
        file_grid = [child for child in flowboxchild.get_children() if isinstance(child, Gtk.Grid)][0]
        self.app.utils.reveal_file_gio(self.app.main_window, file_grid.props.name)

    def update_stack(self, path, mime_type):
        icon = self.generate_default_icon(path, mime_type)
        if "image" in mime_type and not "gif" in mime_type:
            try:
                icon = self.generate_image_icon(path)
            except:
                pass
        if "gif" in mime_type:
            icon = self.generate_gif_icon(path)

        icon.props.halign = icon.props.valign = Gtk.Align.CENTER

        label = Gtk.Label(os.path.basename(path))
        label.props.wrap_mode = Pango.WrapMode.CHAR
        label.props.max_width_chars = 10
        label.props.wrap = True
        label.props.hexpand = True
        label.props.justify = Gtk.Justification.CENTER
        label.props.lines = 2
        label.props.ellipsize = Pango.EllipsizeMode.END

        file_grid = Gtk.Grid()
        file_grid.props.expand = True
        file_grid.props.margin = 4
        file_grid.props.name = path
        file_grid.props.has_tooltip = True
        file_grid.props.halign = file_grid.props.valign = Gtk.Align.CENTER
        file_grid.attach(icon, 0, 0, 1, 1)
        file_grid.attach(label, 0, 1, 1, 1)
        
        self.flowbox.add(file_grid)

    def generate_default_icon(self, path, mime_type):
        icon = Gtk.Image()
        icons = Gio.content_type_get_icon(mime_type)
        for icon_name in icons.to_string().split():
            if icon_name != "." and icon_name != "GThemedIcon":
                try:
                    icon_pixbuf = self.app.icon_theme.load_icon(icon_name, self.icon_size, 0)
                    break
                except:
                    pass
            if "generic" in icon_name:
                try:
                    icon_pixbuf = self.app.icon_theme.load_icon(icon_name, self.icon_size, 0)
                    break
                except:
                    icon_pixbuf = self.app.icon_theme.load_icon("application-octet-stream", self.icon_size, 0)
        icon.props.pixbuf = icon_pixbuf
        return icon

    def generate_image_icon(self, path):
        icon = Gtk.Image()
        icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, self.icon_size, self.icon_size)
        icon.props.pixbuf = icon_pixbuf
        return icon

    def generate_gif_icon(self, path):
        icon = Gtk.Image()
        
        pixbuf_original = GdkPixbuf.PixbufAnimation.new_from_file(path)
        pixbuf_original_height = pixbuf_original.get_height()
        pixbuf_original_width = pixbuf_original.get_width()
        iter = pixbuf_original.get_iter()
        for i in range(0, 250):
            timeval = GLib.TimeVal()
            timeval.tv_sec = int(str(GLib.get_real_time())[:-3])
            iter.advance(timeval)
            self.queue_draw()

        ratio_h_w = pixbuf_original_height / pixbuf_original_width
        ratio_w_h = pixbuf_original_width / pixbuf_original_height

        if ratio_w_h > 1:
            width = self.icon_size
            height = int((10/16)*self.icon_size) + 1
        else:
            width = height = self.icon_size

        pixbuf = GdkPixbuf.PixbufAnimationIter.get_pixbuf(iter)
        pixbuf_fitted = GdkPixbuf.Pixbuf.new(pixbuf.get_colorspace(), pixbuf.get_has_alpha(), pixbuf.get_bits_per_sample(), width, height)

        if int(width * ratio_h_w) < height:
            scaled_pixbuf = pixbuf.scale_simple(int(height * ratio_w_h), height, GdkPixbuf.InterpType.BILINEAR)
        else:
            scaled_pixbuf = pixbuf.scale_simple(width, int(width * ratio_h_w), GdkPixbuf.InterpType.BILINEAR)
        icon.props.pixbuf = scaled_pixbuf
        return icon


# ----------------------------------------------------------------------------------------------------

class SpreadsheetContainer(HtmlContainer):
    def __init__(self, filepath, type, app, *args, **kwargs):
        super().__init__(filepath, type, app)

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

        self.app = app
        scale = self.get_scale_factor()
        self.icon_size = 64 * scale
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
                    icon_pixbuf = self.app.icon_theme.load_icon(icon_name, self.icon_size, 0)
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

        self.props.name = "url-container"

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
        title.props.max_width_chars = 20
        title.props.wrap = True
        title.props.hexpand = True
        title.props.justify = Gtk.Justification.CENTER
        title.props.lines = 3
        title.props.ellipsize = Pango.EllipsizeMode.END
        
        domain = Gtk.Label(domain)

        self.attach(favicon, 0, 0, 1, 1)
        self.attach(title, 0, 1, 1, 1)
        self.attach(domain, 0, 2, 1, 1)
        self.props.margin = 10
        self.props.valign = Gtk.Align.CENTER
        self.props.halign = Gtk.Align.FILL
        
        self.label = "Internet URL"

# ----------------------------------------------------------------------------------------------------

class EmailContainer(DefaultContainer):
    def __init__(self, filepath, type, app, cache_filedir, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.props.name = "email-container"

        self.label = "Email"

        with open(filepath) as file:
            self.content  = file.readlines()

        domain = self.content[0].split("@")[-1].replace("\n","")
        checksum = os.path.splitext(filepath)[0].split("/")[-1]
        
        icon_size = 48 * self.get_scale_factor()
        favicon_file = os.path.join(cache_filedir[:-6],"icon", domain + "-" + checksum + ".ico")
        
        try:
            favicon = Gtk.Image()
            favicon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(favicon_file, icon_size, icon_size)
            favicon.props.pixbuf = favicon_pixbuf
        except:
            favicon = Gtk.Image().new_from_icon_name("mail-send", Gtk.IconSize.LARGE_TOOLBAR)
            favicon.set_pixel_size(icon_size)
            
        favicon.props.margin_bottom = 10

        self.title = self.content[0].split(":")[-1].replace("\n","")

        title = Gtk.Label(self.title)
        title.props.name = "mail-container-title"
        title.props.wrap_mode = Pango.WrapMode.WORD
        title.props.max_width_chars = 40
        title.props.wrap = True
        title.props.hexpand = True
        title.props.justify = Gtk.Justification.CENTER
        title.props.lines = 3
        title.props.ellipsize = Pango.EllipsizeMode.END

        domain = Gtk.Label(domain)

        self.attach(favicon, 0, 0, 1, 1)
        self.attach(title, 0, 1, 1, 1)
        self.attach(domain, 0, 2, 1, 1)
        self.props.margin = 10
        self.props.valign = Gtk.Align.CENTER
        self.props.halign = Gtk.Align.FILL

# ----------------------------------------------------------------------------------------------------

class ProtectedContainer(DefaultContainer):
    def __init__(self, filepath, type, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.props.name = "protected-container"
        self.label = "Protected Clips"

        self.props.margin = 10
        self.props.margin_left = self.props.margin_right = 10

        self.content = Gtk.Label()
        self.content.props.label = "*********"
        self.content.props.hexpand = False
        self.content.props.max_width_chars = 23
        self.content.props.wrap = False
        self.content.props.expand = False
        self.content.props.ellipsize = Pango.EllipsizeMode.NONE
        self.content.props.wrap_mode = Pango.WrapMode.CHAR
        self.content.props.max_width_chars = 23

        self.props.halign = self.props.valign = Gtk.Align.CENTER
        self.props.expand = False
        self.props.hexpand = True

        self.attach(self.content, 0, 0, 1, 1)

