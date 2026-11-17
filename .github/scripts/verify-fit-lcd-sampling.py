#!/usr/bin/env python3
"""Check fractional Fit LCD geometry and preserve exact integer-size masks."""
from pathlib import Path
from math import floor

shader = Path("crates/slot-gfx/src/shaders.rs").read_text()
assert "float authentic_gap_coverage(float phase, float outputPerSource)" in shader
assert "gap = vec2(authentic_gap_coverage(f.x, span.x)," in shader
assert "if (u_lcd.x > 0.5)" in shader, "Monochrome model should keep original sampling"
start = shader.index("    } else if (u_mode > 6.5) {")
end = shader.index("    } else if (!inside) {", start)
lcd = shader[start:end]
assert "mediump " not in lcd, "LCD-grid subpixel precision must use default highp where supported"
assert "vec3 lit = " in lcd, "LCD-grid weighted mask was lost"

def coverage(phase: float, scale: float) -> float:
    scale = max(scale, 1)
    half = .5 / scale
    width = 1 / scale
    lo, hi = phase - half, phase + half
    c = max(0.0, min(hi, width) - max(lo, 0.0))
    prev = max(0.0, min(hi, width - 1) - max(lo, -1))
    nxt = max(0.0, min(hi, width + 1) - max(lo, 1))
    return min(1.0, max(0.0, (c + prev + nxt) * scale))

# At exact integer scaling a native 1-pixel gap stays exactly a binary
# 1-pixel gap. Neither legacy integer nor 3x RG SP views change.
for scale in (2, 3, 4, 5, 6):
    for i in range(scale):
        phase = (i + .5) / scale
        expected = 1.0 if i == 0 else 0.0
        assert abs(coverage(phase, scale) - expected) < 1e-8, (scale, i)

# 640x480 RG35XX H / RGB30 Fit content: a 240x160 GBA image is
# 640/240=2.666.. horizontally, and around 427/160 vertically.
# Fractional coverage produces partial alpha while preserving the intended
# proportion of dark gaps, instead of rounding every sample to 0 or 1.
for src, dest in ((240, 640), (160, 427), (160, 480)):
    scale = dest / src
    samples = [coverage(((i + .5) / scale) % 1, scale) for i in range(dest)]
    assert any(.01 < v < .99 for v in samples), (src, dest)
    actual = sum(samples) / len(samples)
    expected = 1 / scale
    assert abs(actual - expected) < .005, (src, dest, actual, expected)
    assert min(samples) >= 0.0 and max(samples) <= 1.0

# The ON/OFF mode and the separate reflection option still use the
# previously verified Authentic routes; geometry fix must not replace them.
assert "uniform float u_authentic_correction;" in shader
assert "lin = mix(u_dark, u_light, response);" in shader
print("PASS: 640x480 Fit masks are coverage-weighted; integer 2x-6x masks unchanged")
