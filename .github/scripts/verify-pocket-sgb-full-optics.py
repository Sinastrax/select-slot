#!/usr/bin/env python3
"""CPU-modeled visual parity check for Pocket Color vs Pocket SGB.

Render the same four-shade test frame under GBC and SGB RGB palettes.
The optical formulas below mirror the Pocket's shader: shared ink,
fractional Fit gap/neighbor blending, simulated dot shadow, and the
shared pixel/reflector/shadow mix. Shader is separately compiled as
OpenGL ES 2.0 by check-gles2-shader.py.

This checks visual structure across distinct colors, not physical
handheld GPU output, brightness or emulation performance.
"""
from pathlib import Path
import math

shader=Path("crates/slot-gfx/src/shaders.rs").read_text()
auth=Path("crates/slot-gfx/src/authentic.rs").read_text()
core=Path("crates/slot/src/core.rs").read_text()
app=Path("crates/slot/src/app.rs").read_text()
front=Path("crates/slot/src/frontend.rs").read_text()
assert "float pocketOpticalGapShare = gapShare;" in shader
assert "pocketOpticalGapShare = min(gapShare, physicalPocketGap);" in shader
assert "float physicalPocketGap = gap.x + gap.y - gap.x * gap.y;" in shader
assert "mix(panelRgb, reflector, pocketOpticalGapShare)" in shader
assert "float sgbGapShare = gap.x + gap.y - gap.x * gap.y;" not in shader
assert "float shadowShare = clamp(dotLuma / max(baseLuma, 0.03), 0.0, 1.0);" in shader
assert "float gapShare = clamp((dotLuma - baseLuma) /" in shader
assert "float shadow = ink_near(" in shader
assert "float leftGap = u_ink.z * (a + west);" in shader
assert "float upperGap = u_ink.z * (a + north);" in shader
assert "vec3 panelRgb = raw;" in shader
assert "if (u_authentic_correction > 0.5 && u_lcd.x < 2.5)" in shader
assert "vec3 sgbCode = floor(raw * 31.0 + vec3(0.5));" in shader
assert "vec3 reflector = u_authentic_correction > 0.5" in shader
assert "let mut look = Screen::PocketColor.look();" in auth
assert "look.lcd[0] = 3.0;" in auth
assert "GbModel::PocketSgb => slot_gfx::Screen::PocketSgb" in front
assert "Shader::Authentic if self.gb_model() == GbModel::PocketSgb => GbColors::SgbAuto" in app
assert 'core.set_option("mgba_gb_model", "Super Game Boy");' in core

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def clamp(x):return max(0.,min(1.,x))
def mix(a,b,t):return tuple(x*(1-t)+y*t for x,y in zip(a,b))
def subpalette(rgb):return tuple(x/255 for x in rgb)
L=subpalette((166,172,132))
D=subpalette((18,25,34))
weights=(.2126,.7152,.0722)
glass=(.8,.9,.76)
ref=(1.,1.,1.)
uink=(3/3.5,.03,.38,.8*.9*.45)
GBC=[(254,255,250),(178,212,165),(85,120,100),(20,45,36)]
SGB=[(255,255,245),(252,205,71),(174,74,39),(62,33,112)]
SGB2=[(250,242,245),(209,104,191),(76,47,193),(11,5,40)]
GW,GH=24,18
OW,OH=96,60

