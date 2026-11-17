#!/usr/bin/env python3
"""Band-limit 640x480 Fit LCD masks without changing integer-scale rendering.

Apply after fix-authentic-colour-reflection.py, which owns the model colour
calibration. This patch operates on geometry and shader arithmetic only.
"""
from pathlib import Path

p = Path("crates/slot-gfx/src/shaders.rs")
source = p.read_text()


def replace_once(old: str, new: str, label: str) -> None:
    global source
    count = source.count(old)
    assert count == 1, f"{label}: expected one insertion point, found {count}"
    source = source.replace(old, new, 1)


# The original GBA/GBC Authentic gap is a hard, single-framebuffer-pixel step.
# At a Fit scale such as 640/240 = 2 2/3, some emulated pixels then get an
# entire dark gap sample and others get none. Integrate the 1-output-pixel-wide
# gap over each destination pixel instead. This matches the old exact binary
# mask at integer scales 2x/3x/4x but smooths fractional coverage.
# Keep monochrome GB dot/ink sampling unchanged: its neighbour lookup chooses
# a discrete neighbouring source pixel and must not use fractional gap flags.
anchor = """vec3 lcd_ramp(vec3 x) {
    vec3 u = fract(x + 0.5) - 0.5;
    return u - 2.0 * u * abs(u);
}
void main() {"""
replacement = """vec3 lcd_ramp(vec3 x) {
    vec3 u = fract(x + 0.5) - 0.5;
    return u - 2.0 * u * abs(u);
}
// The fraction of a destination pixel covered by the source pixel's
// one-output-pixel-wide leading LCD gap. Also integrate the neighbouring
// gap when a sample straddles a source pixel boundary; unlike hard step(),
// this stays phase-stable at fractional Fit scales.
float authentic_gap_coverage(float phase, float outputPerSource) {
    float scale = max(outputPerSource, 1.0);
    float half = 0.5 / scale;
    float width = 1.0 / scale;
    float lo = phase - half;
    float hi = phase + half;
    float current = max(0.0, min(hi, width) - max(lo, 0.0));
    float previous = max(0.0, min(hi, width - 1.0) - max(lo, -1.0));
    float next = max(0.0, min(hi, width + 1.0) - max(lo, 1.0));
    return clamp((current + previous + next) * scale, 0.0, 1.0);
}
void main() {"""
replace_once(anchor, replacement, "Authentic gap coverage helper")

replace_once(
    """        vec2 gap = step(f * span, vec2(1.0));
        if (u_lcd.x > 0.5) {""",
    """        vec2 gap = step(f * span, vec2(1.0));
        if (u_lcd.x < 0.5) {
            // GBA and GBC colour LCD: resolve subpixel gaps at actual
            // destination resolution instead of rounding to whole pixels.
            gap = vec2(authentic_gap_coverage(f.x, span.x),
                       authentic_gap_coverage(f.y, span.y));
        }
        if (u_lcd.x > 0.5) {""",
    "GBA/GBC Authentic gap selection",
)

# The LCD-grid shader is used instead of fixed 3x LCD on 640x480 panels.
# Its 3-channel integrator relies on fractional source pixel coordinates.
# Explicit 'mediump' truncates them severely around X=200 on mobile GPUs,
# producing uneven stripes/bands with fractional Fit scales. Use the fragment
# shader's highest available default float precision instead (highp when
# GL_FRAGMENT_PRECISION_HIGH exists; mediump only on older GPUs without it).
lcd_start = source.index("    } else if (u_mode > 6.5) {")
lcd_end = source.index("    } else if (!inside) {", lcd_start)
block = source[lcd_start:lcd_end]
assert block.count("mediump ") >= 10, "LCD-grid block precision annotations changed"
new_block = block.replace("mediump ", "")
assert "mediump " not in new_block
source = source[:lcd_start] + new_block + source[lcd_end:]

assert source.count("authentic_gap_coverage(") == 3
assert "lin = mix(u_dark, u_light, response);" in source, "Historic colour calibration was lost"
assert "bool gbaRawLcd = " in source, "Uncorrected GBA brightness fix was lost"
assert "if (u_lcd.x > 0.5)" in source, "GB/Pocket ink geometry was lost"
p.write_text(source)
print("Fit LCD sampling fixed: coverage-weighted GBA/GBC Authentic gaps and precise LCD-grid stripes")
