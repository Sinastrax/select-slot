#!/usr/bin/env python3
"""Check the Pocket Authentic routing and gap coverage without hardware claims."""
from pathlib import Path
import math

src = Path("crates/slot-gfx/src/shaders.rs").read_text()
app = Path("crates/slot/src/app.rs").read_text()
front = Path("crates/slot/src/frontend.rs").read_text()
model = Path("crates/slot-gfx/src/authentic.rs").read_text()

start = src.index("        } else if (u_lcd.x > 0.5) {")
end = src.index("            // The dots' shadow on the reflector", start)
pocket = src[start:end]
assert "if (gap.x + gap.y > 0.5)" not in pocket
assert "if (gap.x + gap.y > 0.0)" in pocket
assert "gap.x * (1.0 - gap.y) * leftGap" in pocket
assert "(1.0 - gap.x) * gap.y * upperGap" in pocket
assert "float leftGap = u_ink.z * (a + west);" in pocket
assert "float upperGap = u_ink.z * (a + north);" in pocket
assert "if (all(greaterThanEqual(leftDot, u_pic.xy)))" in pocket
assert "if (all(greaterThanEqual(upperDot, u_pic.xy)))" in pocket
# The GB Authentic/Pocket menu path actually reaches this shader branch.
assert "Shader::Authentic => ScreenEffect::Authentic" in app
assert "Platform::Gb => self.gb_shader()" in app
assert "GbModel::Pocket => slot_gfx::Screen::Pocket" in front
assert "Screen::Pocket => POCKET.look" in model
assert "lcd: [1.0, 0.0, 0.0, 0.0]" in model

# Existing SGB fastpath, GBA/GBC calibration, and correction toggle survive.
sgb = src[src.index("if (u_lcd.x > 2.5) {"):start]
assert "float a = 0.0;" not in sgb
assert "vec3 sgbRgb = raw;" in sgb
assert "uniform float u_authentic_correction;" in src
assert "bool gbaRawLcd" in src
assert "lin = mix(u_dark, u_light, response);" in src

def ink_coverage(x, y, center, west, north, blend=.38):
    h = blend * (center + west)
    v = blend * (center + north)
    return (1-x)*(1-y)*center + x*(1-y)*h + (1-x)*y*v

# At exact integer scale, both gap axes are 0 or 1 and results are the
# same as the original hard-threshold branch, including intersections.
for center in (0, .2, .7, 1):
    for west in (0, .2, 1):
        for north in (0, .5, 1):
            assert ink_coverage(0,0,center,west,north)==center
            assert abs(ink_coverage(1,0,center,west,north)-.38*(center+west))<1e-12
            assert abs(ink_coverage(0,1,center,west,north)-.38*(center+north))<1e-12
            assert ink_coverage(1,1,center,west,north)==0

def coverage(f, scale):
    integer = max(1, math.floor(scale+.5))
    width = 1 / integer
    half = .5 / max(scale,1)
    low, high = f-half, f+half
    area = max(0,min(high,width)-max(low,0))
    area += max(0,min(high,1+width)-max(low,1))
    return max(0,min(1,scale*area))

# The RG35XX H 480/144 = 3.33x GB Fit projection produces partial
# vertical gaps. They now contribute proportionally instead of vanishing.
scale = 480 / 144
samples = [coverage(((p+.5)/scale)%1,scale) for p in range(480)]
assert any(.05 < x < .5 for x in samples)
assert any(.5 < x < .95 for x in samples)
assert abs(sum(samples)/len(samples) - 1/3) < .01
for gap in samples:
    result = ink_coverage(gap,0,.8,.1,.2)
    assert min(.8,.38*(.8+.1))-1e-9 <= result <= .8+1e-9
assert ink_coverage(.25,0,1,1,1) != ink_coverage(.75,0,1,1,1)
print("PASS: Pocket Authentic routes to ink shader; Fit gaps blend continuously and integer masks agree")
