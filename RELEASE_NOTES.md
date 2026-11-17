# select. slot. 1.16.0 Ver. 11

## Changes since select. slot. 1.16.0 Ver. 10

- **Pocket SGB now actually looks like Pocket Color:** removed the visually different SGB-only shader that used arbitrary gap multipliers and a simplified neighboring-dot shadow. Pocket SGB uses Pocket Color's exact LCD pixel-gap, ink, 4-tap shadow, reflector, glass and fractional Fit calculations. Both modes use the same physical LCD settings and ghosting.
- **Only the colors differ:** Pocket Color retains its measured GBC color response. Pocket SGB takes the SGB colors directly from mGBA, bypassing GBC calibration; its Color Correction Off preserves the core's RGB, and On uses the existing SNES CRT gamma ramp.
- Added exact source-level checks for the common optical rendering path and its individual palette transforms. Retained the full OTA installation package and previous compatible update identifiers.

**Hardware verification required:** sharing Pocket Color's complete shader may increase SGB graphics cost compared with the previous simplified fast path; the CI build checks compilation and packaging, not measured on-device FPS. Real RG35XX H SGB appearance and performance need confirmation.
