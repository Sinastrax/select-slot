# Custom slot. 1.16.0 Ver. 4

## Changes since Custom slot. 1.16.0 Ver. 3

- Fixed **GBA Authentic with Color Correction Off** looking too bright and too similar to an unfiltered LCD image: pixel centres now retain the source RGB without the inverse pixel-grid brightness boost, so the dark LCD gaps naturally reduce the overall brightness.
- **Authentic with Color Correction On** still uses the original measured GBA LCD response and calibrated panel levels from Ver. 3.
- Other Authentic modes (GB, GBC, Pocket Color and Pocket SGB), Reflection, LCD response, emulator cores and scaling remain unchanged.
- Added a regression check to keep this change limited to uncorrected GBA rendering.

The adjustment does not introduce additional color tint or alter the underlying game palette.
