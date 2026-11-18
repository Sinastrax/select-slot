# select. slot. 1.16.0 Ver. 19

## Changes since select. slot. 1.16.0 Ver. 18

- **Original GBA is now a selectable GBA bezel** alongside the existing **AGS-102 (GBA SP)** and **None**. Its bottom text reads **GAME BOY ADVANCE**, not **GAME BOY ADVANCE SP**. The existing 640×480 SP artwork provides the exact same transparent screen opening, bottom bar geometry and on/off slide animation.
- **Only the 3.5-inch 640×480 Anbernic framed layout offers this new option**, including the RG35XX H. The RG SP and RG34XXSP's 720×480 fullscreen GBA layout is unchanged and does not expose it. Selecting it does not alter display scaling, image cropping or shader properties.
- **Saved per-platform selection.** Original GBA persists as `bezel_gba=agb-001`; the existing AGS-102 remains the default for existing and new configurations. Any custom GBA bezel files still work.
- **Licensed image derived from upstream Slot's original SP bezel** by recentering the existing GAME BOY ADVANCE lettering and removing SP. Preserves all alpha values, gameplay-opening pixels, and top/bottom screen artwork outside the bottom 32-pixel text band. The image is generated inside `System/bezels` during each H700 firmware build, with upstream CC BY-SA 4.0 attribution retained.
- **No changes to shaders, palettes, core options, frame timings or Miyoo firmware.** CI hash-locks the complete Ver. 18 shader and the hardware-confirmed Pocket/SGB profiles. Only the H700 menu, bezel drawing, and generated image differ.

**Verification:** CI builds the menu code, validates the 640×480-only selection, verifies the generated PNG retains the original alpha mask and screen opening, checks updater compatibility, and produces the complete H700 OTA. Actual bezel appearance still requires a 3.5-inch Anbernic device test.
