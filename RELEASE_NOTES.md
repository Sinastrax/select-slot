# select. slot. 1.16.0 Ver. 12

## Changes since select. slot. 1.16.0 Ver. 11

- **mGBA Pocket SGB visual regression:** Ver. 11 passed pre-colorized SGB pixels through Pocket Color's grayscale-ink-based reflector blend; saturated source colors could become dominated by the neutral reflector. The SGB path now preserves each dot's SGB RGB and uses the Pocket LCD's actual fractional/int-indexed separator coverage for its reflector instead of computing SGB color coverage from brightness. The original Pocket Color palette, physical optical model and other GB/GBA shaders are unchanged.
- **Visible Fit pixel separation:** SGB uses the same integer-reference dot-gap geometry as Pocket Color, analytically integrated at fractional Fit sizes. Color Correction Off/On, mGBA hardware/palette settings, and reflection controls remain independent and unchanged.
- Added source and analytical tests of SGB source-RGB conservation at pixel interiors, gap visibility and mGBA routing. Firmware is built and published as a full OTA-compatible update.

**Hardware verification required:** CI can prove the GLSL compiles and the SGB path preserves chromatic pixel interiors and geometric LCD gaps, but cannot verify the precise screen appearance or mGBA FPS on physical RG35XX H hardware.
