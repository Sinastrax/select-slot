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
CUSTOM_VERSION="11"
ZIP="$WORK/select-slot-$SLOT_VERSION-ver$CUSTOM_VERSION-miyoo.zip"

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
test -s "$STAGE/System/launch_frontend.sh"
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
    config["label"] = "select. slot."
    config["description"] = "Miyoo Mini / Mini Plus / Mini Flip (original display path)"
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
PY

# No display hooks or brightness migrations are installed: this is the
# original Dean launcher, with no changes to its PWM or framebuffer setup.
cmp -s "$STAGE/System/launch_frontend.sh" "$PORT/card/System/launch_frontend.sh" || {
    echo "Packaged launcher differs from original Miyoo port; refusing build" >&2
    exit 1
}
! grep -E '^diff --git a/crates/(slot-gfx|slot-power)/' "$PORT/patches/0028-custom-gambatte-defaults.patch"
! grep -q 'set_backlight' "$PORT/patches/0028-custom-gambatte-defaults.patch"

# Optional autoboot delegates to the original launcher and leaves Onion's
# runtime, keymon, BMO theme assets, and display services unmodified.
cp "$ROOT/miyoo/onion-autoboot.sh" "$STAGE/System/autoboot/onion-startup.sh"
cp "$ROOT/miyoo/INSTALL.md" "$STAGE/System/select-slot-install.md"
cat > "$STAGE/System/select-slot-version.txt" <<EOF
select. slot. $SLOT_VERSION Ver. $CUSTOM_VERSION - clean Miyoo rebuild
Base: https://github.com/deanmarano/slot-miyoo
Pinned original: $PORT_COMMIT
GB/GBC: Gambatte; GBA: gpSP; mGBA available for legacy selections
Per-game scaling: Original, Integer, Aspect Fit, Fill/Crop, Full Stretch
Resume On Power / Insert: independent
Physical brightness, framebuffer, renderer, PWM, launcher: original Miyoo port
OnionOS BMO: native theme and power path
Experimental preview; no H700 OTA publication
EOF

rm -f "$ZIP"
(cd "$STAGE" && zip -qr "$ZIP" .)
unzip -t "$ZIP" | tail -1
sha256sum "$ZIP" > "$ZIP.sha256"
printf '\nBuilt %s\n' "$ZIP"
