# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2021 Adi Hezral <hezral@gmail.com>

"""
Wayland clipboard monitor using wlr-data-control / ext-data-control protocol.

This provides background clipboard monitoring on Wayland without requiring window focus.
GTK's Gtk.Clipboard "owner-change" signal doesn't fire reliably on Wayland when the
app doesn't have focus - this module solves that limitation.

The monitor receives clipboard data and creates a synthetic GTK SelectionData-like
object that can be processed by the existing clipboard_manager.py code.
"""

import os
import socket
import struct
import select
import threading
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import GLib, Gdk


# =============================================================================
# Wayland Wire Protocol Helpers
# =============================================================================

class WaylandMessage:
    """Wayland message header encoding/decoding."""
    HEADER_FORMAT = "II"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    
    @staticmethod
    def pack_header(object_id: int, opcode: int, size: int) -> bytes:
        size_opcode = (size << 16) | opcode
        return struct.pack(WaylandMessage.HEADER_FORMAT, object_id, size_opcode)
    
    @staticmethod
    def unpack_header(data: bytes) -> Tuple[int, int, int]:
        object_id, size_opcode = struct.unpack(WaylandMessage.HEADER_FORMAT, data)
        return object_id, size_opcode & 0xFFFF, size_opcode >> 16


class WaylandArg:
    """Wayland argument encoding/decoding."""
    
    @staticmethod
    def uint(value: int) -> bytes:
        return struct.pack("I", value)
    
    @staticmethod
    def string(value: str) -> bytes:
        if value is None:
            return struct.pack("I", 0)
        encoded = value.encode('utf-8') + b'\x00'
        length = len(encoded)
        padded = (length + 3) & ~3
        return struct.pack("I", length) + encoded + b'\x00' * (padded - length)
    
    @staticmethod
    def read_uint(data: bytes, offset: int) -> Tuple[int, int]:
        return struct.unpack_from("I", data, offset)[0], offset + 4
    
    @staticmethod
    def read_string(data: bytes, offset: int) -> Tuple[str, int]:
        length = struct.unpack_from("I", data, offset)[0]
        offset += 4
        if length == 0:
            return "", offset
        string = data[offset:offset + length - 1].decode('utf-8')
        return string, offset + ((length + 3) & ~3)


# Protocol constants
WL_DISPLAY_SYNC = 0
WL_DISPLAY_GET_REGISTRY = 1
WL_REGISTRY_BIND = 0
WL_REGISTRY_GLOBAL = 0
DCM_GET_DATA_DEVICE = 1
DCD_DATA_OFFER = 0
DCD_SELECTION = 1
DCD_FINISHED = 2
DCO_RECEIVE = 0
DCO_DESTROY = 1
DCO_OFFER = 0


@dataclass
class WlObject:
    id: int
    interface: str
    version: int = 1


@dataclass 
class DataOffer:
    id: int
    mime_types: List[str] = field(default_factory=list)


# =============================================================================
# Synthetic SelectionData for clipboard_manager.py compatibility
# =============================================================================

class WaylandSelectionData:
    """
    Mimics Gtk.SelectionData interface for Wayland clipboard data.
    
    This allows clipboard_manager.py to process Wayland clipboard data
    using the same code path as X11.
    """
    
    def __init__(self, data: bytes, mime_type: str):
        self._data = data
        self._mime_type = mime_type
    
    def get_data(self) -> bytes:
        return self._data
    
    def get_text(self) -> Optional[str]:
        if self._data is None:
            return None
        try:
            return self._data.decode('utf-8')
        except:
            return None
    
    def get_data_type(self) -> str:
        return self._mime_type


# =============================================================================
# Wayland Connection Manager
# =============================================================================

