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
CUSTOM_VERSION="22"
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
# Verify every control path is disabled in the generated patch before release.
shader_patch="$PORT/patches/0028-custom-gambatte-defaults.patch"
grep -Fq '+        compositor.set_screen_effect(ScreenEffect::None);' "$shader_patch"
grep -Fq '+    fn step_shader(&mut self, _right: bool) {' "$shader_patch"
grep -Fq '+        // Force the unfiltered picture even for pre-existing saved choices.' "$shader_patch"
grep -Fq '+        Shader::Off' "$shader_patch"
grep -Fq '+            QuickRow::Shader, QuickRow::GbaShader,' "$shader_patch"
grep -Fq '+            shader_gba: Shader::Off,' "$shader_patch"
grep -Fq '+            shader_gb: Shader::Off,' "$shader_patch"
grep -Fq '+            shader_gbc: Shader::Off,' "$shader_patch"
# No shader render implementation, game shader backend or panel path is modified.
! grep -Eq '^diff --git a/crates/slot-gfx/' "$shader_patch"
! grep -Eq '^\+.*(draw_shimmerless|shimmer_axis|dot_axis_factor)' "$shader_patch"
echo "Verified shader-free Miyoo frontend, menus, shortcuts and default state"
# The setting, displayed row, physical blanking and OnionOS handoff must
# all be present. A successful compile alone does not prove wiring.
grep -Fq '+    pub const GENERAL: [QuickRow; 9]' "$shader_patch"
grep -Fq '+    pub const ALL: [QuickRow; 84]' "$shader_patch"
grep -Fq '+    pub menu_screen_off_min: u8,' "$shader_patch"
grep -Fq '+    pub menu_power_off_min: u8,' "$shader_patch"
grep -Fq '+            menu_screen_off_min: 3,' "$shader_patch"
grep -Fq '+            menu_power_off_min: 15,' "$shader_patch"
grep -Fq '+            QuickRow::MenuScreenOff => "Menu Screen Off",' "$shader_patch"
grep -Fq '+            QuickRow::MenuPowerOff => "Menu Power Off",' "$shader_patch"
grep -Fq '+    pub fn set_idle_blank(&mut self, blank: bool) {' "$shader_patch"
grep -Fq '+    fn tick_menu_idle(&mut self) {' "$shader_patch"
grep -Fq '+        self.tick_menu_idle();' "$shader_patch"
grep -Fq '+            if std::fs::write("/tmp/.offOrder", b"").is_ok() {' "$shader_patch"
grep -Fq '+                std::process::exit(0);' "$shader_patch"
echo "Verified independent menu timers and OnionOS shutdown handoff"

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
# Only PWM selection/testing and menu-specific blanking may differ in slot-power.
! grep -Fq "diff --git a/crates/slot-gfx/" "$PORT/patches/0028-custom-gambatte-defaults.patch"
grep -Fq 'diff --git a/crates/slot-power/src/device.rs' "$PORT/patches/0028-custom-gambatte-defaults.patch"
! grep -E '^diff --git a/crates/slot-power/src/lib\.rs' "$PORT/patches/0028-custom-gambatte-defaults.patch"
grep -Fq 'diff --git a/crates/slot-power/src/power.rs' "$PORT/patches/0028-custom-gambatte-defaults.patch"
grep -Fq '+    pub fn set_idle_blank(&mut self, blank: bool) {' "$PORT/patches/0028-custom-gambatte-defaults.patch"
# Check that the original nine levels and PWM duty table are untouched.
# The generated patch includes only a migration for older brightness=10..12
# values so the *rest* of slot.state still loads.
grep -Fq 'pub const BRIGHTNESS_MAX: u8 = 9;' "$PORT/upstream/slot/crates/slot-store/src/slot_state.rs"
grep -Fq 'pub const LEVELS: [QuickValue; 10]' "$PORT/upstream/slot/crates/slot-ui/src/quick_menu.rs"
grep -Fq '+            "brightness" => brightness = Some(value.parse::<u8>().ok()?.min(BRIGHTNESS_MAX)),' "$PORT/patches/0028-custom-gambatte-defaults.patch"
! grep -Eq '^\+.*(BRIGHTNESS_MAX: u8 = 12|Level10|Level11|Level12|let percent: u32|set_backlight\(12\))' "$PORT/patches/0028-custom-gambatte-defaults.patch"
! grep -Fq '+                let duty = if step <= TOP_STEP as u8 {' "$PORT/patches/0028-custom-gambatte-defaults.patch"
echo 'Verified legacy brightness 0–9 and compatibility migration'

# Optional autoboot delegates to the original launcher and leaves Onion's
# runtime, keymon, the selected theme, and display services unmodified.
cp "$ROOT/miyoo/onion-autoboot.sh" "$STAGE/System/autoboot/onion-startup.sh"
cp "$ROOT/miyoo/INSTALL.md" "$STAGE/System/select-slot-install.md"
cat > "$STAGE/System/select-slot-version.txt" <<EOF
select. slot. $SLOT_VERSION Ver. $CUSTOM_VERSION - menu idle timers, shaders off, brightness 1-9
Base: https://github.com/deanmarano/slot-miyoo
Pinned original: $PORT_COMMIT
GB/GBC: Miyoo-native mGBA default; Gambatte optional; GBA: gpSP default (mGBA alternative)
Per-game scaling: Original, Integer, Aspect Fit, Fill/Crop, Full Stretch
Resume On Power / Insert: independent
Brightness: original 0-9 PWM hardware levels (UI 1-9); previously saved 10-12 migrate to 9 without resetting other settings
Framebuffer: original unfiltered Miyoo CPU renderer; no effects, orientation and launcher unchanged
Shaders: disabled globally for GB/GBC/GBA; menu controls hidden and shortcuts inert; pre-existing shader settings ignored
Menu Screen Off: Off/1/3/5/10/15/30 minutes; default 3; first press wakes without opening an item
Menu Power Off: Off/1/3/5/10/15/30 minutes; default 15; hands off to OnionOS themed shutdown
OnionOS: theme-independent keymon POWER/suspend/shutdown handoff; retains whichever OnionOS theme is selected
Onion PWM: original 0-9 brightness duty table; select physical PWM over unrelated legacy backlight interfaces
Experimental preview; no H700 OTA publication
EOF

rm -f "$ZIP"
(cd "$STAGE" && zip -qr "$ZIP" .)
unzip -t "$ZIP" | tail -1
sha256sum "$ZIP" > "$ZIP.sha256"
printf '\nBuilt %s\n' "$ZIP"
