#!/bin/bash
# Check status of Clips clipboard daemon

echo "=== Clips Clipboard Daemon Status ==="
echo

# Check if DBus service is registered
echo "1. Checking DBus service registration..."
if dbus-send --session --print-reply \
    --dest=com.github.hezral.clips.Clipboard \
    /com/github/hezral/clips/Clipboard \
    com.github.hezral.clips.Clipboard.Ping 2>/dev/null | grep -q "boolean true"; then
    echo "   ✓ DBus service is RUNNING"
else
    echo "   ✗ DBus service is NOT running"
fi
echo

# Check process
echo "2. Checking process..."
if pgrep -f "clips_clipboard_daemon" > /dev/null; then
    echo "   ✓ Daemon process found:"
    ps aux | grep clips_clipboard_daemon | grep -v grep
else
    echo "   ✗ Daemon process NOT found"
fi
echo

# Check DBus service list
echo "3. Checking DBus service list..."
if busctl --user list 2>/dev/null | grep -q "com.github.hezral.clips.Clipboard"; then
    echo "   ✓ Service appears in busctl list"
    busctl --user list | grep clips
else
    echo "   ✗ Service does NOT appear in busctl list"
fi
echo

# Check wl-clipboard availability
echo "4. Checking wl-clipboard..."
if command -v wl-paste &> /dev/null; then
    echo "   ✓ wl-paste is available"
    wl-paste --version
else
    echo "   ✗ wl-paste is NOT available"
fi
echo

echo "=== End Status ==="
