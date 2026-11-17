# select. slot. 1.16.0 Ver. 9

## Changes since select. slot. 1.16.0 Ver. 8

- **Authentic at Fit scaling:** the previous filter measured its LCD gap as one *output-screen pixel*, making it proportionally different at 2.67× or 3.33× than at integer scaling. The pixel-gap width now comes from the nearest native integer-size reference grid (e.g. 3×), with actual pixel coverage integrated against the display's fractional Fit scale.
- **Authentic GBA/GBC brightness:** the LCD brightness compensation now uses that same reference gap width, avoiding a mismatch between visual gap coverage and the brighter LCD pixel centres. Color Correction On/Off and measured color response remain unchanged.
- **Standard LCD:** removed the extra Fit-only attenuation, leaving the original area-integrated RGB stripe calculations and integer-scale rendering in place.
- **Pocket SGB performance:** SGB now has a dedicated shader branch *before* the expensive monochrome Pocket ink, multi-tap shadow and reflector calculations. The old code computed those effects and discarded them. The existing SGB color-correction toggle, optional reflection and dot separation are preserved.
- Added analytical reference-grid, integer-parity and shader-source regression tests. The H700 build compiles the final OpenGL ES shader.

**Fit cannot be pixel-for-pixel identical to Integer on a 640×480 display:** a 240-pixel GBA line would require 720 pixels at 3×, so fitting it into 640 pixels necessarily combines some adjacent LCD features. This update targets consistent *native-pixel geometry* and avoids additional contrast fading. Exact physical RG35XX H display appearance and mGBA SGB full-speed performance still require device verification.
