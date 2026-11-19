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
CUSTOM_VERSION="4"
ZIP="$WORK/select-slot-$SLOT_VERSION-ver$CUSTOM_VERSION-miyoo.zip"
ZIP_ONION="$WORK/select-slot-$SLOT_VERSION-ver$CUSTOM_VERSION-miyoo-onion-autoboot.zip"
ZIP_STOCK="$WORK/select-slot-$SLOT_VERSION-ver$CUSTOM_VERSION-miyoo-stock-autoboot.zip"

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
# Use only the port's existing mGBA/gpSP tasks. No Gambatte source or core is built.

# Assemble the Miyoo port's exact patch baseline first. The custom patch is
# generated against that baseline, then all patches are cleanly reapplied by
# the port's normal release task. This avoids assuming the H700 source layout.
(
  cd "$PORT"
  task patch
)
python3 "$ROOT/miyoo/apply_custom.py" "$PORT/upstream/slot" "$PORT/patches/0028-select-miyoo-config.patch"
# Verify every control path is disabled in the generated patch before release.
shader_patch="$PORT/patches/0028-select-miyoo-config.patch"
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
grep -Fq '+    pub const ALL: [QuickRow; 88]' "$shader_patch"
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
# Emit a useful failure explaining which verification is missing, instead of
# aborting the build without context when one hunk is not in the generated patch.
check_patch() {
  if ! grep -Fq "$1" "$shader_patch"; then
    printf 'Missing Miyoo patch wiring: %s\n' "$1" >&2
    exit 1
  fi
}
# GB/GBC/GBA each has its own Scaling row under Screen > system.
# The General screen stays unmodified; no single global selector remains.
check_patch '+    pub const SCREEN_GBA: [QuickRow; 4]'
check_patch '+    pub const SCREEN_GBC: [QuickRow; 4]'
check_patch '+    pub const SCREEN_GB: [QuickRow; 5]'
check_patch '+        QuickRow::GbaScaling,'
check_patch '+        QuickRow::GbcScaling,'
check_patch '+        QuickRow::GbScaling,'
check_patch '+            QuickRow::GbaScaling | QuickRow::GbScaling | QuickRow::GbcScaling => "Scaling",'
check_patch '+pub fn default_video_mode(root: &Path, platform: Platform) -> VideoMode {'
check_patch '+        Platform::Gb => "default_gb",'
check_patch '+        Platform::Gbc => "default_gbc",'
check_patch '+        Platform::Gba => "default_gba",'
check_patch '+        .or_else(|| ini::value(root, VIDEO_MODE_FILE, "default")'
check_patch '+        .unwrap_or_else(|| default_video_mode(root, platform))'
check_patch '+    ini::write(root, VIDEO_MODE_FILE, platform_default_key(platform), mode.as_str())'
check_patch '+            .set_video_mode(crate::video_mode::video_mode_for(&self.root, stem, platform));'
check_patch '+        if matches!(row, QuickRow::GbaScaling | QuickRow::GbScaling | QuickRow::GbcScaling) {'
if grep -Fq '+            QuickRow::DefaultScaling' "$shader_patch"; then
  echo "ERROR: global Default Scaling row found in Ver. 25" >&2
  exit 1
fi
echo "Verified three saved system scaling defaults, per-ROM overrides, and no general scaling row"
# Scaling became the first item on all three pages in Ver. 25.
# parent() must match the first row; otherwise B jumps to the shelf.
check_patch '+            QuickRow::GbaScaling => Some(QuickRow::ScreenGba),'
check_patch '+            QuickRow::GbcScaling => Some(QuickRow::ScreenGbc),'
check_patch '+            QuickRow::GbScaling => Some(QuickRow::ScreenGb),'
if grep -Eq '^\+.*QuickRow::(Gba|Gbc|Gb)Shader => Some\(QuickRow::Screen(Gba|Gbc|Gb)\),' "$shader_patch"; then
  echo "ERROR: old shader-first parent mapping reintroduced" >&2
  exit 1
fi
echo "Verified GB, GBC and GBA B-button returns to Screen menu"

