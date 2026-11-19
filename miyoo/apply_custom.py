#!/usr/bin/env python3
"""Generate the deterministic Miyoo customization against the PINNED ARMv7 port.

Each feature module is imported in a fixed order because several edit the
same Rust source. Exact-match and allowlist checks fail closed on drift.
This script does not alter the port, SD card, or any upstream repository.
"""
from importlib import import_module
from pathlib import Path
import sys

from custom.patcher import configure, changes

if len(sys.argv) != 5:
    raise SystemExit("usage: apply_custom.py PATCHED_SLOT_TREE OUTPUT_PATCH SLOT_VERSION CUSTOM_VERSION")

src = Path(sys.argv[1])
dest = Path(sys.argv[2])
slot_version, custom_version = sys.argv[3:]
if not slot_version or not custom_version.isdecimal():
    raise SystemExit("invalid Miyoo version values")
version_label = f"{slot_version} Ver. {custom_version}"
configure(src, version_label)

# Preserve the historical exact order. Later modules can safely replace
# source already amended by earlier ones; final diffs have one hunk per file.
for feature in (
    "emulators",
    "onion_power",
    "power_timing",
    "rendering",
    "idle",
    "scaling",
    "bezels",
    "ui",
):
    import_module(f"custom.{feature}")

# Invariants: preserve the port's renderer, physically measured brightness,
# keymon, OnionOS theme and boot integration. Only approved module paths may
# change, with an exact one-match replacement for every generated hunk.
allowed = {
    "crates/slot-store/src/core.rs",
    "crates/slot-store/src/slot_state.rs",
    "crates/slot-store/src/gb_palette.rs",
    "crates/slot/src/session.rs",
    "crates/slot/src/video_mode.rs",
    "crates/slot/src/app.rs",
    "crates/slot/src/persist.rs",
    "crates/slot/src/emu.rs",
    "crates/slot-ui/src/quick_menu.rs",
    "crates/slot-power/src/device.rs",
    "crates/slot-power/src/power.rs",
    "crates/slot-power/tests/device.rs",
    "crates/slot/src/frontend.rs",
    "crates/slot-input/src/gesture.rs",
    "crates/slot-input/src/raw.rs",
    "crates/slot/src/input/evdev.rs",
    "crates/slot/src/input/device.rs",
    "crates/slot-input/tests/gesture.rs",
}
if set(changes) != allowed:
    raise RuntimeError(f"rebuild source changed unexpected paths: {sorted(set(changes) ^ allowed)}")
# Ignore unified diff context; check only changed lines, not unchanged neighbors.
for path, diff in changes.items():
    for line in diff.splitlines():
        if not (line.startswith("+") or line.startswith("-")) or line.startswith(("+++", "---")):
            continue
        if any(term in line for term in (
            "SLOT_ONION_",
            "blue_light_gain", "onion_splash",
            "fn sleep(", "fn wake(", "fn doze(",
        )):
            raise RuntimeError(f"forbidden brightness/power patch in {path}: {line}")

parts = []
for path, diff in changes.items():
    parts.append(f"diff --git a/{path} b/{path}\n{diff}")
dest.write_text("".join(parts))
print(f"Miyoo {version_label}: {len(changes)} patched source files; unchanged CPU rendering and OS boot")
