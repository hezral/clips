#!/bin/sh
# Wrapper script to launch Clips with --no-a11y-bus for AT-SPI access
# This enables active window detection on Wayland

exec /app/bin/com.github.hezral.clips "$@"
