# select. slot. 1.8.1 Ver. 11 — Miyoo clean rebuild

This is an **experimental fresh rebuild from the original, working [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo)**, pinned to commit `d096bdb87f25f3aba62de6b40ef859b61d841e43`. Original Slot upstream is v1.8.1.

**Why this rebuild exists:** The original Miyoo Slot displayed correctly on the user's physical original Miyoo Mini, but the modified version made **the entire display too dark even at brightness level 9**. Earlier attempts changing Onion brightness synchronization and stored settings did not fix it. The screen is not being treated as a palette or color-correction fault.

The clean rebuild keeps these **unaltered from Dean's original port**:

- `card/System/launch_frontend.sh` (verified byte-for-byte identical during packaging)
- `crates/slot-power/` and its original PWM/backlight calibration
- `crates/slot-gfx/` including the software compositor, all brightness handling, framebuffer rotation, and the native LCD3x effect
- Original screen-off, sleep/wake, shutdown and button-power handling
- Original OnionOS boot/shutdown transitions, including existing BMO theme assets; no extra BMO animation hooks are installed
- No `SLOT_ONION_BRIGHTNESS` import, brightness state migration, display diagnostics, or new brightness logic

The feature patch is *allowlisted* to eight non-hardware source files, and the build rejects changed backlight handling.

## Preserved custom features

- Game Boy / Game Boy Color default core: **Gambatte**, configured with neutral dark-filter level 0. Game Boy palettes include Off and the supported built-in choices. Optional GBC correction uses accurate mode rather than a forced darkening fast mode.
- Game Boy Advance default core: **gpSP**. mGBA remains available for legacy selections and some game overrides.
- Per-game scaling: Original, Integer, Aspect Fit, Fill/Crop, Full Stretch.
- **Resume on Power On** and **Resume on Insert** as separate preferences.
- Original SLOT menu, framebuffer software renderer, power-management behavior and OnionOS runtime.

**Deferred to keep the brightness fix isolated:** Added menu-idle screen-off/power-off timers; custom splash interventions during SLOT sleep/wake; H700-only Authentic shaders and GLSL color correction; H700 OTA. These are **not** included in this clean Miyoo rebuild. The original Mini has no onboard Wi-Fi.

## Installation

1. Back up your SD card, especially `Config/slot.state`, `Saves/` and any current `System/slot`.
2. Download the successful **select-slot-miyoo-clean-rebuild** artifact from GitHub Actions. The artifact contains `select-slot-1.8.1-ver11-miyoo.zip` and a SHA-256 checksum.
3. Extract **the contents** of `select-slot-1.8.1-ver11-miyoo.zip` to the root of your Miyoo SD card. Your card should directly contain `System/slot`, `App/Slot/`, and `Apps/slot.pak/`.
4. Reboot and launch **select. slot.** from the installed app.
5. ROMs go in `Games/GB/`, `Games/GBC/`, and `Games/GBA/`; a legally obtained GBA BIOS may be put in `BIOS/gba_bios.bin`.

This is an **ARMv7 application**, **not firmware**, and does not replace OnionOS. It overwrites the same `System/slot` path as Dean's version. No H700 SD2 files are included.

### Optional auto-boot

The included `System/autoboot/onion-startup.sh` can be copied manually to `.tmp_update/startup/custom-slot.sh` for OnionOS autoboot. It delegates to Dean's unchanged launcher and never replaces `.tmp_update/runtime.sh`. To revert autoboot, delete or rename the custom startup file.

### If you are comparing to the original Dean release

This build is intentionally minimal. It will not modify a previously saved brightness value in `Config/slot.state`; it uses Dean's original read and power setup. A clean test on a separate backed-up configuration can eliminate settings left by earlier experimental builds, but this build will not delete or reset user settings automatically.

## Build and verification

The build script clones the exact Dean port commit and adds Gambatte through the original ARMv7 toolchain. Only the allowlisted custom app/core modules receive the generated patch. The workflow checks package structure, checksums, CPU architecture and **launcher byte equality** with the original port.

This remains **hardware-untested** until used on the physical Mini. A successful CI build proves packaging/compilation, not visual brightness or working sleep/wake behavior.

## Credits and licence

Original SLOT: [slot-cfw/slot](https://github.com/slot-cfw/slot). Original Miyoo port and software renderer: [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo). Select customizations: [Sinastrax/select-slot](https://github.com/Sinastrax/select-slot). Respect upstream GPL-3.0-or-later and bundled core licences; no ROMs or BIOS images are distributed.
