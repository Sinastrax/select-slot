# select. slot. 1.16.0 Ver. 18

## Changes since select. slot. 1.16.0 Ver. 17

- **Improve GBA Authentic specifically at fractional Fit on the RG35XX H.** A 240×160 GBA game displayed at 640×427 uses ~2.67 output pixels per source pixel. The existing nearest-integer-reference LCD band and antialiasing remain; now overlapping vertical and horizontal GBA pixel gaps are combined by physical area union at noninteger scaling, instead of `max()`. This prevents partly covered intersections from losing their grid strength.
- **Match the GBA brightness compensation to the integrated mask.** The corrected RGB cell average is updated only under fractional GBA Authentic Fit; original GBA measured color response, pale blue-white panel, source palette, reflective glass and ghosting remain unchanged. With Color Correction Off, source RGB remains unboosted and the pixel effect stays active.
- **Preserve every integer-scaled Authentic frame.** The new fractional blend is zero at exact integer 2×/3×/4×. This also leaves the standard GBA Dot, Grid and LCD effects unchanged: their existing RG35XX H fractional-scale improvements already apply to GBA, not just GB/GBC.
- **Lock the user-confirmed Ver. 17 Pocket Color and Pocket SGB rendering.** CI checks that their complete Authentic Look implementation is byte-for-byte identical and that the merged fragment shader has precisely two GBA-only optical edits from Ver. 17. No palette/core changes, saved-setting changes or modifications to Miyoo firmware.

**Tests:** CPU coverage verification for GBA 640×427 Fit and original integer scale, shader-diff isolation, OpenGL ES 2.0 shader compilation/linking, full H700 build and OTA integrity verification. These checks cannot substitute for an actual RG35XX H display test. Like any noninteger scaling, slight uneven pixel widths are unavoidable.

