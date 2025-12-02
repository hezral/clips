#!/usr/bin/env python3
import sys
import gi
import datetime

gi.require_version("Gtk", "4.0")
gi.require_version("WebKit", "6.0")
from gi.repository import Gtk, GLib, WebKit, Gio

def main(url, out_basename="screenshot", width=1280, height=48, delay_ms=0):
    Gtk.init()

    win = Gtk.Window()
    win.set_default_size(width, height)

    webview = WebKit.WebView()
    win.set_child(webview)
    webview.set_size_request(width, height)

    loop = GLib.MainLoop()

    def take_snapshot():
        options = WebKit.SnapshotOptions.NONE

        def on_snapshot_ready(webview, result, user_data):
            try:
                pixbuf = webview.get_snapshot_finish(result)
            except Exception as e:
                print(f"Snapshot failed: {e}", file=sys.stderr)
                loop.quit()
                return

            if not pixbuf:
                print("No pixbuf returned from snapshot", file=sys.stderr)
                loop.quit()
                return

            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"{out_basename}-{timestamp}.png"
            pixbuf.save_to_png(filename)
            print(f"Saved screenshot to {filename}")
            loop.quit()

        # Correct signature: options, cancellable, callback, user_data
        #webview.get_snapshot(options, None, on_snapshot_ready, None)
        webview.get_snapshot(
            WebKit.SnapshotRegion.FULL_DOCUMENT,
            WebKit.SnapshotOptions.NONE,
            None,  # GCancellable
            on_snapshot_ready,
            None   # user_data
        )

    def on_load_changed(view, load_event):
        print("Load event:", load_event)  # debug
        if load_event == WebKit.LoadEvent.FINISHED:
            if delay_ms > 0:
                GLib.timeout_add(delay_ms, lambda: (take_snapshot() or False))
            else:
                take_snapshot()

    webview.connect("load-changed", on_load_changed)

    # Realize window so WebKit paints, then minimize immediately
    win.present()
    # win.minimize()

    webview.load_uri(url)
    loop.run()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: screenshot.py <url> [basename] [width height delay_ms]", file=sys.stderr)
        sys.exit(1)
    url = sys.argv[1]
    out_basename = sys.argv[2] if len(sys.argv) > 2 else "screenshot"
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1280
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 48
    delay_ms = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    main(url, out_basename, width, height, delay_ms)
