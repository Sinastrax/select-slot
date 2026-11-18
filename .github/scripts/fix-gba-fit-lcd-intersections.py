#!/usr/bin/env python3
"""Integrate GBA Authentic pixel-gap intersections at fractional Fit scales.

On the RG35XX H (640x480), a 240x160 GBA frame uses 640x427 Fit (~2.67
screen pixels per GBA pixel). The shader already analytically integrates
1/3-source-pixel gap coverage for each screen pixel, but combines its
vertical/horizontal LCD grid components with max(). This is correct for
the old integer-scale look but undercounts partially covered *intersections*
at 2.67x, weakening/unevenly modulating pixel separation.

Use the coverage-weighted union of the two GBA grid opacities at fractional
scale, and its matching average for corrected RGB cell compensation.
This preserves original source RGB, the calibrated GBA light/dark levels,
the existing 2.67x antialiasing, and exact original integer-scale output.

Apply only to Authentic GBA (u_lcd.x=0,y=0), not GBC, Pocket, Pocket SGB,
DMG, GBA standard Dot/Grid/LCD effects, or the emulated core.
"""
from pathlib import Path
import hashlib

path = Path("crates/slot-gfx/src/shaders.rs")
source = path.read_text()
expected_ver17 = "14aa798dfc1232d160b6fecebb9a681b17a996ba1c141177369257f8ed6463c1"
assert hashlib.sha256(source.encode()).hexdigest() == expected_ver17, (
    "Unexpected source shader. Ver. 17 is the proven Pocket/SGB baseline; "
    "refuse to modify an unmatched rendering pipeline."
)

old_grid = """            float grid = thin.x * (1.0 - thin.y) * u_lcd.z + thin.y * (1.0 - thin.x) * u_lcd.w
                + thin.x * thin.y * max(u_lcd.z, u_lcd.w);
            // The reflector shows through the colour filter as a fine sparkle."""
new_grid = """            float grid = thin.x * (1.0 - thin.y) * u_lcd.z + thin.y * (1.0 - thin.x) * u_lcd.w
                + thin.x * thin.y * max(u_lcd.z, u_lcd.w);
            // GBA Authentic at fractional Fit (640x427 on the RG35XX H).
            // Each output pixel sees PART of each physical LCD gap. The
            // union of the row/column optical coverage, not max(), gives
            // the right attenuation at their partly-covered intersections.
            // Gate this to GBA only: the now-verified Pocket/SGB RGB profiles
            // both use u_lcd.x=2 and must not change.
            vec2 gbaFraction = abs(span - referenceSpan);
            float gbaFit = (u_lcd.x < 0.5 && u_lcd.y < 0.5)
                ? smoothstep(0.03, 0.28, max(gbaFraction.x, gbaFraction.y))
                : 0.0;
            // Use precisely the matching average for corrected LCD cells:
            // mean(A union B) = mean(A)+mean(B)-mean(A)*mean(B).
            // Color Correction Off retains the old unboosted GBA pixel RGB.
            float gbaUnionAverage = thin.x * u_lcd.z + thin.y * u_lcd.w
                - thin.x * thin.y * u_lcd.z * u_lcd.w;
            grid = mix(grid, gbaUnionAverage, gbaFit);
            // The reflector shows through the colour filter as a fine sparkle."""
assert source.count(old_grid)==1, "GBA/GBC cell grid anchor must be unique"
source=source.replace(old_grid,new_grid,1)

old_gap = """            lin = mix(lin, panelDark, max(gap.x * u_lcd.z, gap.y * u_lcd.w));
            c = pow(lin, vec3(1.0 / 2.2));"""
new_gap = """            float oldGridCover = max(gap.x * u_lcd.z, gap.y * u_lcd.w);
            float gbaUnionCover = gap.x * u_lcd.z + gap.y * u_lcd.w
                - gap.x * gap.y * u_lcd.z * u_lcd.w;
            lin = mix(lin, panelDark, mix(oldGridCover, gbaUnionCover, gbaFit));
            c = pow(lin, vec3(1.0 / 2.2));"""
assert source.count(old_gap)==1, "Authentic pixel-grid final mix anchor must be unique"
source=source.replace(old_gap,new_gap,1)

# Hard invariants against repeating Pocket Color/SGB regressions.
assert "Screen::PocketColor" not in source
assert "vec3 gbcWhite = pow(vec3(134.0, 140.0, 122.0)" in source
assert "if (u_lcd.x > 1.5)" in source
assert "vec2 gapWidth = 1.0 / referenceSpan;" in source
assert "vec3 response = clamp(u_response * pow(light, u_gamma)" in source
assert "bool gbaRawLcd = u_lcd.x < 0.5 && u_lcd.y < 0.5" in source
assert "float gridCoverage = mix(max(edge.x, edge.y), unionCoverage, gridFit);" in source
assert "c *= mix(dotMask, 0.47, 0.15 * dotFit);" in source
assert "mediump vec3 lit =" in source

path.write_text(source)
print("PASS: GBA-only fractional-Fit Authentic gap intersections, GBA color science unchanged")
