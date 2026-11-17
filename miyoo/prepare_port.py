#!/usr/bin/env python3
"""Integrate Gambatte build in the pinned Miyoo port's Taskfile."""
from pathlib import Path
import sys

port = Path(sys.argv[1])
task = port / "taskfile.yml"
text = task.read_text()

def replace_once(old, new):
    global text
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"Taskfile anchor mismatch ({n} matches): {old!r}")
    text = text.replace(old, new, 1)

new_task = """  core:gambatte:
    desc: Build Gambatte for GB and GBC on Miyoo ARMv7
    deps: [image]
    status:
      - test -s vendor-miyoo/gambatte_libretro.so
    cmds:
      - mkdir -p third-party vendor-miyoo target-miyoo
      - test -s third-party/gambatte-src.tar.gz || curl -fsSL --retry 5 -o third-party/gambatte-src.tar.gz "https://github.com/libretro/gambatte-libretro/archive/77f2567d718b8973d02caa2daa8dce4953faf811.tar.gz"
      - task: sh
        vars:
          CMD: sh cores/gambatte/build-miyoo.sh third-party/gambatte-src.tar.gz vendor-miyoo/gambatte_libretro.so target-miyoo/gambatte
      - task: verify:arm
        vars: {FILE: vendor-miyoo/gambatte_libretro.so}

"""
replace_once("  shim:\n", new_task + "  shim:\n")
replace_once("      - task: core:mgba\n", "      - task: core:mgba\n      - task: core:gambatte\n")
replace_once("      - cp vendor-miyoo/gpsp_libretro.so vendor-miyoo/mgba_libretro.so {{.OUT}}/System/\n",
             "      - cp vendor-miyoo/gpsp_libretro.so vendor-miyoo/mgba_libretro.so vendor-miyoo/gambatte_libretro.so {{.OUT}}/System/\n")
replace_once("      - cp vendor-miyoo/gpsp_libretro.so.meta vendor-miyoo/mgba_libretro.so.meta {{.OUT}}/System/licenses/\n",
             "      - cp vendor-miyoo/gpsp_libretro.so.meta vendor-miyoo/mgba_libretro.so.meta {{.OUT}}/System/licenses/\n      - cp third-party/gambatte-src.tar.gz {{.OUT}}/System/licenses/\n")
replace_once('          echo "gpsp        {{.GPSP_COMMIT}}"\n',
             '          echo "gpsp        {{.GPSP_COMMIT}}"\n          echo "gambatte    77f2567d718b8973d02caa2daa8dce4953faf811"\n')
task.write_text(text)
(port / "cores/gambatte").mkdir(parents=True, exist_ok=True)

# Enable the non-destructive OnionOS theme bridge from both the optional
# autoboot hook and manual App/Slot launches. Stock/Allium are unaffected.
launch = port / "card/System/launch_frontend.sh"
body = launch.read_text()
needle = 'export SLOT_ROOT="$SD"\n'
if body.count(needle) != 1:
    raise RuntimeError("Miyoo launcher: unexpected SLOT_ROOT block")
body = body.replace(needle, needle + """
# Only for OnionOS: its own theme renderer supplies transitions. Do not
# replace Onion's runtime.sh or boot assets, and support user opt-out.
if [ -f "$SD/.tmp_update/onionVersion/version.txt" ] \\
    && [ -f "$SYS/onion-splash.sh" ]; then
    export SLOT_ONION_VISUALS=1
fi
""", 1)
# The Flip's 752x560 LCD is mounted upside-down; this is not true of the
# original Mini or Mini Plus (640x480). Dean's default forced rotation on all.
old_rotation = 'export SLOT_FB_ROTATE=180'
if body.count(old_rotation) != 1:
    raise RuntimeError("Miyoo launcher: expected Mini Flip rotation once")
body = body.replace(old_rotation, """# Only the 752x560 Flip needs 180-degree framebuffer rotation.
# Mini and Mini Plus should not inherit the Flip's panel orientation.
case "$(cat /sys/class/graphics/fb0/virtual_size 2>/dev/null)" in
    752,*) export SLOT_FB_ROTATE=180 ;;
    *)     export SLOT_FB_ROTATE=0 ;;
esac""", 1)

# Onion starts keymon BEFORE running custom startup hooks. Competing POWER
# handlers can freeze Slot mid-save or prevent the screen turning off.
# Let keymon manage POWER only while it actually runs; otherwise Slot retains
# its standard doze, wake and shutdown handling.
old_visuals = '    export SLOT_ONION_VISUALS=1\nfi'
if body.count(old_visuals) != 1:
    raise RuntimeError("Miyoo launcher: expected OnionOS visual block once")
body = body.replace(old_visuals, """    export SLOT_ONION_VISUALS=1
    if pgrep -x keymon >/dev/null 2>&1; then
        export SLOT_ONION_POWER_OWNER=1
    fi
fi""", 1)
# The Mini and Mini Plus should start with Onion's actual user brightness
# instead of Slot's independent level-5 default. Onion's keymon restores that
# brightness on wake, so starting at the same level avoids visible jumps.
old_keymon = '''    if pgrep -x keymon >/dev/null 2>&1; then
        export SLOT_ONION_POWER_OWNER=1
    fi'''
if body.count(old_keymon) != 1:
    raise RuntimeError("Miyoo launcher: cannot find Onion keymon block")
body = body.replace(old_keymon, '''    if [ -x /customer/app/jsonval ]; then
        onion_brightness=$(/customer/app/jsonval brightness 2>/dev/null)
        case "$onion_brightness" in
            0|1|2|3|4|5|6|7|8|9|10) export SLOT_ONION_BRIGHTNESS="$onion_brightness" ;;
        esac
    fi
    if pgrep -x keymon >/dev/null 2>&1; then
        export SLOT_ONION_POWER_OWNER=1
    fi''', 1)
launch.write_text(body)
print("Gambatte, per-device orientation, Onion power ownership and brightness sync registered")
