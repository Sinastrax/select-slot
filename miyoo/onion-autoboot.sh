#!/bin/sh
# Optional OnionOS 4.3+ autoboot hook for Custom slot on the Miyoo Mini.
# INSTALL MANUALLY: copy this file to:
#   /mnt/SDCARD/.tmp_update/startup/custom-slot.sh
# Do NOT replace .tmp_update/runtime.sh; that is OnionOS's own boot manager.
#
# Disable without touching OnionOS:
#   remove/rename .tmp_update/startup/custom-slot.sh
# Alternatively create .tmp_update/config/.skip-custom-slot-autoboot
#
# Onion's runtime runs startup scripts synchronously after LCD, audio and
# system initialization, before entering its own MainUI loop. Returning from
# Custom slot therefore gives control back to OnionOS.
ROOT=/mnt/SDCARD
[ -e "$ROOT/.tmp_update/config/.skip-custom-slot-autoboot" ] && exit 0
[ -s "$ROOT/System/slot" ] || exit 0
[ -f "$ROOT/System/launch_frontend.sh" ] || exit 0

# This uses the same launcher that App/Slot/launch.sh invokes, including
# its audioserver stop/restart and crash protection. Do not bypass it by
# invoking System/slot directly.
SLOT_ROOT="$ROOT" sh "$ROOT/System/launch_frontend.sh"

# On exit or crash, Onion's normal boot continues (safe fallback).
exit 0
