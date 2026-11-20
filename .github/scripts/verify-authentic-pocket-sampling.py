#!/usr/bin/env python3
"""Check the shader fetch optimization preserves shared Pocket sampling."""
from pathlib import Path

source = Path("crates/slot-gfx/src/shaders.rs").read_text()
assert "    vec3 c = texture2D(u_game, uv).rgb;" not in source
assert "    vec3 c;" in source
assert "        c = texture2D(u_game, uv).rgb;\n        if (!inside)" in source
assert "float ink_rgb(vec3 color)" in source
assert "centreRgb = texture2D(u_game, centre).rgb;" in source
assert "centreInk = ink_rgb(centreRgb);" in source
assert "vec3 raw = centreRgb;" in source
assert "float baseInk = centreInk;" in source
assert "vec3 raw = texture2D(u_game, centre).rgb;" not in source
assert "float baseInk = ink(centre);" not in source
assert "float shadow = ink_near(" in source
assert "c = clamp(mix(panelRgb, reflector, gapShare) * shadowShare, 0.0, 1.0);" in source

print("PASS: Pocket/SGB renderer keeps its exact equations with redundant texture reads removed")
