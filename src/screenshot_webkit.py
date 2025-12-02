#!/usr/bin/env python3

import gi
import sys

gi.require_version('Gtk', '4.0')
gi.require_version('WebKit', '6.0')
from gi.repository import Gtk, Gdk, WebKit, GLib, Gio

class WebScreenshotter:
    def __init__(self, url, output_file):
        self.url = url
        self.output_file = output_file
        self.loop = GLib.MainLoop()
        
        self.window = Gtk.Window()
        self.window.set_default_size(1920, 1080)
        #self.window.set_opacity(0.0) 

        self.webview = WebKit.WebView()

        settings = self.webview.get_settings()
        settings.set_user_agent("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
        
        self.webview.connect("load-changed", self.on_load_changed)
        
        self.window.set_child(self.webview)
        self.window.present() 
        
        print(f"Loading {self.url}...")
        self.webview.load_uri(self.url)

        # --- NEW: Attributes for scrolling ---
        self.scroll_pos = 0
        self.scroll_step = 800 # How much to scroll each time (like a mouse wheel)
        self.max_scroll = 0
        # --- END NEW ---

    def on_load_changed(self, webview, load_event):
        """
        Called when the page load status changes.
        """
        if load_event == WebKit.LoadEvent.FINISHED:
            print("Page finished loading. Starting incremental scroll...")
            
            # Start the scroll loop by getting the page height
            self.webview.evaluate_javascript(
                "document.body.scrollHeight", -1, None, None, None,
                self.start_scroll_loop, None
            )

    def start_scroll_loop(self, webview, result, user_data):
        """
        NEW: Called after we get the page height.
        """
        try:
            # The JS result is a number, we need to get it
            js_result = webview.evaluate_javascript_finish(result)
            self.max_scroll = js_result.to_int32()
            print(f"Page height is: {self.max_scroll}px. Starting scroll...")
            
            # Start the Python-driven loop
            GLib.timeout_add(250, self.scroll_step_callback) # scroll every 200ms
            
        except GLib.Error as e:
            print(f"Error getting page height: {e}")
            self.loop.quit()

    def scroll_step_callback(self):
        """
        NEW: This function is called repeatedly by GLib.timeout_add.
        It scrolls one step and decides whether to continue.
        """
        self.scroll_pos += self.scroll_step
        
        if self.scroll_pos < self.max_scroll:
            # We still have more to scroll
            print(f"Scrolling to... {self.scroll_pos}px")
            self.webview.evaluate_javascript(
                f"window.scrollTo(0, {self.scroll_pos});",
                -1, None, None, None, None, None
            )
            return True # Tell GLib to call this function again
        else:
            # We've reached the bottom
            print("Finished scrolling. Waiting 5s for final images...")
            self.webview.evaluate_javascript(
                f"window.scrollTo(0, {self.max_scroll});",
                -1, None, None, None, None, None
            )
            # Wait 5 seconds for the last batch of images
            GLib.timeout_add(2000, self.take_snapshot)
            return False # Tell GLib to stop calling this

    def take_snapshot(self):
        """
        Take the snapshot of the webview.
        """
        print("Taking snapshot...")
        self.webview.get_snapshot(
            WebKit.SnapshotRegion.FULL_DOCUMENT,
            WebKit.SnapshotOptions.NONE,
            None,  # GCancellable
            self.on_snapshot_ready,
            None   # user_data
        )
        return False

    def on_snapshot_ready(self, webview, result, user_data):
        """
        Callback for when the snapshot is ready.
        """
        try:
            texture = webview.get_snapshot_finish(result)
            
            print(f"Saving screenshot to {self.output_file}...")
            success = texture.save_to_png(self.output_file)
            
            if success:
                print("Successfully saved screenshot!")
            else:
                print("Error: Failed to save snapshot.")
            
        except GLib.Error as e:
            print(f"Error taking snapshot: {e}")
            
        finally:
            self.window.close()
            self.loop.quit()

    def run(self):
        try:
            self.loop.run()
        except KeyboardInterrupt:
            print("\nProcess interrupted.")
            self.loop.quit()
            if self.window:
                self.window.close()


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <URL> <output.png>")
        sys.exit(1)
        
    url = sys.argv[1]
    output_file = sys.argv[2]
    
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    Gtk.init()
    app = WebScreenshotter(url, output_file)
    app.run()

if __name__ == "__main__":
    main()