"""Preserve OnionOS's native shutdown while finishing Slot's launcher cleanup."""
from pathlib import Path
import sys

# Onion's shutdown command uses reboot on the original Mini (device 283).
# If POWER is still physically down, that Mini can boot straight back into Slot.
# detectKey samples the same input device as Onion's own key monitor.
AFTER_EXIT = '''if [ -f "$SD/.tmp_update/onionVersion/version.txt" ] && [ -f /tmp/.offOrder ]; then
    if [ "$status" -eq 0 ]; then
        rm -f "$guard"
    fi
    echo "launch: handing off to OnionOS shutdown (slot exit=$status)" >> "$LOGS/slot-launch.txt"
    onion_bin="$SD/.tmp_update/bin"
    detect_key="$onion_bin/detectKey"
    if [ "$(cat /tmp/deviceModel 2>/dev/null)" = 283 ] && [ -x "$detect_key" ]; then
        waited=0
        while [ "$waited" -lt 80 ] && "$detect_key" 116; do
            sleep 0.1
            waited=$((waited + 1))
        done
        echo "launch: POWER release wait: $waited checks" >> "$LOGS/slot-launch.txt"
    fi

    # Finish the request here while it is known to be pending. Onion's
    # bootScreen consumes .offOrder as part of drawing the End screen.
    if [ -f "$onion_bin/shutdown" ]; then
        touch /tmp/shutting_down
        # Match OnionOS's native check_off_order hooks for App launches too.
        find "$SD/.tmp_update/checkoff" -type f -name '*.sh' 2>/dev/null |
            while IFS= read -r hook; do
                sh "$hook"
            done
        if [ -x "$onion_bin/bootScreen" ]; then
            "$onion_bin/bootScreen" End &
            sleep 1
        fi
        boot_id="$(cat /proc/sys/kernel/random/boot_id 2>/dev/null || true)"
        echo "launch: invoking OnionOS shutdown (boot=${boot_id:-unknown})" >> "$LOGS/slot-launch.txt"
        sync
        # Use the SD card's Onion helper explicitly and run it as a shell
        # script, just like the startup hook, including on noexec mounts.
        shutdown_status=0
        sh "$onion_bin/shutdown" || shutdown_status=$?
        echo "launch: OnionOS shutdown unexpectedly returned ($shutdown_status)" >> "$LOGS/slot-launch.txt"
    else
        echo "launch: OnionOS shutdown helper missing" >> "$LOGS/slot-launch.txt"
    fi
fi
'''

def patch_launcher(path):
    source = path.read_text()
    old = 'kill "$sleeper" 2>/dev/null\n'
    if source.count(old) != 1:
        raise ValueError('Miyoo launch guard changed')
    # Wait at the end, after the existing audio return and sync have completed.
    if not source.endswith('sync\n'):
        raise ValueError('Miyoo launcher exit changed')
    path.write_text(source + '\n' + AFTER_EXIT)

if __name__ == '__main__':
    patch_launcher(Path(sys.argv[1]))
