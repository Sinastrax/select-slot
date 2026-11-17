# select. slot. 1.16.0 Ver. 17

## Changes since select. slot. 1.16.0 Ver. 16

- **Restore Pocket Color's correct tinted LCD white for Pocket SGB.** Ver. 16 successfully restored both actual Pocket Color colors and the mGBA SGB palette, and its LCD grid looks correct. But Pocket SGB's Color Correction On was still selecting an SNES CRT transfer that leaves full-bright white nearly pure RGB white. Pocket Color's measured response produces the characteristic olive-gray LCD white (~RGB 134, 140, 122). The user specifically identified this missing physical screen hue.
- **Use exactly the same GPU `Screen::PocketColor.look()` for Pocket SGB.** Both modes now share all LCD optics, GBC measured response and white/black points when corrected. Only the underlying mGBA hardware color source differs: SGB palettes remain SGB, GBC palettes remain GBC. This replicates the real RG SP observation that switching the *display* to Pocket Color without restarting retains SGB colors and immediately produces the desired appearance.
- **Do not modify any LCD shader calculations or the now-working Ver. 16 core palette routing.** The build verifies that the entire merged fragment shader is byte-for-byte identical to Ver. 16, and asserts mGBA's SGB model/preset and GBC automatic palette routing are unchanged.
- **Color Correction semantics:** On provides the calibrated Pocket LCD white hue and color response; Off leaves RGB whites untinted as requested while the physical pixel grid, shadows, and glass remain in place. This is an intentional hybrid screen look, not an SNES TV simulation.

**Verification:** Final source routing, GLES2 compilation, H700 package and OTA verification are automated. The visual appearance still requires verification on a real RG SP or RG35XX H. Separate OTA download-size optimization is not included.
