# select. slot. 1.16.0 Ver. 15

## Changes since select. slot. 1.16.0 Ver. 14

- **Pocket SGB now uses EXACTLY the Pocket Color Authentic rendering profile.** On the physical RG SP, switching the running SGB game to Pocket Color instantly produced the desired LCD appearance while the previously loaded SGB palette was still active. The existing Pocket SGB profile instead set `u_lcd.x = 3.0`, selecting a different shader color path; Pocket Color used `2.0`.
- **No longer treat SGB as a separate GPU screen.** Its `Screen::PocketSgb` profile now returns `Screen::PocketColor.look()` *unchanged*: same physical dot geometry, ink, gap blending, reflector, ghosting, glass, correction-on and correction-off GLSL paths. The shader source itself is not modified.
- **Keep mGBA's actual SGB palette and hardware on restart.** Slot still saves Pocket SGB as a distinct model and launches mGBA in `Super Game Boy` mode with SGB presets and borders off. This keeps the visual profile separate from emulation mode.
- Added a final-stage regression test proving that Authentic selection is independent of Color Correction On/Off, and that Pocket SGB and Pocket Color select identical GPU optics while the mGBA hardware palette selection stays separate.

**Verification:** Source routing, OpenGL ES 2.0 compilation and complete OTA packaging are checked in CI. Physical appearance and performance remain subject to a real RG SP/RG35XX H test. In this version the screen *look* is deliberately identical, while the underlying game palette is chosen by the emulator. This does not include the separate OTA size optimization.
