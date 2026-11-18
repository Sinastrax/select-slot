#!/usr/bin/env python3
"""Verify GBA Authentic fractional-Fit behavior and immutable GB/SGB visuals.

This is source/analytic regression testing, NOT a physical RG35XX H capture.
The shader must equal the successful Ver. 17 shader except the two isolated
GBA grid-coverage expressions. Test x/y scaling at 640x427 Fit, including
partial LCD gap coverage, and exact original output for integer scaling.
"""
from pathlib import Path
import hashlib
import math

shader = Path("crates/slot-gfx/src/shaders.rs").read_text()
auth = Path("crates/slot-gfx/src/authentic.rs").read_text()
p = Path("crates/slot-gfx/src/pipeline.rs").read_text()
app = Path("crates/slot/src/app.rs").read_text()
base = "14aa798dfc1232d160b6fecebb9a681b17a996ba1c141177369257f8ed6463c1"
auth_base = "6990dbe1e03ee7d03cd2b53f5a826b7345ab05ab9ee401af14050a8242a0ca12"
assert hashlib.sha256(auth.encode()).hexdigest() == auth_base, (
    "Pocket/SGB verified looks OR GBA color calibration changed unexpectedly")
# Reconstruct the exact Ver. 17 GLSL and compare hashes: all other shader
# branches (Pocket/SGB, GBA color correction, Dot/Grid/LCD) are immutable.
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
old_gap = """            lin = mix(lin, panelDark, max(gap.x * u_lcd.z, gap.y * u_lcd.w));
            c = pow(lin, vec3(1.0 / 2.2));"""
new_gap = """            float oldGridCover = max(gap.x * u_lcd.z, gap.y * u_lcd.w);
            float gbaUnionCover = gap.x * u_lcd.z + gap.y * u_lcd.w
                - gap.x * gap.y * u_lcd.z * u_lcd.w;
            lin = mix(lin, panelDark, mix(oldGridCover, gbaUnionCover, gbaFit));
            c = pow(lin, vec3(1.0 / 2.2));"""
assert shader.count(new_grid) == shader.count(new_gap) == 1
recovered = shader.replace(new_grid, old_grid).replace(new_gap, old_gap)
assert hashlib.sha256(recovered.encode()).hexdigest() == base, (
    "Unexpected shader alteration outside GBA Fit Authentic gap calculations")

assert "look.lcd[0] = 2.0;" in auth
assert "Screen::PocketSgb => {" in auth and "Screen::PocketColor.look()" in auth
assert "Screen::Gba => {" in auth
assert "lcd: [0.0, 0.0, 0.45, 0.20]" in auth
assert "shader == Shader::Authentic" in app
assert "gbaRawLcd ? 1.0 : 1.0 / max(1.0 - grid, 0.001)" in shader
assert "uniform float u_authentic_correction;" in shader
assert "pub fn set_authentic_colour_correction" in p
# Other GBA effects ALREADY use fractional-scale antialiasing. They
# need no speculative modifications, only regression coverage.
assert "float unionCoverage = edge.x + edge.y - edge.x * edge.y;" in shader
assert "float gridCoverage = mix(max(edge.x, edge.y), unionCoverage, gridFit);" in shader
assert "c *= mix(dotMask, 0.47, 0.15 * dotFit);" in shader
assert "float dotFit = smoothstep(0.03, 0.28" in shader
assert "mediump vec3 lit =" in shader
assert "lcd_stripe * (gr1 - gr0)" in shader

def smoothstep(start, end, x):
    t=max(0.,min(1.,(x-start)/(end-start)))
    return t*t*(3-2*t)

def fit_strength(sx, sy, model):
    v=max(abs(sx-round(sx)),abs(sy-round(sy)))
    return smoothstep(.03,.28,v) if model=="GBA" else 0.

def gap_cov(f, scale):
    ref=round(scale)
    width=1/ref
    half=.5/scale
    lo, hi=f-half,f+half
    return max(0.,min(1.,(max(0.,min(hi,width)-max(lo,0.))
              +max(0.,min(hi,1+width)-max(lo,1.)))*scale))

def axis_values(src, dst):
    scale=dst/src
    return [gap_cov(((i+0.5)/scale)%1.,scale) for i in range(dst)]

# 640x427 is the 640x480 Fit picture area for 240x160 GBA.
sx=640/240
sy=427/160
assert abs(sx-8/3) < 1e-9
assert fit_strength(sx,sy,"GBA")>.98
assert fit_strength(sx,sy,"GBC")==fit_strength(sx,sy,"SGB")==0
assert fit_strength(3,3,"GBA")==fit_strength(2,2,"GBA")==0

x=axis_values(240,640)
y=axis_values(160,427)
assert any(.001<v<.999 for v in x)
assert any(.001<v<.999 for v in y)
assert min(x)>=0 and max(x)<=1 and min(y)>=0 and max(y)<=1
ax=sum(x)/len(x)
ay=sum(y)/len(y)
assert abs(ax-1/3)<.007,(ax,ay)
assert abs(ay-1/3)<.007,(ax,ay)

# GBA physical gap attenuations (column, row), chosen by the existing
# GBA look. Area union is always >= max and <= 1.
col,row=.45,.20
oldmean=(1/3)*(2/3)*col + (1/3)*(2/3)*row + (1/9)*max(col,row)
newmean=(1/3)*col + (1/3)*row - (1/9)*col*row
sampledmean = ax*col + ay*row - ax*ay*col*row
assert abs(sampledmean-newmean)<.006
assert newmean>oldmean
for ix in range(0,len(x),19):
    for iy in range(0,len(y),13):
        a,b=x[ix]*col,y[iy]*row
        orig=max(a,b)
        union=a+b-a*b
        assert orig-1e-8<=union<=1+1e-8
# On the full physical intersection, the grid is darker under Fit
# than when the two bands were combined with max().
assert abs((col+row-col*row)-.56)<1e-9
assert max(col,row)==.45

# On integer 3x and 2x, the GBA union never participates. Dot/Grid
# standard modes are not altered at ANY scale.
for sc in (2,3,4,5):
    assert fit_strength(sc,sc,"GBA")==0
print("PASS: GBA Fit at 640x427 has separated fractional LCD gaps with matched corrected cell average")
print("PASS: integer GBA and ALL GB/GBC/SGB + Dot/Grid/LCD GLSL exactly preserved")
