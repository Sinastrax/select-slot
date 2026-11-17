#!/usr/bin/env python3
"""Keep Authentic On identical to pvaibhav's calibrated screen response.

Run after merge-1.16-fixes.py. This applies to the generated upstream source,
not the older v1.15.3 patch baseline. Every replacement is asserted so future
upstream changes cannot silently drop or partially apply either fix.
"""

from pathlib import Path


def replace_once(source: str, old: str, new: str, what: str) -> str:
    count = source.count(old)
    if count != 1:
        raise AssertionError(f"{what}: expected exactly one match, found {count}")
    return source.replace(old, new, 1)


# Authentic ON: use the original measured GBA/GBC LCD colour response, including
# its calibrated panel white and black values. The v2 neutral-axis conversion
# preserved source luminance instead of the real screen's luminance, bleaching
# yellows and shifting the intended result. Authentic OFF: source RGB is
# unmodified, with the same LCD dot/grid treatment still applied.
shader_path = Path("crates/slot-gfx/src/shaders.rs")
shader = shader_path.read_text()

pocket_old = """                    vec3 sourceLin = pow(raw, vec3(2.2));
                    float sourceLuma = dot(sourceLin, luma_coeff);
                    float convertedLuma = dot(response, luma_coeff);
                    float chroma = max(max(raw.r, raw.g), raw.b) - min(min(raw.r, raw.g), raw.b);
                    vec3 balanced = clamp(response * (sourceLuma / max(convertedLuma, 0.0001)), 0.0, 1.0);
                    panelRgb = pow(mix(sourceLin, balanced, smoothstep(0.015, 0.075, chroma)), vec3(1.0 / 2.2));"""
pocket_new = """                    // Match the measured GBC panel response used in upstream Authentic.
                    vec3 gbcWhite = pow(vec3(134.0, 140.0, 122.0) / 255.0, vec3(2.2));
                    vec3 gbcBlack = pow(vec3(14.0, 25.0, 28.0) / 255.0, vec3(2.2));
                    panelRgb = pow(mix(gbcBlack, gbcWhite, response), vec3(1.0 / 2.2));"""
shader = replace_once(shader, pocket_old, pocket_new, "Pocket Color response")
# Do not apply GBC calibration to Pocket SGB: that mode uses SNES/SGB palettes
# and has no equivalent upstream GBC LCD to simulate.
shader = replace_once(
    shader,
    """if (u_authentic_correction > 0.5) {
                    vec3 code = (floor((raw * 255.0 + 0.5) / 8.0) + 0.5) / 32.0;""",
    """if (u_lcd.x < 2.5 && u_authentic_correction > 0.5) {
                    vec3 code = (floor((raw * 255.0 + 0.5) / 8.0) + 0.5) / 32.0;""",
    "Pocket SGB should keep its hardware palette",
)

colour_old = """                float rawY = dot(lin, luma_coeff);
                float correctedY = dot(response, luma_coeff);
                float chroma = max(max(rawColour.r, rawColour.g), rawColour.b)
                    - min(min(rawColour.r, rawColour.g), rawColour.b);
                vec3 balanced = clamp(response * (rawY / max(correctedY, 0.0001)), 0.0, 1.0);
                lin = mix(lin, balanced, smoothstep(0.015, 0.075, chroma));"""
colour_new = """                // Exactly the colour response and panel tint from upstream Authentic.
                lin = mix(u_dark, u_light, response);"""