# The earlier OnionOS POWER passthrough is still used for short presses,
# while long hold must request real shutdown before keymon sleeps the app.
check_patch '+pub const POWER_HOLD_MS: Millis = 350;'
check_patch '+                Action::PowerHold => {'
check_patch '+                    self.menu_shutdown_onion = true;'
check_patch '+        if self.shutting_down() {'
check_patch '+                    && root.join(".tmp_update/onionVersion/version.txt").is_file()'
echo "Verified menu scaling persistence, quick shutdown, and input lock"
# The original GBA uses the SP bezel's exact static-surround geometry,
# with its own saved menu value and independently loaded alternate texture.
check_patch '+    Agb001,'
check_patch '+            BezelPick::Agb001 => "agb-001".to_string(),'
check_patch '+            BezelPick::Agb001 => "GBA".to_string(),'
check_patch '+            BezelPick::Ags102 => "GBA SP".to_string(),'
check_patch '+                choices.push(BezelPick::Agb001);'
check_patch '+    gba_strip: Option<TexId>,'
check_patch '+    pub fn set_gba_strip(&mut self, tex: Option<TexId>) {'
check_patch '+            self.gba_strip.or(self.sp_strip)'
check_patch '+            BezelPick::None | BezelPick::Ags102 | BezelPick::Agb001 => None,'
check_patch '+        let gba_path = self.session.app().root()'
echo "Verified original GBA / SP bottom-strip selector without new render backend"

# Ver. 4: require the native restart entry, all-page scrolling and separate
# high-contrast clock/battery menu textures; keep original shelf rendering.
check_patch '+    pub const MAIN: [QuickRow; 6]'
check_patch '+        QuickRow::Restart,'
check_patch '+            QuickRow::Restart => self.begin_restart(),'
check_patch '+fn scrolls(page: &[QuickRow]) -> bool {'
check_patch '+    !page.is_empty()'
check_patch '+    menu_battery_percent: slot_ui::Printed,'
check_patch '+    menu_clock: slot_ui::Printed,'
check_patch '+    menu_clock_tex: Option<TexId>,'
check_patch '+    menu_battery_tex: Option<TexId>,'
check_patch '+        version: "1.8.1 Ver. 4",'
echo "Verified Ver. 4 restart, viewport scrolling, menu status text and About version"




(
  cd "$PORT"
  task unpatch
  task release OUT=release
)

test -s "$STAGE/System/slot"
test -s "$STAGE/System/mgba_libretro.so"
test -s "$STAGE/System/gpsp_libretro.so"
# Do not ship Gambatte; old per-game "gambatte" settings map to mGBA.
test ! -e "$STAGE/System/gambatte_libretro.so"
test ! -e "$STAGE/System/licenses/gambatte-src.tar.gz"
test -s "$STAGE/System/licenses/build-info.txt"
test -s "$STAGE/System/launch_frontend.sh"
file "$STAGE/System/slot" | grep -q 'ELF 32-bit LSB .*ARM'

# Use the EXISTING Perfect GBA (no grid) bezel by mugwomp93 from KNULLI,
# not generated or redrawn artwork. Original source is a 1024x768 PNG.
# Resizing it to 640x480 with Pillow LANCZOS preserves EXACTLY the same
# alpha mask as Slot's current SP bezel (checked pixel-for-pixel).
# Original Slot SP asset is preserved byte-for-byte.
ORIGINAL_GBA_COMMIT="75aa66c41548ebaa95f31d260d47eea2baab9d8a"
ORIGINAL_GBA_URL="https://raw.githubusercontent.com/chrizzo-hb/knulli-bezels/$ORIGINAL_GBA_COMMIT/default-knulli/systems/gba-4_3.png"
ORIGINAL_GBA_SOURCE_SHA256="1d25c249c08580c6082656d353d001158e8378653b9a3d90c80e85700990ca93"
command -v curl >/dev/null || { echo 'Missing build dependency: curl' >&2; exit 1; }
if ! python3 -c 'from PIL import Image' >/dev/null 2>&1; then
  echo "Installing Pillow for asset resizing (host build dependency, NOT shipped to Miyoo)"
  python3 -m pip -q install pillow
fi
test -s "$STAGE/System/bezels/640x480.png"
test ! -e "$STAGE/System/bezels/gba-original.png"
curl --fail --location --silent --show-error --retry 3 "$ORIGINAL_GBA_URL" -o "$WORK/gba-original-source.png"
echo "$ORIGINAL_GBA_SOURCE_SHA256  $WORK/gba-original-source.png" | sha256sum -c -
python3 - "$WORK/gba-original-source.png" "$STAGE/System/bezels/640x480.png" "$STAGE/System/bezels/gba-original.png" <<'PY'
from pathlib import Path
import sys
from PIL import Image, ImageChops
original_path, sp_path, out_path = map(Path, sys.argv[1:])
with Image.open(original_path) as inp:
    if inp.size != (1024, 768):
        raise SystemExit(f"Unexpected source dimensions: {inp.size}")
    original = inp.convert("RGBA").resize((640, 480), Image.Resampling.LANCZOS)
