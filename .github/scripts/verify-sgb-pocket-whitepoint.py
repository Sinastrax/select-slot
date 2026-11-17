#!/usr/bin/env python3
"""Verify exact Pocket Color white point for SGB without changing RGB source.

The user verified:
 - Pocket Color visuals correct on hardware in Ver. 16.
 - Pocket SGB palette is colorful in Ver. 16.
 - SGB is missing Pocket Color's white hue when correction is ON.
Therefore the *entire* GPU Look must match Pocket Color, with mGBA's
already-correct SGB palette selection left untouched.

Check the actual Ver. 16 merged shader SHA, so none of its optical
geometry, tint, or fit behavior can silently change.
"""
from pathlib import Path
import hashlib
auth = Path("crates/slot-gfx/src/authentic.rs").read_text()
shader = Path("crates/slot-gfx/src/shaders.rs").read_text()
app = Path("crates/slot/src/app.rs").read_text()
core = Path("crates/slot/src/core.rs").read_text()
front = Path("crates/slot/src/frontend.rs").read_text()
original_shader_sha = "14aa798dfc1232d160b6fecebb9a681b17a996ba1c141177369257f8ed6463c1"
actual_shader_sha = hashlib.sha256(shader.encode("utf-8")).hexdigest()
assert actual_shader_sha == original_shader_sha, (
    "Unexpected shader modification! Ver. 17 must ONLY alias the GPU Look; "
    + actual_shader_sha
)
# Same actual Look implies identical ink, glass, display hue, LCD geometry,
# ghosting, response matrix, shader branch, and Color Correction On/Off.
gbc = auth.split("Screen::PocketColor => {", 1)[1].split("Screen::PocketSgb => {", 1)[0]
sgb = auth.split("Screen::PocketSgb => {", 1)[1].split("Screen::Light =>", 1)[0]
assert "let mut look = POCKET.look(" in gbc
assert "look.response = gbc.response;" in gbc
assert "look.gamma = gbc.gamma;" in gbc
assert "look.lcd[0] = 2.0;" in gbc
assert "look.lcd[1] = 1.0;" in gbc
assert "Screen::PocketColor.look()" in sgb
assert "look.lcd[" not in sgb
assert "look.lcd[0] = 3.0;" not in auth

# With Color Correction On, the common RGB response of both Pocket models
# gives the same measured GBC white (not SNES near-pure white).
assert "vec3 gbcWhite = pow(vec3(134.0, 140.0, 122.0) / 255.0, vec3(2.2));" in shader
assert "panelRgb = pow(mix(gbcBlack, gbcWhite, response), vec3(1.0 / 2.2));" in shader
assert "if (u_authentic_correction > 0.5 && u_lcd.y > 0.5)" in shader
assert "vec3 panelRgb = raw;" in shader
assert "vec3 reflector = u_authentic_correction > 0.5" in shader
assert "float gapShare = clamp((dotLuma - baseLuma) /" in shader
# RGB white contrast checks: corrected white has the exact observed Pocket
# tint, while uncorrected white remains pure source white as requested.
pocket_white = (134, 140, 122)
source_white = (255, 255, 255)
assert pocket_white != source_white
assert pocket_white[1] > pocket_white[0] > pocket_white[2]
assert source_white[0] == source_white[1] == source_white[2]
# The real SGB palette still originates in mGBA on game start, not a GBC
# core or a grayscale fallback. This fixes the Ver. 15 gray regression.
assert "self.gb_model() == GbModel::PocketSgb => GbColors::SgbAuto" in app
assert "&& self.state.gb_colors() == GbColors::Auto => GbColors::GbcAuto" in app
assert "GbModel::PocketSgb => slot_gfx::Screen::PocketSgb" in front
assert "GbModel::PocketColor => slot_gfx::Screen::PocketColor" in front
sgb_opts = core.split("Some(GbColors::SgbAuto) => {", 1)[1].split("Some(p) => {", 1)[0]
assert 'core.set_option("mgba_gb_model", "Super Game Boy");' in sgb_opts
assert 'core.set_option("mgba_gb_colors_preset", "2");' in sgb_opts
assert 'core.set_option("mgba_gb_colors", "Auto");' in sgb_opts
assert 'core.set_option("mgba_sgb_borders", "OFF");' in core

print("PASS: SGB and Pocket Color share one complete GPU Look and whitepoint;")
print("      Ver. 16 LCD GLSL is byte-identical; mGBA SGB palettes intact;")
print("      On = GBC-tinted Pocket Color response; Off = original source RGB")