shader = replace_once(shader, colour_old, colour_new, "GBC/GBA response")
# ON must use upstream's measured panel floor (u_dark), while OFF keeps
# neutral RGB. Applying one neutral floor to both broke the Authentic look.
shader = replace_once(
    shader, "vec3 panelDark = vec3(0.0);",
    "vec3 panelDark = u_authentic_correction > 0.5 ? u_dark : vec3(0.0);",
    "Authentic panel black calibration",
)
# Pocket Color is our own hybrid; preserve original GBC panel tint when On,
# keep the reflector neutral when Off. Pocket SGB stays independent.
shader = replace_once(
    shader, "vec3 reflector = vec3(1.0);",
    """vec3 reflector = u_lcd.x > 2.5 ? vec3(0.90)
                    : (u_authentic_correction > 0.5
                        ? vec3(134.0, 140.0, 122.0) / 255.0 : vec3(1.0));""",
    "Pocket Color correction-dependent reflector",
)
# Remove superseded explanatory comments from Ver. 2 that incorrectly claimed
# neutral luminance was part of Authentic's measured colour simulation.
comments = [
    (
        """// Treat colour correction as a source-colour conversion only.
                    // Preserve the source's luminance and neutral greys, including
                    // white, rather than changing the simulated LCD white/black point.""",
        """// On uses the calibrated GBC colour response and panel white/black;
                    // Off passes the game's original colours to the Pocket LCD grid.""",
    ),
    (
        """// Reflector and pixel gaps must be identical for both correction
                // settings; do not switch panel tint when correction is toggled.""",
        """// Pocket Color's measured reflector is part of the calibrated On mode.
                // Off keeps neutral gaps; Pocket SGB retains its own reflector.""",
    ),
    (
        """// One neutral floor for either setting; the switch acts on source
            // colour only, not panel brightness, contrast, or gap tint.""",
        """// The original Authentic LCD has a measured black and white point.
            // Only Off uses a neutral black floor to preserve uncorrected RGB.""",
    ),
    (
        """// Keep luminance and neutral values identical to the uncorrected
                // source; only the chromatic response is corrected.""",
        """// The measured upstream response also includes brightness and panel tint.""",
    ),
]
for old, new in comments:
    shader = replace_once(shader, old, new, "Outdated colour-correction description")

# Verify exactly the original calibration is active on the On branch.
assert "lin = mix(u_dark, u_light, response);" in shader
assert "vec3 panelDark = u_authentic_correction > 0.5 ? u_dark : vec3(0.0);" in shader
assert "lin = pow(rawColour, vec3(2.2));" in shader
assert "authentic_corrected_linear(" not in shader
if "uniform float u_authentic_correction;" not in shader:
    raise AssertionError("Authentic colour-correction toggle uniform is missing")
shader_path.write_text(shader)

# Slot already has GamePass::set_glass and Compositor::set_authentic_glass,
# but the frontend never passed the in-game Reflection option to either.
# A default Authentic bezel contains its OWN glass texture; the shader must
# not double-apply sheen/shade there. With any other bezel, the shader draws
# the shade regardless, but draws the sheen only while Reflection is enabled.
fbo = Path("crates/slot-gfx/src/fbo.rs").read_text()
if "pub fn set_authentic_glass(&mut self, sheen: bool, shade: bool)" not in fbo:
    raise AssertionError("Expected upstream Authentic glass compositor API missing")

frontend_path = Path("crates/slot/src/frontend.rs")
frontend = frontend_path.read_text()
if "compositor.set_authentic_glass(" in frontend:
    raise AssertionError("Frontend already controls Authentic glass: review upstream changes")
glass_old = "        compositor.set_authentic_screen(authentic_screen(self.session.app()));"
glass_new = """        compositor.set_authentic_screen(authentic_screen(self.session.app()));
        // Reflection is separate from the LCD colour correction and pixel grid.
        // Default Authentic bezel art already draws its own glass. Otherwise,
        // keep the bezel shade but only show the shader sheen when requested.
        let app = self.session.app();
        let platform = app.playing_platform();
        let bezel_has_glass = app.resolved_bezel(platform) == BezelPick::Default
            && app.bezel_art().is_some_and(BezelArt::authentic);
        compositor.set_authentic_glass(
            !bezel_has_glass && app.reflection(platform),
            !bezel_has_glass,
        );"""
frontend = replace_once(frontend, glass_old, glass_new, "Reflection setting wiring")
frontend_path.write_text(frontend)

print("Restored pvaibhav Authentic colour calibration for On; Off remains uncorrected, reflection remains independent")
