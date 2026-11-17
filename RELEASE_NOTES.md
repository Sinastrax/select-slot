# select. slot. 1.16.0 Ver. 8

## Changes since select. slot. 1.16.0 Ver. 7

- **Authentic GBA/GBC, Fit scaling:** restores visible LCD pixel-gap separation. The previous fractional-scale anti-aliasing removed up to 85% of the vertical contrast; now it reduces at most 15%, while preserving the gap coverage and the existing calibrated On/uncorrected Off colors.
- **Standard LCD shader, Fit scaling:** retains 85% of its original RGB stripe modulation instead of 15%. Existing analytic coverage integration and integer-scale appearance remain intact.
- **Grid shader:** replaces the flattened near-uniform fractional-scale grid with the area-weighted *union* of its vertical and horizontal bands. Grid intersections now have coherent coverage at noninteger Fit sizes.
- **Dot shader:** keeps 85% of the original dot-mask contrast at fractional Fit instead of flattening 55% of the detail. Exact integer scaling remains unchanged.
- **Pocket SGB:** stronger, clearly separated Pocket-style pixel gaps with a subtle neighboring-dot shadow. No longer treats SGB palette saturation as monochrome Pocket ink.
- **SGB Color Correction:** **Off** preserves the emulator's SGB/SNES RGB palette. **On** uses Near's documented 32-code SNES CRT gamma approximation; it never applies the GBC LCD calibration to SGB colors. The separate LCD geometry and Reflection setting remain active in both modes.
- Updated source and numeric regression tests, including a check of all 32 SNES gamma values. The CI build validates the resulting OpenGL ES shader.

*The SNES CRT gamma ramp is a documented approximation, not a measured colorimetric calibration for your specific TV or handheld. RG35XX H and RG SP display appearance still require physical verification.*
