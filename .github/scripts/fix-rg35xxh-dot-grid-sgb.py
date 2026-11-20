#!/usr/bin/env python3
"""Fix fractional-Fit Dot/Grid aliasing and preserve Super Game Boy source RGB.

Run after the existing Authentic and Fit patch scripts. The RG35XX H's
640x480 panel makes GB output ~3.33x and GBA output ~2.67x in Fit mode.
The original Dot/Grid contrast patterns alias when sampled at non-integer
scale. Retain the optical mask's spatial average; reduce only variation
at non-integer pixel scales. Exact integer scales remain unchanged.

Pocket SGB previously processed coloured SGB RGB data as monochrome Pocket
ink and applied the physical GBC panel response to SNES colors. Neither is
valid. Keep the core's palette exactly, then render visible, antialiased Pocket-style pixel separation and an independent
SGB/SNES CRT gamma setting; never use the GBC LCD calibration. This works
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
                    vec2 sgbSoft = 0.15 * smoothstep(vec2(0.03), vec2(0.28), sgbFraction);
                    sgbGap = mix(sgbGap, 1.0 / max(span, vec2(1.0)), sgbSoft);
                    // OFF uses SGB/SNES palette RGB without changing its hues.
                    // ON uses the 32-entry SNES CRT gamma ramp documented by
                    // Near (bsnes / Color Emulation), NOT the GBC LCD matrix.
                    // Values 0..16 are triangular numbers; 17..30 step by 8.
                    // The final SNES code 31 maps to 255, not 256.
                    vec3 sgbRgb = raw;
                    if (u_authentic_correction > 0.5) {
                        vec3 sgbCode = floor(raw * 31.0 + vec3(0.5));
                        vec3 sgbLow = sgbCode * (sgbCode + vec3(1.0)) / 510.0;
                        vec3 sgbHigh = min(
                            (vec3(136.0) + 8.0 * (sgbCode - vec3(16.0))) / 255.0,
                            vec3(1.0));
                        sgbRgb = mix(sgbLow, sgbHigh, step(vec3(16.5), sgbCode));
                    }
                    // Reinstate a visible Pocket-style gap and a gentle
                    // off-axis dot shadow. Unlike ink(), these operate on
                    // spatial geometry, not RGB interpreted as grayscale.
                    vec2 sgbAdjacent = clamp(
                        centre + vec2(texel.x, -texel.y),
                        u_pic.xy + 0.5 * texel, u_pic.zw - 0.5 * texel);
                    float sgbNeighborDark = 1.0 -
                        dot(texture2D(u_game, sgbAdjacent).rgb, luma_coeff);
                    float sgbShadow = 1.0 -
                        0.12 * sgbNeighborDark * (1.0 - sgbGap.x) * sgbGap.y;
                    c = clamp(sgbRgb * (1.0 - 0.62 * sgbGap.x)
                        * (1.0 - 0.42 * sgbGap.y) * sgbShadow, 0.0, 1.0);
                }""",
    "Pocket SGB true-RGB rendering",
)

# Grid already analytically integrates a 1/3-pixel wide grid band across
# each destination pixel. Its max(X,Y) mask still creates disproportionately
# contrasting columns/rows at 2.67x or 3.33x. Use the area-weighted union of horizontal and vertical grid coverage
# at fractional scales; don't fade the entire grid towards a constant.
replace(
    """        vec2 edge = (grid_band(f + hp) - grid_band(f - hp)) / (2.0 * hp);
        c *= 1.0 - 0.75 * max(edge.x, edge.y);""",
    """        vec2 edge = (grid_band(f + hp) - grid_band(f - hp)) / (2.0 * hp);
        vec2 gridSpan = u_rect.zw * u_fbo / (u_uv.zw * u_src);
        vec2 gridFraction = abs(gridSpan - floor(gridSpan + vec2(0.5)));
        float gridFit = smoothstep(0.03, 0.28, max(gridFraction.x, gridFraction.y));
        // The actual area covered by a vertical OR horizontal grid
        // band is their union. Max() exaggerated intersections and
        // flattening to 5/9 removed the visible grid at Fit scaling.
        float unionCoverage = edge.x + edge.y - edge.x * edge.y;
        float gridCoverage = mix(max(edge.x, edge.y), unionCoverage, gridFit);
        c *= 1.0 - 0.75 * gridCoverage;""",
    "Grid anti-aliased fractional contrast",
)

# Dot uses a radial kernel and its neighbours, but only point samples the
# result at a single output-pixel position. This aliases strongly during
# fractional scaling. Reduce the spatial variation by only 15% while retaining
# the original mean dot mask (~0.47 for typical bloom) and its shape.
# Same math at 2x/3x/4x integer scales (gridFit=0), including other devices.
replace(
    """        c = mix(c, mix(1.2 * c * mid, c * sum, 0.85), 0.85);""",
    """        vec2 dotSpan = u_rect.zw * u_fbo / (u_uv.zw * u_src);
        vec2 dotFraction = abs(dotSpan - floor(dotSpan + vec2(0.5)));
        float dotFit = smoothstep(0.03, 0.28, max(dotFraction.x, dotFraction.y));
        float dotMask = mix(1.0, mix(1.2 * mid, sum, 0.85), 0.85);
        c *= mix(dotMask, 0.47, 0.15 * dotFit);""",
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

# Gambatte's SGB presets are intended for TV output. Its GBC LCD correction
# in "always" mode changes these SGB palettes incorrectly (libretro docs).
# This applies even when a user explicitly selects an SGB palette outside
# Authentic. Existing GBC game correction is unaffected.
core_path = Path("crates/slot/src/core.rs")
core = core_path.read_text()
old_core = """        Core::Gambatte => {
            core.set_option("gambatte_gb_hwmode", "Auto");
            for (key, value) in palette_options(which, palette.unwrap_or(GbColors::Auto)) {
                core.set_option(key, value);
            }
            if let Some((key, value)) = colour_option(which, platform, colour) {
                core.set_option(key, value);
            }
        }"""
new_core = """        Core::Gambatte => {
            core.set_option("gambatte_gb_hwmode", "Auto");
            for (key, value) in palette_options(which, palette.unwrap_or(GbColors::Auto)) {
                core.set_option(key, value);
            }
            // SGB colors target a TV, not the GBC LCD. In particular, Gambatte's
            // 'always' correction distorts SGB palettes. Includes SGB presets.
            let sgb_palette = platform == Platform::Gb && palette.is_some_and(|p| match p {
                GbColors::SgbAuto => true,
                GbColors::Palette(choice) => choice.core_name().starts_with("SGB "),
                GbColors::Auto => false,
            });
            if let Some((key, value)) = colour_option(which, platform, colour) {
                core.set_option(key, if sgb_palette { "disabled" } else { value });
            }
        }"""
assert core.count(old_core) == 1, "Expected Gambatte core options block changed"
core_path.write_text(core.replace(old_core, new_core, 1))

print("Restored visible Fit grid/dots and Pocket SGB separation with selectable SNES gamma; SGB core palette RGB remains uncorrected")
