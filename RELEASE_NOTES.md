# select. slot. 1.16.0 Ver. 5 — replacement candidate

## Changes since select. slot. 1.16.0 Ver. 4

- Rebuilt the Fit scaling fix from the Ver. 4 shader baseline after the initial Ver. 5 caused a startup loop on the RG35XX H.
- **Authentic GBA/GBC with fractional Fit scaling:** use a small, coverage-weighted LCD gap expression to reduce irregular gap stripes on the 640×480 screen.
- Kept the **standard LCD-grid shader exactly as in Ver. 4**, including its original GPU precision declarations. The earlier invasive pixel-grid rewrite was removed.
- Preserved integer pixel scaling, Authentic calibrated On/uncorrected Off modes, Reflection, and all emulator cores.
- Added regression checks for subpixel coverage and OpenGL ES 2.0 shader compilation/linking during the H700 build.

**Testing status:** Not confirmed on RG35XX H yet. This candidate remains unpublished until it boots and its Fit scaling can be inspected on-device.
