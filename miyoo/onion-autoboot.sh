#!/bin/sh
# OnionOS 4.3+ autoboot hook for select. slot. on the Miyoo Mini family.
# Installed automatically by the *OnionOS Autoboot* SD-root ZIP at:
#   /mnt/SDCARD/.tmp_update/startup/select-slot.sh
# Do NOT replace .tmp_update/runtime.sh; that is OnionOS's own boot manager.
#
# Disable without touching OnionOS:
#   remove/rename .tmp_update/startup/select-slot.sh
# Alternatively create .tmp_update/config/.skip-custom-slot-autoboot
#
# OnionOS runs startup scripts synchronously after LCD, audio and
# system initialization, before entering its own MainUI loop. Returning from
# select. slot. therefore gives control back to OnionOS.
ROOT=/mnt/SDCARD
[ -e "$ROOT/.tmp_update/config/.skip-custom-slot-autoboot" ] && exit 0
[ -s "$ROOT/System/slot" ] || exit 0
[ -f "$ROOT/System/launch_frontend.sh" ] || exit 0

# This uses the same launcher that App/Slot/launch.sh invokes, including
# its audioserver stop/restart and crash protection. Do not bypass it by
# invoking System/slot directly.
SLOT_ROOT="$ROOT" sh "$ROOT/System/launch_frontend.sh"

# The shared launcher also handles OnionOS shutdown requests.
exit 0
