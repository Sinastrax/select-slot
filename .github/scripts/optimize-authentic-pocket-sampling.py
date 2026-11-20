#!/usr/bin/env python3
"""Remove redundant texture fetches from the Authentic Game Boy shader."""
from pathlib import Path

path = Path("crates/slot-gfx/src/shaders.rs")
source = path.read_text()

# Authentic writes a simulated panel over every pixel, so its input sample at
# uv is discarded. Fetch it only on the non-Authentic path that uses it.
old = "    vec3 c = texture2D(u_game, uv).rgb;\n"
new = "    vec3 c;\n"
if source.count(old) == 1:
    source = source.replace(old, new, 1)
else:
    assert source.count(new) == 1, "Expected the main game-pixel sample"

old = """    } else if (!inside) {
        // Past the picture, the source shows as it is.
    } else if (u_mode > 6.5) {"""
new = """    } else {
        c = texture2D(u_game, uv).rgb;
        if (!inside) {
            // Past the picture, the source shows as it is.
        } else if (u_mode > 6.5) {"""
if source.count(old) == 1:
    source = source.replace(old, new, 1)
else:
    assert source.count(new) == 1, "Expected the non-Authentic shader branch"

# The non-Authentic branch now owns one additional scope.
old = """    } else if (u_mode > 0.5) {
        vec2 angle = f * 6.283185307;
        float yfactor = (16.0 + sin(angle.y)) / 17.0;
        vec3 xfactors = (4.0 + sin(angle.x + offsets)) / 5.0;
        c *= yfactor * xfactors;
    }
    FRAG_COLOR = vec4(c * u_bright, 1.0);"""
new = """        } else if (u_mode > 0.5) {
            vec2 angle = f * 6.283185307;
            float yfactor = (16.0 + sin(angle.y)) / 17.0;
            vec3 xfactors = (4.0 + sin(angle.x + offsets)) / 5.0;
            c *= yfactor * xfactors;
        }
    }
    FRAG_COLOR = vec4(c * u_bright, 1.0);"""
if source.count(old) == 1:
    source = source.replace(old, new, 1)
else:
    assert source.count(new) == 1, "Expected the final non-Authentic shader branch"

# Reuse the center RGB sample for ink, the color transform, and reflector
# coverage. Keep the original equations and sampling coordinates unchanged.
old = """float ink(vec2 at) {
    return min(u_ink.x * (1.0 - dot(texture2D(u_game, at).rgb, vec3(1.0 / 3.0))) + u_ink.y, 1.0);
}"""
new = """float ink_rgb(vec3 color) {
    return min(u_ink.x * (1.0 - dot(color, vec3(1.0 / 3.0))) + u_ink.y, 1.0);
}
float ink(vec2 at) {
    return ink_rgb(texture2D(u_game, at).rgb);
}"""
if source.count(old) == 1:
    source = source.replace(old, new, 1)
else:
    assert source.count(new) == 1, "Expected the ink sampling helper"

old = """            float a = 0.0;
            if (inside) {
                a = ink(centre);"""
new = """            float a = 0.0;
            vec3 centreRgb = vec3(0.0);
            float centreInk = 0.0;
            if (inside) {
                centreRgb = texture2D(u_game, centre).rgb;
                centreInk = ink_rgb(centreRgb);
                a = centreInk;"""
if source.count(old) == 1:
    source = source.replace(old, new, 1)
else:
    assert source.count(new) == 1, "Expected Authentic's center ink sample"

old = "                vec3 raw = texture2D(u_game, centre).rgb;"
new = "                vec3 raw = centreRgb;"
if source.count(old) == 1:
    source = source.replace(old, new, 1)
else:
    assert source.count(new) == 1, "Expected Pocket RGB center sample"

old = "                float baseInk = ink(centre);"
new = "                float baseInk = centreInk;"
if source.count(old) == 1:
    source = source.replace(old, new, 1)
else:
    assert source.count(new) == 1, "Expected Pocket reflector center ink"

path.write_text(source)
print("Authentic now avoids the unused input sample and reuses its center RGB/ink samples")
