#!/usr/bin/env python3
"""Match Authentic's integer-scale reference geometry at fractional Fit sizes.

The physical display's noninteger output coverage is averaged analytically,
but the logical LCD gap retains the same 1-in-N pixel width as its nearest
integer reference scale. This avoids using one *output* pixel as the gap at
every scale, which changes the apparent LCD geometry under Fit.

Pocket SGB also bypasses the expensive monochrome ink/shadow work entirely:
the previous pipeline calculated it, then overwrote it with the SGB RGB path.
No added multipass rendering, derivative extensions or GLES precision changes.
"""
from pathlib import Path
import re

p = Path("crates/slot-gfx/src/shaders.rs")
shader = p.read_text()

def replace_once(old: str, new: str, what: str):
    global shader
    count = shader.count(old)
    assert count == 1, f"{what}: expected one match, got {count}"
    shader = shader.replace(old, new, 1)

# Move the existing SGB RGB rendering to its own branch *before* Pocket's
# monochrome ink/reflector/16-tap shadow. Preserve the exact current color
# correction, neighboring-dot shadow and glass compositing below the branch.
header = "                if (u_lcd.x > 2.5) {\n"
tail = "                }\n            }\n        } else if (!inside) {"
assert shader.count(header) == 1, "Expected one SGB override"
start = shader.index(header)
end = shader.index(tail, start)
sgb_body = shader[start + len(header):end]
assert "vec3 sgbRgb = raw;" in sgb_body
assert "u_authentic_correction > 0.5" in sgb_body
assert "sgbNeighborDark" in sgb_body
shader = shader[:start] + shader[end + len("                }\n"):]
old_gap_start = "                    vec2 sgbPhase = f * span;\n"
old_gap_end = "                    sgbGap = mix(sgbGap, 1.0 / max(span, vec2(1.0)), sgbSoft);\n"
assert sgb_body.count(old_gap_start) == 1
assert sgb_body.count(old_gap_end) == 1
i = sgb_body.index(old_gap_start)
j = sgb_body.index(old_gap_end, i) + len(old_gap_end)
sgb_body = sgb_body[:i] + "                    vec2 sgbGap = gap;\n" + sgb_body[j:]

# Reference-width gap, with analytic area coverage of each output pixel.
# The native LCD pixel's separator is 1/N of a source pixel, where N is the
# nearest integer output scale. A Fit ratio 8/3 keeps 3x LCD geometry.
# At exact integer scale the old hard step is retained explicitly.
gap_block = """        // Treat the LCD mask as an integer-scale reference picture, then
        // integrate each output pixel's overlap with the logical dot gaps.
        // Source pixel position is f in [0,1); output footprint is 1/span.
        vec2 referenceSpan = max(floor(span + vec2(0.5)), vec2(1.0));
        vec2 gapWidth = 1.0 / referenceSpan;
        vec2 halfFootprint = 0.5 / max(span, vec2(1.0));
        vec2 low = f - halfFootprint;
        vec2 high = f + halfFootprint;
        vec2 gapArea =
            max(vec2(0.0), min(high, gapWidth) - max(low, vec2(0.0)))
          + max(vec2(0.0), min(high, vec2(1.0) + gapWidth) - max(low, vec2(1.0)));
        vec2 gap = clamp(gapArea * span, vec2(0.0), vec2(1.0));
        // Preserve the original sample-exact result at any integer scale.
        vec2 integralScale = vec2(1.0) -
            step(vec2(0.0005), abs(span - referenceSpan));
        gap = mix(gap, step(f * span, vec2(1.0)), integralScale);
        if (u_lcd.x > 2.5) {
            // Dedicated SGB branch: skip monochrome Pocket ink, gap
            // neighbours and multi-tap reflector shadows completely.
            if (inside) {
                vec3 raw = texture2D(u_game, centre).rgb;
""" + sgb_body + """            } else {
                c = pow(u_light, vec3(1.0 / 2.2));
            }
        } else if (u_lcd.x > 0.5) {"""

old = re.compile(
    r"        vec2 gap = step\(f \* span, vec2\(1\.0\)\);\n"
    r"        if \(u_lcd\.x < 0\.5\) \{[\s\S]*?"
    r"        if \(u_lcd\.x > 0\.5\) \{"
)
shader, count = old.subn(lambda m: gap_block, shader, count=1)
assert count == 1, f"Authentic gap anchor: {count} matches"

# Before this fix, brightness compensation assumed the physical gap was
# 1/output-scale wide. The gap is now 1/reference-scale wide, so use the
# SAME reference for the bright pixel-cell average. No color transfer,
# panel black/white point or correction toggle is changed.
replace_once(
    "vec2 thin = min(1.0 / span, vec2(1.0));",
    "vec2 thin = min(1.0 / referenceSpan, vec2(1.0));",
    "Authentic brightness / grid reference consistency",
)

# The standard LCD effect already integrates subpixel stripes over output
# coverage analytically. Remove the extra fractional-specific attenuation,
# which distorts it relative to integer scaling.
lcd_begin = """    } else if (u_mode > 6.5) {
        vec2 lcdSpan = u_rect.zw * u_fbo / (u_uv.zw * u_src);
        float stripeFractional = abs(lcdSpan.x - floor(lcdSpan.x + 0.5));
        float stripeStrength = lcd_stripe
            * (1.0 - 0.15 * smoothstep(0.03, 0.28, stripeFractional));
        vec2 hp = 0.5 * u_uv.zw * u_src / (u_rect.zw * u_fbo);"""
lcd_new = """    } else if (u_mode > 6.5) {
        vec2 hp = 0.5 * u_uv.zw * u_src / (u_rect.zw * u_fbo);"""
replace_once(lcd_begin, lcd_new, "Restore source-relative LCD subpixel integration")
lcd_start = shader.index("    } else if (u_mode > 6.5) {")
lcd_end = shader.index("    } else if (u_mode > 4.5) {", lcd_start)
lcd = shader[lcd_start:lcd_end]
assert lcd.count("stripeStrength * ") == 2
lcd = lcd.replace("stripeStrength * ", "lcd_stripe * ")
shader = shader[:lcd_start] + lcd + shader[lcd_end:]

assert shader.count("if (u_lcd.x > 2.5) {") == 1
assert "if (u_lcd.x > 2.5) {\n            // Dedicated SGB branch" in shader
assert shader.count("sgbNeighborDark") == 2
assert "if (u_lcd.x > 1.5 && inside)" in shader  # Pocket Color untouched
assert "lin = mix(u_dark, u_light, response);" in shader
assert "bool gbaRawLcd" in shader
assert "uniform float u_authentic_correction;" in shader
assert lcd.count("mediump ") >= 10
p.write_text(shader)
print("Applied native-pixel integer-reference Fit geometry, and independent fast Pocket SGB rendering")
