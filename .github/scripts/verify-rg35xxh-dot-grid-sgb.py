#!/usr/bin/env python3
"""Validate Fit LCD masks and SGB CRT correction without hardware claims."""
from pathlib import Path
import math

shader = Path("crates/slot-gfx/src/shaders.rs").read_text()
core = Path("crates/slot/src/core.rs").read_text()

# SGB colors are TV/SNES RGB, not monochrome Pocket ink or GBC LCD colors.
sgb_start = shader.index("if (u_lcd.x > 2.5) {")
sgb_end = shader.index("        } else if (!inside) {", sgb_start)
sgb = shader[sgb_start:sgb_end]
assert "vec3 sgbRgb = raw;" in sgb
assert "if (u_authentic_correction > 0.5)" in sgb
assert "vec3 sgbCode = floor(raw * 31.0 + vec3(0.5));" in sgb
assert "vec3 sgbLow = sgbCode * (sgbCode + vec3(1.0)) / 510.0;" in sgb
assert "sgbRgb = mix(sgbLow, sgbHigh, step(vec3(16.5), sgbCode));" in sgb
assert "0.12 * sgbNeighborDark * (1.0 - sgbGap.x) * sgbGap.y;" in sgb
assert "c = clamp(sgbRgb * (1.0 - 0.62 * sgbGap.x)" in sgb
assert "* (1.0 - 0.42 * sgbGap.y) * sgbShadow, 0.0, 1.0);" in sgb
assert "vec2 sgbSoft = 0.15 * smoothstep" in sgb
assert "sgbGap = mix(sgbGap, 1.0 / max(span, vec2(1.0)), sgbSoft);" in sgb
assert "u_response" not in sgb and "float baseInk" not in sgb

# The SNES gamma ramp is Near's 32-step CRT approximation: the first
# 17 values are triangular; later values rise by 8 per code.
near_ramp = [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105, 120,
             136, 144, 152, 160, 168, 176, 184, 192, 200, 208, 216, 224,
             232, 240, 248, 255]
def crt_code(k: int) -> int:
    return min(255, k * (k + 1) // 2 if k <= 16 else 136 + 8 * (k - 16))
assert [crt_code(k) for k in range(32)] == near_ramp
assert crt_code(0) == 0 and crt_code(31) == 255
assert crt_code(8) != round(8 * 255 / 31)  # ON visibly differs from OFF
assert "vec3 sgbHigh = min(" in sgb

# Gambatte always outputs source SGB palettes without GBC LCD filtering.
# SGB ON/OFF correction belongs to the shader instead of the emulator core.
assert 'GbColors::SgbAuto => true,' in core
assert 'choice.core_name().starts_with("SGB ")' in core
assert 'core.set_option(key, if sgb_palette { "disabled" } else { value });' in core

# Original Authentic physical GBA/GBC color response and raw RGB OFF remain.
assert "lin = mix(u_dark, u_light, response);" in shader
assert "bool gbaRawLcd =" in shader
assert "uniform float u_authentic_correction;" in shader
assert "float stripeStrength = lcd_stripe" in shader
assert "mediump vec3 lit =" in shader
assert "vec2 dotSpan = u_rect.zw * u_fbo / (u_uv.zw * u_src);" in shader
assert "float dotMask = mix(1.0, mix(1.2 * mid, sum, 0.85), 0.85);" in shader
assert "c *= mix(dotMask, 0.47, 0.15 * dotFit);" in shader

# Grid coverage: union of vertical and horizontal bands. With fractional
# coverage, max(x,y) is not the union, and blending to a constant destroys it.
assert "float unionCoverage = edge.x + edge.y - edge.x * edge.y;" in shader
assert "float gridCoverage = mix(max(edge.x, edge.y), unionCoverage, gridFit);" in shader
for x in (0, .12, .33, .67, 1):
    for y in (0, .12, .33, .67, 1):
        u = x + y - x*y
        assert max(x,y)-1e-10 <= u <= 1+1e-10
        assert abs(u - (1 - (1-x)*(1-y))) < 1e-10

def fade(scale: float) -> float:
    v = abs(scale - math.floor(scale + .5))
    t = max(0., min(1., (v - .03) / (.28 - .03)))
    return t*t*(3-2*t)

# Preserve original Dot/Grid rendering at integer scales.
for k in range(2, 7):
    assert fade(k) == 0.
    for mask in (.07, .2, .47, .85, 1.0):
        assert mask*(1-.15*fade(k)) + .47*.15*fade(k) == mask
    for x in (0, .2, .6, 1):
        for y in (0, .2, .6, 1):
            assert max(x,y)*(1-fade(k))+(x+y-x*y)*fade(k)==max(x,y)

for src, dst in ((240,640), (160,427), (160,533), (144,480)):
    scale = dst / src
    a = .15 * fade(scale)
    assert .12 < a <= .15, (src,dst,a)
    for original in (.1,.3,.8,.9):
        smoothed=(1-a)*original+a*.47
        assert abs(smoothed-.47)>abs(original-.47)*.8

# SGB 1-output-pixel gaps are coverage weighted at fractional Fit scales.
def cov(phase:float,scale:float)->float:
    return min(1.,max(0.,1-abs(phase-.5))+max(0.,1-abs(phase-scale-.5)))
for k in (2,3,4,5):
    for i in range(k):
        assert abs(cov(i+.5,k)-float(i==0))<1e-9
for src,dst in ((160,533),(144,480)):
    scale=dst/src
    seq=[cov(((i+.5)/scale%1)*scale,scale) for i in range(dst)]
    assert any(.02<x<.98 for x in seq)
    assert abs(sum(seq)/len(seq)-1/scale) < .006

print("PASS: stronger Fit masks, exact SNES gamma ramp and visible SGB Pocket dot separation")
