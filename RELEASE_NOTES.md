# select. slot. 1.16.0 Ver. 16

## Changes since select. slot. 1.16.0 Ver. 15

**The LCD effect is already correct. This version changes color routing ONLY.**

- **Pocket Color Auto no longer forces monochrome Game Boy hardware.** Slot previously passed the saved Auto palette through the explicit-palette branch, which selected `mgba_gb_model=Game Boy` and disabled game-specific GBC hardware colors at restart. An internal, non-menu `GbcAuto` directive now selects `Game Boy Color` hardware, GBC automatic title palettes, and the user's independent Pocket LCD renderer. Explicitly selected palettes and the original monochrome Authentic models keep their previous behavior.
- **Pocket SGB keeps its real SGB palettes when Color Correction is enabled.** Ver. 15 correctly reused Pocket Color's optical screen but the shared `u_lcd.x=2` inadvertently selected the GBC color-correction transfer for SGB too. Both profiles still use `u_lcd.x=2` for the **identical full Pocket LCD optics**; the otherwise unused color-ramp selector `u_lcd.y` now distinguishes the GBC measured response (Pocket Color) from the optional SNES CRT response (SGB).
- **Color Correction Off** continues passing the emulator's RGB unchanged. **On** applies the appropriate console color response. Neither toggle switches off the Authentic LCD filter.
- **No changes** to the pixel-gap mask, neighbor ink, reflections, shadows, persistence, fit scaling, or the renderer's optical final mix. No change to ROMs, saves, or mGBA core binary.
- Added regression checks for the mGBA model/palette options actually selected when starting games, correction-path selection, and unchanged LCD mathematics.

**Verification boundary:** CI verifies the final merged source, GLSL ES2 shader, Rust compilation and OTA package. Physical colors still need confirmation on RG SP / RG35XX H. The separate OTA size optimization is not included.
