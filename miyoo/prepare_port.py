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
launch.write_text(body)
print("Gambatte core and optional OnionOS visuals integration registered")
