#!/usr/bin/env bash
# Build the Miyoo variant from dean marano's pinned ARMv7 port.
# Run from any directory: bash miyoo/build.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$ROOT/.build/miyoo"
PORT="$WORK/slot-miyoo"
STAGE="$PORT/release/stage"
PORT_COMMIT="d096bdb87f25f3aba62de6b40ef859b61d841e43"
SLOT_VERSION="1.8.1"
CUSTOM_VERSION="9"
ZIP="$WORK/custom-slot-$SLOT_VERSION-ver$CUSTOM_VERSION-miyoo.zip"

for command in git task docker zip unzip python3 file; do
  command -v "$command" >/dev/null || { echo "Missing build dependency: $command" >&2; exit 1; }
done

mkdir -p "$WORK"
if [ -e "$PORT" ]; then
  echo "Refusing to replace existing source checkout: $PORT" >&2
  echo "Remove that directory if you want a fresh build." >&2
  exit 1
fi

git clone --recurse-submodules https://github.com/deanmarano/slot-miyoo.git "$PORT"
git -C "$PORT" checkout --detach "$PORT_COMMIT"
git -C "$PORT" submodule update --init --recursive
test "$(git -C "$PORT" rev-parse HEAD)" = "$PORT_COMMIT"

# The port owns its ARMv7 patches and builds those plus our changes in order.
# Keeping these separate avoids applying H700/GLES-only patches to the Miyoo.
cp "$ROOT"/miyoo/patches/*.patch "$PORT/patches/"
cp "$ROOT/miyoo/build-gambatte.sh" "$PORT/cores/gambatte-build-miyoo.sh"
# The Taskfile expects a standalone subdirectory.
mkdir -p "$PORT/cores/gambatte"
cp "$ROOT/miyoo/build-gambatte.sh" "$PORT/cores/gambatte/build-miyoo.sh"
python3 "$ROOT/miyoo/prepare_port.py" "$PORT"

# Assemble the Miyoo port's exact patch baseline first. The custom patch is
# generated against that baseline, then all patches are cleanly reapplied by
# the port's normal release task. This avoids assuming the H700 source layout.
(
  cd "$PORT"
  task patch
)
python3 "$ROOT/miyoo/apply_custom.py" "$PORT/upstream/slot" "$PORT/patches/0028-custom-gambatte-defaults.patch"
(
  cd "$PORT"
  task unpatch
  task release OUT=release
)

test -s "$STAGE/System/slot"
test -s "$STAGE/System/mgba_libretro.so"
test -s "$STAGE/System/gpsp_libretro.so"
test -s "$STAGE/System/gambatte_libretro.so"
test -s "$STAGE/System/licenses/gambatte-src.tar.gz"
test -s "$STAGE/System/licenses/build-info.txt"
file "$STAGE/System/slot" | grep -q 'ELF 32-bit LSB .*ARM'

# Brand the launcher without renaming its directories or any runtime binary.
# That preserves the install paths expected by the proven Miyoo port.
python3 - "$STAGE" <<'PY'
import json
import pathlib
import sys

stage = pathlib.Path(sys.argv[1])
for rel in ("App/Slot/config.json", "Apps/slot.pak/config.json"):
    path = stage / rel
    with path.open(encoding="utf-8") as f:
        config = json.load(f)
    config["label"] = "Custom slot"
    config["description"] = "Custom slot for Miyoo Mini, Mini Plus and Mini Flip"
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
PY

# Supply both optional startup methods as examples, without enabling either.
# Installing into Onion's .tmp_update/startup/ remains an explicit user action.
cp "$ROOT/miyoo/onion-autoboot.sh" "$STAGE/System/autoboot/onion-startup.sh"
cp "$ROOT/miyoo/onion-splash.sh" "$STAGE/System/onion-splash.sh"
test -s "$STAGE/System/onion-splash.sh"
grep -q "SLOT_ONION_VISUALS" "$STAGE/System/launch_frontend.sh"
grep -q "SLOT_ONION_POWER_OWNER" "$STAGE/System/launch_frontend.sh"
! grep -q "SLOT_ONION_BRIGHTNESS" "$STAGE/System/launch_frontend.sh"
grep -q "SLOT_FB_ROTATE=180" "$STAGE/System/launch_frontend.sh"
grep -Fq '.tmp_update/runtime.sh' "$STAGE/System/launch_frontend.sh"
! grep -Fq 'onionVersion/version.txt' "$STAGE/System/launch_frontend.sh"
! grep -Fq 'onionVersion/version.txt' "$STAGE/System/onion-splash.sh"
! grep -Fq 'trace-display.txt' "$STAGE/System/launch_frontend.sh"
cp "$ROOT/miyoo/INSTALL.md" "$STAGE/System/custom-slot-install.md"
cat > "$STAGE/System/custom-slot-version.txt" <<EOF
Custom slot. $SLOT_VERSION Ver. $CUSTOM_VERSION
Platform: Miyoo Mini / Mini Plus / Mini Flip (ARMv7)
Port: https://github.com/deanmarano/slot-miyoo
Port commit: $PORT_COMMIT
Original Slot: https://github.com/slot-cfw/slot
Custom source: https://github.com/Sinastrax/select-slot
Resume on Power On and Resume on Insert are independent settings
Menu Screen Off: Off/1/3/5/10/15/30 min (default 3)
Menu Power Off: Off/1/3/5/10/15/30 min (default 15)
GB/GBC default: Gambatte
GBA default: gpSP
Onion theme visuals: native Boot, End_Save on Slot shutdown; Onion keymon handles POWER sleep/wake
Framebuffer orientation: restored original 180 degrees (Ver. 5 regression fix)
Onion PWM: original Miyoo hardware curve; one-time recovery from Ver. 5 saved low brightness (<5) on Onion; no diagnostics; native Onion power handoff
Authentic renderer: NOT YET PORTED
Scaling: Original, Integer, Aspect Fit, Fill/Crop, Full Stretch (per game)
State: experimental; this custom variant has not been hardware-tested
EOF

rm -f "$ZIP"
(cd "$STAGE" && zip -qr "$ZIP" .)
unzip -t "$ZIP" | tail -1
sha256sum "$ZIP" > "$ZIP.sha256"
printf '\nBuilt %s\n' "$ZIP"
