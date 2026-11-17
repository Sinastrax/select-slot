#!/usr/bin/env python3
"""Make Pocket SGB use Pocket Color's identical optical LCD rendering.

Run last, after the Ver. 10 native Pocket Fit coverage update. Previous
versions had a separate SGB path with hand-tuned gap multipliers and an
approximate one-neighbour shadow. That could never visually match the
Pocket Color ink, gap, reflector and full dot-shadow calculations.

Share the existing, proven Pocket Color GLSL rendering path outright.
Only the RGB source conversion differs: mGBA's SGB colors are passed
unchanged with Color Correction Off, or through the existing selectable
SNES CRT gamma ramp with On. Do not run a GBC LCD matrix on SNES colors.
"""
from pathlib import Path

shader_path = Path("crates/slot-gfx/src/shaders.rs")
shader = shader_path.read_text()

# Eliminate the separate simplified SGB renderer. Pocket Color and SGB
# now reach exactly the SAME dot geometry, ink, shadows and reflector code.
sgb_start_token = "        if (u_lcd.x > 2.5) {\n            // Dedicated SGB branch:"
sgb_end_token = "        } else if (u_lcd.x > 0.5) {"
assert shader.count(sgb_start_token) == 1, "Expected Ver. 9 SGB fast-path"
assert shader.count(sgb_end_token) == 1, "Expected shared Pocket ink branch"
sgb_start = shader.index(sgb_start_token)
sgb_end = shader.index(sgb_end_token, sgb_start)
legacy = shader[sgb_start:sgb_end]
for old in ("vec3 sgbRgb = raw;", "float sgbShadow = 1.0", "vec2 sgbGap = gap;"):
    assert old in legacy, f"SGB legacy path changed: {old}"
shader = (shader[:sgb_start] +
          "        if (u_lcd.x > 0.5) {" +
          shader[sgb_end + len(sgb_end_token):])

# The Pocket Color branch must continue doing its existing measured GBC
# color conversion, but it must be disabled for the SGB palette.
pocket_start = shader.index("if (u_lcd.x > 1.5 && inside) {")
rgb_idx = shader.index("                vec3 panelRgb = raw;", pocket_start)
# Preserve Pocket Color's existing conditional GBC color response.
# SGB receives the optional SNES response instead.
gbc_if = "                if (u_authentic_correction > 0.5) {"
window = shader[rgb_idx:rgb_idx + 900]
assert gbc_if in window, "Expected Pocket GBC correction near source RGB; got: " + repr(window)
gbc_idx = shader.index(gbc_if, rgb_idx)
new_gbc_if = "                if (u_authentic_correction > 0.5 && u_lcd.x < 2.5) {"
shader = shader[:gbc_idx] + shader[gbc_idx:].replace(gbc_if, new_gbc_if, 1)
cursor = gbc_idx + len(new_gbc_if)
depth = 1
while depth:
    assert cursor < len(shader), "Unclosed Pocket Color correction block"
    if shader[cursor] == "{":
        depth += 1
    elif shader[cursor] == "}":
        depth -= 1
    cursor += 1
gbc_block = shader[gbc_idx:cursor]
assert "panelRgb =" in gbc_block and "gbcWhite" in gbc_block, "GBC calibrated branch changed"

# The same Color Correction setting that controls Pocket Color's GBC
# response instead chooses the existing SNES CRT response for SGB.
# OFF always retains exact source SGB RGB, without forcing GBC transforms.
sgb_color = """ else if (u_authentic_correction > 0.5) {
                    // SGB: preserve mGBA's per-game SNES RGB palette.
                    // Optional original SNES CRT response, never GBC LCD.
                    vec3 sgbCode = floor(raw * 31.0 + vec3(0.5));
                    vec3 sgbLow = sgbCode * (sgbCode + vec3(1.0)) / 510.0;
                    vec3 sgbHigh = min(
                        (vec3(136.0) + 8.0 * (sgbCode - vec3(16.0))) / 255.0,
                        vec3(1.0));
                    panelRgb = mix(sgbLow, sgbHigh, step(vec3(16.5), sgbCode));
                }"""
shader = shader[:cursor] + sgb_color + shader[cursor:]

# Pocket Color and Pocket SGB must use the same reflector for the same
# correction setting: no white/grey split specific to the SGB model.
old_reflector = """vec3 reflector = u_lcd.x < 2.5 && u_authentic_correction > 0.5
                    ? vec3(134.0, 140.0, 122.0) / 255.0 : vec3(1.0);"""
new_reflector = """vec3 reflector = u_authentic_correction > 0.5
                    ? vec3(134.0, 140.0, 122.0) / 255.0 : vec3(1.0);"""
assert shader.count(old_reflector) == 1, "Expected independently tinted Pocket reflector"
shader = shader.replace(old_reflector, new_reflector, 1)

assert shader.count("if (u_lcd.x > 2.5) {") == 0
assert shader.count("if (u_lcd.x > 0.5) {") == 1
assert shader.count("if (u_lcd.x > 1.5 && inside)") == 1
assert "vec2 gapWidth = 1.0 / referenceSpan;" in shader
assert "float leftGap = u_ink.z * (a + west);" in shader
assert "float upperGap = u_ink.z * (a + north);" in shader
assert "float shadow = ink_near(" in shader
assert "float sgbShadow =" not in shader
assert "vec2 sgbGap =" not in shader
assert "lin = mix(u_dark, u_light, response);" in shader
shader_path.write_text(shader)

# Identical model parameter sets: copy Pocket Color's calibrated response,
# pixel ink/shadow, reflector and ghosting. Keep only the discriminator
# u_lcd.x=3.0 so its COLOR input is SGB rather than the GBC palette.
authentic_path = Path("crates/slot-gfx/src/authentic.rs")
authentic = authentic_path.read_text()
start_marker = "            Screen::PocketSgb => {\n"
end_marker = "            Screen::Light =>"
assert authentic.count(start_marker) == 1
at = authentic.index(start_marker)
end = authentic.index(end_marker, at)
before = authentic[at:end]
assert "let mut look = POCKET.look(" in before
assert "look.lcd[0] = 3.0;" in before
replacement = """            Screen::PocketSgb => {
                // Exactly Pocket Color's LCD optical model and response.
                // Only the source palette is SGB/SNES, selected by lcd.x.
                let mut look = Screen::PocketColor.look();
                look.lcd[0] = 3.0;
                look
            },
"""
authentic_path.write_text(authentic[:at] + replacement + authentic[end:])
print("Pocket SGB now shares Pocket Color optics exactly; only palette response differs")
