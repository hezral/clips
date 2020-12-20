#!/usr/bin/env python3

'''
   Copyright 2020 Adi Hezral (hezral@gmail.com) (https://github.com/hezral)

   This file is part of Ghoster ("Application").

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
gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
from gi.repository import Gtk, Gdk, Granite, GObject

#------------------CONSTANTS------------------#

WORKSPACE_WIDTH = 384
WORKSPACE_HEIGHT = 250
WORKSPACE_RADIUS = 4

DOCK_WIDTH = 120
DOCK_HEIGHT = 10
DOCK_RADIUS = 3

PANEL_HEIGHT = 8

OVERLAY_COLOR = Gdk.RGBA(red=252 / 255.0, green=245 / 255.0, blue=213 / 255.0, alpha=0.35)
WORKSPACE_COLOR = Gdk.RGBA(red=33 / 255.0, green=33 / 255.0, blue=33 / 255.0, alpha=1)


#------------------CLASS-SEPARATOR------------------#

class WorkspacesView(Gtk.Grid):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add custom signals for callback AppManager if application_opened/closed events are triggered
        # GObject.signal_new(signal_name, type, flags, return_type, param_types)
        # param_types is a list example [GObject.TYPE_PYOBJECT, GObject.TYPE_STRING]
        GObject.signal_new("on-workspace-view-event", Gtk.Grid, GObject.SIGNAL_RUN_LAST, GObject.TYPE_BOOLEAN, [GObject.TYPE_PYOBJECT])

        # display = Gdk.Display.get_default()
        # monitor = display.get_primary_monitor()
        # geo = monitor.get_geometry()
        # print(geo.width, geo.height)
        # print(int(geo.width / 5), int(geo.height / 5))

        #-- stack & stack_switcher --------#
        stack = Gtk.Stack()
        stack.props.name = "workspaces-stack"
        stack.props.transition_type = Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        stack.props.transition_duration = 750
        self.stack = stack
        
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.props.no_show_all = True
        stack_switcher.props.homogeneous = False
        stack_switcher.props.halign = stack_switcher.props.valign = Gtk.Align.CENTER
        stack_switcher.props.stack = stack
        stack_switcher.set_size_request(-1, 24)
        stack_switcher.get_style_context().add_class("workspaces-switcher")
        self.stack_switcher = stack_switcher

        #-- construct --------#
        self.props.name = "workspaces-view"
        self.get_style_context().add_class(self.props.name)
        self.props.expand = True
        self.props.margin = 20
        self.props.column_spacing = 6
        self.connect("on-workspace-view-event", self.on_workspace_view_event)
        self.attach(stack, 0, 1, 1, 1)
        self.attach(stack_switcher, 0, 2, 1, 1)

    def on_workspace_view_event(self, view, workspaces_dict):
        self.update_workspaces_stack(self.stack, self.stack_switcher, workspaces_dict)

    def update_workspaces_stack(self, stack, stack_switcher, workspaces_dict):
        #print(locals())

        # delete all stack children if any
        if stack.get_children():
            for child in stack.get_children():
                stack.remove(child)

        # create new stacks for each workspace
        for workspace_number in workspaces_dict:
            #print(workspace_number)
            stack_name = "Workspace " + str(1 + workspace_number)
            stack_child = WorkspaceContainer(workspace_number, workspaces_dict[workspace_number])
            stack.add_named(stack_child, stack_name)

        stack.show_all()

        # Use icon instead for stack switcher
        for child in stack.get_children():
            stack.child_set_property(child, "icon-name", "user-offline")

        # add tooltip text to stack switcher buttons
        for child in stack_switcher.get_children():
            child.props.has_tooltip = True
            child_index = stack_switcher.get_children().index(child)
            child.props.tooltip_text = stack.get_children()[child_index].props.name

        if len(stack.get_children()) > 1:
            stack_switcher.show()
        
        

class WorkspaceContainer(Gtk.Grid):
    def __init__(self, workspace_number, workspace, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #print(workspace)
        workspace_name = "Workspace " + str(1 + workspace_number)

        #-- layout for placing AppContainer --------#
        layout = Gtk.Layout()
        layout.set_size_request(WORKSPACE_WIDTH, WORKSPACE_HEIGHT)

        flowbox = Gtk.FlowBox()
        flowbox.props.orientation = Gtk.Orientation.HORIZONTAL
        #flowbox.props.halign = Gtk.Align.CENTER
        
        flowbox.props.halign = flowbox.props.valign = Gtk.Align.CENTER
        flowbox.props.homogeneous = False
        flowbox.props.max_children_per_line = 8
        flowbox.props.min_children_per_line = 8
        flowbox.props.selection_mode = Gtk.SelectionMode.NONE

        # box_for_flowbox = Gtk.Box()
        # box_for_flowbox.props.halign = box_for_flowbox.props.valign = Gtk.Align.CENTER
        # box_for_flowbox.add(flowbox)

        for app_xid in workspace:
            print("Workspace:", workspace_number + 1, workspace[app_xid]["name"], workspace[app_xid]["app_pid"], workspace[app_xid]["app_id"], workspace[app_xid]["wnck_wm_class_name"], workspace[app_xid]["wnck_wm_class_group"], workspace[app_xid]["proc_state"])


        for app_xid in workspace:
            app = AppContainer(app_info=workspace[app_xid])
            flowbox.add(app)
        

        #-- workspace label --------#
        workspace_label = Gtk.Label(workspace_name)
        workspace_label.props.name = "workspace-name"

        #-- construct --------#
        self.props.name = workspace_name
        self.props.hexpand = True
        self.props.halign = self.props.valign = Gtk.Align.CENTER
        self.props.row_spacing = 20
        self.attach(flowbox, 0, 1, 1, 1)
        self.attach(WorkspaceArea(), 0, 1, 1, 1)
        self.attach(workspace_label, 0, 2, 1, 1)

class AppContainer(Gtk.Button):
    def __init__(self, 
                app_info,
                iconsize=Gtk.IconSize.DND, 
                *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app_info
        self.name = app_info["name"]
        self.icon_name = app_info["icon_name"]
        self.state = app_info["proc_state"]

        if self.icon_name.find("/") != -1:
            image = Gtk.Image().new_from_file(self.icon_name)
            new_pixbuf = image.props.pixbuf.scale_simple(32, 32, 2)
            image.props.pixbuf = new_pixbuf
        else:
            image = Gtk.Image().new_from_icon_name(self.icon_name, iconsize)
        
        self.props.name = self.name
        self.props.image = image
        self.props.always_show_image = True
        self.props.expand = False
        self.props.halign = self.props.valign = Gtk.Align.CENTER
        self.props.margin = 2
        
        tooltip_text = self.name + "\n" + "State:" + self.state
        self.props.has_tooltip = True
        self.props.tooltip_text = tooltip_text
        
        self.get_style_context().add_class("app-container")
        self.connect("clicked", self.on_app_clicked)
        # self.connect("map", self.on_realize)

        if self.state == "S":
            self.get_style_context().add_class("app-container-")


    def on_app_clicked(self, button):
        print("Clicked", self.props.name)

        self.app["gdk_window"].get_scale_factor()

        # monitor = Gdk.Display.get_primary_monitor(display)
        # scale = monitor.get_scale_factor()

        from gi.repository import GdkX11
        #GdkX11.X11Display.set_window_scale(self.app["gdk_window"].get_display(), 2)
        self.app["gdk_window"].get_display().set_window_scale(2)

    # def on_realize(self, *args):
    #     #print(locals())
    #     layout = self.get_parent()
    #     print("x:",layout.get_allocation().x, " y:", layout.get_allocation().y)
    #     #layout.move(self, 0, 0)
    #     print(self.props.name, "x:",self.get_allocation().x, " y:", self.get_allocation().y)


class WorkspaceArea(Gtk.Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        drawing_area = Gtk.DrawingArea()
        drawing_area.set_size_request(WORKSPACE_WIDTH, WORKSPACE_HEIGHT)
        drawing_area.props.expand = True
        drawing_area.props.halign = self.props.valign = Gtk.Align.FILL
        drawing_area.connect("draw", self.draw)

        self.props.name = "workspace-area"
        self.add(drawing_area)

    def draw(self, drawing_area, cairo_context):

        height = drawing_area.get_allocated_height()
        width = drawing_area.get_allocated_width()
        
        try:
            # clip mask
            Granite.DrawingUtilities.cairo_rounded_rectangle(cairo_context, 0, 0, width, height, WORKSPACE_RADIUS)
            cairo_context.clip()

            # workspace area
            COLOR = WORKSPACE_COLOR
            cairo_context.set_source_rgba(COLOR.red, COLOR.green, COLOR.blue, 0.1)
            Granite.DrawingUtilities.cairo_rounded_rectangle(cairo_context, 0, 0, width, height, WORKSPACE_RADIUS)
            cairo_context.fill()

            # border highlights
            COLOR = OVERLAY_COLOR
            cairo_context.set_source_rgba(COLOR.red, COLOR.green, COLOR.blue, 0.4)
            cairo_context.set_line_width(4)
            Granite.DrawingUtilities.cairo_rounded_rectangle(cairo_context, 0, 0, width, height, WORKSPACE_RADIUS)
            cairo_context.stroke()

            # wingpanel
            cairo_context.set_source_rgba(COLOR.red, COLOR.green, COLOR.blue, 0.4)
            cairo_context.rectangle (0, 0, width, PANEL_HEIGHT)
            cairo_context.fill()

            # plank
            Granite.DrawingUtilities.cairo_rounded_rectangle(cairo_context, (width - DOCK_WIDTH) / 2, height - DOCK_HEIGHT, DOCK_WIDTH, DOCK_HEIGHT + DOCK_RADIUS, DOCK_RADIUS)
            cairo_context.fill()

        except KeyboardInterrupt:
            # Alt-Tab causes map singal to fail somehow
            pass



