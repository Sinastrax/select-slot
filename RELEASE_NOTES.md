# select. slot. 1.16.0 Ver. 7

## Changes since select. slot. 1.16.0 Ver. 6

- **RG35XX H Fit / Dot shader:** reduced uneven pixel-dot intensity at noninteger GBA/GB scaling (e.g. GBA 2.67×, GB 3.33×), keeping the dot structure and average darkness rather than changing game colors.
- **RG35XX H Fit / Grid shader:** stabilized the contrast of the pixel grid's intersecting rows and columns at fractional scale. The existing area-integrated grid geometry remains.
- **Pocket SGB with Gambatte and mGBA:** corrected the shared rendering path so colored SGB palette pixels are not interpreted as monochrome Pocket ink or run through the GBC LCD calibration. Their original RGB hues survive with a mild, antialiased Pocket-style pixel pattern.
- **Gambatte SGB palettes:** disables its additional GBC LCD color correction for SGB selections, which are intended for TV display.
- **Integer scaling:** Dot and Grid visual masks are unchanged at exact 2×, 3×, and other integer multiples. Existing GBA/GBC color correction, reflection toggles, regular Pocket and Pocket Color models, cores, and saves remain unchanged.
- Added source/numerical regression checks; the complete H700 build still validates the generated OpenGL ES shaders.

**Note:** Gambatte supplies game-specific SGB preset palettes, whereas mGBA supports SGB hardware and in-game palette commands. Their resulting colors may differ by game. The update is delivered via the existing OTA updater; physical RG35XX H appearance requires on-device verification.
