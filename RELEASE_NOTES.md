# select. slot. 1.16.0 Ver. 14

## Changes since select. slot. 1.16.0 Ver. 13

- **Restore the known-working pre-RG35XX H Pocket Color optics.** In Ver. 5–13, attempts to fix fractional Fit scaling replaced the original Pocket Color LCD gap mask and ink/neighbor blend, then compounded the changes with new SGB reflector calculations. Ver. 14 restores the original Ver. 4 mask, ink blending and shared reflector/shadow formula for **both Pocket Color and Pocket SGB**.
- **Keep the SGB palette separate.** mGBA still provides the real SGB palette rather than a grayscale source. Pocket Color retains its GBC transfer response; Pocket SGB retains its optional SNES CRT response, without applying GBC color conversion to SGB colors. The physical LCD rendering code shared between these two profiles is restored, with no new mGBA settings or emulator changes.
- Other visual modes (monochrome GB models, regular Dot, Grid, GBA) retain their existing behavior; ROMs, saves and settings are untouched. Added final-stage checks of Ver. 4 optical expressions and independent SGB palette handling.

**Trade-off and verification:** original Ver. 4 color-Pocket dot sampling is intentionally restored on fractional Fit scaling, so old Fit artifacts may return for these two color models on 640×480 devices. The build and static checks cannot confirm physical LCD appearance. The goal is to recover the hardware-proven baseline first, not to claim this iteration is visually verified.