with Image.open(sp_path) as inp:
    sp = inp.convert("RGBA")
if original.size != sp.size or original.size != (640, 480):
    raise SystemExit("The original GBA bezel and existing SP strip have different dimensions")
if ImageChops.difference(original.getchannel("A"), sp.getchannel("A")).getbbox():
    raise SystemExit("Refusing package: original GBA does not match SP opening and lower-strip shape")
if not ImageChops.difference(original.convert("RGB"), sp.convert("RGB")).getbbox():
    raise SystemExit("Original GBA logo is identical to SP; expected different artwork")
original.save(out_path, optimize=True)
with Image.open(out_path) as check:
    if check.convert("RGBA").tobytes() != original.tobytes():
        raise SystemExit("Original GBA PNG verification failed")
print("Existing KNULLI Perfect GBA bezel: same 640x480 mask and lower strip as Slot SP")
PY
test -s "$STAGE/System/bezels/gba-original.png"
test -s "$STAGE/System/licenses/bezel-CC-BY-SA-4.0.txt"
cp "$ROOT/miyoo/GBA-BEZEL-CREDITS.txt" "$STAGE/System/licenses/gba-original-bezel-credits.txt"

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
! grep -Fq "diff --git a/crates/slot-gfx/" "$PORT/patches/0028-select-miyoo-config.patch"
grep -Fq 'diff --git a/crates/slot-power/src/device.rs' "$PORT/patches/0028-select-miyoo-config.patch"
! grep -E '^diff --git a/crates/slot-power/src/lib\.rs' "$PORT/patches/0028-select-miyoo-config.patch"
grep -Fq 'diff --git a/crates/slot-power/src/power.rs' "$PORT/patches/0028-select-miyoo-config.patch"
grep -Fq '+    pub fn set_idle_blank(&mut self, blank: bool) {' "$PORT/patches/0028-select-miyoo-config.patch"
# Check that the original nine levels and PWM duty table are untouched.
# The generated patch includes only a migration for older brightness=10..12
# values so the *rest* of slot.state still loads.
grep -Fq 'pub const BRIGHTNESS_MAX: u8 = 9;' "$PORT/upstream/slot/crates/slot-store/src/slot_state.rs"
grep -Fq 'pub const LEVELS: [QuickValue; 10]' "$PORT/upstream/slot/crates/slot-ui/src/quick_menu.rs"
grep -Fq '+            "brightness" => brightness = Some(value.parse::<u8>().ok()?.min(BRIGHTNESS_MAX)),' "$PORT/patches/0028-select-miyoo-config.patch"
! grep -Eq '^\+.*(BRIGHTNESS_MAX: u8 = 12|Level10|Level11|Level12|let percent: u32|set_backlight\(12\))' "$PORT/patches/0028-select-miyoo-config.patch"
! grep -Fq '+                let duty = if step <= TOP_STEP as u8 {' "$PORT/patches/0028-select-miyoo-config.patch"
echo 'Verified legacy brightness 0–9 and compatibility migration'

# The OnionOS autoboot helper delegates to the original launcher and leaves
# runtime, keymon, the selected theme and display services unmodified.
cp "$ROOT/miyoo/onion-autoboot.sh" "$STAGE/System/autoboot/onion-startup.sh"
cp "$ROOT/miyoo/INSTALL.md" "$STAGE/System/select-slot-install.md"
cat > "$STAGE/System/select-slot-version.txt" <<EOF
select. slot. $SLOT_VERSION Ver. $CUSTOM_VERSION - Restart, scrolling, menu HUD and About version; mGBA/gpSP only
Base: https://github.com/deanmarano/slot-miyoo
Pinned original: $PORT_COMMIT
GB/GBC: Miyoo-native mGBA only; GBA: gpSP default (mGBA alternative); legacy Gambatte profile choices migrate to mGBA
Scaling: Original, Integer, Aspect Fit, Fill/Crop, Full Stretch; separate persisted defaults in Screen > GB/GBC/GBA plus in-game per-ROM overrides
GBA Bezel: None, GBA SP (unchanged default), GBA; same bottom size and pixel positions
Resume On Power / Insert: independent
Framebuffer: original unfiltered Miyoo CPU renderer; no effects, orientation and launcher unchanged
Shaders: disabled globally for GB/GBC/GBA; menu controls hidden and shortcuts inert; pre-existing shader settings ignored
Menu Screen Off: Off/1/3/5/10/15/30 minutes; default 3; first press wakes without opening an item
Menu Power Off: Off/1/3/5/10/15/30 minutes; default 15; instant input lock and OnionOS theme handoff
Power hold: on OnionOS, quick hold uses native themed shutdown; short press stays native OnionOS standby
OnionOS: theme-independent keymon POWER/suspend/shutdown handoff; retains whichever OnionOS theme is selected
Miyoo release; separate from H700 firmware and OTA
EOF

