# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

from os.path import basename
import gi
gi.require_version('Gtk', '3.0')
# gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, GdkPixbuf, Pango, Gdk, Gio, GLib
import cairo
from . import custom_widgets
from .utils import log_function_calls


import os
from datetime import datetime
import time

import chardet

global stop_threads

class ClipsView(Gtk.Grid):

    current_selected_flowboxchild_index = 0
    multi_select_mode = False
    filter_count = 0

    @log_function_calls
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
        self.flowbox.connect("add", self.on_child_count)
        self.flowbox.connect("remove", self.on_child_count)
        
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.props.expand = True
        scrolled_window.props.hscrollbar_policy = Gtk.PolicyType.NEVER
        scrolled_window.add(self.flowbox)

        self.multi_delete_revealer = self.generate_multi_delete_revealer()

        self.clips_view_overlay = Gtk.Overlay()
        self.clips_view_overlay.add(scrolled_window)
        self.clips_view_overlay.add_overlay(self.multi_delete_revealer)
        self.clips_view_overlay.set_overlay_pass_through(self.multi_delete_revealer, True)

        self.props.name = "clips-view"
        self.props.expand = True
        self.attach(self.clips_view_overlay, 0, 0, 1, 1)

    @log_function_calls
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
        button_grid.attach(cancel_multi_delete_button, 0, 0, 1, 1)
        button_grid.attach(self.select_all_button, 1, 0, 1, 1)
        button_grid.attach(self.delete_selected_button, 2, 0, 1, 1)

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

            if clips_container.type in ("plaintext", "html", "url/https", "url/http", "mail", "files") and clips_container.protected != "yes":
                with open(clips_container.cache_file) as file:
                    lines = file.readlines()
                contents = ''.join(lines)
                contents_single_keyword = [str(clips_container.id), clips_container.type.lower(), clips_container.target.lower(), clips_container.source_app.lower(), clips_container.created_short.lower(), clips_container.extended_info.lower(), contents.lower()]
                contents_multi_keyword = ' '.join(contents_single_keyword)
            else:
                contents_single_keyword = [str(clips_container.id), clips_container.type.lower(), clips_container.target.lower(), clips_container.source_app.lower(), clips_container.created_short.lower(), clips_container.extended_info.lower()]
                contents_multi_keyword = ' '.join(contents_single_keyword)

            if "," in search_text:
                if '"' in search_text:
                    search_text = search_text.replace('"',"")
                search_texts = search_text.split(",")
                search_texts = [text.lstrip(' ') for text in search_texts]
                search_texts = [text.rstrip(' ') for text in search_texts]
                if all(i in contents_multi_keyword for i in search_texts):
                    return True
                else:
                    return False
            else:
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

    @log_function_calls
    def new_clip(self, clip):

        app = self.app
        main_window = self.app.main_window
        id = clip[0]
        cache_file = os.path.join(app.cache_manager.cache_filedir, clip[6])
        new_flowboxchild = [child for child in self.flowbox.get_children() if child.get_children()[0].id == id]

        if os.path.exists(cache_file) and len(new_flowboxchild) == 0:
            self.flowbox.add(ClipsContainer(self.app, clip, app.cache_manager.cache_filedir, app.utils))
            main_window.update_total_clips_label("add")
            self.flowbox.show_all()

    @log_function_calls
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

    @log_function_calls
    def on_child_multi_selected(self, flowbox, flowboxchild):

        for flowboxchild in self.flowbox.get_selected_children():
            clips_container = flowboxchild.get_children()[0]
            clips_container.clip_overlay_revealer.set_reveal_child(True)
            clips_container.clip_action_revealer.set_reveal_child(False)
            clips_container.source_icon_revealer.set_reveal_child(False)
            clips_container.select_button.get_style_context().add_class("clip-selected")
        self.delete_selected_button.props.label = "Delete ({count})".format(count=str(len(self.flowbox.get_selected_children()))) 

    @log_function_calls
    def on_child_multi_unselected(self, clips_container):

        clips_container.clip_overlay_revealer.set_reveal_child(False)
        self.app.main_window.clips_view.flowbox.unselect_child(clips_container.get_parent())
        self.delete_selected_button.props.label = "Delete ({count})".format(count=str(len(self.flowbox.get_selected_children())))
        if len(self.flowbox.get_selected_children()) == 0:
            self.off_multi_select()

    @log_function_calls
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

    @log_function_calls
    def on_delete_selected(self, button):

        for flowboxchild in self.flowbox.get_selected_children():
            clips_container = flowboxchild.get_children()[0]
            clips_container.on_clip_action(action="multi-delete")
            flowboxchild.destroy()
        self.off_multi_select()

    @log_function_calls
    def on_cancel_multi_delete(self, button):

        self.off_multi_select()
        self.flowbox.unselect_all()
        self.select_all_button.props.name = "select-all-off"
        self.select_all_button.props.label = "Select All"
        self.delete_selected_button.props.label = "Delete ({count})".format(count=str(len(self.flowbox.get_selected_children())))
    
    @log_function_calls
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

    @log_function_calls
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

    def on_child_count(self, flowbox, obj):
        if len(flowbox.get_children()) == 1:
            flowbox.props.homogeneous = True
            flowbox.props.max_children_per_line = 1
        else:
            flowbox.props.homogeneous = False
            flowbox.props.max_children_per_line = 8


