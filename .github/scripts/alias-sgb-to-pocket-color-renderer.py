#!/usr/bin/env python3
"""Make Pocket SGB use the *identical* Pocket Color Authentic screen renderer.

Confirmed using the live-change observation on RG SP: switching from
Pocket SGB to Pocket Color while an mGBA SGB game is already running
immediately produces exactly the desired LCD appearance, while the SGB
source RGB persists until the emulator restarts.

Keep Core::Mgba with GbColors::SgbAuto and the saved model selection.
Change ONLY the selected GPU profile: both screen variants now return
precisely the same Look, including the shader discriminator lcd.x=2.
The same GLSL branch handles corrected and uncorrected colors, same dot
geometry, shadow, reflector, ghosting, and glass. No new optical formula.
"""
from pathlib import Path
path=Path("crates/slot-gfx/src/authentic.rs")
src=path.read_text()
old="""            Screen::PocketSgb => {
                // Exactly Pocket Color's LCD optical model and response.
                // Only the source palette is SGB/SNES, selected by lcd.x.
                let mut look = Screen::PocketColor.look();
                look.lcd[0] = 3.0;
                look
            },"""
new="""            Screen::PocketSgb => {
                // Use EXACTLY the same GPU screen profile as Pocket Color.
                // The SGB palette comes from mGBA core options, not u_lcd.x.
                // Identical uniforms intentionally select identical GLSL
                // branches, for both Color Correction On and Off.
                Screen::PocketColor.look()
            },"""
assert src.count(old)==1, "Expected Ver. 14 SGB-specific shader discriminator"
assert src.count("Screen::PocketColor => {")==1
src=src.replace(old,new,1)
assert "look.lcd[0] = 3.0;" not in src
assert "look.lcd[0] = 2.0;" in src
path.write_text(src)
print("PASS: Pocket SGB GPU Look is now byte-for-byte equivalent to Pocket Color")
