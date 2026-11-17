#!/usr/bin/env python3
"""Match Pocket Color's *entire calibrated appearance* with mGBA SGB colors.

The on-device test isolated the missing effect: Pocket SGB now has the
correct optical LCD grid and real SGB palettes, but its corrected white is
still SNES-white (near #fff). Pocket Color's measured GBC response instead
maps source white to its olive/gray LCD white (~#868c7a).

The Ver. 16 color-source fix must stay. Only the display Look changes:
return Screen::PocketColor.look() for SGB too, WITHOUT the lcd.y=0 SNES
transfer override. lcd.x=2 and lcd.y=1 thus match Pocket Color perfectly.

Correction On: same GBC measured response and physical white/black as
Pocket Color, applied to the *SGB RGB supplied by the mGBA core*.
Correction Off: the original RGB palette + the exact same Pocket LCD
dot/optics, with no color transformation.
"""
from pathlib import Path
path = Path("crates/slot-gfx/src/authentic.rs")
src = path.read_text()
old = """            Screen::PocketSgb => {
                // Identical geometry, panel, shadow, ghost and glass to
                // Pocket Color (lcd.x = 2). lcd.y is used ONLY to choose
                // the RGB transfer family when Color Correction is On.
                // SGB colors come from mGBA; never run them through GBC's LCD.
                let mut look = Screen::PocketColor.look();
                look.lcd[1] = 0.0;
                look
            },"""
new = """            Screen::PocketSgb => {
                // SGB hardware/palette is chosen by mGBA, not by the GPU.
                // Render its already-colorized RGB through EXACTLY the same
                // measured Pocket Color LCD response, including the olive
                // white point when correction is On and the full dot optics.
                // Off passes source RGB unchanged while retaining the grid.
                Screen::PocketColor.look()
            },"""
assert src.count(old) == 1, "Expected Ver. 16 Pocket SGB SNES-white override"
src = src.replace(old, new, 1)
assert src.count("Screen::PocketColor.look()") == 1
assert "look.lcd[1] = 0.0;" not in src
path.write_text(src)
print("PASS: SGB source palettes now receive exact Pocket Color LCD white point and optics")
