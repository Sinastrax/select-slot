# Custom slot. 1.16.0 Ver. 3

## Changes since Custom slot. 1.16.0 Ver. 2

- Restored pvaibhav's original measured GBA and GBC LCD colour calibration for **Authentic → Color Correction: On**, including the panel's own white point, black point and brightness response.
- **Color Correction: Off** now retains the uncorrected game RGB under Authentic's existing LCD pixel grid and screen effects, without applying a simulated panel colour transform.
- Aligned the custom Pocket Color mode with the original GBC colour response when correction is On; kept its uncorrected palette colours when Off.
- Preserved separate Reflection controls and existing GB/GBC/GBA shader effects.

No emulator-core, audio or control changes.
