# Custom slot. 1.16.0 Ver. 5

## Changes since Custom slot. 1.16.0 Ver. 4

- Fixed **Authentic GBA/GBC LCD pixel-gap aliasing at fractional Fit scales**, particularly the RG35XX H's 640×480 panel (approximately 2.67 output pixels per GBA pixel). Fractional gaps now use destination-pixel coverage rather than uneven hard on/off samples.
- Improved **standard LCD-grid shader precision** on non-3:2 panels to reduce uneven subpixel stripes and banding at Fit scaling. Keeps the existing LCD mask, without adding blur to game artwork.
- Preserved integer-scale Authentic gap rendering (2× through 6×) and did not change game aspect ratios, shaders' calibrated color correction, reflection settings, or emulator cores.
- Added a deterministic geometry regression test for Fit and integer scaling.

Physical display differences and camera moiré may still be noticeable at 2.67× because this is not an integer pixel scale.
