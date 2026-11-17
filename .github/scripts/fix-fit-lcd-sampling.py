#!/usr/bin/env python3
"""Minimal, GLES2-compatible antialiasing of Authentic's fractional LCD gaps.

Unlike the first Ver. 5 candidate, do NOT add any GLSL functions or change
precision annotations in the standard LCD-grid effect. The old candidate
caused a boot loop on RG35XX H; root cause is not yet established, so only
one small shader expression is changed for hardware testing.
"""
from pathlib import Path

p = Path("crates/slot-gfx/src/shaders.rs")
shader = p.read_text()

old = """        vec2 gap = step(f * span, vec2(1.0));
        if (u_lcd.x > 0.5) {"""
new = """        vec2 gap = step(f * span, vec2(1.0));
        if (u_lcd.x < 0.5) {
            // Antialias only fractional Fit colour-LCD gaps. One framebuffer
            // pixel covers part of the next game pixel at non-integer scales.
            // Both ends of the interval contribute to its dark gap.
            // The result is identical to step() at exact integer scales.
            vec2 phase = f * span;
            gap = min(vec2(1.0),
                max(vec2(0.0), vec2(1.0) - abs(phase - vec2(0.5)))
                + max(vec2(0.0), vec2(1.0) - abs(phase - span - vec2(0.5))));
        }
        if (u_lcd.x > 0.5) {"""

assert shader.count(old) == 1, "Expected one original Authentic LCD-gap mask"
shader = shader.replace(old, new, 1)
assert "authentic_gap_coverage(" not in shader, "Old heavy GLSL helper is still present"
assert "lin = mix(u_dark, u_light, response);" in shader, "Authentic calibration changed"
assert "bool gbaRawLcd =" in shader, "Ver. 4 uncorrected GBA luminance missing"
assert "u_mode > 6.5" in shader, "Standard LCD-grid mode disappeared"
p.write_text(shader)
print("Applied lightweight Fit LCD gap antialiasing; standard LCD-grid shader unchanged")
