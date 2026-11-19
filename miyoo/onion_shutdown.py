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
    detect_key="$SD/.tmp_update/bin/detectKey"
    if [ "$(cat /tmp/deviceModel 2>/dev/null)" = 283 ] && [ -x "$detect_key" ]; then
        waited=0
        while [ "$waited" -lt 80 ] && "$detect_key" 116; do
            sleep 0.1
            waited=$((waited + 1))
        done
        echo "launch: POWER release wait: $waited checks" >> "$LOGS/slot-launch.txt"
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
