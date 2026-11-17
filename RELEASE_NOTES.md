# select. slot. 1.16.0 Ver. 5

## Changes since select. slot. 1.16.0 Ver. 4

- Fixed **Authentic GBA/GBC LCD pixel-gap aliasing at fractional Fit scales**, including on the RG35XX H's 640×480 display. Fractional gaps use destination-pixel coverage rather than uneven hard samples.
- Improved **standard LCD-grid shader precision** on non-3:2 panels to reduce subpixel banding at Fit scaling without blurring artwork.
- Preserved integer-scaling behavior, calibrated color correction, reflection settings, emulator cores and game aspect ratios.
- Added a deterministic geometry regression test for Fit and integer scaling.

The project name changed to **select. slot.** without publishing a separate firmware version or altering the Ver. 5 tag and archive.
