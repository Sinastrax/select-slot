#!/usr/bin/env python3
"""Use fractional Pocket LCD gap coverage for its actual ink geometry.

Apply after fix-fit-reference-sgb-fastpath.py. Native Pocket/DMG/Light
(and Pocket Color) treated analytically integrated fractional gaps as binary
flags. At Fit, partially covered separators disappeared or snapped to full
pixel width. Blend the centre, left gap, upper gap and empty intersection by
their covered area. Integer-scale output is pixel-identical to before.

The SGB RGB fastpath, measured color correction, glass and other shader
modes are not modified.
"""
from pathlib import Path

path = Path("crates/slot-gfx/src/shaders.rs")
source = path.read_text()
old = """            float a = 0.0;
            if (inside) {
                a = ink(centre);
                if (gap.x + gap.y > 0.5) {
                    vec2 back = centre - (gap.x > 0.5 ? vec2(texel.x, 0.0) : vec2(0.0, texel.y));
                    float other = all(greaterThanEqual(back, u_pic.xy)) ? ink(back) : 0.0;
                    a = gap.x + gap.y > 1.5 ? 0.0 : u_ink.z * (a + other);
                }
            }"""
new = """            float a = 0.0;
            if (inside) {
                a = ink(centre);
                if (gap.x + gap.y > 0.0) {
                    // Each fractional gap covers a share of an LCD dot.
                    // The intersection of horizontal and vertical gaps has
                    // no ink. Exact integer-scale masks remain unchanged.
                    float west = 0.0;
                    if (gap.x > 0.0) {
                        vec2 leftDot = centre - vec2(texel.x, 0.0);
                        if (all(greaterThanEqual(leftDot, u_pic.xy))) {
                            west = ink(leftDot);
                        }
                    }
                    float north = 0.0;
                    if (gap.y > 0.0) {
                        vec2 upperDot = centre - vec2(0.0, texel.y);
                        if (all(greaterThanEqual(upperDot, u_pic.xy))) {
                            north = ink(upperDot);
                        }
                    }
                    float leftGap = u_ink.z * (a + west);
                    float upperGap = u_ink.z * (a + north);
                    a = (1.0 - gap.x) * (1.0 - gap.y) * a
                        + gap.x * (1.0 - gap.y) * leftGap
                        + (1.0 - gap.x) * gap.y * upperGap;
                }
            }"""
assert source.count(old) == 1, f"Expected one Pocket ink block, got {source.count(old)}"
assert "if (u_lcd.x > 2.5) {\n            // Dedicated SGB branch" in source
assert "vec2 gapWidth = 1.0 / referenceSpan;" in source
assert "lin = mix(u_dark, u_light, response);" in source
assert "uniform float u_authentic_correction;" in source
assert "vec2 thin = min(1.0 / referenceSpan, vec2(1.0));" in source
path.write_text(source.replace(old, new, 1))
print("Pocket LCD Fit separation uses fractional ink/gap coverage")
