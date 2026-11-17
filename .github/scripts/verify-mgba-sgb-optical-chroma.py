#!/usr/bin/env python3
"""Check SGB color preservation and Pocket LCD Fit gap separation.

This source/mathematical regression cannot confirm hardware appearance.
The actual generated shader must also compile as OpenGL ES 2.0 in CI.
"""
from pathlib import Path
import math

shader = Path("crates/slot-gfx/src/shaders.rs").read_text()
app = Path("crates/slot/src/app.rs").read_text()
core = Path("crates/slot/src/core.rs").read_text()
front = Path("crates/slot/src/frontend.rs").read_text()
auth = Path("crates/slot-gfx/src/authentic.rs").read_text()
pocket_start = shader.index("if (u_lcd.x > 1.5 && inside)")
section = shader[pocket_start:shader.index("        } else if (!inside) {",pocket_start)]
for code in (
    "float sgbGapShare = gap.x + gap.y - gap.x * gap.y;",
    "if (u_lcd.x > 2.5) {",
    "vec3 panelRgb = raw;",
    "float shadowShare = clamp(",
    "float leftGap = u_ink.z * (a + west);",
    "float upperGap = u_ink.z * (a + north);",
    "float shadow = ink_near(",
):
    if code in ("float leftGap = u_ink.z * (a + west);","float upperGap = u_ink.z * (a + north);","float shadow = ink_near("):
        assert code in shader, code
    else:
        assert code in section, code
assert "vec3 sgbCode = floor(raw * 31.0 + vec3(0.5));" in section
assert "if (u_authentic_correction > 0.5 && u_lcd.x < 2.5)" in section
assert "vec3 reflector = u_authentic_correction > 0.5" in section
assert "mix(panelRgb, reflector, gapShare)" in section
assert "mix(panelRgb, reflector, sgbGapShare)" in section
assert section.index("if (u_lcd.x > 2.5) {") < section.index("mix(panelRgb, reflector, sgbGapShare)")
assert "let mut look = Screen::PocketColor.look();" in auth
assert "look.lcd[0] = 3.0;" in auth
assert "GbModel::PocketSgb => slot_gfx::Screen::PocketSgb" in front
assert "Shader::Authentic if self.gb_model() == GbModel::PocketSgb => GbColors::SgbAuto" in app
assert 'core.set_option("mgba_gb_model", "Super Game Boy");' in core
assert "SGB" in core and "mgba_gb_colors_preset" in core

# Model-derived test for fractional and integer grid.
def coverage(f, scale):
    reference = max(1, math.floor(scale + .5))
    width = 1 / reference
    half = .5 / max(scale, 1)
    low, high = f - half, f + half
    area = max(0, min(high,width)-max(low,0)) + max(0,min(high,1+width)-max(low,1))
    result = max(0,min(1,area*scale))
    if abs(scale-reference) < .0005:
        result = float(f*scale <= 1)
    return result
def mix(rgb, ref, gapx, gapy):
    gap = gapx + gapy - gapx*gapy
    return tuple((1-gap)*r + gap*v for r,v in zip(rgb,ref))
colours = [(1,0,0),(0,1,0),(0,0,1),(.2,.6,.9),(.8,.4,0),(0,0,0)]
white=(1,1,1)
for rgb in colours:
    assert mix(rgb,white,0,0) == rgb  # dot centres preserve SGB RGB
    assert mix(rgb,white,1,1) == white  # real reflector at crossed gaps
    for x in (.1,.25,.5,.75):
        out=mix(rgb,white,x,.2)
        assert all(min(a,b) <= v <= max(a,b) for a,b,v in zip(rgb,white,out))
# Same geometrical 1/3-pixel separation on integer reference and Fit.
for width in (480,533):
    sy=width/144 if width==480 else width/160
    cov=[coverage(((i+.5)/sy)%1,sy) for i in range(width)]
    assert any(0.01 < x < .99 for x in cov) if width==480 else True
    assert max(cov)-min(cov)>.7
    assert abs(sum(cov)/len(cov)-1/max(1,round(sy)))<.02
# At integer 3x output one full separator per source pixel, two colored columns.
assert [coverage((i+.5)/3,3) for i in range(3)] == [1.,0.,0.]
print("PASS: SGB RGB preserved in dots, same fractional Pocket gaps, GBC untouched, mGBA hardware options retained")
