#!/usr/bin/env bash
# Official Dean Marano slot-miyoo v0.3.0 + ONE OnionOS POWER fix.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$ROOT/.build/miyoo-stock"
PORT="$WORK/slot-miyoo"
# v0.3.0 annotated tag resolves to this original release commit.
COMMIT="13b5404b2550ab9bf11bd442f319ac450a65463c"
VERSION="0.3.0"
ZIP="$WORK/slot-miyoo-v${VERSION}-onion-standby-fix.zip"
STAGE="$PORT/release/stage"

for command in git task docker zip unzip python3 file; do
    command -v "$command" >/dev/null || { echo "Missing $command" >&2; exit 1; }
done
mkdir -p "$WORK"
test ! -e "$PORT" || { echo "Refusing to reuse existing checkout $PORT" >&2; exit 1; }

git clone --recurse-submodules https://github.com/deanmarano/slot-miyoo.git "$PORT"
git -C "$PORT" checkout --detach "$COMMIT"
git -C "$PORT" submodule update --init --recursive
test "$(git -C "$PORT" rev-parse HEAD)" = "$COMMIT"

# Generate exactly one patch on top of the *original* v0.3.0 port.
(cd "$PORT" && task patch)
python3 "$ROOT/miyoo-stock/patch_onion_power.py" \
    "$PORT/upstream/slot" "$PORT/patches/0028-onion-stock-power-owner.patch"
! grep -E '^diff --git a/.*(slot-power|slot-gfx|input|display|theme)' \
    "$PORT/patches/0028-onion-stock-power-owner.patch"
test "$(grep -c '^diff --git a/' "$PORT/patches/0028-onion-stock-power-owner.patch")" -eq 1
grep -Fq 'pgrep' "$PORT/patches/0028-onion-stock-power-owner.patch"
(cd "$PORT" && task unpatch && task release OUT=release)

# No modification to Dean's launcher or OnionOS/theme files.
cmp -s "$STAGE/System/launch_frontend.sh" "$PORT/card/System/launch_frontend.sh"
test -s "$STAGE/System/slot"
test -s "$STAGE/System/licenses/build-info.txt"
file "$STAGE/System/slot" | grep -q 'ELF 32-bit LSB .*ARM'

cat > "$STAGE/System/slot-onion-standby-fix.txt" <<'EOF'
slot-miyoo v0.3.0 (Dean Marano) + experimental OnionOS POWER ownership fix
This is the ORIGINAL port, original mGBA/gpSP cores, original PWM/calibration,
original software renderer, and original launch script.
Only app.rs: if Onion's keymon is running, POWER belongs to Onion.
Stock firmware and Allium continue to use Slot's original POWER behavior.
BMO/Onion theme files and animations are not replaced.
Experimental: verify on physical Mini; back up SD before replacing files.
Upstream original: https://github.com/deanmarano/slot-miyoo/releases/tag/v0.3.0
EOF

rm -f "$ZIP"
(cd "$STAGE" && zip -qr "$ZIP" .)
unzip -t "$ZIP" | tail -1
sha256sum "$ZIP" > "$ZIP.sha256"
echo "Built $ZIP"
