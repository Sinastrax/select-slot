# select. slot. 1.16.0 Ver. 6

## Changes since select. slot. 1.16.0 Ver. 5

- Reduced the pronounced **vertical LCD stripes** when using **Fit scaling** at fractional pixel ratios on the 640×480 RG35XX H.
- **Authentic GBA/GBC:** softly suppresses the uneven vertical gap contrast when individual source pixels cannot be displayed at an integer multiple, while maintaining their average dark-gap coverage and brightness.
- **Standard LCD shader:** softly suppresses its RGB vertical stripe contrast at fractional pixel scales without altering horizontal scanlines, texture area integration, or precision settings.
- **Integer scaling remains identical:** the original Authentic and standard LCD stripe patterns are retained at exact 2×, 3×, and other integer scaling ratios.
- Unchanged: calibrated Authentic color correction, Color Correction Off, Reflection, emulator cores, and game scaling geometry.
- Added numerical Fit/integer regression checks and retained automatic OpenGL ES shader compilation validation.

This is an OTA update from Ver. 5. Hardware appearance still requires visual confirmation on the RG35XX H.
