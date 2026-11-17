#!/usr/bin/env python3
"""Fix fractional-Fit Dot/Grid aliasing and preserve Super Game Boy source RGB.

Run after the existing Authentic and Fit patch scripts. The RG35XX H's
640x480 panel makes GB output ~3.33x and GBA output ~2.67x in Fit mode.
The original Dot/Grid contrast patterns alias when sampled at non-integer
scale. Retain the optical mask's spatial average; reduce only variation
at non-integer pixel scales. Exact integer scales remain unchanged.

Pocket SGB previously processed coloured SGB RGB data as monochrome Pocket
ink and applied the physical GBC panel response to SNES colors. Neither is
valid. Keep the core's palette exactly, then render a mild, anti-aliased
Pocket-style pixel separation independent of palette brightness. This works
for both cores; Gambatte provides presets, mGBA provides SGB emulation.

No extra GLSL functions, changes to precision declarations, or new textures.
"""
from pathlib import Path

path = Path("crates/slot-gfx/src/shaders.rs")
shader = path.read_text()

def replace(old: str, new: str, label: str) -> None:
    global shader
    count = shader.count(old)
    assert count == 1, f"{label}: expected one anchor, got {count}"
    shader = shader.replace(old, new, 1)

# Existing SGB path uses ink() and its shadow calculations on fully colored
# core RGB values. e.g. pure red has luminance 1/3 and is treated as dark ink.
# Override the final SGB RGB result only, without disturbing Pocket Color
# or monochrome Pocket rendering. The final sheen/shade pass is unaffected.
replace(
    "                c = clamp(mix(panelRgb, reflector, gapShare) * shadowShare, 0.0, 1.0);",
    """                c = clamp(mix(panelRgb, reflector, gapShare) * shadowShare, 0.0, 1.0);
                if (u_lcd.x > 2.5) {
                    // SGB palettes are already rendered to TV/SNES RGB by
                    // the core. No GBC LCD conversion or grayscale ink mask.
                    // Use a spatially integrated Pocket-style pixel gap,
                    // avoiding hard 1-pixel aliasing at fractional Fit.
                    vec2 sgbPhase = f * span;
                    vec2 sgbGap = min(vec2(1.0),
                        max(vec2(0.0), vec2(1.0) - abs(sgbPhase - vec2(0.5)))
                        + max(vec2(0.0), vec2(1.0) - abs(sgbPhase - span - vec2(0.5))));
                    vec2 sgbFraction = abs(span - floor(span + vec2(0.5)));
                    vec2 sgbSoft = 0.5 * smoothstep(vec2(0.03), vec2(0.28), sgbFraction);
                    sgbGap = mix(sgbGap, 1.0 / max(span, vec2(1.0)), sgbSoft);
                    c = raw * (1.0 - 0.28 * sgbGap.x) * (1.0 - 0.20 * sgbGap.y);
                }""",
    "Pocket SGB true-RGB rendering",
)

# Grid already analytically integrates a 1/3-pixel wide grid band across
# each destination pixel. Its max(X,Y) mask still creates disproportionately
# contrasting columns/rows at 2.67x or 3.33x. Fade the mask's variation
# toward the area-average of the union (5/9) only when scale is fractional.
replace(
    """        vec2 edge = (grid_band(f + hp) - grid_band(f - hp)) / (2.0 * hp);
        c *= 1.0 - 0.75 * max(edge.x, edge.y);""",
    """        vec2 edge = (grid_band(f + hp) - grid_band(f - hp)) / (2.0 * hp);
        vec2 gridSpan = u_rect.zw * u_fbo / (u_uv.zw * u_src);
        vec2 gridFraction = abs(gridSpan - floor(gridSpan + vec2(0.5)));
        float gridFit = smoothstep(0.03, 0.28, max(gridFraction.x, gridFraction.y));
        float gridCoverage = mix(max(edge.x, edge.y), 5.0 / 9.0, 0.55 * gridFit);
        c *= 1.0 - 0.75 * gridCoverage;""",
    "Grid anti-aliased fractional contrast",
)

# Dot uses a radial kernel and its neighbours, but only point samples the
# result at a single output-pixel position. This aliases strongly during
# fractional scaling. Reduce the spatial variation by 55% while retaining
# the original mean dot mask (~0.47 for typical bloom) and its shape.
# Same math at 2x/3x/4x integer scales (gridFit=0), including other devices.
replace(
    """        c = mix(c, mix(1.2 * c * mid, c * sum, 0.85), 0.85);""",
    """        vec2 dotSpan = u_rect.zw * u_fbo / (u_uv.zw * u_src);
        vec2 dotFraction = abs(dotSpan - floor(dotSpan + vec2(0.5)));
        float dotFit = smoothstep(0.03, 0.28, max(dotFraction.x, dotFraction.y));
        float dotMask = mix(1.0, mix(1.2 * mid, sum, 0.85), 0.85);
        c *= mix(dotMask, 0.47, 0.55 * dotFit);""",
    "Dot anti-aliased fractional contrast",
)

# Keep all established behaviors independent and prevent accidental shader
# cross-mode edits in future source merges.
assert shader.count("if (u_lcd.x > 2.5) {") >= 1
assert "lin = mix(u_dark, u_light, response);" in shader
assert "bool gbaRawLcd =" in shader
assert "uniform float u_authentic_correction;" in shader
assert "float stripeStrength = lcd_stripe" in shader
assert shader.count("mediump ") >= 10
path.write_text(shader)
print("Applied fractional Dot/Grid filtering and palette-preserving Pocket SGB geometry")