class WaylandConnection:
    """Manages the Wayland Unix socket connection."""
    
    def __init__(self):
        self.socket: Optional[socket.socket] = None
        self.objects: Dict[int, WlObject] = {}
        self.next_id = 2
        self.recv_buffer = bytearray()
        self.fds_buffer: List[int] = []
    
    def connect(self) -> bool:
        display = os.environ.get('WAYLAND_DISPLAY', 'wayland-0')
        runtime_dir = os.environ.get('XDG_RUNTIME_DIR', '')
        
        if not runtime_dir:
            return False
            
        socket_path = os.path.join(runtime_dir, display) if not display.startswith('/') else display
        
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect(socket_path)
            self.socket.setblocking(False)
            self.objects[1] = WlObject(1, 'wl_display', 1)
            return True
        except Exception:
            return False
    
    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
    
    def alloc_id(self) -> int:
        obj_id = self.next_id
        self.next_id += 1
        return obj_id
    
    def send(self, object_id: int, opcode: int, payload: bytes = b'', fds: List[int] = None):
        size = WaylandMessage.HEADER_SIZE + len(payload)
        msg = WaylandMessage.pack_header(object_id, opcode, size) + payload
        
        if fds:
            ancdata = [(socket.SOL_SOCKET, socket.SCM_RIGHTS, struct.pack(f'{len(fds)}i', *fds))]
            self.socket.sendmsg([msg], ancdata)
        else:
            self.socket.send(msg)
    
    def recv(self, timeout: float = 0.1) -> List[Tuple[int, int, bytes, List[int]]]:
        messages = []
        
        try:
            readable, _, _ = select.select([self.socket], [], [], timeout)
        except (ValueError, OSError):
            return messages
            
        if not readable:
            return messages
        
        try:
            data, ancdata, _, _ = self.socket.recvmsg(4096, socket.CMSG_SPACE(64))
            if not data:
                return messages
            
            for cmsg_level, cmsg_type, cmsg_data in ancdata:
                if cmsg_level == socket.SOL_SOCKET and cmsg_type == socket.SCM_RIGHTS:
                    num_fds = len(cmsg_data) // 4
                    self.fds_buffer.extend(struct.unpack(f'{num_fds}i', cmsg_data))
            
            self.recv_buffer.extend(data)
            
            while len(self.recv_buffer) >= WaylandMessage.HEADER_SIZE:
                obj_id, opcode, size = WaylandMessage.unpack_header(
                    bytes(self.recv_buffer[:WaylandMessage.HEADER_SIZE])
                )
                if len(self.recv_buffer) < size:
                    break
                
                payload = bytes(self.recv_buffer[WaylandMessage.HEADER_SIZE:size])
                del self.recv_buffer[:size]
                
                msg_fds = self.fds_buffer.copy()
                self.fds_buffer.clear()
                messages.append((obj_id, opcode, payload, msg_fds))
                
        except BlockingIOError:
            pass
        except Exception:
            pass
        
        return messages


# =============================================================================
# Wayland Clipboard Monitor
# =============================================================================

