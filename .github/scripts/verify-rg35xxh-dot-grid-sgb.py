#!/usr/bin/env python3
"""Guard RG35XX H noninteger Fit masks and SGB palette integrity."""
from pathlib import Path
import math

shader = Path("crates/slot-gfx/src/shaders.rs").read_text()
core = Path("crates/slot/src/core.rs").read_text()

# Every fragment effect keeps its existing branch and no shader modes swap.
assert shader.count("if (u_lcd.x > 2.5) {") >= 1
assert "c = raw * (1.0 - 0.28 * sgbGap.x) * (1.0 - 0.20 * sgbGap.y);" in shader
assert "sgbGap = mix(sgbGap, 1.0 / max(span, vec2(1.0)), sgbSoft);" in shader
assert "sgbPhase = f * span;" in shader
assert "vec2 dotSpan = u_rect.zw * u_fbo / (u_uv.zw * u_src);" in shader
assert "float dotMask = mix(1.0, mix(1.2 * mid, sum, 0.85), 0.85);" in shader
assert "c *= mix(dotMask, 0.47, 0.55 * dotFit);" in shader
assert "float gridCoverage = mix(max(edge.x, edge.y), 5.0 / 9.0, 0.55 * gridFit);" in shader
assert "lin = mix(u_dark, u_light, response);" in shader
assert "bool gbaRawLcd =" in shader
assert "uniform float u_authentic_correction;" in shader
assert "float stripeStrength = lcd_stripe" in shader
assert "mediump vec3 lit =" in shader

# Verify core SGB colors bypass inappropriate Gambatte GBC LCD correction.
assert 'GbColors::SgbAuto => true,' in core
assert 'choice.core_name().starts_with("SGB ")' in core
assert 'core.set_option(key, if sgb_palette { "disabled" } else { value });' in core

# Integer scaling does not change the Dot or Grid result. At Fit both
# dark-mask deviations shrink, retaining their area-average luminance.
def fade(scale: float) -> float:
    v = abs(scale - math.floor(scale + .5))
    t = max(0., min(1., (v - .03) / (.28 - .03)))
    return t*t*(3-2*t)

for k in range(2, 7):
    assert fade(k) == 0.
    for mask in (.07, .2, .47, .85, 1.0):
        assert mask*(1-.55*fade(k)) + .47*.55*fade(k) == mask
        assert mask*(1-.55*fade(k)) + (5/9)*.55*fade(k) == mask

for src, dst in ((240,640), (160,427), (160,533), (144,480)):
    scale = dst / src
    a = .55 * fade(scale)
    assert a > .45, (src,dst,a)
    for original, mean in ((.1,.47),(.9,.47),(.15,5/9),(.95,5/9)):
        smooth = (1-a)*original+a*mean
        assert abs(smooth-mean) < abs(original-mean)*.55, (scale, original)

# The 1px Pocket SGB optical gap remains geometrically correct on exact
# integer scales and gets coverage-weighted on the RG35XX H's Fit scales.
def cov(phase:float,scale:float)->float:
    return min(1.,max(0.,1-abs(phase-.5))+max(0.,1-abs(phase-scale-.5)))
for k in (2,3,4,5):
    for i in range(k):
        assert abs(cov(i+.5,k)-float(i==0))<1e-9

for src,dst in ((160,533),(144,480)):
    scale=dst/src
    seq=[cov(((i+.5)/scale%1)*scale,scale) for i in range(dst)]
    assert any(.02<x<.98 for x in seq)
    assert abs(sum(seq)/len(seq)-1/scale) < .006

print("PASS: Dot/Grid integer parity, fractional mask contrast, and SGB source-RGB behavior")
