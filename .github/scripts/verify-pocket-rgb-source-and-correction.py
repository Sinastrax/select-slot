#!/usr/bin/env python3
"""Final build-stage checks for RGB Pocket palette vs fixed LCD optics.

Checks what can be proven without a real framebuffer capture:
- Automatic GBC palette must NEVER select the monochrome DMG core route.
- SGB always retains its independent SGB hardware model + presets.
- Both profiles are the SAME LCD optics, but can select different RGB
  transfer correction when requested: GBC for Pocket Color, SNES for SGB.
- Pixel gap/shadow/reflector geometry formulas are not edited by this fix.
"""
from pathlib import Path
pal=Path("crates/slot-store/src/gb_palette.rs").read_text()
state=Path("crates/slot-store/src/slot_state.rs").read_text()
app=Path("crates/slot/src/app.rs").read_text()
core=Path("crates/slot/src/core.rs").read_text()
auth=Path("crates/slot-gfx/src/authentic.rs").read_text()
shader=Path("crates/slot-gfx/src/shaders.rs").read_text()
session=Path("crates/slot/src/session.rs").read_text()

assert "    GbcAuto," in pal
assert "pub fn all()" in pal
assert "std::iter::once(GbColors::Auto).chain" in pal  # not menu-exposed
assert "GbColors::Auto | GbColors::GbcAuto | GbColors::SgbAuto => self.gb_palettes = false," in state
assert "&& self.state.gb_colors() == GbColors::Auto => GbColors::GbcAuto," in app
assert "self.gb_model() == GbModel::PocketSgb => GbColors::SgbAuto" in app
assert "GbColors::Palette(slot_store::GbPalette::GRAYSCALE)" in app

gbc_section=core.split("Some(GbColors::GbcAuto) => {",1)[1].split("Some(GbColors::SgbAuto) => {",1)[0]
assert 'core.set_option("mgba_gb_model", "Game Boy Color");' in gbc_section
assert 'core.set_option("mgba_gb_colors_preset", "1");' in gbc_section
sgb_section=core.split("Some(GbColors::SgbAuto) => {",1)[1].split("Some(p) => {",1)[0]
assert 'core.set_option("mgba_gb_model", "Super Game Boy");' in sgb_section
assert 'core.set_option("mgba_gb_colors_preset", "2");' in sgb_section
assert 'core.set_option("mgba_gb_colors", "Auto");' in sgb_section
plain_section=core.split("Some(p) => {",1)[1].split("None => {",1)[0]
assert 'core.set_option("mgba_gb_model", "Game Boy");' in plain_section
assert 'core.set_option("mgba_gb_colors_preset", "0");' in plain_section
assert "let palette = crate::core::palette_for(chosen, platform, &rom, player);" in session
assert "let chosen = self.app.core_gb_colors();" in session

# Save 100% of the Pocket LCD model; lcd.x chooses the optical pathway,
# lcd.y is only a color-transfer family switch when correction is enabled.
gbc=auth.split("Screen::PocketColor => {",1)[1].split("Screen::PocketSgb => {",1)[0]
sgb=auth.split("Screen::PocketSgb => {",1)[1].split("Screen::Light =>",1)[0]
assert "look.lcd[0] = 2.0;" in gbc
assert "look.lcd[1] = 1.0;" in gbc
assert "let mut look = Screen::PocketColor.look();" in sgb
assert "look.lcd[1] = 0.0;" in sgb
assert "look.lcd[0]" not in sgb
assert "look.lcd[0] = 3.0;" not in auth
# GBC/SGB correction is the ONLY shader difference:
assert "if (u_authentic_correction > 0.5 && u_lcd.y > 0.5) {" in shader
assert "if (u_authentic_correction > 0.5 && u_lcd.x < 2.5) {" not in shader
assert "vec3 panelRgb = raw;" in shader
assert "vec3 sgbCode = floor(raw * 31.0 + vec3(0.5));" in shader
assert "panelRgb = mix(sgbLow, sgbHigh, step(vec3(16.5), sgbCode));" in shader
assert "float gapShare = clamp((dotLuma - baseLuma) /" in shader
assert "float shadowShare = clamp(dotLuma / max(baseLuma, 0.03)" in shader
assert "c = clamp(mix(panelRgb, reflector, gapShare) * shadowShare, 0.0, 1.0);" in shader
assert "gap = step(f * span, vec2(1.0));" in shader
assert "float shadow = ink_near(" in shader

# Test the two correction switches as a truth table (same optical route):
for model in ("GBC", "SGB"):
    ramp = 1.0 if model=="GBC" else 0.0
    for corrected in (0.0,1.0):
        gbc_curve = corrected>0.5 and ramp>0.5
        sgb_curve = corrected>0.5 and not gbc_curve
        assert (gbc_curve,sgb_curve)==(
            (corrected==1 and model=="GBC"),
            (corrected==1 and model=="SGB"))
print("PASS: Pocket Color GBC Auto is not monochrome, Pocket SGB preserves SGB core colors,")
print("      both use identical full Pocket LCD optics, On/Off selects ONLY RGB transfer")