# Keep the original app-only ZIP for people who do NOT want autostart.
# Never install or overwrite any OS boot hook in this base package.
rm -f "$ZIP" "$ZIP_ONION" "$ZIP_STOCK"
(cd "$STAGE" && zip -qr "$ZIP" .)

# OnionOS 4.3+ explicitly executes every .sh file in this dedicated startup
# directory. Crucially, DO NOT put runtime.sh at the card root: that belongs
# to OnionOS itself. This hook is ignored by stock firmware.
test ! -e "$STAGE/.tmp_update/startup/select-slot.sh"
mkdir -p "$STAGE/.tmp_update/startup"
cp "$ROOT/miyoo/onion-autoboot.sh" "$STAGE/.tmp_update/startup/select-slot.sh"
(cd "$STAGE" && zip -qr "$ZIP_ONION" .)
rm "$STAGE/.tmp_update/startup/select-slot.sh"

# Stock Miyoo firmware uses .tmp_update/runtime.sh as its real startup
# script. Copy Dean's proven original *unmodified* stock-autoboot hook only
# into the separate, conspicuously named stock ZIP. NEVER ship it inside
# OnionOS/autoboot or the normal app ZIP: overwriting an existing OnionOS
# runtime.sh would stop that operating system from booting.
test -s "$PORT/card/System/autoboot/runtime.sh"
test ! -e "$STAGE/.tmp_update/runtime.sh"
mkdir -p "$STAGE/.tmp_update"
cp "$PORT/card/System/autoboot/runtime.sh" "$STAGE/.tmp_update/runtime.sh"
cmp -s "$STAGE/.tmp_update/runtime.sh" "$PORT/card/System/autoboot/runtime.sh"
(cd "$STAGE" && zip -qr "$ZIP_STOCK" .)
rm "$STAGE/.tmp_update/runtime.sh"

# Verify cross-OS isolation; a wrong runtime.sh in OnionOS is dangerous.
for z in "$ZIP" "$ZIP_ONION" "$ZIP_STOCK"; do
  unzip -t "$z" | tail -1 | grep -q 'No errors detected'
  unzip -Z1 "$z" | grep -qx 'System/slot'
  unzip -Z1 "$z" | grep -qx 'System/bezels/640x480.png'
  unzip -Z1 "$z" | grep -qx 'System/bezels/gba-original.png'
  unzip -Z1 "$z" | grep -qx 'App/Slot/launch.sh'
  unzip -Z1 "$z" | grep -qx 'Apps/slot.pak/launch.sh'
  ! unzip -Z1 "$z" | grep -Ei '(gambatte|gambatte-src)'
  sha256sum "$z" > "$z.sha256"
done
! unzip -Z1 "$ZIP" | grep -q '^.tmp_update/'
unzip -Z1 "$ZIP_ONION" | grep -qx '.tmp_update/startup/select-slot.sh'
! unzip -Z1 "$ZIP_ONION" | grep -qx '.tmp_update/runtime.sh'
unzip -Z1 "$ZIP_STOCK" | grep -qx '.tmp_update/runtime.sh'
! unzip -Z1 "$ZIP_STOCK" | grep -qx '.tmp_update/startup/select-slot.sh'
unzip -p "$ZIP_ONION" '.tmp_update/startup/select-slot.sh' | grep -Fq 'System/launch_frontend.sh'
unzip -p "$ZIP_STOCK" '.tmp_update/runtime.sh' | cmp -s - "$PORT/card/System/autoboot/runtime.sh"
echo "Verified app-only, OnionOS hook, and stock runtime ZIPs are isolated"
printf '\nBuilt\n  %s\n  %s\n  %s\n' "$ZIP" "$ZIP_ONION" "$ZIP_STOCK"
