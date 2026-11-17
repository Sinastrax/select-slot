#!/usr/bin/env python3
"""Keep Authentic's colour controls independent from LCD rendering and glass.

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


shader_path = Path("crates/slot-gfx/src/shaders.rs")
shader = shader_path.read_text()

# Correction ON restores the measured LCD transform from upstream Slot:
# 5-bit code -> measured ramp -> response matrix -> physical panel black/white.
# Correction OFF keeps source RGB untouched except for the Authentic pixel grid.
# Do not force neutral whites / source luminance in the ON path; doing so
# destroys the calibrated LCD appearance and desaturates bright yellow.
pocket_old = """                    vec3 sourceLin = pow(raw, vec3(2.2));
                    float sourceLuma = dot(sourceLin, luma_coeff);
                    float convertedLuma = dot(response, luma_coeff);
                    float chroma = max(max(raw.r, raw.g), raw.b) - min(min(raw.r, raw.g), raw.b);
                    vec3 balanced = clamp(response * (sourceLuma / max(convertedLuma, 0.0001)), 0.0, 1.0);
                    panelRgb = pow(mix(sourceLin, balanced, smoothstep(0.015, 0.075, chroma)), vec3(1.0 / 2.2));"""
pocket_new = """                    // Pocket Color's corrected mode uses the measured GBC
                    // response and physical black/white points.
                    vec3 gbcWhite = pow(vec3(134.0, 140.0, 122.0) / 255.0, vec3(2.2));
                    vec3 gbcBlack = pow(vec3(14.0, 25.0, 28.0) / 255.0, vec3(2.2));
                    panelRgb = pow(mix(gbcBlack, gbcWhite, response), vec3(1.0 / 2.2));"""
shader = replace_once(shader, pocket_old, pocket_new, "Pocket Color response")

colour_old = """                float rawY = dot(lin, luma_coeff);
                float correctedY = dot(response, luma_coeff);
                float chroma = max(max(rawColour.r, rawColour.g), rawColour.b)
                    - min(min(rawColour.r, rawColour.g), rawColour.b);
                vec3 balanced = clamp(response * (rawY / max(correctedY, 0.0001)), 0.0, 1.0);
                lin = mix(lin, balanced, smoothstep(0.015, 0.075, chroma));"""
colour_new = """                // Original Slot physical GBA/GBC panel calibration.
                lin = mix(u_dark, u_light, response);"""
shader = replace_once(shader, colour_old, colour_new, "GBC/GBA response")
# Keep the control paths independent, with a neutral uncorrected RGB image
# and the upstream calibrated panel response when correction is enabled.
shader = replace_once(
    shader, "vec3 panelDark = vec3(0.0);",
    "vec3 panelDark = u_authentic_correction > 0.5 ? u_dark : vec3(0.0);",
    "GBA/GBC calibrated LCD black point"
)
shader = replace_once(
    shader, "vec3 reflector = vec3(1.0);",
    """vec3 reflector = u_lcd.x < 2.5 && u_authentic_correction > 0.5
                    ? vec3(134.0, 140.0, 122.0) / 255.0 : vec3(1.0);""",
    "Pocket Color corrected reflector tint"
)
if "authentic_corrected_linear(" in shader:
    raise AssertionError("Old colour-only/luma-locking correction survived")
if "lin = mix(u_dark, u_light, response);" not in shader:
    raise AssertionError("Authentic calibrated panel response missing")
if "vec3 lin = pow(rawColour, vec3(2.2));" not in shader:
    raise AssertionError("Uncorrected RGB mode missing")
if "uniform float u_authentic_correction;" not in shader:
    raise AssertionError("Authentic colour-correction toggle uniform is missing")
# Authentic's LCD grid darkens the pixel gaps. In the current Off path
# the 1/(1-grid) inverse compensation brightens pixel centres enough to
# recover the source's average luminance, making Off resemble the unfiltered
# picture instead of the modestly darker regular LCD shader.
# GBA Off is not a physical colour calibration, so keep the original source
# RGB at pixel centres and let the optical grid darken the full image slightly.
# Keep GBA On, GBC On/Off and the GB/Pocket modes completely unchanged.
shader = replace_once(
    shader,
    "lin = min(panelDark + (lin - panelDark) * sparkle / (1.0 - grid), vec3(1.0));",
    """// Only uncorrected GBA omits inverse grid-brightness compensation:
            // RGB at pixel centres stays unchanged, dark gaps reduce luminance.
            // Calibrated On, GBC and Pocket modes retain original behaviour.
            bool gbaRawLcd = u_lcd.x < 0.5 && u_lcd.y < 0.5
                && u_authentic_correction < 0.5;
            float cellCompensation = gbaRawLcd ? 1.0 : 1.0 / max(1.0 - grid, 0.001);
            lin = min(panelDark + (lin - panelDark) * sparkle * cellCompensation, vec3(1.0));""",
    "GBA Authentic Off optical LCD brightness"
)
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

print("Restored measured Authentic panel colour correction, neutral OFF mode and per-platform Reflection control")
