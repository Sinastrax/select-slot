# select. slot. 1.16.0 Ver. 13

## Changes since select. slot. 1.16.0 Ver. 12

- **Pocket SGB now reuses Pocket Color's full optical treatment, not just its pixel-gap outline.** Ver. 12 overrode Pocket Color's ink-derived reflector calculation with a raw geometric mask. That made roughly half the synthetic Fit image act like reflector, instead of approximately 6% with Pocket Color's physical optical model. Ver. 13 restores the same Pocket Color ink-dependent gap response, multi-tap shadow, ghosting, reflector and glass calculations for SGB.
- **Keep the correct mGBA SGB colors.** SGB source RGB is unchanged at dot interiors. The real geometric gap is only an upper bound on reflector coverage to prevent Ver. 11's gray/washed-out saturated SGB pixels. The calibrated GBC transfer remains exclusive to Pocket Color, the optional SNES CRT response remains exclusive to SGB.
- Added CPU-modeled rendered reference frames for two distinct SGB palettes against the Pocket Color optical reference, including fractional Fit gaps. The CI stores a visual comparison preview and checks optical-gap coverage. All previous mGBA, Pocket Color, shader, settings, and OTA compatibility tests remain.

**Hardware check:** Synthetic reference renders and OpenGL ES compilation cannot replace a photograph or FPS measurement from a real H700 device. Verify SGB appearance and performance on RG35XX H before considering the issue fully resolved.