class ClipsContainer(Gtk.EventBox):

    @log_function_calls
    def __init__(self, app, clip, cache_filedir, utils, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.props.name = "clip-container"
        self.app = app
        self.scale = self.get_scale_factor()
        self.cache_filedir = cache_filedir
        self.id = clip[0]
        self.target = clip[1]
        self.created = datetime.strptime(clip[2], '%Y-%m-%d %H:%M:%S.%f')
        self.created_short = self.created.strftime('%a, %b %d %Y, %H:%M:%S')
        self.fuzzytimestamp = self.app.utils.get_fuzzy_timestamp(self.created)
        self.source = clip[3]
        self.source_app = clip[4]
        self.source_icon = clip[5]
        self.cache_file = clip[6]
        self.type = clip[7]
        self.protected = clip[8]
        self.cache_file = os.path.join(self.cache_filedir, self.cache_file)
        self.content = None

        self.content = self._select_container()

        self.extended_info = self.content.label
        self.clip_action_notify_revealer = self.generate_clip_action_notify()
        self.clip_overlay_revealer = self.generate_clip_overlay()

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

        self.on_cursor_entering_clip_handler_id = self.connect("enter-notify-event", self.on_cursor_entering_clip)
        self.on_cursor_leaving_clip_handler_id = self.connect("leave-notify-event", self.on_cursor_leaving_clip)
        self.on_double_clicked_clip_handler_id = self.connect("button-press-event", self.on_double_clicked_clip)

    def _select_container(self):
        # Container types based on clips_supported.py
        if "office/spreadsheet" in self.type:
            return SpreadsheetContainer(self.cache_file, self.type, self.app)
        elif "office/presentation" in self.type:
            return PresentationContainer(self.cache_file, self.type, self.app)
        elif "office/word" in self.type:
            return WordContainer(self.cache_file, self.type, self.app)
        elif "files" in self.type:
            is_files = True
            file = open(self.cache_file, "rb")
            encoding_name = chardet.detect(file.read())["encoding"]
            file.close()
            with open(self.cache_file, encoding=encoding_name) as file:
                file_content = file.readlines()
            if len(file_content) == 1:
                file_content = file_content[0].replace("copy","").replace("file://","").strip().replace("%20", " ").replace("\n","")
                if os.path.exists(file_content):
                    mime_type, val = Gio.content_type_guess(file_content, data=None)
                    if "image" in mime_type and not "webp" in mime_type:
                        return ImageContainer(file_content, mime_type, self.app)
                        is_files = False
            if is_files:
                return FilesContainer(self.cache_file, self.type, self.app)
        elif "image" in self.type:
            return ImageContainer(self.cache_file, self.type, self.app)
        elif "html" in self.type:
            thumbnail = self.get_thumbnail_path(self.cache_file)
            if thumbnail:
                return HtmlContainer(self.cache_file, self.type, self.app)
            else:
                return PlainTextContainer(self.cache_file, self.type, self.app)
        elif "richtext" in self.type:
            return FilesContainer(self.cache_file, self.type, self.app)
        elif "plaintext" in self.type and self.protected == "no":
            return PlainTextContainer(self.cache_file, self.type, self.app)
        elif "plaintext" in self.type and self.protected == "yes":
            return ProtectedContainer(self.cache_file, self.type, self.app)
        elif "color" in self.type:
            return ColorContainer(self.cache_file, self.type, self.app)
        elif "url" in self.type:
            with open(self.cache_file, encoding="utf-8", errors="replace") as file:
                url = file.readline().strip()
            thumbnail = self.get_thumbnail_path(self.cache_file)
            if thumbnail and self.app.utils.is_image_url(url):
                return UrlImageContainer(self.cache_file, self.type, self.app, self.cache_filedir)
            else:
                return UrlContainer(self.cache_file, self.type, self.app, self.cache_filedir)
        elif "mail" in self.type:
            return EmailContainer(self.cache_file, self.type, self.app, self.cache_filedir)
        else:
            self.app.logger.debug("clips_view.py: FallbackContainer: " + self.cache_file + " " + self.type)
            return FallbackContainer(self.cache_file, self.type, self.app)

    @log_function_calls
    def refresh(self):
        """Refresh the container content, e.g. when thumbnail or metadata is ready"""
        # Remove old content
        self.container_overlay.remove(self.content)
        
        # Select and add new content
        self.content = self._select_container()
        self.container_overlay.add(self.content)
        
        self.content.show_all()
        self.extended_info = self.content.label

    def get_thumbnail_path(self, filepath):
        import glob
        thumbnail_files = glob.glob(os.path.splitext(filepath)[0]+'-thumb.*')
        if thumbnail_files:
            return thumbnail_files[0]
        return None

    def generate_clip_select_button(self):
        button = Gtk.Button(image=Gtk.Image().new_from_icon_name("com.github.hezral.clips-select", Gtk.IconSize.SMALL_TOOLBAR))
        button.set_size_request(30, 30)
        button.props.name = "clip-select"
        button.props.halign = Gtk.Align.END
        button.props.valign = Gtk.Align.START
        button.props.can_focus = False
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

    def generate_clip_action_notify(self):
        action_notify_box = Gtk.Grid()
        action_notify_box.props.name = "clip-action-notify"
        action_notify_box.props.column_spacing = 6
        action_notify_box.props.halign = action_notify_box.props.valign = Gtk.Align.CENTER
        icon = Gtk.Image().new_from_icon_name("process-completed", Gtk.IconSize.SMALL_TOOLBAR)
        label = Gtk.Label("Copied to clipboard")
        action_notify_box.attach(icon, 0, 0, 1, 1)
        action_notify_box.attach(label, 1, 0, 1, 1)
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
        
        if "html" in self.type:
            copy_formatted_action = self.generate_action_button("edit-copy-style", "Copy", "copy")
            copy_action = self.generate_action_button("edit-copy-symbolic", "Copy Plaintext", "copy-plaintext")
        else:
            copy_action = self.generate_action_button("edit-copy-symbolic", "Copy", "copy")

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
        
        clip_action.attach(reveal_action, 4, 0, 1, 1)

        if "yes" in self.protected:
            clip_action.attach(protect_action, 2, 0, 1, 1)
        else:
            clip_action.attach(view_action, 2, 0, 1, 1)
            if "color" in self.type or "spreadsheet" in self.type or "presentation" in self.type:
                view_action.props.sensitive = False
                view_action.get_style_context().add_class("clip-action-disabled")

        if "html" in self.type:
            clip_action.attach(copy_formatted_action, 0, 0, 1, 1)
            clip_action.attach(copy_action, 1, 0, 1, 1)
        else:
            clip_action.attach(copy_action, 0, 0, 1, 1)

        clip_action.attach(delete_action, 3, 0, 1, 1)

        self.fuzzytimestamp_label = self.generate_fuzzytimestamp_label()
        clip_action.attach(self.fuzzytimestamp_label, 5, 0, 1, 1)

        self.select_button = self.generate_clip_select_button()

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
        clip_overlay_revealer.props.can_focus = False
        
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

    def generate_clip_info(self):
        id_label = Gtk.Label("ID: " + str(self.id))
        id_label.props.hexpand = True
        id_label.props.halign = Gtk.Align.START
        cache_file_label = Gtk.Label("Cache: " + os.path.basename(self.cache_file))
        cache_file_label.props.hexpand = True
        cache_file_label.props.halign = Gtk.Align.START
        source_app_label = Gtk.Label("Source: " + self.source_app)
        source_app_label.props.hexpand = True
        source_app_label.props.halign = Gtk.Align.START
        created_label = Gtk.Label("Created: " + self.created_short)
        created_label.props.hexpand = True
        created_label.props.halign = Gtk.Align.START
        type_label = Gtk.Label("Type: {type} ({target})".format(type=self.type, target=self.target))
        type_label.props.hexpand = True
        type_label.props.halign = Gtk.Align.START
        extended_label = Gtk.Label("Info: " + self.extended_info)
        extended_label.props.hexpand = True
        extended_label.props.halign = Gtk.Align.START
        
        grid = Gtk.Grid()
        grid.props.margin = 6
        grid.props.row_spacing = 6
        grid.attach(id_label, 0, 0, 1, 1)
        grid.attach(cache_file_label, 0, 1, 1, 1)
        grid.attach(source_app_label, 0, 2, 1, 1)
        grid.attach(created_label, 0, 3, 1, 1)
        grid.attach(type_label, 0, 4, 1, 1)
        grid.attach(extended_label, 0, 5, 1, 1)
        grid.show_all()
        return grid

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
            self.on_clip_action(button=None, action="copy")

    def on_cursor_entering_clip(self, widget, eventcrossing):
        self.get_parent().get_style_context().add_class("hover")
        self.clip_overlay_revealer.set_reveal_child(True)
        self.clip_action_revealer.set_reveal_child(True)
        self.source_icon_revealer.set_reveal_child(True)
        image_container = self.app.utils.get_widget_by_name(widget=self, child_name="image-container", level=0)
        if image_container is None:
            image_container = self.app.utils.get_widget_by_name(widget=self, child_name="url-image-container", level=0)
        if image_container is None:
            image_container = self.app.utils.get_widget_by_name(widget=self, child_name="html-container", level=0)

        if image_container is not None:
            if "gif" in image_container.type or image_container.filepath.lower().endswith(".gif"):
                image_container.stop_threads = False
                import threading
                image_container.play_gif_thread = threading.Thread(target=image_container.animation_func)
                image_container.play_gif_thread.start()

    def on_cursor_leaving_clip(self, widget, eventcrossing):
        self.get_parent().get_style_context().remove_class("hover")
        flowboxchild = self.get_parent()
        if flowboxchild.is_selected():
            self.clip_overlay_revealer.set_reveal_child(True)
        else: 
            self.clip_overlay_revealer.set_reveal_child(False)
        if self.clip_action_notify_revealer.get_child_revealed():
            self.clip_action_notify_revealer.set_reveal_child(False)
        flowboxchild_selected = self.app.main_window.clips_view.flowbox.get_selected_children()
        if len(flowboxchild_selected) != 0:
            if flowboxchild_selected[0].get_children()[0].clip_action_notify_revealer.get_child_revealed():
                flowboxchild_selected[0].get_children()[0].clip_action_notify_revealer.set_reveal_child(False)
        image_container = self.app.utils.get_widget_by_name(widget=self, child_name="image-container", level=0)
        if image_container is None:
            image_container = self.app.utils.get_widget_by_name(widget=self, child_name="url-image-container", level=0)
        if image_container is None:
            image_container = self.app.utils.get_widget_by_name(widget=self, child_name="html-container", level=0)

        if image_container is not None:
            if "gif" in image_container.type or image_container.filepath.lower().endswith(".gif"):
                if image_container.play_gif_thread is not None:
                    image_container.stop_threads = True
                    image_container.play_gif_thread.join()
                    image_container.play_gif_thread = None

    @log_function_calls
    def on_clip_action(self, button=None, action=None, validated=False, data=None):

        flowboxchild = self.get_parent()
        flowbox = self.app.main_window.clips_view.flowbox
        flowbox.select_child(flowboxchild)
        action_notify_box = self.clip_action_notify_revealer.get_children()[0]

        if action == "protect":
            if "yes" in self.protected:
                protected_container = self.app.utils.get_widget_by_name(self, "protected-container", 0, doPrint=False)
                content = protected_container.content
                title = "Reveal Content"
                callback = self.on_authenticated
                if validated:
                    decrypt, decrypted_data = self.app.utils.do_encryption("decrypt", data, self.cache_file)
                    if decrypt:
                        self.on_revealcontent_timeout(content, decrypted_data.decode("utf-8"))
                else:
                    self.authenticate_dialog = self.on_authenticate(title, action, callback, content)

        elif action == "reveal":
            self.app.file_manager.show_files_in_file_manager(self.cache_file)

        elif action == "view":
            if "url" in self.type:
                file = open(self.cache_file, "rb")
                encoding_name = chardet.detect(file.read())["encoding"]
                file.close()
                with open(self.cache_file, encoding=encoding_name) as file:
                    lines = file.readlines()
                self.app.utils.open_url_gtk(lines[0].replace('\n',''))
            elif "files" in self.type:
                file = open(self.cache_file, "rb")
                encoding_name = chardet.detect(file.read())["encoding"]
                file.close()
                with open(self.cache_file, encoding=encoding_name) as file:
                    file_content = file.readlines()
                if len(file_content) == 1:
                    file_path = file_content[0].replace("copy","").replace("file://","").strip().replace("%20", " ")
                    self.app.file_manager.show_files_in_file_manager(file_path)
                else:
                    files_popover = FilesContainerPopover(self.cache_file, self.type, self.app, button)
                    files_popover.popup()
            else:
                self.app.utils.open_file_gio(self.cache_file)

        elif action == "copy":
            self.app.logger.debug(f"clips_view.py: Copy action triggered for type={self.type}, target={self.target}, id={self.id}")
            copy_result = False
            temp_file_uri = ""
            title = "Copy Content"
            callback = self.on_authenticated

            # Set flag to prevent clipboard monitoring from capturing our own copy operation
            # This prevents the window from becoming unresponsive on Wayland
            if hasattr(self.app, 'clipboard_manager'):
                self.app.clipboard_manager._skip_clipboard_monitoring = True
                self.app.logger.debug("Set _skip_clipboard_monitoring flag before copy")

            if "yes" in self.protected:
                if validated:
                    decrypt, decrypted_data = self.app.utils.do_encryption("decrypt", data, self.cache_file)
                    if decrypt:
                        import tempfile
                        temp_filename = next(tempfile._get_candidate_names()) + tempfile.gettempprefix()
                        temp_file_uri = os.path.join(tempfile.gettempdir(), temp_filename)
                        with open(temp_file_uri, 'wb') as file:
                            file.write(decrypted_data)
                        copy_result = self.app.utils.copy_to_clipboard(self.target, temp_file_uri, self.type)
                else:
                    self.authenticate_dialog = self.on_authenticate(title, action, callback)
                    # Clear flag if we're showing authentication dialog
                    if hasattr(self.app, 'clipboard_manager'):
                        self.app.clipboard_manager._skip_clipboard_monitoring = False
            else:
               copy_result = self.app.utils.copy_to_clipboard(self.target, self.cache_file, self.type)

            # Clear flag after a short delay
            if hasattr(self.app, 'clipboard_manager'):
                def clear_flag():
                    self.app.clipboard_manager._skip_clipboard_monitoring = False
                    self.app.logger.debug("Cleared _skip_clipboard_monitoring flag after copy")
                    return False
                GLib.timeout_add(500, clear_flag)  # 500ms delay

            self.app.logger.debug(f"clips_view.py: Copy action completed, result={copy_result}")

            if copy_result:
                action_notify_box.show_all()
                self.clip_action_notify_revealer.set_reveal_child(True)
                self.app.cache_manager.update_cache_on_recopy(self.cache_file)
                if "yes" in self.protected:
                    os.remove(temp_file_uri)
                self.quick_paste()

        elif action == "copy-plaintext":
            alt_target = "text/plain;charset=utf-8"
            alt_type = "text"
            alt_cache_file = self.cache_file.replace("html", "txt")

            # Set flag to prevent clipboard monitoring from capturing our own copy operation
            if hasattr(self.app, 'clipboard_manager'):
                self.app.clipboard_manager._skip_clipboard_monitoring = True
                self.app.logger.debug("Set _skip_clipboard_monitoring flag before copy-plaintext")

            copy_result = self.app.utils.copy_to_clipboard(alt_target, alt_cache_file, alt_type)

            # Clear flag after a short delay
            if hasattr(self.app, 'clipboard_manager'):
                def clear_flag():
                    self.app.clipboard_manager._skip_clipboard_monitoring = False
                    self.app.logger.debug("Cleared _skip_clipboard_monitoring flag after copy-plaintext")
                    return False
                GLib.timeout_add(500, clear_flag)  # 500ms delay

            if copy_result:
                action_notify_box.show_all()
                self.clip_action_notify_revealer.set_reveal_child(True)
                self.app.cache_manager.update_cache_on_recopy(self.cache_file)
                self.quick_paste()

        elif action == "force_delete" or (isinstance(action, tuple) and action[0] == "force_delete"):
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

    def quick_paste(self):
        """
        Quickly paste clipboard contents to the previously active window.
        
        On X11: Can explicitly set the active window before pasting.
        On Wayland: Cannot control window focus due to security model.
                   The paste goes to whatever window receives focus after
                   Clips hides (usually the previously focused window).
        """
        from .sub_utils.display_backend import is_wayland
        
        def paste(data=None):
            if not is_wayland():
                try:
                    self.app.utils.set_active_window_by_xwindow(
                        self.app.utils.get_active_window_xlib()
                    )
                except Exception as e:
                    self.app.logger.debug(f"X11 window activation: {e}")
            self.app.utils.paste_from_clipboard(self.app)
            self.app.on_clipsapp_action()

        if self.app.gio_settings.get_value("quick-paste"):
            self.app.main_window.hide()
            self.app.on_clipsapp_action()
            GLib.timeout_add(100, paste, None)

    def update_timestamp_on_clips(self, dt):
        self.created = dt
        self.created_short = dt.strftime('%a, %b %d %Y, %H:%M:%S')
        self.fuzzytimestamp = self.app.utils.get_fuzzy_timestamp(dt)
        self.fuzzytimestamp_label.props.label = self.fuzzytimestamp

    def on_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        tooltip.set_custom(None)
        tooltip.set_custom(self.generate_clip_info())
        return True

    def on_authenticate(self, title, action, callback, data=None):
        action_label = "reveal" if action == "protect" else action
        password_editor = custom_widgets.PasswordEditor(
            main_label="Password required to {0} content".format(action_label), 
            gtk_application=self.app,
            type="authenticate",
            auth_callback=callback,
            action=action)
        authenticate_dialog = custom_widgets.CustomDialog(
            dialog_parent_widget=self,
            dialog_title=title,
            dialog_content_widget=password_editor,
            action_button_label="Authenticate",
            action_button_name="authenticate",
            action_callback=password_editor.on_current_password_entry_activated,
            action_type="suggested",
            size=[250,-1],
        )
        return authenticate_dialog

    def on_authenticated(self, action=None):
        do_authenticate, authenticated_data = self.app.utils.do_authentication("get")
        if do_authenticate:
            self.on_clip_action(button=None, action=action, validated=True, data=authenticated_data)
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


# Container classes
class DefaultContainer(Gtk.Grid):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.props.name = "default-container"
        self.props.halign = self.props.valign = Gtk.Align.FILL
        self.props.expand = True
        self.get_style_context().add_class("clip-containers")


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
        self.props.name = "default-container"
        self.attach(self.content, 0, 0, 1, 1)
        self.label = str(len(type)) + " chars"

class ImageContainer(DefaultContainer):
    def __init__(self, filepath, type, app, scale_mode="fill", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = type
        self.filepath = filepath
        self.stop_threads = False
        self.play_gif_thread = None
        self.alpha = False
        self.scale_mode = scale_mode
        if "gif" in self.type or filepath.lower().endswith(".gif"):
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
        if self.alpha and "thumb" not in filepath:
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

    def animation_func(self, *args):
        import time
        while True:
            self.iter.advance()
            self.queue_draw()
            time.sleep(self.iter.get_delay_time()/1000)
            if self.stop_threads:
                break

    def draw(self, drawing_area, cairo_context, hover_scale=1):
        from math import pi
        scale = self.get_scale_factor()
        width = int(self.get_allocated_width() * scale * hover_scale)
        height = int(self.get_allocated_height() * scale * hover_scale)
        radius = 4 * scale
        
        if "gif" in self.type or self.filepath.lower().endswith(".gif"):
            pixbuf = GdkPixbuf.PixbufAnimationIter.get_pixbuf(self.iter)
        else:
            pixbuf = self.pixbuf_original

        if self.scale_mode == "fit":
            # "Aspect Fit" (Contain) - show the entire image within the allocated area
            if self.ratio_h_w * width > height:
                new_h = height
                new_w = height * self.ratio_w_h
            else:
                new_w = width
                new_h = width * self.ratio_h_w
            
            final_pixbuf = pixbuf.scale_simple(int(new_w), int(new_h), GdkPixbuf.InterpType.BILINEAR)
            x = (width - final_pixbuf.get_width()) / 2
            y = (height - final_pixbuf.get_height()) / 2

        elif self.scale_mode == "height":
            # "Fit to Height" - Scale height to match, crop sides if wide, center horizontally
            new_h = height
            new_w = height * self.ratio_w_h
            
            final_pixbuf = pixbuf.scale_simple(int(new_w), int(new_h), GdkPixbuf.InterpType.BILINEAR)
            # Center the scaled image horizontally (crops sides if new_w > width)
            x = (width - final_pixbuf.get_width()) / 2
            y = 0
        elif self.scale_mode == "natural-left":
            # "Natural Left" - show image at its natural size, aligned to the left, centered vertically
            final_pixbuf = pixbuf
            x = 0
            y = (height - final_pixbuf.get_height()) / 2
        else:
            # "Aspect Fill" (Cover) - default behavior
            # Choose scale factor to cover the entire area
            if self.ratio_h_w * width < height:
                new_h = height
                new_w = height * self.ratio_w_h
            else:
                new_w = width
                new_h = width * self.ratio_h_w
            
            # Avoid upscaling small images in 'fill' mode if they fit
            if self.pixbuf_original_width < width and self.pixbuf_original_height < height:
                final_pixbuf = pixbuf
            else:
                scaled_pixbuf = pixbuf.scale_simple(int(new_w), int(new_h), GdkPixbuf.InterpType.BILINEAR)
                # Create a pixbuf of exact target size and copy area to it (cropping)
                final_pixbuf = GdkPixbuf.Pixbuf.new(pixbuf.get_colorspace(), pixbuf.get_has_alpha(), pixbuf.get_bits_per_sample(), width, height)
                
                # Source x/y for the crop (centered)
                src_x = max(0, (scaled_pixbuf.get_width() - width) / 2)
                src_y = max(0, (scaled_pixbuf.get_height() - height) / 2)
                scaled_pixbuf.copy_area(int(src_x), int(src_y), width, height, final_pixbuf, 0, 0)
            
            x = (width - final_pixbuf.get_width()) / 2
            y = (height - final_pixbuf.get_height()) / 2

        cairo_context.save()
        cairo_context.scale(1.0 / scale, 1.0 / scale)
        cairo_context.new_sub_path()
        cairo_context.arc(width - radius, radius, radius, 0-pi/2, 0)
        cairo_context.arc(width - radius, height - radius, radius, 0, pi/2)
        cairo_context.arc(radius, height - radius, radius, pi/2, pi)
        cairo_context.arc(radius, radius, radius, pi, pi + pi/2)
        cairo_context.close_path()
        Gdk.cairo_set_source_pixbuf(cairo_context, final_pixbuf, x, y)
        cairo_context.clip()
        cairo_context.paint()
        cairo_context.restore()


class ColorContainer(DefaultContainer):
    def __init__(self, filepath, type, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = open(filepath, "r").read()
        rgb, a = app.utils.to_rgb(self.content)
        color_code = "rgba({r},{g},{b},{a})".format(r=rgb[0],g=rgb[1],b=rgb[2],a=a)
        if app.utils.is_light_color(rgb) == "light" and a >= 0.5:
            font_color = "rgba(0,0,0,0.85)"
        else:
            font_color = "rgba(255,255,255,0.85)" if a >= 0.5 else "rgba(0,0,0,0.85)"
        css = ".color-container-bg {background-color: " + color_code + "; color: " + font_color + ";}"
        provider = Gtk.CssProvider()
        provider.load_from_data(bytes(css.encode()))
        self.content = Gtk.Label(self.content)
        self.content.props.expand = True
        self.content.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        if str(a) != "1":
            self.get_style_context().add_class("checkerboard")
        self.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.get_style_context().add_class("color-container-bg")
        self.props.name = "color-container"
        self.attach(self.content, 0, 0, 1, 1)
        self.label = type.split("/")[1].upper()


class PlainTextContainer(DefaultContainer):
    def __init__(self, filepath, type, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(filepath, encoding="utf-8", errors="replace") as file:
            firstNlines = file.readlines()[0:10]
        self.content = ''.join(firstNlines)
        self.content = Gtk.Label(self.content)
        self.content.props.wrap_mode = Pango.WrapMode.CHAR
        self.content.props.max_width_chars = 23
        self.content.props.wrap = True
        self.content.props.selectable = False
        self.content.props.expand = True
        self.content.props.ellipsize = Pango.EllipsizeMode.END
        self.props.margin = 10
        self.props.name = "plaintext-container"
        self.attach(self.content, 0, 0, 1, 1)
        i = 0
        with open(filepath, encoding="utf-8", errors="replace") as file:
            for i, l in enumerate(file):
                pass
        if not i+1 < 10:
            lines = Gtk.Label(str(i+1-10) + " lines more...")
            lines.props.halign = Gtk.Align.END
            self.attach(lines, 0, 1, 1, 1)
        self.label = str(len(self.content.props.label)) + " chars"


class HtmlContainer(ImageContainer):
    def __init__(self, filepath, type, app, *args, **kwargs):
        import glob
        thumbnail_files = glob.glob(os.path.splitext(filepath)[0]+'-thumb.*')
        thumbnail = thumbnail_files[0] if thumbnail_files else os.path.splitext(filepath)[0]+'-thumb.png'
        # Screenshot is generated before this container is created
        # See ClipsContainer.__init__ for HTML type handling
        super().__init__(thumbnail, type, app, scale_mode="natural-left")
        self.content = open(filepath, "r").read()
        css_bg_color = app.utils.get_css_background_color(self.content)
        if css_bg_color is not None:
            rgb, a = app.utils.to_rgb(css_bg_color)
            color_code = "rgba({r},{g},{b},{a})".format(r=rgb[0],g=rgb[1],b=rgb[2],a=a)
        else:
            color_code = "@theme_base_color"
        html_content_css = ".html-container-bg {{background-color: {0};}}".format(color_code)
        provider = Gtk.CssProvider()
        provider.load_from_data(bytes(html_content_css.encode()))
        self.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.get_style_context().add_class("html-container-bg")
        self.props.name = "html-container"
        self.type = type
        self.label = str(len(self.content)) + " chars"


class FilesContainer(DefaultContainer):
    def __init__(self, filepath, type, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        scale = self.get_scale_factor()
        self.icon_size = 72 * scale
        self.iconstack_offset = 0
        self.iconstack_overlay = Gtk.Overlay()
        self.iconstack_overlay.props.expand = True
        file = open(filepath, "rb")
        encoding_name = chardet.detect(file.read())["encoding"]
        file.close()
        with open(filepath, encoding=encoding_name) as file:
            file_content = file.readlines()
        for line in file_content:
            if "file://" in line:
                line = line.replace("copy","").replace("file://","").strip().replace("%20", " ")
                if os.path.exists(line):
                    mime_type = "inode/directory" if os.path.isdir(line) else Gio.content_type_guess(line, data=None)[0]
                    self.update_stack(line, mime_type)
        self.props.name = "files-container"
        self.attach(self.iconstack_overlay, 0, 0, 1, 1)
        self.label = str(len(file_content)) + " files"

    def update_stack(self, path, mime_type):
        icon = self.generate_default_icon(mime_type)
        if "image" in mime_type and "gif" not in mime_type:
            try:
                icon = Gtk.Image()
                icon.props.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(path, self.icon_size, self.icon_size)
            except:
                pass
        icon.props.halign = icon.props.valign = Gtk.Align.CENTER
        import random
        if len(self.iconstack_overlay.get_children()) != 1:
            margin = random.randint(24,64) + self.iconstack_offset
            random.choice([icon.set_margin_bottom, icon.set_margin_top, icon.set_margin_left, icon.set_margin_right])(margin)
        self.iconstack_overlay.add_overlay(icon)
        self.iconstack_offset = 0 if self.iconstack_offset >= 30 else self.iconstack_offset + 2

    def generate_default_icon(self, mime_type):
        icon = Gtk.Image()
        icons = Gio.content_type_get_icon(mime_type)
        for icon_name in icons.to_string().split():
            if icon_name not in (".", "GThemedIcon"):
                try:
                    icon.props.pixbuf = self.app.icon_theme.load_icon(icon_name, self.icon_size, 0)
                    break
                except:
                    pass
        return icon


class FilesContainerPopover(Gtk.Popover):
    def __init__(self, filepath, type, app, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.icon_size = 48 * self.get_scale_factor()
        self.flowbox = Gtk.FlowBox()
        self.flowbox.props.name = "files-popover-flowbox"
        self.flowbox.props.expand = True
        self.flowbox.props.max_children_per_line = 3
        self.flowbox.props.min_children_per_line = 3
        self.flowbox.connect("child-activated", self.on_files_activated)
        file = open(filepath, "rb")
        encoding_name = chardet.detect(file.read())["encoding"]
        file.close()
        with open(filepath, encoding=encoding_name) as file:
            for line in file.readlines():
                if "file://" in line:
                    line = line.replace("copy","").replace("file://","").strip().replace("%20", " ")
                    if os.path.exists(line):
                        mime_type = "inode/directory" if os.path.isdir(line) else Gio.content_type_guess(line, data=None)[0]
                        self.add_file_item(line, mime_type)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.props.expand = True
        scrolled_window.add(self.flowbox)
        grid = Gtk.Grid()
        grid.props.expand = True
        grid.props.margin = 4
        grid.attach(scrolled_window, 0, 0, 1, 1)
        self.props.name = "files-popover"
        self.props.position = Gtk.PositionType.BOTTOM
        self.props.relative_to = parent
        self.set_size_request(320, 240 if len(self.flowbox.get_children()) > 3 else 160)
        self.add(grid)
        self.connect("closed", lambda *a: self.destroy())
        self.show_all()

    def on_files_activated(self, flowbox, flowboxchild):
        file_grid = [c for c in flowboxchild.get_children() if isinstance(c, Gtk.Grid)][0]
        self.app.file_manager.show_files_in_file_manager(file_grid.props.name)

    def add_file_item(self, path, mime_type):
        icon = Gtk.Image()
        icons = Gio.content_type_get_icon(mime_type)
        for icon_name in icons.to_string().split():
            if icon_name not in (".", "GThemedIcon"):
                try:
                    icon.props.pixbuf = self.app.icon_theme.load_icon(icon_name, self.icon_size, 0)
                    break
                except:
                    pass
        label = Gtk.Label(os.path.basename(path))
        label.props.max_width_chars = 10
        label.props.ellipsize = Pango.EllipsizeMode.END
        file_grid = Gtk.Grid()
        file_grid.props.margin = 4
        file_grid.props.name = path
        file_grid.attach(icon, 0, 0, 1, 1)
        file_grid.attach(label, 0, 1, 1, 1)
        self.flowbox.add(file_grid)


class SpreadsheetContainer(ImageContainer):
    def __init__(self, filepath, type, app, *args, **kwargs):
        thumbnail = os.path.splitext(filepath)[0]+'-thumb.png'
        super().__init__(thumbnail, type, app, scale_mode="natural-left")
        self.props.name = "spreadsheet-container"
        self.label = "Spreadsheet"


class PresentationContainer(ImageContainer):
    def __init__(self, filepath, type, app, *args, **kwargs):
        thumbnail = os.path.splitext(filepath)[0]+'-thumb.png'
        super().__init__(thumbnail, type, app, scale_mode="natural-left")
        self.props.name = "presentation-container"
        self.label = "Presentation"


class WordContainer(DefaultContainer):
    def __init__(self, filepath, type, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.icon_size = 64 * self.get_scale_factor()
        mime_type = Gio.content_type_guess(filepath, data=None)[0] if os.path.isfile(filepath) else "inode/directory"
        icons = Gio.content_type_get_icon(mime_type)
        for icon_name in icons.to_string().split():
            if icon_name not in (".", "GThemedIcon"):
                try:
                    icon = Gtk.Image().new_from_pixbuf(self.app.icon_theme.load_icon(icon_name, self.icon_size, 0))
                    self.attach(icon, 0, 0, 1, 1)
                    break
                except:
                    pass
        label = Gtk.Label("Preview with View action")
        label.props.margin_top = 10
        self.attach(label, 0, 1, 1, 1)
        self.props.name = "word-container"
        self.props.halign = self.props.valign = Gtk.Align.CENTER
        self.label = "Word Document"


class UrlContainer(DefaultContainer):
    def __init__(self, filepath, type, app, cache_filedir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.props.name = "url-container"
        with open(filepath, encoding="utf-8") as file:
            self.content = file.readlines()
        domain = app.utils.get_domain(self.content[0].replace("\n",""))
        checksum = os.path.splitext(filepath)[0].split("/")[-1]
        icon_size = 32 * self.get_scale_factor()
        favicon_file = os.path.join(cache_filedir[:-6],"icon", domain + "-" + checksum + ".ico")
        try:
            # Keep a reference to the pixbuf to avoid RuntimeWarning
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(favicon_file, icon_size, icon_size)
            favicon = Gtk.Image()
            favicon.props.pixbuf = pixbuf
        except:
            favicon = Gtk.Image().new_from_icon_name("applications-internet", Gtk.IconSize.LARGE_TOOLBAR)
            favicon.set_pixel_size(icon_size)
        # favicon.props.margin_bottom = 10
        favicon.props.hexpand = True
        favicon.props.vexpand = True
        title = Gtk.Label(self.content[1] if len(self.content) > 1 else domain)
        title.props.max_width_chars = 20
        title.props.wrap = True
        title.props.ellipsize = Pango.EllipsizeMode.NONE
        title.props.justify = Gtk.Justification.CENTER
        title.props.halign = Gtk.Align.FILL
        title.props.hexpand = True
        title.props.vexpand = True
        domain_label = Gtk.Label(domain)
        domain_label.props.halign = Gtk.Align.FILL
        domain_label.props.hexpand = True
        domain_label.props.vexpand = True
        self.attach(favicon, 0, 0, 1, 1)
        self.attach(title, 0, 1, 1, 1)
        self.attach(domain_label, 0, 2, 1, 1)
        self.props.margin = 10
        self.props.valign = Gtk.Align.FILL
        self.label = "Internet URL"


class UrlImageContainer(ImageContainer):
    def __init__(self, filepath, type, app, cache_filedir, *args, **kwargs):
        import glob
        thumbnail_files = glob.glob(os.path.splitext(filepath)[0]+'-thumb.*')
        thumbnail = thumbnail_files[0] if thumbnail_files else os.path.splitext(filepath)[0]+'-thumb.png'
        super().__init__(thumbnail, type, app, scale_mode="fill")
        self.props.name = "url-image-container"
        
        with open(filepath, encoding="utf-8") as file:
            self.content = file.readlines()
        domain = app.utils.get_domain(self.content[0].replace("\n",""))
        checksum = os.path.splitext(filepath)[0].split("/")[-1]
        icon_size = 32 * self.get_scale_factor()
        favicon_file = os.path.join(cache_filedir[:-6],"icon", domain + "-" + checksum + ".ico")
        
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(favicon_file, icon_size, icon_size)
            favicon = Gtk.Image()
            favicon.props.pixbuf = pixbuf
        except:
            favicon = Gtk.Image().new_from_icon_name("applications-internet", Gtk.IconSize.LARGE_TOOLBAR)
            favicon.set_pixel_size(icon_size)
            
        favicon.props.hexpand = True
        favicon.props.vexpand = True
        
        title = Gtk.Label(self.content[1] if len(self.content) > 1 else domain)
        title.props.max_width_chars = 20
        title.props.wrap = True
        title.props.ellipsize = Pango.EllipsizeMode.NONE
        title.props.justify = Gtk.Justification.CENTER
        title.props.halign = Gtk.Align.FILL
        title.props.hexpand = True
        title.props.vexpand = True
        
        domain_label = Gtk.Label(domain)
        domain_label.props.halign = Gtk.Align.FILL
        domain_label.props.hexpand = True
        domain_label.props.vexpand = True

        # Create a grid for the elements to overlay on top of the image
        overlay_grid = Gtk.Grid()
        overlay_grid.attach(favicon, 0, 0, 1, 1)
        overlay_grid.attach(title, 0, 1, 1, 1)
        overlay_grid.attach(domain_label, 0, 2, 1, 1)
        overlay_grid.props.margin = 10
        overlay_grid.props.valign = Gtk.Align.FILL
        overlay_grid.props.hexpand = True
        overlay_grid.props.vexpand = True
        
        # Add a semi-transparent background to the overlay grid to make text readable
        css = "#url-image-overlay { background-color: rgba(0,0,0,0.4); border-radius: 4px; }"
        provider = Gtk.CssProvider()
        provider.load_from_data(bytes(css.encode()))
        overlay_grid.get_style_context().add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        overlay_grid.props.name = "url-image-overlay"
        
        # Use an overlay to put the grid on top of the DrawingArea (which is attached to self by ImageContainer)
        # Wait, if I want to use Gtk.Overlay, I should have used it from the start.
        # But ImageContainer is a Grid.
        # I'll try to use a little trick: attach the overlay_grid to the same cell as the DrawingArea.
        self.attach(overlay_grid, 0, 0, 1, 1)
        
        self.label = "Internet URL"


class EmailContainer(DefaultContainer):
    def __init__(self, filepath, type, app, cache_filedir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.props.name = "email-container"
        self.label = "Email"
        file = open(filepath, "rb")
        encoding_name = chardet.detect(file.read())["encoding"]
        file.close()
        with open(filepath, encoding=encoding_name) as file:
            self.content = file.readlines()
        domain = self.content[0].split("@")[-1].replace("\n","")
        checksum = os.path.splitext(filepath)[0].split("/")[-1]
        icon_size = 48 * self.get_scale_factor()
        favicon_file = os.path.join(cache_filedir[:-6],"icon", domain + "-" + checksum + ".ico")
        try:
            # Keep a reference to the pixbuf to avoid RuntimeWarning
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(favicon_file, icon_size, icon_size)
            favicon = Gtk.Image()
            favicon.props.pixbuf = pixbuf
        except:
            favicon = Gtk.Image().new_from_icon_name("mail-send", Gtk.IconSize.LARGE_TOOLBAR)
            favicon.set_pixel_size(icon_size)
        favicon.props.margin_bottom = 10
        title = Gtk.Label(self.content[0].split(":")[-1].replace("\n",""))
        title.props.max_width_chars = 40
        title.props.wrap = True
        title.props.ellipsize = Pango.EllipsizeMode.END
        domain_label = Gtk.Label(domain)
        self.attach(favicon, 0, 0, 1, 1)
        self.attach(title, 0, 1, 1, 1)
        self.attach(domain_label, 0, 2, 1, 1)
        self.props.margin = 10
        self.props.valign = Gtk.Align.CENTER


class ProtectedContainer(DefaultContainer):
    def __init__(self, filepath, type, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.props.name = "protected-container"
        self.label = "Protected Clips"
        self.props.margin = 10
        self.content = Gtk.Label()
        self.content.props.label = "*********"
        self.content.props.hexpand = False
        self.content.props.max_width_chars = 23
        self.props.halign = self.props.valign = Gtk.Align.CENTER
        self.props.hexpand = True
        self.attach(self.content, 0, 0, 1, 1)