class WaylandClipboardMonitor:
    """
    Background clipboard monitor for Wayland using data-control protocol.
    
    Integrates with existing clipboard_manager.py by providing data in a
    compatible format.
    """
    
    def __init__(self, gtk_application):
        self.app = gtk_application
        self.conn = WaylandConnection()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        # Protocol state
        self.registry_id: Optional[int] = None
        self.seat_id: Optional[int] = None
        self.manager_id: Optional[int] = None
        self.device_id: Optional[int] = None
        self.manager_interface = ""
        self.using_ext = False
        
        # State
        self.globals: Dict[int, Tuple[str, int]] = {}
        self.current_offer: Optional[DataOffer] = None
        self.pending_offer: Optional[DataOffer] = None
        
        # Callback
        self._on_clipboard_change: Optional[Callable] = None
    
    def set_clipboard_callback(self, callback: Callable):
        """
        Set callback for clipboard changes.
        
        Callback signature: callback(mime_types: List[str], get_data_func: Callable)
        """
        self._on_clipboard_change = callback
    
    def is_available(self) -> bool:
        """Check if Wayland data-control protocol is available."""
        if not os.environ.get('WAYLAND_DISPLAY'):
            return False
        
        if not self.conn.connect():
            return False
        
        self.registry_id = self.conn.alloc_id()
        self.conn.objects[self.registry_id] = WlObject(self.registry_id, 'wl_registry')
        self.conn.send(1, WL_DISPLAY_GET_REGISTRY, WaylandArg.uint(self.registry_id))
        
        self._roundtrip()
        
        has_manager = any(
            iface in ('zwlr_data_control_manager_v1', 'ext_data_control_manager_v1')
            for iface, _ in self.globals.values()
        )
        
        if not has_manager:
            self.conn.disconnect()
            self.app.logger.warning(
                "Wayland compositor does not support data-control protocol. "
                "Background clipboard monitoring unavailable."
            )
            return False
        
        self.app.logger.info("Wayland data-control protocol available")
        return True
    
    def start(self):
        """Start clipboard monitoring."""
        if self._running:
            return
        
        if not self.conn.socket:
            if not self.is_available():
                raise RuntimeError("Wayland data-control not available")
        
        if not self._bind_globals():
            raise RuntimeError("Failed to bind Wayland globals")
        
        self._running = True
        self._thread = threading.Thread(
            target=self._monitor_loop, 
            daemon=True, 
            name="clips-wayland-clipboard"
        )
        self._thread.start()
        
        self.app.logger.info(f"Wayland clipboard monitor started ({self.manager_interface})")
    
    def stop(self):
        """Stop clipboard monitoring."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        self.conn.disconnect()
        self.app.logger.info("Wayland clipboard monitor stopped")
    
    def _roundtrip(self):
        """Perform a Wayland roundtrip."""
        sync_id = self.conn.alloc_id()
        self.conn.objects[sync_id] = WlObject(sync_id, 'wl_callback')
        self.conn.send(1, WL_DISPLAY_SYNC, WaylandArg.uint(sync_id))
        
        done = False
        while not done:
            for obj_id, opcode, payload, fds in self.conn.recv(timeout=1.0):
                self._handle_event(obj_id, opcode, payload, fds)
                if obj_id == sync_id:
                    done = True
                    if sync_id in self.conn.objects:
                        del self.conn.objects[sync_id]
    
    def _bind_globals(self) -> bool:
        """Bind to required Wayland globals."""
        # Find seat
        seat_name = None
        for name, (iface, ver) in self.globals.items():
            if iface == 'wl_seat':
                seat_name = name
                break
        
        if seat_name is None:
            return False
        
        # Bind seat
        self.seat_id = self.conn.alloc_id()
        self.conn.objects[self.seat_id] = WlObject(self.seat_id, 'wl_seat')
        payload = (WaylandArg.uint(seat_name) + WaylandArg.string('wl_seat') +
                   WaylandArg.uint(1) + WaylandArg.uint(self.seat_id))
        self.conn.send(self.registry_id, WL_REGISTRY_BIND, payload)
        
        # Find manager (prefer ext over zwlr)
        manager_name = None
        for name, (iface, ver) in self.globals.items():
            if iface == 'ext_data_control_manager_v1':
                manager_name = name
                self.manager_interface = iface
                self.using_ext = True
                break
        
        if manager_name is None:
            for name, (iface, ver) in self.globals.items():
                if iface == 'zwlr_data_control_manager_v1':
                    manager_name = name
                    self.manager_interface = iface
                    self.using_ext = False
                    break
        
        if manager_name is None:
            return False
        
        # Bind manager
        self.manager_id = self.conn.alloc_id()
        self.conn.objects[self.manager_id] = WlObject(self.manager_id, self.manager_interface)
        payload = (WaylandArg.uint(manager_name) + WaylandArg.string(self.manager_interface) +
                   WaylandArg.uint(1) + WaylandArg.uint(self.manager_id))
        self.conn.send(self.registry_id, WL_REGISTRY_BIND, payload)
        
        # Create data device
        self.device_id = self.conn.alloc_id()
        device_iface = 'ext_data_control_device_v1' if self.using_ext else 'zwlr_data_control_device_v1'
        self.conn.objects[self.device_id] = WlObject(self.device_id, device_iface)
        payload = WaylandArg.uint(self.device_id) + WaylandArg.uint(self.seat_id)
        self.conn.send(self.manager_id, DCM_GET_DATA_DEVICE, payload)
        
        self._roundtrip()
        return True
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                for obj_id, opcode, payload, fds in self.conn.recv(timeout=0.5):
                    self._handle_event(obj_id, opcode, payload, fds)
            except Exception as e:
                if self._running:
                    self.app.logger.error(f"Wayland monitor error: {e}")
    
    def _handle_event(self, obj_id: int, opcode: int, payload: bytes, fds: List[int]):
        """Handle Wayland events."""
        obj = self.conn.objects.get(obj_id)
        if not obj:
            return
        
        if obj.interface == 'wl_registry' and opcode == WL_REGISTRY_GLOBAL:
            offset = 0
            name, offset = WaylandArg.read_uint(payload, offset)
            iface, offset = WaylandArg.read_string(payload, offset)
            ver, _ = WaylandArg.read_uint(payload, offset)
            self.globals[name] = (iface, ver)
        
        elif obj.interface in ('zwlr_data_control_device_v1', 'ext_data_control_device_v1'):
            if opcode == DCD_DATA_OFFER:
                new_id, _ = WaylandArg.read_uint(payload, 0)
                offer_iface = 'ext_data_control_offer_v1' if self.using_ext else 'zwlr_data_control_offer_v1'
                self.conn.objects[new_id] = WlObject(new_id, offer_iface)
                self.pending_offer = DataOffer(id=new_id)
            
            elif opcode == DCD_SELECTION:
                offer_id, _ = WaylandArg.read_uint(payload, 0)
                
                if self.current_offer:
                    self._destroy_offer(self.current_offer.id)
                
                if offer_id and self.pending_offer and self.pending_offer.id == offer_id:
                    self.current_offer = self.pending_offer
                    self.pending_offer = None
                    self._process_clipboard_change()
                else:
                    self.current_offer = None
            
            elif opcode == DCD_FINISHED:
                self.app.logger.warning("Wayland data control device finished")
                self._running = False
        
        elif obj.interface in ('zwlr_data_control_offer_v1', 'ext_data_control_offer_v1'):
            if opcode == DCO_OFFER:
                mime_type, _ = WaylandArg.read_string(payload, 0)
                if self.pending_offer and self.pending_offer.id == obj_id:
                    self.pending_offer.mime_types.append(mime_type)
    
    def _destroy_offer(self, offer_id: int):
        if offer_id in self.conn.objects:
            self.conn.send(offer_id, DCO_DESTROY)
            del self.conn.objects[offer_id]
    
    def _process_clipboard_change(self):
        """Process clipboard change and notify callback."""
        if not self.current_offer or not self.current_offer.mime_types:
            return
        
        offer = self.current_offer
        self.app.logger.debug(f"Wayland clipboard: {offer.mime_types}")
        
        if self._on_clipboard_change:
            # Create a data getter function
            def get_data(mime_type: str) -> Optional[bytes]:
                return self._receive_data(offer.id, mime_type)
            
            GLib.idle_add(
                self._on_clipboard_change,
                offer.mime_types.copy(),
                get_data
            )
    
    def _receive_data(self, offer_id: int, mime_type: str) -> Optional[bytes]:
        """Receive data from offer."""
        if offer_id not in self.conn.objects:
            return None
        
        read_fd, write_fd = os.pipe()
        
        try:
            payload = WaylandArg.string(mime_type)
            self.conn.send(offer_id, DCO_RECEIVE, payload, fds=[write_fd])
            os.close(write_fd)
            write_fd = -1
            
            self._roundtrip()
            
            chunks = []
            max_size = 50 * 1024 * 1024
            total = 0
            
            while True:
                readable, _, _ = select.select([read_fd], [], [], 2.0)
                if not readable:
                    break
                chunk = os.read(read_fd, 65536)
                if not chunk:
                    break
                chunks.append(chunk)
                total += len(chunk)
                if total > max_size:
                    return None
            
            return b''.join(chunks) if chunks else None
            
        except Exception:
            return None
        finally:
            if write_fd != -1:
                try:
                    os.close(write_fd)
                except:
                    pass
            try:
                os.close(read_fd)
            except:
                pass
    
    def get_selection_data(self, mime_type: str, data: bytes) -> WaylandSelectionData:
        """Create a SelectionData-compatible object."""
        return WaylandSelectionData(data, mime_type)
    
    def convert_to_gdk_atom(self, mime_type: str) -> Gdk.Atom:
        """Convert MIME type string to Gdk.Atom."""
        return Gdk.Atom.intern(mime_type, False)
