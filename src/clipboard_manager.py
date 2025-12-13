# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from datetime import datetime

from . import clips_supported
from .utils import log_function_calls

# Import display backend detection
from .display_backend import is_wayland


class ClipboardManager():

    events = []
    proceed = True

    # Wayland support
    wayland_monitor = None
    _wayland_clipboard_data = None  # Temp storage for Wayland clipboard data
    _clipboard = None  # Lazy-initialized clipboard
    _skip_clipboard_monitoring = False  # Flag to skip monitoring during copy operations

    @log_function_calls
    def __init__(self, gtk_application=None):
        super().__init__()

        self.app = gtk_application
        self.clips_supported = clips_supported

    @property
    def clipboard(self):
        """Lazy initialization of clipboard to ensure GDK display is ready."""
        if self._clipboard is None:
            # Get the default display
            display = Gdk.Display.get_default()
            if display is None:
                raise RuntimeError("No GDK display available - clipboard cannot be initialized")
            self._clipboard = Gtk.Clipboard.get_for_display(display, Gdk.SELECTION_CLIPBOARD)
        return self._clipboard

    @log_function_calls
    def get_settings(self, gio_settings_keyname):
        return self.app.gio_settings.get_value(gio_settings_keyname).get_strv()

    # =========================================================================
    # Wayland Clipboard Support
    # =========================================================================
    
    @log_function_calls
    def setup_wayland_monitoring(self, cache_manager_callback):
        """
        Setup Wayland clipboard monitoring.

        Args:
            cache_manager_callback: The cache_manager.update_cache method to call
        """
        if not is_wayland():
            return False

        # Try data-control protocol first (best option)
        try:
            from .clipboard_monitor_wayland import WaylandClipboardMonitor

            self.wayland_monitor = WaylandClipboardMonitor(self.app)

            if self.wayland_monitor.is_available():
                # Store callback for later
                self._cache_manager_callback = cache_manager_callback
                self.wayland_monitor.set_clipboard_callback(self._on_wayland_clipboard_change)
                self.wayland_monitor.start()
                self.app.logger.info("Wayland clipboard monitoring enabled (data-control protocol)")
                return True
            else:
                self.app.logger.info("Wayland data-control not available, trying wl-clipboard...")

        except Exception as e:
            self.app.logger.error(f"Failed to setup data-control monitoring: {e}")

        # Try DBus clipboard daemon (best fallback for compositors without data-control)
        try:
            from .clipboard_monitor_dbus import DBusClipboardMonitor

            self.wayland_monitor = DBusClipboardMonitor(self.app)

            if self.wayland_monitor.is_available():
                # Store callback for later
                self._cache_manager_callback = cache_manager_callback
                self.wayland_monitor.set_clipboard_callback(self._on_wayland_clipboard_change)
                self.wayland_monitor.start()
                self.app.logger.info("Wayland clipboard monitoring enabled (DBus daemon)")
                return True
            else:
                self.app.logger.info("DBus clipboard daemon not available")

        except Exception as e:
            self.app.logger.error(f"Failed to setup DBus monitoring: {e}")

        # Last resort: wl-clipboard polling (experimental, may cause interference)
        import os
        if os.environ.get('CLIPS_ENABLE_WL_CLIPBOARD_POLLING') == '1':
            try:
                from .clipboard_monitor_wlclipboard import WlClipboardMonitor

                self.wayland_monitor = WlClipboardMonitor(self.app)

                if self.wayland_monitor.is_available():
                    # Store callback for later
                    self._cache_manager_callback = cache_manager_callback
                    self.wayland_monitor.set_clipboard_callback(self._on_wayland_clipboard_change)
                    self.wayland_monitor.start()
                    self.app.logger.info("Wayland clipboard monitoring enabled (wl-clipboard polling - EXPERIMENTAL)")
                    return True
                else:
                    self.app.logger.warning("wl-clipboard not available")
                    return False

            except Exception as e:
                self.app.logger.error(f"Failed to setup wl-clipboard monitoring: {e}")
                return False
        else:
            self.app.logger.info(
                "No background clipboard monitoring available. "
                "Clipboard will only work when Clips window has focus."
            )
            return False
    
    @log_function_calls
    def stop_wayland_monitoring(self):
        """Stop Wayland clipboard monitoring."""
        if self.wayland_monitor:
            self.wayland_monitor.stop()
            self.wayland_monitor = None
    
    def _on_wayland_clipboard_change(self, mime_types: list, get_data_func):
        """
        Handle clipboard change from Wayland monitor.

        This method bridges Wayland clipboard data to the existing
        get_clipboard_contents() logic.
        """
        # Skip if we're currently performing a copy operation from Clips
        # This flag is set when user clicks the copy button in Clips
        if self._skip_clipboard_monitoring:
            self.app.logger.debug("Skipping clipboard processing - Clips is performing a copy operation")
            return

        # Skip if Clips window is currently focused (prevents interference with user interaction)
        # When window is active, user might be clicking buttons, selecting text, etc.
        # This is more reliable than checking active_app on Wayland
        if self.app.main_window and self.app.main_window.is_active():
            self.app.logger.debug("Skipping clipboard processing - Clips window is currently focused")
            return

        # Get source app info for metadata
        active_app, active_app_icon = self.app.utils.get_active_appinfo(app=self.app)
        self.app.logger.debug(f"Clipboard change detected from app: {active_app}")
        
        # Check excluded apps
        if active_app in self.get_settings("excluded-apps"):
            self.app.logger.debug(f"Clipboard from excluded app: {active_app}")
            return
        
        # Store the Wayland data getter for use in get_clipboard_contents
        self._wayland_mime_types = mime_types
        self._wayland_get_data = get_data_func
        
        # Process clipboard using existing logic
        clipboard_contents = self._get_wayland_clipboard_contents(active_app)
        
        if clipboard_contents is not None:
            target, content, thumbnail, file_extension, additional_desc, content_type, alt_content, alt_file_extension = clipboard_contents
            
            source_app = active_app
            source_icon = active_app_icon
            created = datetime.now()
            
            protected = "no"
            if self.app.gio_settings.get_value("protected-mode"):
                if source_app in self.get_settings("protected-apps"):
                    protected = "yes"
            
            # Return tuple matching what clipboard_changed() returns
            data_tuple = (target, content, source_app, source_icon, created, 
                         protected, thumbnail, file_extension, content_type, 
                         alt_content, alt_file_extension, additional_desc)
            
            # Call the cache manager callback directly
            if hasattr(self, '_cache_manager_callback'):
                self._cache_manager_callback(self.clipboard, None, self, _wayland_data=data_tuple)
    
    def _get_wayland_clipboard_contents(self, active_app):
        """
        Process Wayland clipboard using existing clips_supported logic.

        This mirrors get_clipboard_contents() but works with Wayland data.
        """
        # Import the appropriate SelectionData class based on which monitor is active
        SelectionDataClass = None
        for module_name, class_name in [
            ('clipboard_monitor_wayland', 'WaylandSelectionData'),
            ('clipboard_monitor_dbus', 'DBusClipboardSelectionData'),
            ('clipboard_monitor_wlclipboard', 'WlClipboardSelectionData'),
        ]:
            try:
                module = __import__(f'clips.{module_name}', fromlist=[class_name])
                SelectionDataClass = getattr(module, class_name)
                break
            except (ImportError, AttributeError):
                continue

        if SelectionDataClass is None:
            self.app.logger.error("No Wayland clipboard monitor available")
            return None
        
        clip_saved = False
        alt_target = None
        alt_content = None
        alt_file_extension = None
        
        mime_types = self._wayland_mime_types
        get_data = self._wayland_get_data
        
        # Convert available MIME types to Gdk.Atoms for comparison
        available_atoms = set()
        for mime in mime_types:
            available_atoms.add(mime)
        
        for supported_target in self.clips_supported.supported_targets:
            target_mime = supported_target[0]
            
            # Check if this supported target is available
            if target_mime not in available_atoms:
                continue
            
            if clip_saved:
                break
            
            proceed = True
            
            # Get the data for this MIME type
            data = get_data(target_mime)
            if data is None:
                continue

            # Create synthetic SelectionData
            content = SelectionDataClass(data, target_mime)
            
            file_extension = supported_target[1]
            additional_desc = supported_target[2]
            content_type = supported_target[3]
            thumbnail = supported_target[4]
            
            # Apply the same filtering logic as get_clipboard_contents
            
            # WPS/LibreOffice filtering
            if "WPS" in active_app and "WPS" not in supported_target[2]:
                proceed = False
            if "Libre" in active_app and "Libre" not in supported_target[2]:
                proceed = False
            
            # Content type detection for text
            if "text/plain" in target_mime or target_mime in ("UTF8_STRING", "STRING", "TEXT"):
                text = content.get_text()
                if text:
                    text = text.strip()
                    
                    # Color code detection
                    if "color" in content_type:
                        if self.app.utils.is_valid_color_code(text):
                            content_type = "color/" + self.app.utils.is_valid_color_code(text)[1]
                        else:
                            proceed = False
                    
                    # URL detection
                    elif "url" in content_type:
                        if self.app.utils.is_valid_url(text):
                            content_type = "url/" + text.split(":")[0]
                        else:
                            proceed = False
                    
                    # Email detection
                    elif "mail" in content_type:
                        if self.app.utils.is_valid_email(text):
                            content_type = "mail"
                        else:
                            proceed = False
                    
                    # Files detection
                    elif "files" in content_type:
                        lines = text.splitlines()
                        if lines:
                            last_line = lines[-1].replace("file://", "")
                            if self.app.utils.is_valid_unix_uri(last_line):
                                content_type = "files"
                            else:
                                proceed = False
            
            # HTML alt content
            if "text/html" in target_mime:
                alt_target = Gdk.Atom.intern('text/plain', False)
                alt_file_extension = "txt"
                # Try to get plain text version
                if 'text/plain' in available_atoms:
                    alt_data = get_data('text/plain')
                    if alt_data:
                        alt_content = SelectionDataClass(alt_data, 'text/plain')
            
            if proceed:
                # Handle thumbnail
                if thumbnail:
                    if content_type == "html":
                        thumbnail = True
                    elif 'image/png' in available_atoms:
                        png_data = get_data('image/png')
                        if png_data:
                            thumbnail = SelectionDataClass(png_data, 'image/png')
                        else:
                            thumbnail = None
                    else:
                        thumbnail = None
                else:
                    thumbnail = None
                
                target = Gdk.Atom.intern(target_mime, False)
                clip_saved = True
                
                self.app.logger.debug(
                    f"Wayland clipboard: target={target_mime}, type={content_type}"
                )
                
                return target, content, thumbnail, file_extension, additional_desc, content_type, alt_content, alt_file_extension
        
        return None

    # =========================================================================
    # Original X11 Methods (unchanged)
    # =========================================================================

    @log_function_calls
    def clipboard_changed(self, clipboard, event, _wayland_data=None):
        """
        Handle clipboard change events.
        
        For Wayland, _wayland_data contains pre-processed data from the monitor.
        For X11, this processes the GTK clipboard event normally.
        """
        # If we have Wayland data, return it directly
        if _wayland_data is not None:
            return _wayland_data
        
        self.app.logger.debug(f"clipboard_changed called with clipboard: {clipboard} and event: {event}")

        event_id = None  # Initialize event_id

        if event.reason is Gdk.OwnerChange.NEW_OWNER and event.owner is not None:
            event_id = 0

        if event.reason is Gdk.OwnerChange.NEW_OWNER and event.owner is None:
            event_id = 1

        if event.reason is Gdk.OwnerChange.DESTROY and event.owner is None:
            event_id = 1

        if event.reason is Gdk.OwnerChange.CLOSE and event.owner is None:
            event_id = 1

        self.app.logger.debug(f"Event: reason={event.reason}, owner={event.owner}, event_id={event_id}")

        if len(self.events) == 0 and event_id == 0:
            self.events.append(event_id)
            self.proceed = True
        elif len(self.events) == 1 and self.events[0] == 0 and event_id == 1:
            self.events.append(event_id)
            self.proceed = False
        elif len(self.events) == 2 and self.events[0] == 0 and self.events[1] == 1 and event_id == 0:
            self.events.append(event_id)
            self.proceed = False
        elif len(self.events) == 2 and self.events[0] == 0 and self.events[1] == 1 and event_id == 1:
            self.events.append(event_id)
            self.proceed = False
        elif len(self.events) == 3 and self.events[0] == 0 and self.events[1] == 1 and self.events[2] == 1 and event_id == 0:
            self.events = []
            self.proceed = True
        elif len(self.events) == 3 and self.events[0] == 0 and self.events[1] == 1 and self.events[2] == 0 and event_id == 0:
            self.events = []
            self.proceed = True

        self.app.logger.debug(f"Event tracking: events={self.events}, proceed={self.proceed}")

        # exclude apps
        active_app, active_app_icon = self.app.utils.get_active_appinfo(app=self.app)

        if active_app != "Clips":
            if active_app not in self.get_settings("excluded-apps"):
                if self.proceed:
                    created = datetime.now()
                    clipboard_contents = self.get_clipboard_contents(clipboard, event, active_app)
                    if clipboard_contents is not None:
                        target, content, thumbnail, file_extension, additional_desc, content_type, alt_content, alt_file_extension = clipboard_contents
                        source_app = active_app
                        source_icon = active_app_icon

                        protected = "no"
                        if self.app.gio_settings.get_value("protected-mode"):
                            if source_app in self.get_settings("protected-apps"):
                                protected = "yes"

                        self.app.logger.debug(f"clipboard event captured: {self.events}, {active_app}")
                        return target, content, source_app, source_icon, created, protected, thumbnail, file_extension, content_type, alt_content, alt_file_extension, additional_desc
            else:
                self.app.logger.debug(f"clipboard event ignored: {self.events}, {event_id}, {active_app}")
                pass

    @log_function_calls
    def get_clipboard_contents(self, clipboard, event, active_app):
        self.app.logger.debug(
            f"get_clipboard_contents called with clipboard: {clipboard}, event: {event}, and active_app: {active_app}"
        )
        
        clip_saved = False
        alt_target = None
        alt_content = None
        alt_file_extension = None

        for supported_target in self.clips_supported.supported_targets:   
            for target in clipboard.wait_for_targets()[1]:
                self.app.logger.debug(f"Processing target: {target}")
                if target not in self.clips_supported.excluded_targets and supported_target[0] in str(target) and clip_saved is False:
                    proceed = True

                    content = clipboard.wait_for_contents(target)
                    if content is not None:
                        self.app.logger.debug(f"Content retrieved for target: {target}, content: {content}")

                        file_extension = supported_target[1]
                        additional_desc = supported_target[2]
                        content_type = supported_target[3]
                        thumbnail = supported_target[4]

                        # only get the right target for these types
                        if "WPS" in active_app and not "WPS" in supported_target[2]:
                            proceed = False

                        if "Libre" in active_app and not "Libre" in supported_target[2]:
                            proceed = False

                        if "WPS Spreadsheets" in supported_target[2] or "LibreOffice Calc" in supported_target[2]:
                            target = Gdk.Atom.intern('text/html', False)

                        if "WPS Writer" in supported_target[2] or "LibreOffice Writer" in supported_target[2]:
                            target = Gdk.Atom.intern('text/rtf', False)

                        if "LibreOffice Impress" in supported_target[2]:
                            target = Gdk.Atom.intern('application/x-openoffice-embed-source-xml;windows_formatname="Star Embed Source (XML)"', False)

                        if "text/html" in supported_target[0]:
                            alt_target = Gdk.Atom.intern('text/plain', False)
                            alt_file_extension = "txt"

                        if "text/plain;charset=utf-8" in supported_target[0] and "color" in supported_target[3]:
                            if clipboard.wait_for_contents(target).get_text() is not None:
                                if self.app.utils.is_valid_color_code(clipboard.wait_for_contents(target).get_text().strip()):
                                    content_type = "color/" + self.app.utils.is_valid_color_code(content.get_text().strip())[1]
                                else:
                                    proceed = False

                        if ("text/plain;charset=utf-8" in supported_target[0] or "text/plain" in supported_target[0]) and "url" in supported_target[3]:
                            if clipboard.wait_for_contents(target).get_text() is not None:
                                if self.app.utils.is_valid_url(clipboard.wait_for_contents(target).get_text().strip()):
                                    content_type = "url/" + clipboard.wait_for_contents(target).get_text().split(":")[0]
                                else:
                                    proceed = False

                        if ("text/plain;charset=utf-8" in supported_target[0] or "text/plain" in supported_target[0]) and "mail" in supported_target[3]:
                            if clipboard.wait_for_contents(target).get_text() is not None:
                                if self.app.utils.is_valid_email(clipboard.wait_for_contents(target).get_text().strip()):
                                    content_type = "mail"
                                else:
                                    proceed = False

                        if ("text/plain;charset=utf-8" in supported_target[0] or "text/plain" in supported_target[0]) and "files" in supported_target[3]:
                            if clipboard.wait_for_contents(target).get_text() is not None:
                                if self.app.utils.is_valid_unix_uri(clipboard.wait_for_contents(target).get_text().strip().splitlines()[-1].replace("file://","")):
                                    content_type = "files"
                                else:
                                    proceed = False

                        if proceed:
                            if thumbnail:
                                if content_type == "html":
                                    thumbnail = True
                                else:
                                    thumbnail = clipboard.wait_for_contents(Gdk.Atom.intern('image/png', False))
                            else:
                                thumbnail = None

                            content = clipboard.wait_for_contents(target)

                            if alt_target is not None:
                                alt_content = clipboard.wait_for_contents(alt_target)

                            clip_saved = True

                            self.app.logger.debug(
                                f"Returning clipboard data: "
                                f"target={target}, "
                                f"content={content}, "
                                f"thumbnail={thumbnail}, "
                                f"file_extension={file_extension}, "
                                f"additional_desc={additional_desc}, "
                                f"content_type={content_type}, "
                                f"alt_content={alt_content}, "
                                f"alt_file_extension={alt_file_extension}"
                            )
                            return target, content, thumbnail, file_extension, additional_desc, content_type, alt_content, alt_file_extension