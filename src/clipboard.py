#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib

def on_text_received(clipboard, text, user_data):
    """
    Callback function executed AFTER the text is received.
    """
    if text:
        print(f"--- Clipboard Changed ---\n{text}\n---------------------------\n")
    else:
        print("--- Clipboard Changed (now empty or non-text) ---")

def on_owner_change(clipboard, event, user_data):
    """
    Callback function executed when the clipboard ownership changes
    (i.e., something new is copied).
    """
    print("Change detected! Requesting new content...")
    
    # Asynchronously request the clipboard content as text.
    # When the text is ready, 'on_text_received' will be called.
    clipboard.request_text(on_text_received, None)

def main():
    # Get the default clipboard (for Ctrl+C/Ctrl+V)
    # Gdk.SELECTION_PRIMARY is for middle-click paste
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    # Connect our function to the 'owner-change' signal.
    # This fires when a new application takes ownership of the clipboard.
    clipboard.connect('owner-change', on_owner_change, None)
    
    print("Monitoring clipboard (GTK3) for changes... Press Ctrl+C to stop.")

    # Start the Gtk main loop to listen for events
    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("\nStopping monitor.")
        Gtk.main_quit()

if __name__ == "__main__":
    main()