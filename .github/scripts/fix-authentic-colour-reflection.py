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

# The previous implementation scaled the measured response by source luma
# separately for every pixel and crossfaded using an arbitrary saturation
# threshold. That can blow out saturated channels and yield discontinuous
# colours close to grey. Instead, compare the calibrated colour response with
# its own neutral axis, use ONLY that response's chroma, and retain the source
# luminance. White, black, and every neutral grey remain neutral. The original
# LCD cell, dot shadows, grid, grain, and glass code remains untouched.
anchor = """vec3 lcd_ramp(vec3 x) {
    vec3 u = fract(x + 0.5) - 0.5;
    return u - 2.0 * u * abs(u);
}
void main() {"""
corrector = """vec3 lcd_ramp(vec3 x) {
    vec3 u = fract(x + 0.5) - 0.5;
    return u - 2.0 * u * abs(u);
}
// Colour correction affects only colour, not the LCD's pixels or glass.
// Work in linear light and keep Y where the corrected chroma fits the RGB
// gamut. For bright saturated input, shift Y rather than whitening the colour.
// Neutrals remain neutral; no individual-channel clipping or hue discontinuity.
vec3 authentic_corrected_linear(vec3 sourceRgb, vec3 measured, vec3 response) {
    vec3 sourceLinear = pow(sourceRgb, vec3(2.2));
    float sourceY = dot(sourceLinear, luma_coeff);
    float measuredGrey = dot(measured, luma_coeff);
    vec3 calibratedGrey = clamp(
        u_response * pow(vec3(measuredGrey), u_gamma), u_least, vec3(1.0));
    vec3 chroma = response - calibratedGrey;
    chroma -= vec3(dot(chroma, luma_coeff));

    // Chroma-first gamut mapping: a bright saturated yellow has very little
    // room above its original Y. Forcing that Y and shrinking chroma makes the
    // yellow nearly white. Prefer shifting Y into the available interval while
    // keeping the measured hue/saturation; compress chroma only if its span
    // would exceed the entire 0..1 gamut.
    float low = min(min(chroma.r, chroma.g), chroma.b);
    float high = max(max(chroma.r, chroma.g), chroma.b);
    chroma *= min(1.0, 1.0 / max(high - low, 0.0001));
    low = min(min(chroma.r, chroma.g), chroma.b);
    high = max(max(chroma.r, chroma.g), chroma.b);
    float correctedY = clamp(sourceY, max(0.0, -low), min(1.0, 1.0 - high));
    return clamp(vec3(correctedY) + chroma, 0.0, 1.0);
}
void main() {"""
shader = replace_once(shader, anchor, corrector, "Authentic helper insertion")

pocket_old = """                    vec3 sourceLin = pow(raw, vec3(2.2));
                    float sourceLuma = dot(sourceLin, luma_coeff);
                    float convertedLuma = dot(response, luma_coeff);
                    float chroma = max(max(raw.r, raw.g), raw.b) - min(min(raw.r, raw.g), raw.b);
                    vec3 balanced = clamp(response * (sourceLuma / max(convertedLuma, 0.0001)), 0.0, 1.0);
                    panelRgb = pow(mix(sourceLin, balanced, smoothstep(0.015, 0.075, chroma)), vec3(1.0 / 2.2));"""
pocket_new = """                    panelRgb = pow(authentic_corrected_linear(raw, measured, response),
                                   vec3(1.0 / 2.2));"""
shader = replace_once(shader, pocket_old, pocket_new, "Pocket Color response")

colour_old = """                float rawY = dot(lin, luma_coeff);
                float correctedY = dot(response, luma_coeff);
                float chroma = max(max(rawColour.r, rawColour.g), rawColour.b)
                    - min(min(rawColour.r, rawColour.g), rawColour.b);
                vec3 balanced = clamp(response * (rawY / max(correctedY, 0.0001)), 0.0, 1.0);
                lin = mix(lin, balanced, smoothstep(0.015, 0.075, chroma));"""
colour_new = """                lin = authentic_corrected_linear(rawColour, light, response);"""
shader = replace_once(shader, colour_old, colour_new, "GBC/GBA response")
if shader.count("authentic_corrected_linear(") != 3:
    raise AssertionError("Expected helper and two Authentic colour-conversion call sites")
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

print("Applied Authentic neutral-axis colour correction and per-platform Reflection control")
