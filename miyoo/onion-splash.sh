#!/bin/sh
# Use the currently selected OnionOS theme's own boot/shutdown artwork.
# Optional visual integration for the Miyoo Custom slot build.
# Called synchronously at safe transition points by Slot, not on every frame.
# Do not replace Onion's runtime.sh, keymon, assets or system files.
set -u
ROOT=${SLOT_ROOT:-/mnt/SDCARD}
ONION="$ROOT/.tmp_update"
[ -f "$ONION/runtime.sh" ] || exit 0
[ -f "$ONION/config/.skip-custom-slot-splashes" ] && exit 0
case "${1:-}" in
    sleep|shutdown) screen=End_Save ;;
    wake)           screen=Boot ;;
    *)              exit 0 ;;
esac

# Onion normally exports this on boot; use an absolute binary as fallback.
# Its own 'bootScreen' renderer resolves the active theme and overlays the
# current theme's extra/bootScreen or extra/Screen_Off_Save assets.
if command -v bootScreen >/dev/null 2>&1; then
    bootScreen "$screen" >/dev/null 2>&1
elif [ -f "$ONION/bin/bootScreen" ]; then
    "$ONION/bin/bootScreen" "$screen" >/dev/null 2>&1
fi
exit 0
