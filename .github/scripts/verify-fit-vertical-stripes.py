#!/usr/bin/env python3
"""Regression checks for fractional Fit vertical LCD stripe attenuation.

Both Authentic and LCD-grid must preserve their complete original
integer-scale appearance; source geometry, calibrated color and brightness
must not be changed. Numerical checks use source/destination pixel coverage.
"""
from pathlib import Path
import math

shader = Path("crates/slot-gfx/src/shaders.rs").read_text()
assert shader.count("float fractional = abs(span.x - floor(span.x + 0.5));") == 1
assert "float soften = 0.85 * smoothstep(0.03, 0.28, fractional);" in shader
assert "gap.x = mix(gap.x, min(1.0, 1.0 / max(span.x, 1.0)), soften);" in shader
assert shader.count("float stripeFractional = abs(lcdSpan.x - floor(lcdSpan.x + 0.5));") == 1
assert "float stripeStrength = lcd_stripe" in shader
assert "stripeStrength * (lcd_ramp(-lcd_centres) - gl0)" in shader
assert "stripeStrength * (gr1 - gr0)" in shader
assert "lin = mix(u_dark, u_light, response);" in shader
assert "bool gbaRawLcd =" in shader
assert "uniform float u_authentic_correction;" in shader

lcd_start = shader.index("    } else if (u_mode > 6.5) {")
lcd_end = shader.index("    } else if (u_mode > 4.5) {", lcd_start)
lcd = shader[lcd_start:lcd_end]
assert lcd.count("mediump ") >= 10, "Preserve known-good LCD-grid precision"
assert "mediump vec3 lit =" in lcd, "Preserve area integration in LCD-grid"
assert "mediump float wt" in lcd and "mediump float wb" in lcd


def fade(scale: float) -> float:
    distance = abs(scale - math.floor(scale + 0.5))
    t = max(0.0, min(1.0, (distance - 0.03) / (0.28 - 0.03)))
    return 0.85 * t * t * (3.0 - 2.0 * t)


def gap(phase: float, scale: float) -> float:
    current = max(0.0, 1.0 - abs(phase - 0.5))
    previous = max(0.0, 1.0 - abs(phase - scale - 0.5))
    return min(1.0, current + previous)


def softened(phase: float, scale: float) -> float:
    weight = fade(scale)
    return gap(phase, scale) * (1 - weight) + weight / scale


# Integer scales must remain exactly the pre-change picture, for both modes.
for scale in range(2, 7):
    assert fade(scale) == 0.0
    assert abs(0.9 * (1 - fade(scale)) - 0.9) < 1e-12
    for i in range(scale):
        centre = i + 0.5
        assert softened(centre, scale) == gap(centre, scale), (scale, i)

# For fractional Fit, reduce the vertical contrast while keeping the mean
# one-destination-pixel gap coverage: do not globally lighten/darken GBA.
for src, output in ((240, 640), (160, 427), (160, 533)):
    scale = output / src
    before = []
    after = []
    for x in range(output):
        phase = ((x + 0.5) / scale % 1.0) * scale
        before.append(gap(phase, scale))
        after.append(softened(phase, scale))
    assert fade(scale) > 0.7, (src, output, fade(scale))
    assert max(after) - min(after) < (max(before) - min(before)) * 0.3
    assert abs(sum(after) / output - 1.0 / scale) < 0.005
    assert abs(sum(before) / output - sum(after) / output) < 0.005

# At an exactly 3x output scale, Authentic is identical to the original.
# At Fit, standard LCD-grid subpixel intensity falls to 15% of its old
# strength, with its horizontal LCD scanline effects unchanged.
assert abs(0.9 * (1 - fade(640/240)) - 0.135) < .001

print("PASS: integer LCD grids unchanged, Fit vertical contrast reduced, average brightness preserved")
