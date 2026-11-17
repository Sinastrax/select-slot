#!/usr/bin/env python3
"""Fit mask regression and isolation checks for safe Ver. 5 candidate."""
from pathlib import Path

shader = Path("crates/slot-gfx/src/shaders.rs").read_text()
assert "vec2 phase = f * span;" in shader
assert "clamp(vec2(1.5) - phase, vec2(0.0), vec2(1.0))" in shader
assert "clamp(phase - (span - vec2(0.5)), vec2(0.0), vec2(1.0))" in shader
assert "authentic_gap_coverage(" not in shader, "Crashing Ver. 5 GLSL helper retained"
assert "if (u_lcd.x > 0.5) {" in shader, "Monochrome GB ink must stay untouched"
assert "lin = mix(u_dark, u_light, response);" in shader
assert "bool gbaRawLcd =" in shader
assert "uniform float u_authentic_correction;" in shader

# No changes to upstream LCD-grid rendering/precision in this candidate.
start = shader.index("    } else if (u_mode > 6.5) {")
end = shader.index("    } else if (u_mode > 4.5) {", start)
lcd = shader[start:end]
assert lcd.count("mediump ") >= 10, "The previously altered LCD-grid precision must be restored"

def mask(phase, span):
    return min(1., max(0., min(1., 1.5 - phase)) +
               max(0., min(1., phase - (span - .5))))

# At each exact integer scale, the mask stays 1 on the first display pixel,
# zero on all other output pixels, identical to Ver. 4's hard step().
for span in range(2, 7):
    for i in range(span):
        at = i + .5
        want = float(i == 0)
        assert abs(mask(at, span) - want) < 1e-9, (span, i, mask(at, span))

# For the 640px RG35XX H screen, Fit yields 2.666.. output px per GBA px.
# At that scale the trailing boundary is partially covered instead of being
# arbitrarily treated as either fully dark or fully bright.
for src, dest in ((240, 640), (160, 427)):
    span = dest / src
    pixels = [mask(((i + .5) / span % 1) * span, span) for i in range(dest)]
    assert any(0.01 < x < .99 for x in pixels), (src, dest)
    assert abs(sum(pixels)/len(pixels) - (1/span)) < .006, (src, dest)
    assert 0 <= min(pixels) <= max(pixels) <= 1

print("PASS: integer 2x..6x unchanged; fractional Fit masks partially covered; standard LCD shader untouched")
