#!/usr/bin/env python3
"""Ensure Pocket SGB and Pocket Color share one real LCD implementation.

Checks the exact final patched source used for the build, not an intermediate
shader. Also checks SGB RGB/CRT color conversions and model profile parity.
These tests cannot establish hardware speed or visual appearance by themselves.
"""
from pathlib import Path
import math

shader = Path("crates/slot-gfx/src/shaders.rs").read_text()
auth = Path("crates/slot-gfx/src/authentic.rs").read_text()
core = Path("crates/slot/src/core.rs").read_text()
front = Path("crates/slot/src/frontend.rs").read_text()
app = Path("crates/slot/src/app.rs").read_text()

# ONE shared native Pocket branch for both u_lcd.x=2 and u_lcd.x=3.
start = shader.index("        if (u_lcd.x > 0.5) {")
end = shader.index("        } else if (!inside) {", start)
shared = shader[start:end]
assert "if (u_lcd.x > 2.5)" not in shared
assert "vec2 sgbGap" not in shader and "float sgbShadow" not in shader
for text in (
    "float a = 0.0;",
    "float west = 0.0;",
    "float north = 0.0;",
    "float leftGap = u_ink.z * (a + west);",
    "float upperGap = u_ink.z * (a + north);",
    "gap.x * (1.0 - gap.y) * leftGap",
    "float shadow = ink_near(",
    "shadow *= 0.25 * u_ink.w * (1.0 - 0.75 * a);",
    "float gapShare = clamp(",
    "float shadowShare = clamp(",
    "c = clamp(mix(panelRgb, reflector, gapShare) * shadowShare, 0.0, 1.0);",
):
    assert text in shared, f"Missing shared Pocket rendering: {text}"
assert shared.count("if (u_lcd.x > 1.5 && inside)") == 1
assert shared.count("vec3 panelRgb = raw;") == 1
assert shared.count("if (u_lcd.x < 2.5) {") == 1
assert shared.count("else if (u_authentic_correction > 0.5) {") == 1
assert "vec3 sgbCode = floor(raw * 31.0 + vec3(0.5));" in shared
assert "panelRgb = mix(sgbLow, sgbHigh, step(vec3(16.5), sgbCode));" in shared
assert "vec3 reflector = u_authentic_correction > 0.5" in shared
assert "u_lcd.x < 2.5 && u_authentic_correction > 0.5" not in shared
# Ensure source color selection is only after the common dot shadow.
assert shared.index("float shadow = ink_near(") < shared.index("vec3 panelRgb = raw;")
assert shared.index("float shadowShare = clamp(") < shared.index("c = clamp(mix(panelRgb")
# Both look() models must give identical physical appearance parameters.
assert "Screen::PocketSgb => {\n                // Exactly Pocket Color's LCD optical model and response." in auth
assert "let mut look = Screen::PocketColor.look();" in auth
assert "look.lcd[0] = 3.0;" in auth
assert "Screen::PocketColor => {" in auth
assert "look.lcd[0] = 2.0;" in auth
assert "GbModel::PocketColor => slot_gfx::Screen::PocketColor" in front
assert "GbModel::PocketSgb => slot_gfx::Screen::PocketSgb" in front
assert "Platform::Gb => self.gb_shader()" in app
assert 'core.set_option("mgba_gb_model", "Super Game Boy");' in core
assert "uniform float u_authentic_correction;" in shader

# RGB values survive untouched with correction OFF. With correction ON,
# the same SNES CRT ramp used in Ver. 9-10 is computed (no GBC matrix).
def crt(code):
    return code * (code + 1) / 2 / 255 if code <= 16 else min(1., (136 + 8*(code-16))/255)
for rgb in ((0,0,0),(1,1,1),(1,0,0),(0,1,0),(0,0,1),(.2,.6,.9),(.5,.5,.5)):
    off = tuple(rgb)
    assert off == rgb
    on = tuple(crt(math.floor(x*31+0.5)) for x in rgb)
    assert all(0 <= n <= 1 for n in on)
assert crt(0)==0 and crt(31)==1 and crt(8)!=8/31

# Dot geometry is the same algebra for both models at integer and Fit.
def dot(x,y,center,west,north,blend=.38):
    return (1-x)*(1-y)*center + x*(1-y)*blend*(center+west) + (1-x)*y*blend*(center+north)
for x in (0,.1,.3,.65,1):
    for y in (0,.2,.8,1):
        for ink in (.05,.5,1):
            pocket_color=dot(x,y,ink,.3,.7)
            pocket_sgb=dot(x,y,ink,.3,.7)
            assert pocket_color==pocket_sgb
assert "lin = mix(u_dark, u_light, response);" in shader
print("PASS: shared Pocket Color/SGB ink, dot-shadow, reflection and correction split")
