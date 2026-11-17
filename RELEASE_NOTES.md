# select. slot. 1.16.0 Ver. 10

## Changes since select. slot. 1.16.0 Ver. 9

- **Game Boy Pocket Authentic at Fit scaling (RG35XX H):** fixed the monochrome shader's handling of partially covered LCD dot separators. Ver. 9 calculated fractional gap coverage, but the final Pocket ink routine still used an all-or-nothing 0.5 threshold. Fit now blends the actual ink contribution of the centre dot, the left/upper gap and their ink-free intersection instead of dropping or snapping partial gaps.
- **Pixel geometry and performance isolation:** integer-scaled DMG, Pocket and Light dots retain the exact original ink calculation. The independent Pocket SGB fastpath, GBA/GBC color response, Authentic Color Correction On/Off, glass/reflections and other scaling modes are unchanged.
- Added source-routing checks to confirm that the GB Authentic + Pocket menu choices reach the expected shader path, and numerical tests of fractional Fit coverage and exact integer-scale parity. The H700 pipeline also checks OpenGL ES shader compilation.

**Device verification is still required:** the source-level issue and its mathematical treatment have been corrected, but the exact appearance of the RG35XX H panel cannot be confirmed from build tests alone.
