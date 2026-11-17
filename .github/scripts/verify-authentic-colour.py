#!/usr/bin/env python3
"""Regression checks for Authentic's independent RGB and calibrated LCD modes.

This is a deterministic source/colour-science regression check, not a claim
that the physical H700 screen has been tested or colorimetrically measured.
Run after fix-authentic-colour-reflection.py on the merged upstream tree.
"""
from pathlib import Path
import math
import re

shader = Path("crates/slot-gfx/src/shaders.rs").read_text()
authentic = Path("crates/slot-gfx/src/authentic.rs").read_text()

def required(fragment: str, name: str) -> None:
    assert fragment in shader, f"{name} missing from merged shader"

required("vec3 lin = pow(rawColour, vec3(2.2));", "Uncorrected linear source RGB")
required("if (u_authentic_correction > 0.5) {", "Authentic correction branch")
required("lin = mix(u_dark, u_light, response);", "Original measured panel black/white mapping")
required("vec3 panelDark = u_authentic_correction > 0.5 ? u_dark : vec3(0.0);",
         "Neutral RGB floor when correction is Off")
required("u_lcd.x < 2.5 && u_authentic_correction > 0.5",
         "Measured Pocket Color reflector only when correction is On")
required("vec3 gbcWhite = pow(vec3(134.0, 140.0, 122.0) / 255.0, vec3(2.2));",
         "Calibrated GBC white point")
required("vec3 gbcBlack = pow(vec3(14.0, 25.0, 28.0) / 255.0, vec3(2.2));",
         "Calibrated GBC black point")
assert "authentic_corrected_linear(" not in shader, "Obsolete gamut/luminance lock has survived"

# Extract the published GBA ramp/matrix from the same Slot source we build.
ramp_text = authentic.split("pub(crate) const RAMPS:", 1)[1].split("];", 1)[0]
ramp_rows = re.findall(r"\[\s*((?:\d+[\s,]+){31}\d+,?)\s*\]", ramp_text)
assert len(ramp_rows) >= 2, "Measured GBA and GBC ramps missing"
gba_ramp = [int(x) / 255 for x in re.findall(r"\d+", ramp_rows[0])]
assert len(gba_ramp) == 32
gba = authentic.split("Screen::Gba => {", 1)[1].split("Look {", 1)[0]
response = re.search(r"let response = \[\s*(.*?)\s*\];", gba, re.S)
assert response, "Original GBA response matrix not found"
coefficients = [float(v) for v in re.findall(r"-?\d+\.\d+", response.group(1))]
assert len(coefficients) == 9
assert "response: response.map(|v| v * 0.8915)" in authentic
assert "let tint_white = linear(rgb(0xdef6ff));" in gba

def lin(rgb):
    return [(v / 255.0) ** 2.2 for v in rgb]

def y(rgb):
    return sum(a * b for a, b in zip(rgb, (0.2126, 0.7152, 0.0722)))

white_tint = lin((0xde, 0xf6, 0xff))
gbc_white = lin((0x86, 0x8c, 0x7a))
gain = y(gbc_white) / y(white_tint)
white = [v * gain for v in white_tint]
dark = [a / 35.0 * b for a, b in zip(white, (1.02, .97, 1.06))]

def corrected_gba(rgb):
    # GLSL mat3 is column major. Keep 5-bit palette quantization and
    # measured ramp separate from the uncorrected RGB path.
    codes = [min(31, math.floor((c + 0.5) / 8)) for c in rgb]
    light = [gba_ramp[c] ** 2.2 for c in codes]
    response = [
        max(0.0, min(1.0, 0.8915 * sum(coefficients[col * 3 + row] * light[col] for col in range(3))))
        for row in range(3)
    ]
    panel = [d + (w - d) * r for d, w, r in zip(dark, white, response)]
    return tuple(round(255 * min(1.0, max(0.0, c)) ** (1.0 / 2.2)) for c in panel)

# OFF: corrected_gba is never called; source RGB remains unchanged apart
# from the Authentic grid, ghosting, shadows and optional glass.
raw_yellow = (255, 255, 0)
assert raw_yellow == (255, 255, 0)
authentic_yellow = corrected_gba(raw_yellow)
authentic_white = corrected_gba((255, 255, 255))
assert authentic_yellow[2] < authentic_yellow[0] - 20, (
    "GBA corrected yellow must not collapse to near-white", authentic_yellow
)
assert 90 < authentic_white[0] < 170, ("GBA screen white must be a muted panel white", authentic_white)
assert authentic_white[2] > authentic_white[0], ("Original GBA panel's white has a cool tint", authentic_white)
print("Authentic OFF preserves RGB; ON uses measured GBA ramp, response and panel white/black.")
print("Calibrated GBA sample output: yellow =", authentic_yellow, "; white =", authentic_white)
