#!/usr/bin/env python3
"""Preserve visible LCD pixel separation with mild fractional-scale antialiasing.

At e.g. GBA 240 -> 640 pixels, a simulated one-output-pixel vertical LCD
gap repeats every 2 2/3 pixels and looks like a high-contrast column pattern.
The previous Fit fix antialiased gap edges, but vertical contrast persisted.
Preserve average gap coverage to avoid changing brightness or color response.

Keep monochrome GB Authentic and the calibrated color transformation intact.
For standard LCD-grid, reduce the per-channel vertical RGB stripe modulation
while retaining horizontal scanlines and area integration.

No new GLSL functions or precision changes (Ver. 5 boot regression).
"""
from pathlib import Path

path = Path("crates/slot-gfx/src/shaders.rs")
shader = path.read_text()


def replace_exact(old: str, new: str, label: str) -> None:
    global shader
    count = shader.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match; got {count}")
    shader = shader.replace(old, new, 1)


# Authentic GBA/GBC. Preserve the spatial average of a dark gap, but
# attenuate its horizontal variation at fractional pixel scales.
# At integer 2x, 3x, etc., fractional==0 and the old mask is preserved.
replace_exact(
    """                + max(vec2(0.0), vec2(1.0) - abs(phase - span - vec2(0.5))));
        }
        if (u_lcd.x > 0.5) {""",
    """                + max(vec2(0.0), vec2(1.0) - abs(phase - span - vec2(0.5))));
            // Fractional Fit creates uneven vertical line widths.
            // Keep the mean 1/scale gap and soften only its modulation, retaining at least 85% of the original contrast.
            float fractional = abs(span.x - floor(span.x + 0.5));
            float soften = 0.15 * smoothstep(0.03, 0.28, fractional);
            gap.x = mix(gap.x, min(1.0, 1.0 / max(span.x, 1.0)), soften);
        }
        if (u_lcd.x > 0.5) {""",
    "Authentic GBA/GBC vertical gap",
)

# The LCD-grid shader is automatically chosen on the RG35XX H. It already
# integrates RGB stripes against source pixels. Preserve precision,
# horizontal scanlines, and area integration; only slightly reduce x stripe contrast
# when the display scale is fractional.
replace_exact(
    """    } else if (u_mode > 6.5) {
        vec2 hp = 0.5 * u_uv.zw * u_src / (u_rect.zw * u_fbo);""",
    """    } else if (u_mode > 6.5) {
        vec2 lcdSpan = u_rect.zw * u_fbo / (u_uv.zw * u_src);
        float stripeFractional = abs(lcdSpan.x - floor(lcdSpan.x + 0.5));
        float stripeStrength = lcd_stripe
            * (1.0 - 0.15 * smoothstep(0.03, 0.28, stripeFractional));
        vec2 hp = 0.5 * u_uv.zw * u_src / (u_rect.zw * u_fbo);""",
    "LCD-grid scale-dependent stripe attenuation",
)
lcd_start = shader.index("    } else if (u_mode > 6.5) {")
lcd_end = shader.index("    } else if (u_mode > 4.5) {", lcd_start)
lcd = shader[lcd_start:lcd_end]
assert lcd.count("lcd_stripe * (lcd_ramp(-lcd_centres) - gl0)") == 1
assert lcd.count("lcd_stripe * (gr1 - gr0)") == 1
lcd = lcd.replace(
    "lcd_stripe * (lcd_ramp(-lcd_centres) - gl0)",
    "stripeStrength * (lcd_ramp(-lcd_centres) - gl0)",
)
lcd = lcd.replace("lcd_stripe * (gr1 - gr0)", "stripeStrength * (gr1 - gr0)")
assert lcd.count("mediump ") >= 10, "Original LCD-grid precision changed"
shader = shader[:lcd_start] + lcd + shader[lcd_end:]

assert shader.count("float fractional = abs(span.x - floor(span.x + 0.5));") == 1
assert shader.count("float stripeFractional = abs(lcdSpan.x - floor(lcdSpan.x + 0.5));") == 1
assert "lin = mix(u_dark, u_light, response);" in shader
assert "bool gbaRawLcd =" in shader
assert "uniform float u_authentic_correction;" in shader
path.write_text(shader)
print("Reduced vertical stripe contrast for fractional Fit, preserving integer LCD masks")
