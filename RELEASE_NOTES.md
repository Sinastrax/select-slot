# Custom slot. 1.16.0 Ver. 3

## Changes since Custom slot. 1.16.0 Ver. 2

- Fixed **Authentic → Color Correction On** for GBA and GBC: restore the original measured LCD response, including the model's physical panel tint, brightness and black/white levels, rather than preserving modern RGB brightness and neutral whites.
- **Color Correction Off** keeps the original game's RGB colors with Authentic's pixel grid, shadows and LCD response still active.
- Restored calibrated GBC panel colours for Pocket Color when correction is enabled; its uncorrected palette mode remains neutral.
- Added regression checks to protect the independent On/Off behavior and avoid the near-white/yellow desaturation introduced in Ver. 2.

The Reflection toggle fix and other Authentic geometry and emulator changes remain unchanged.
