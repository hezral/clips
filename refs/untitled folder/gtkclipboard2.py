#!/usr/bin/env python3
# 

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

def test_clipboard():
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    targets = clipboard.wait_for_targets()
    print("Targets available:", ", ".join(map(str, targets)))
    for target in targets[1]:
        print("Trying '%s'..." % str(target))
        contents = clipboard.wait_for_contents(target)
        if contents:
            print(contents.data)

test_clipboard()

# def main():
#     mainloop = GLib.MainLoop()
#     def cb():
#         test_clipboard()
#         mainloop.quit()
#     GLib.idle_add(cb)
#     mainloop.run()

# if __name__ == "__main__":
#     main()