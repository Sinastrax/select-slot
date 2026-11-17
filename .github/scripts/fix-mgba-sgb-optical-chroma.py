#!/usr/bin/env python3
"""Keep actual SGB RGB in each Pocket LCD dot, and show real Fit dot gaps.

Run after fix-pocket-sgb-parity.py. Ver. 11 mixed the core's SGB palette
toward the Pocket's neutral reflector using a luminance-derived gapShare,
which comes from interpreting the already-colorized RGB as grayscale ink.
On some SGB palettes that loses the source chroma and obscures the grid.

The existing Pocket Color renderer, its physical look, 4-neighbor shadow,
ghosting, reflection and all other shader modes remain untouched.
Use the *same analytically integrated integer-reference dot gap geometry*
as Pocket Color, but use actual geometric coverage for the SGB
source-RGB -> reflector mix. Therefore interior dots remain SGB RGB,
while only true dot separators show the Pocket panel/reflector.
"""
from pathlib import Path

path = Path("crates/slot-gfx/src/shaders.rs")
source = path.read_text()
old = "                c = clamp(mix(panelRgb, reflector, gapShare) * shadowShare, 0.0, 1.0);"
new = """                if (u_lcd.x > 2.5) {
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
assert source.count(old) == 1, "Expected Ver. 11 Pocket Color/SGB color mixer"
assert "vec2 gap = clamp(gapArea * span, vec2(0.0), vec2(1.0));" in source
assert "vec3 panelRgb = raw;" in source
assert "vec3 sgbCode = floor(raw * 31.0 + vec3(0.5));" in source
assert "if (u_lcd.x > 1.5 && inside)" in source
assert "float leftGap = u_ink.z * (a + west);" in source
assert "float shadow = ink_near(" in source
assert "float gapShare = clamp((dotLuma - baseLuma)" in source
source = source.replace(old,new,1)
assert source.count("float sgbGapShare = gap.x + gap.y - gap.x * gap.y;") == 1
path.write_text(source)
print("SGB colors stay inside actual LCD dots, with Pocket reference gap geometry and shared shadow/reflection")
