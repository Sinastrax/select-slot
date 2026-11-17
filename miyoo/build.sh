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
CUSTOM_VERSION="1"
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
cp "$ROOT/miyoo/port_features.py" "$PORT/tools/custom-slot-feature-layer.py"
# Execute our source adaptation after Dean's 26 ARMv7 hardware patches and
# Custom slot's resume fix. The task performs this on a fresh clean tree.
python3 - "$PORT/taskfile.yml" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
s = p.read_text()
needle = "\n  unpatch:\n"
assert s.count(needle) == 1, "port taskfile patch lifecycle changed"
s = s.replace(needle, "\n      - python3 tools/custom-slot-feature-layer.py upstream/slot\n" + needle, 1)
p.write_text(s)
PY
git -C "$PORT/upstream/slot" apply --check "$ROOT/miyoo/patches/0027-custom-auto-load-off.patch"

(
  cd "$PORT"
  task release OUT=release
)

test -s "$STAGE/System/slot"
test -s "$STAGE/System/gpsp_libretro.so"

# Compile a real ARMv7 Gambatte core instead of shipping mGBA as a GB fallback.
GAMBATTE_COMMIT=77f2567d718b8973d02caa2daa8dce4953faf811
GAMBATTE_SOURCE="$PORT/third-party/gambatte-$GAMBATTE_COMMIT.tar.gz"
mkdir -p "$PORT/third-party/gambatte"
curl -fsSL --retry 4 --retry-all-errors \
  "https://github.com/libretro/gambatte-libretro/archive/$GAMBATTE_COMMIT.tar.gz" \
  -o "$GAMBATTE_SOURCE"
tar -xzf "$GAMBATTE_SOURCE" -C "$PORT/third-party/gambatte" --strip-components=1
docker run --rm -u "$(id -u):$(id -g)" -v "$PORT":/src -w /src \
  -e HOME=/tmp slot-miyoo-toolchain:latest bash -ec '
    cd third-party/gambatte
    make -f Makefile.libretro -j2 platform=classic_armv7_a7 \
      CC=arm-linux-gnueabihf-gcc \
      CXX=arm-linux-gnueabihf-g++ AR=arm-linux-gnueabihf-ar
  '
test -s "$PORT/third-party/gambatte/gambatte_libretro.so"
cp "$PORT/third-party/gambatte/gambatte_libretro.so" "$STAGE/System/gambatte_libretro.so"
cp "$GAMBATTE_SOURCE" "$STAGE/System/licenses/gambatte-src.tar.gz"
printf 'libretro/gambatte-libretro %s\n' "$GAMBATTE_COMMIT" \
  > "$STAGE/System/licenses/gambatte_libretro.so.meta"
rm -f "$STAGE/System/mgba_libretro.so"
file "$STAGE/System/gambatte_libretro.so" | grep -q 'ELF 32-bit LSB .*ARM'
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

cp "$ROOT/miyoo/INSTALL.md" "$STAGE/System/custom-slot-install.md"
cat > "$STAGE/System/custom-slot-version.txt" <<EOF
Custom slot. $SLOT_VERSION Ver. $CUSTOM_VERSION
Platform: Miyoo Mini / Mini Plus / Mini Flip (ARMv7)
Port: https://github.com/deanmarano/slot-miyoo
Port commit: $PORT_COMMIT
Original Slot: https://github.com/slot-cfw/slot
Custom source: https://github.com/Sinastrax/slot-rgsp-mod
Custom changes: Gambatte for GB/GBC, gpSP for GBA; 5 scale modes; Auto Load Off fix; no mGBA/SGB
State: experimental; this custom variant has not been hardware-tested
EOF

rm -f "$ZIP"
(cd "$STAGE" && zip -qr "$ZIP" .)
unzip -t "$ZIP" | tail -1
sha256sum "$ZIP" > "$ZIP.sha256"
printf '\nBuilt %s\n' "$ZIP"
