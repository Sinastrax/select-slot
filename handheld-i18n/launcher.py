"""Select the saved UI language at launch and localize the H700 update splash."""
from pathlib import Path
import sys

path = Path(sys.argv[1])
source = path.read_text()
marker = '"$SYS/slot" > "$LOGS/slot.log"'
if source.count(marker) != 1:
    raise ValueError('Unknown device launcher')
line = next(line for line in source.splitlines() if marker in line)
selection = '''frontend="$SYS/slot"
if [ -r "$SD/Config/language.txt" ] && [ "$(cat "$SD/Config/language.txt")" = de ] && [ -s "$SYS/slot-de" ]; then
    frontend="$SYS/slot-de"
fi
'''
source = source.replace(line, selection + line.replace('"$SYS/slot"', '"$frontend"'))
if 'say() {' in source:
    source = source.replace('say() {', '''say() {
    if [ -r "$SD/Config/language.txt" ] && [ "$(cat "$SD/Config/language.txt")" = de ]; then
        case "$1" in
            "UPDATING SELECT. SLOT.") set -- "SLOT-UPDATE" ;;
            "UPDATE FAILED") set -- "UPDATE FEHLER" ;;
            "UPDATE COMPLETE") set -- "UPDATE FERTIG" ;;
            "INSTALLING BOOT LOGO") set -- "BOOTLOGO INSTALL" ;;
        esac
    fi''')
path.write_text(source)
