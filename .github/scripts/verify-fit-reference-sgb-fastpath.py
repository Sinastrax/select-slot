#!/usr/bin/env python3
"""Check integer-reference LCD geometry and fast SGB branch after patch merge.

These are source plus analytical rasterization checks, not a hardware-frame
comparison or benchmark. GLSL must separately pass GLES2 compile and full CI.
"""
from pathlib import Path
import math

shader = Path("crates/slot-gfx/src/shaders.rs").read_text()

def required(token: str, label: str):
    assert token in shader, f"Missing {label}: {token}"

required("vec2 referenceSpan = max(floor(span + vec2(0.5)), vec2(1.0));", "virtual integer scale")
required("vec2 gapWidth = 1.0 / referenceSpan;", "pixel gap width in source-pixel units")
required("vec2 halfFootprint = 0.5 / max(span, vec2(1.0));", "output footprint")
required("vec2 gapArea =", "coverage integral")
required("vec2 thin = min(1.0 / referenceSpan, vec2(1.0));", "matching brightness compensation")
required("gap = mix(gap, step(f * span, vec2(1.0)), integralScale);", "integer pixel identity")
assert "stripeStrength" not in shader, "LCD stripe attenuation survived"
assert "vec3 lit =" in shader and "lcd_stripe * (gr1 - gr0)" in shader
assert shader.count("mediump ") >= 10

sgb_at = shader.index("        if (u_lcd.x > 2.5) {")
ink_at = shader.index("        } else if (u_lcd.x > 0.5) {", sgb_at)
color_at = shader.index("        } else if (!inside) {", ink_at)
sgb = shader[sgb_at:ink_at]
assert "vec3 raw = texture2D(u_game, centre).rgb;" in sgb
assert "vec2 sgbGap = gap;" in sgb
assert "sgbCode" in sgb and "u_authentic_correction > 0.5" in sgb
assert "sgbNeighborDark" in sgb
assert "ink(" not in sgb and "ink_near(" not in sgb, "SGB still does Pocket monochrome ink processing"
assert shader.count("if (u_lcd.x > 2.5) {") == 1
assert "float a = 0.0;" in shader[ink_at:color_at]
assert "if (u_lcd.x > 1.5 && inside)" in shader[ink_at:color_at]
required("lin = mix(u_dark, u_light, response);", "GBA/GBC calibrated ON")
required("bool gbaRawLcd =", "GBA uncorrected OFF")
required("uniform float u_authentic_correction;", "Authentic correction toggle")

def coverage(f, scale):
    reference = max(1, math.floor(scale + 0.5))
    width = 1.0 / reference
    half = .5 / max(scale, 1)
    low, high = f - half, f + half
    a = max(0, min(high, width) - max(low, 0))
    b = max(0, min(high, 1 + width) - max(low, 1))
    value = max(0, min(1, (a + b) * scale))
    if abs(scale - reference) < .0005:
        value = float(f * scale <= 1.0)
    return value

# At 2x through 6x, the exact old 1-pixel band is preserved.
for n in range(2, 7):
    for i in range(n):
        f = (i + 0.5) / n
        assert abs(coverage(f, n) - float(i == 0)) < 1e-10

# Fit operates on the *same* logical 3x cell even though it is scaled to
# 640 (GBA) or ~533 (GB) physical pixels. Integrated black-gap coverage
# matches direct box downsampling of an ideal virtual 3x mask.
for src, width in ((240, 640), (160, 427), (160, 533), (144, 480)):
    scale = width / src
    ref = max(1, math.floor(scale + 0.5))
    values = [coverage(((i + .5) / scale) % 1.0, scale) for i in range(width)]
    assert 0 <= min(values) and max(values) <= 1
    assert any(.001 < v < .999 for v in values), (src, width)
    assert abs(sum(values) / len(values) - 1 / ref) < .008, (src, width)
    # No arbitrary per-scale 15%/85% fade; preserve logical gap darkness.
    assert max(values) - min(values) > .8

# The old scheme fixed the band at one *physical* output pixel, changing
# its relative width at 8/3x. The reference scheme keeps exactly 1/3.
assert abs((1 / (640/240)) - (1/3)) > .03

print("PASS: Authentic Fit matches logical integer-reference mask, SGB fast branch skips ink, LCD retains analytic integration")
