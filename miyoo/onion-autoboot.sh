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

# The standard OnionOS App launcher processes /tmp/.offOrder after an app
# exits. Optional autoboot runs earlier, in startup hooks, so it must hand off
# that marker itself instead of launching MainUI while shutdown is pending.
# Mirror OnionOS's check_off_order("End") without choosing or copying theme
# artwork: bootScreen resolves whichever theme the user selected.
if [ -f /tmp/.offOrder ]; then
    touch /tmp/shutting_down
    if command -v bootScreen >/dev/null 2>&1; then
        bootScreen End &
        sleep 1
    elif [ -x "$ROOT/.tmp_update/bin/bootScreen" ]; then
        "$ROOT/.tmp_update/bin/bootScreen" End &
        sleep 1
    fi
    shutdown
    exit 0
fi

# Normal exit or crash returns control to OnionOS.
exit 0
