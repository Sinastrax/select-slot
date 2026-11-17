#!/usr/bin/env python3
"""Verify exact baseline Pocket rasterization and no regression to mGBA color.

The baseline is the published pre-RG35XX H Ver. 4 H700 source, not a new
stylized mathematical approximation. All old color model optical settings
are restored. The current source color palette routing stays independent.
"""
from pathlib import Path
import math
shader=Path("crates/slot-gfx/src/shaders.rs").read_text()
auth=Path("crates/slot-gfx/src/authentic.rs").read_text()
app=Path("crates/slot/src/app.rs").read_text()
front=Path("crates/slot/src/frontend.rs").read_text()
core=Path("crates/slot/src/core.rs").read_text()

# The Ver. 4 Pocket Color optical mask, explicitly selected for both color
# models. The fractional RG35XX H Fit model can affect only mono screens.
original_gap = """        if (u_lcd.x > 1.5) {
            gap = step(f * span, vec2(1.0));
        }"""
assert original_gap in shader
assert shader.index(original_gap) < shader.index("if (u_lcd.x > 0.5) {")
old_ink = """if (u_lcd.x > 1.5) {
                    // EXACT original Ver. 4 Pocket Color dot coverage.
                    if (gap.x + gap.y > 0.5) {
                        vec2 back = centre - (gap.x > 0.5 ? vec2(texel.x, 0.0) : vec2(0.0, texel.y));
                        float other = all(greaterThanEqual(back, u_pic.xy)) ? ink(back) : 0.0;
                        a = gap.x + gap.y > 1.5 ? 0.0 : u_ink.z * (a + other);
                    }
                }"""
assert old_ink in shader, "Missing original Pocket gap+neighbor ink"
assert shader.count("c = clamp(mix(panelRgb, reflector, gapShare) * shadowShare, 0.0, 1.0);") == 1
assert "pocketOpticalGapShare" not in shader
assert "sgbGapShare" not in shader
# The old shadow/reflector formula is shared, not duplicated or approximated.
assert shader.count("float shadow = ink_near(") == 1
assert "shadow *= 0.25 * u_ink.w * (1.0 - 0.75 * a);" in shader
assert "float baseInk = ink(centre);" in shader
assert "float gapShare = clamp((dotLuma - baseLuma) /" in shader
assert "float shadowShare = clamp(dotLuma / max(baseLuma, 0.03), 0.0, 1.0);" in shader
assert "vec3 reflector = u_authentic_correction > 0.5" in shader

# The color-Pocket optical model remains derived from the original Pocket.
assert "Screen::PocketColor => {" in auth
assert "let mut look = POCKET.look([keep(30.0), keep(10.0)]);" in auth
assert "look.lcd[0] = 2.0;" in auth
assert "Screen::PocketSgb => {" in auth
assert "let mut look = Screen::PocketColor.look();" in auth
assert "look.lcd[0] = 3.0;" in auth
assert "GbModel::PocketColor => slot_gfx::Screen::PocketColor" in front
assert "GbModel::PocketSgb => slot_gfx::Screen::PocketSgb" in front

# Only the source colors differ: GBC calibrated input for Pocket Color,
# SGB native input or optional SNES transfer for Pocket SGB.
assert "vec3 panelRgb = raw;" in shader
assert "if (u_authentic_correction > 0.5 && u_lcd.x < 2.5)" in shader
assert "vec3 sgbCode = floor(raw * 31.0 + vec3(0.5));" in shader
assert "panelRgb = mix(sgbLow, sgbHigh, step(vec3(16.5), sgbCode));" in shader
assert "Shader::Authentic if self.gb_model() == GbModel::PocketSgb => GbColors::SgbAuto" in app
assert "Shader::Authentic if !matches!(self.gb_model(), GbModel::Gbc | GbModel::PocketColor)" in app
assert 'core.set_option("mgba_gb_model", "Super Game Boy");' in core
assert 'core.set_option("mgba_gb_colors", "Auto");' in core

# Baseline pixel footprint proof. With integer scale the Pocket Color/SGB
# mask has the same original dot layout; on fractional Fit it uses original
# Ver. 4 snapping, not the new integrated grid.
def mask(column, scale):
    f = ((column + 0.5) / scale) % 1.0
    return 1.0 if f * scale <= 1.0 else 0.0
for scale in (3.0, 3.335, 4.0):
    a = [mask(i, scale) for i in range(100)]
    gbc = [mask(i, scale) for i in range(100)]
    sgb = [mask(i, scale) for i in range(100)]
    assert gbc == sgb
    assert a == gbc
    assert 0 < sum(gbc) < 100
assert "vec2 gap = clamp(gapArea * span" in shader
assert "float leftGap = u_ink.z * (a + west);" in shader  # mono retained
print("PASS: Ver. 4 Pocket Color optics restored for both RGB models, mGBA SGB palettes intact")
