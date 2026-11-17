# select. slot. 1.16.0 Ver. 5

## Changes since select. slot. 1.16.0 Ver. 4

- Rebuilt the Fit scaling fix from the working Ver. 4 shader baseline after the withdrawn first Ver. 5 caused a frontend boot loop on the RG35XX H.
- **Authentic GBA/GBC with fractional Fit scaling:** replaced the original uneven hard-edged LCD gaps with a minimal one-pixel-coverage calculation for displays such as the RG35XX H's 640×480 screen.
- **Standard LCD-grid shader:** retained Ver. 4 rendering and precision settings instead of the original Ver. 5 rewrite.
- Kept integer scaling, calibrated/uncorrected Authentic color modes, Reflection, and emulator cores unchanged.
- Added OpenGL ES 2.0 shader compilation/linking checks and OTA publisher regression tests.

**Hardware validation:** Automated build and shader checks cannot prove boot compatibility with the RG35XX H's GPU. This replacement should be tested on the handheld. Ver. 4 remains available as a recovery release.
