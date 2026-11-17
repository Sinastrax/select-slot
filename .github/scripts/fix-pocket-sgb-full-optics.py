#!/usr/bin/env python3
"""Reuse Pocket Color's actual optical reflector response on SGB RGB pixels.

Ver. 12 replaced Pocket Color's ink-derived reflector coverage with the raw
geometric gap union (50% of pixels at 4x/3.33x Fit), effectively rendering a
different screen with a white checkerboard and muted optical shadow.

Use the SAME Pocket Color gapShare, shadowShare and physical model for BOTH
screens. A SGB-only physical-gap bound prevents saturated SGB RGB from
erroneously becoming a neutral reflector *inside* an LCD dot, the issue
that had drained the palette in Ver. 11. Color response stays untouched:
mGBA supplies SGB RGB, not the GBC calibrated response.
"""
from pathlib import Path

path=Path("crates/slot-gfx/src/shaders.rs")
shader=path.read_text()
before="""                if (u_lcd.x > 2.5) {
                    // mGBA has already rendered the cartridge's SGB palette.
                    // Never derive SGB color coverage from its RGB luminance:
                    // a saturated blue/red SGB color is not monochrome ink.
                    // The exact same fractional Fit pixel-gap geometry used
                    // by the Pocket renderer identifies the separator area.
                    float sgbGapShare = gap.x + gap.y - gap.x * gap.y;
                    c = clamp(mix(panelRgb, reflector, sgbGapShare)
                        * shadowShare, 0.0, 1.0);
                } else {
                    // Pocket Color's existing measured-color optics unchanged.
                    c = clamp(mix(panelRgb, reflector, gapShare)
                        * shadowShare, 0.0, 1.0);
                }"""
after="""                // Both Pocket models use the SAME ink-derived LCD optics,
                // reflected light, neighbor shadows, and final color blend.
                float pocketOpticalGapShare = gapShare;
                if (u_lcd.x > 2.5) {
                    // mGBA supplies pre-colorized SGB RGB. Unlike GBC RGB,
                    // highly saturated SNES colors must never be mistaken for
                    // a transparent dot outside a physical pixel gap.
                    // Bound only impossible reflector leakage; do not replace
                    // Pocket's optical gap calculation with a white grid.
                    float physicalPocketGap = gap.x + gap.y - gap.x * gap.y;
                    pocketOpticalGapShare = min(gapShare, physicalPocketGap);
                }
                c = clamp(mix(panelRgb, reflector, pocketOpticalGapShare)
                    * shadowShare, 0.0, 1.0);"""
assert shader.count(before)==1,"Expected Ver. 12 SGB raw geometric renderer"
assert shader.count("float gapShare = clamp((dotLuma - baseLuma) /")==1
assert shader.count("float shadowShare = clamp(dotLuma / max(baseLuma, 0.03), 0.0, 1.0);")==1
assert shader.count("vec3 panelRgb = raw;")==1
assert "vec3 sgbCode = floor(raw * 31.0 + vec3(0.5));" in shader
assert "vec2 gapWidth = 1.0 / referenceSpan;" in shader
assert "float shadow = ink_near(" in shader
shader=shader.replace(before,after,1)
path.write_text(shader)
print("PASS: Pocket Color and SGB share optical reflector+shadow response; SGB chroma bounded by true gap coverage")