def source_idx(x,y):
    if 3 <= y < 8 and 4 <= x < 20:
        return 1 if (x+y)%3 else 2
    if (x-7)**2+(y-12)**2 < 20:
        return 2
    if (x-17)**2+(y-13)**2 < 10:
        return 3
    return ((x//3)+(y//3))%4

def gap_fraction(f,span):
    nearest=max(1,int(math.floor(span+.5)))
    width=1/nearest
    footprint=.5/span
    low,high=f-footprint,f+footprint
    area=max(0,min(high,width)-max(low,0))+max(0,min(high,1+width)-max(low,1))
    if abs(span-nearest)<.0005:
        return float(f*span<=1.)
    return clamp(area*span)

def image(palette,screen):
    rgb=[subpalette(p) for p in palette]
    def ink(x,y):
        if not (0<=x<GW and 0<=y<GH):
            return 0.
        color=rgb[source_idx(x,y)]
        return clamp(uink[0]*(1-sum(color)/3)+uink[1])
    spanx,spany=OW/GW,OH/GH
    pixels=[]
    total_gap=0.
    nonempty_chroma=0
    dot_count=0
    for py in range(OH):
        for px in range(OW):
            fx=(px+.5)/spanx
            fy=(py+.5)/spany
            ix,iy=int(fx),int(fy)
            gx=gap_fraction(fx-ix,spanx)
            gy=gap_fraction(fy-iy,spany)
            geo=gx+gy-gx*gy
            raw=rgb[source_idx(ix,iy)]
            baseInk=ink(ix,iy)
            west,north=ink(ix-1,iy),ink(ix,iy-1)
            a=(1-gx)*(1-gy)*baseInk+gx*(1-gy)*uink[2]*(baseInk+west)+(1-gx)*gy*uink[2]*(baseInk+north)
            # Four-tap shadow shader approximated by its local-neighbor
            # average, while its shared gain and ink-occlusion are exact.
            ne=ink(min(ix+1,GW-1),max(iy-1,0))
            shadow=ne*uink[3]*(1-.75*a)
            c=tuple(D[j]*a*(1-glass[0]*a*a)+L[j]*(1-shadow)*(glass[1]-glass[2]*a) for j in range(3))
            base=tuple(D[j]*baseInk*(1-glass[0]*baseInk**2)+L[j]*(glass[1]-glass[2]*baseInk) for j in range(3))
            base_l=dot(base,weights)
            dot_l=dot(c,weights)
            panel_l=dot(L,weights)*glass[1]
            optical=clamp((dot_l-base_l)/max(panel_l-base_l,.03))
            shade=clamp(dot_l/max(base_l,.03))
            if screen=='sgb':
                mask=min(optical,geo)
                # SGB palette must be unmodified in pixel interiors.
                if geo==0.:
                    assert mask==0., "Dot interiors cannot become gray reflector"
                    assert mix(raw,ref,mask)==raw
                    nonempty_chroma+=1
            else:
                mask=optical
            total_gap+=mask
            dot_count+=1
            output=tuple(clamp(v*shade) for v in mix(raw,ref,mask))
            pixels.extend(round(v*255) for v in output)
    return bytes(pixels),total_gap/dot_count,nonempty_chroma

gb,gb_gap,_=image(GBC,'pocket')
sg,sg_gap,chroma=image(SGB,'sgb')
sg2,sg2_gap,_=image(SGB2,'sgb')
assert 0.01 < gb_gap < .16,(gb_gap,sg_gap)
assert 0.01 < sg_gap < .16,(gb_gap,sg_gap)
assert abs(gb_gap-sg_gap) < .035,(gb_gap,sg_gap)
assert abs(gb_gap-sg2_gap) < .035,(gb_gap,sg2_gap)
assert chroma>0
# Render a synthetic two-panel *color-swapped* Pocket reference preview.
# PPM avoids Pillow/image dependencies in the firmware build container.
rows=[]
for y in range(OH):
    a=y*OW*3;b=a+OW*3
    rows.append(gb[a:b]+sg[a:b]+sg2[a:b])
out=Path("pocket-sgb-visual-parity.ppm")
out.write_bytes(f"P6\\n{3*OW} {OH}\\n255\\n".encode("ascii")+b"".join(rows))
print("PASS: Pocket Color and SGB share optical gap density under color swap:",round(gb_gap,4),round(sg_gap,4),round(sg2_gap,4),"; preview",out)
