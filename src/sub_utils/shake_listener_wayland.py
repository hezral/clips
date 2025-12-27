import os
import sys
import logging
from datetime import datetime
import gi
gi.require_version('Gio', '2.0')
gi.require_version('GLib', '2.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, GLib, Gtk

try:
    from snegg import ei
    from snegg.c.libei import libei
    SNEGG_AVAILABLE = True
except ImportError:
    SNEGG_AVAILABLE = False

# Setup basic logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ShakeDetectionWayland:
    def __init__(self, velocity_threshold=5, min_reversals=4, time_window=1.0):
        self.VELOCITY_THRESHOLD = velocity_threshold
        self.MIN_REVERSALS = min_reversals
        self.TIME_WINDOW = time_window
        
        self.reversals = []
        self.last_x_dir = 0
        self.last_y_dir = 0
        self.last_time = datetime.now()
        
        # Absolute motion state
        self.last_abs_x = None
        self.last_abs_y = None

    def process_motion(self, dx, dy):
        now = datetime.now()
        
        # Filter old reversals
        self.reversals = [t for t in self.reversals if (now - t).total_seconds() < self.TIME_WINDOW]

        # Velocity filter
        velocity = (dx**2 + dy**2)**0.5
        if velocity < self.VELOCITY_THRESHOLD:
            return False

        # Direction detection
        current_x_dir = 1 if dx > 0 else (-1 if dx < 0 else 0)
        current_y_dir = 1 if dy > 0 else (-1 if dy < 0 else 0)

        # Check for reversals (X or Y)
        reversed_x = (self.last_x_dir != 0 and current_x_dir != 0 and self.last_x_dir != current_x_dir)
        reversed_y = (self.last_y_dir != 0 and current_y_dir != 0 and self.last_y_dir != current_y_dir)

        if reversed_x or reversed_y:
            self.reversals.append(now)
            logger.info(f"!! REVERSAL !! ({len(self.reversals)}/{self.MIN_REVERSALS}) dx={dx:.1f}, dy={dy:.1f}")
            if len(self.reversals) >= self.MIN_REVERSALS:
                logger.info("SHAKE DETECTED!")
                self.reversals = []
                return True

        if current_x_dir != 0: self.last_x_dir = current_x_dir
        if current_y_dir != 0: self.last_y_dir = current_y_dir
        
        return False

    def process_absolute_motion(self, x, y):
        if self.last_abs_x is None:
            self.last_abs_x, self.last_abs_y = x, y
            return False
        
        dx = x - self.last_abs_x
        dy = y - self.last_abs_y
        self.last_abs_x, self.last_abs_y = x, y
        
        return self.process_motion(dx, dy)

def setup_mutter_session():
    try:
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        
        # 1. Create session
        res = bus.call_sync(
            "org.gnome.Mutter.RemoteDesktop",
            "/org/gnome/Mutter/RemoteDesktop",
            "org.gnome.Mutter.RemoteDesktop",
            "CreateSession",
            None,
            GLib.VariantType.new("(o)"),
            Gio.DBusCallFlags.NONE,
            -1,
            None
        )
        session_path = res.unpack()[0]
        logger.debug(f"Created session at {session_path}")

        # 2. Start session
        # Now re-enabled since we have an event loop handler ready
        bus.call_sync(
            "org.gnome.Mutter.RemoteDesktop",
            session_path,
            "org.gnome.Mutter.RemoteDesktop.Session",
            "Start",
            None,
            None,
            Gio.DBusCallFlags.NONE,
            -1,
            None
        )
        logger.debug("Session started")

        # 3. Connect to EIS (Emulated Input Server)
        v_args = GLib.Variant("(a{sv})", [{}])
        reply, fd_list = bus.call_with_unix_fd_list_sync(
            "org.gnome.Mutter.RemoteDesktop",
            session_path,
            "org.gnome.Mutter.RemoteDesktop.Session",
            "ConnectToEIS",
            v_args,
            GLib.VariantType.new("(h)"),
            Gio.DBusCallFlags.NONE,
            -1,
            None,
            None
        )
        
        handle = reply.get_child_value(0).get_handle()
        fd = fd_list.get(handle)
        logger.info(f"Successfully connected to EIS. Received FD: {fd}")
        
        return bus, session_path, fd

    except Exception as e:
        logger.error(f"Failed to setup Mutter session: {e}")
        return None, None, -1

class HelloWorldWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Hello World")
        self.set_default_size(200, 100)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        label = Gtk.Label(label="Shake Detected! Hello World!")
        self.add(label)
        self.show_all()
        
        GLib.timeout_add_seconds(3, self.destroy)

def show_hello_world():
    HelloWorldWindow()
    return False 

def main():
    detector = ShakeDetectionWayland()
    bus, session_path, fd = setup_mutter_session()
    
    if not session_path or fd == -1:
        print("Mutter RemoteDesktop/EIS session failed. Are you on GNOME/Mutter Wayland?")
        sys.exit(1)

    if not SNEGG_AVAILABLE:
        print("snegg library not found. Real-time capture is unavailable.")
        sys.exit(1)

    print("\n" + "!" * 60)
    print("!!! REAL-TIME SHAKE LISTENER ACTIVE !!!")
    print("Move your mouse/trackpad rapidly to test.")
    print("Desktop remains responsive via snegg/libei async loop.")
    print("!" * 60 + "\n")

    # Initialize snegg Receiver
    # snegg expects an object with a fileno() method
    class FDWrapper:
        def __init__(self, fd): self._fd = fd
        def fileno(self): return self._fd
    
    ctx = ei.Receiver.create_for_fd(FDWrapper(fd))

    def handle_ei_events(fd_source, condition):
        ctx.dispatch()
        for e in ctx.events:
            raw_type = libei.event_get_type(e._cobject)
            try:
                etype = e.event_type
                logger.debug(f"Event: {etype.name} ({raw_type})")
            except ValueError:
                logger.debug(f"Unknown Event type: {raw_type}")
                continue

            if etype == ei.EventType.SEAT_ADDED:
                logger.debug(f"Seat added: {e.seat.name}")
            
            elif etype == ei.EventType.DEVICE_ADDED:
                logger.debug(f"Device added: {e.device.name}")
            
            elif etype == ei.EventType.DEVICE_RESUMED:
                logger.debug(f"Device resumed: {e.device.name}. Ready for events.")
            
            elif etype == ei.EventType.POINTER_MOTION:
                dx = e.pointer_event.dx
                dy = e.pointer_event.dy
                # logger.debug(f"!! POINTER MOTION !! dx={dx}, dy={dy}")
                if detector.process_motion(dx, dy):
                    GLib.idle_add(show_hello_world)
            
            elif etype == ei.EventType.POINTER_MOTION_ABSOLUTE:
                x = e.pointer_absolute_event.x
                y = e.pointer_absolute_event.y
                # logger.debug(f"!! ABSOLUTE MOTION !! x={x}, y={y}")
                if detector.process_absolute_motion(x, y):
                    GLib.idle_add(show_hello_world)
            
            else:
                if etype not in [ei.EventType.CONNECT, ei.EventType.SEAT_ADDED, ei.EventType.DEVICE_ADDED, ei.EventType.DEVICE_RESUMED]:
                    logger.debug(f"Unhandled Event: {etype.name}")
        return True

    # Register the EIS FD with the GLib main loop
    GLib.io_add_watch(ctx.fd, GLib.IOCondition.IN, handle_ei_events)

    def cleanup():
        print("Cleaning up Mutter session...")
        if bus and session_path:
            try:
                bus.call_sync(
                    "org.gnome.Mutter.RemoteDesktop",
                    session_path,
                    "org.gnome.Mutter.RemoteDesktop.Session",
                    "Stop",
                    None,
                    None,
                    Gio.DBusCallFlags.NONE,
                    -1,
                    None
                )
                logger.debug("Session stopped")
            except Exception as e:
                logger.debug(f"Stop() error: {e}")
        Gtk.main_quit()

    try:
        Gtk.main()
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()

