#!/usr/bin/env python3
"""Restore the *working Ver. 4* Pocket Color optical rasterization.

The RG35XX H Fit work replaced the original, binary LCD gap layout
and the Pocket Color/SGB ink blending. Subsequent attempts to compensate
changed the reflector math again, while tests checked invented mathematical
proxies instead of the older behavior that was actually working on hardware.

For color-Pocket modes (u_lcd.x = 2 or 3) reinstate EXACTLY the native
Ver. 4 dot geometry and old ink/neighbor/border blending. Keep the RG35H
fractional Fit improvements only for the original mono DMG/Pocket/Light,
plus independent Grid/Dot adjustments.

Keep the separate, already-working mGBA SGB color transform from Ver. 12/13:
source RGB is mGBA/SNES, not a grayscale Game Boy palette and not GBC
measured color. Both color Pocket modes share the original optical path.
Do not change models, cores, app settings or emulator options.
"""
from pathlib import Path

shader_path=Path("crates/slot-gfx/src/shaders.rs")
shader=shader_path.read_text()

# Revert the color models ONLY to Ver. 4's sampling/physical LCD gap mask.
before="""        if (u_lcd.x > 0.5) {
            // The core draws grey: how much ink each dot holds over the lit panel."""
after="""        // Pocket Color and Pocket SGB: the exact original Ver. 4
        // dot geometry that was visually verified before RG35XX H
        // Fit experiments. Leave monochrome Fit improvements intact.
        if (u_lcd.x > 1.5) {
            gap = step(f * span, vec2(1.0));
        }
        if (u_lcd.x > 0.5) {
            // The core draws grey: how much ink each dot holds over the lit panel."""
assert shader.count(before)==1,"Unexpected shader branch before restoring Pocket sampling"
shader=shader.replace(before,after,1)

# Color Pocket dots should not be changed by the new fractional/multi-neighbor
# ink blend. This is the real Ver. 4 expression, including the intersection.
before="""            float a = 0.0;
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
after="""            float a = 0.0;
            if (inside) {
                a = ink(centre);
                if (u_lcd.x > 1.5) {
                    // EXACT original Ver. 4 Pocket Color dot coverage.
                    if (gap.x + gap.y > 0.5) {
                        vec2 back = centre - (gap.x > 0.5 ? vec2(texel.x, 0.0) : vec2(0.0, texel.y));
                        float other = all(greaterThanEqual(back, u_pic.xy)) ? ink(back) : 0.0;
                        a = gap.x + gap.y > 1.5 ? 0.0 : u_ink.z * (a + other);
                    }
                } else if (gap.x + gap.y > 0.0) {
                    // Preserve fractional Fit ink blending only for DMG,
                    // mono Pocket and Light.
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
assert shader.count(before)==1,"Unexpected Pocket ink path before Ver. 4 recovery"
shader=shader.replace(before,after,1)

# Remove the series of unproven SGB reflector mix experiments (Ver. 11-13).
# The old shared color-Pocket formula is reintroduced exactly.
before="""                // Both Pocket models use the SAME ink-derived LCD optics,
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
after="""                // Restore the working Ver. 4 color-Pocket optical formula.
                // SGB's RGB palette differs; the LCD optics do not.
                c = clamp(mix(panelRgb, reflector, gapShare) * shadowShare, 0.0, 1.0);"""
assert shader.count(before)==1,"Expected Ver. 13 SGB experimental final mix"
shader=shader.replace(before,after,1)

# No changes to palette conversion, physical params, shader activation,
# or any other game mode.
assert shader.count("vec3 panelRgb = raw;")==1
assert "if (u_authentic_correction > 0.5 && u_lcd.x < 2.5) {" in shader
assert "vec3 sgbCode = floor(raw * 31.0 + vec3(0.5));" in shader
assert "float shadow = ink_near(" in shader
assert "vec2 gap = clamp(gapArea * span" in shader
assert "vec2 gapWidth = 1.0 / referenceSpan;" in shader
assert "float leftGap = u_ink.z * (a + west);" in shader
assert "vec3 reflector = u_authentic_correction > 0.5" in shader
shader_path.write_text(shader)
print("RESTORED: Ver. 4 optics for Pocket Color and SGB, kept mGBA RGB palette and other Fit improvements")
