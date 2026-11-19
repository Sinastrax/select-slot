# select. slot. 1.16.0 Ver. 38 — Clearer built-in shortcut guide

An **interface-text-only** refinement of Ver. 37 for Anbernic H700 devices. The user confirmed that the Ver. 37 update mechanism works on RG35XX H, but some short labels were difficult to interpret.

## What changed

- Read-only **Controls → Fixed Shortcuts** entries now spell out button names: **SELECT + VOLUME +**, **BOTH VOLUME BUTTONS**, **MENU TWICE**, **HOLD SELECT**, etc., rather than shorthand such as SEL, VOL, FF KEY, and 2x.
- The Fast-Forward rows now **show the actual configured shortcut button**, such as **R2 TWICE** to lock or **R2** to stop. If the user has rebound it, the displayed key follows that setting. An unassigned key explicitly reads **NOT ASSIGNED**.
- The double-MENU action is labeled **Screenshots / States** to reflect its context-sensitive behavior. Game Boy and Game Boy Color references no longer use the unclear GB/C abbreviation.
- The reference remains **read-only**. The pre-existing editable Shortcuts page has not changed.

## Explicitly unchanged

- Every physical shortcut, volume/mute timing, POWER/MENU input handling, fast-forward operation, gameplay mapping, Link Play controls, save states, and emulator behavior.
- Existing configuration files, user mappings, achievements, saved games, Wi-Fi, shaders, OTA updates and installed ROMs. No migration.
- Miyoo firmware and releases.

## Verification

H700 CI runs the full Rust regression suite, plain-label and dynamic-binding tests, shader checks, source/OTA safety validation, firmware build, archive checksums, and release publication checks. These automated tests cannot prove text readability or appearance on a physical device.

**Platforms:** compatible Anbernic H700 handhelds (including RG35XX H, RG35XXSP and RG34XXSP). **Not for Miyoo Mini**. Ver. 36 remains a confirmed working fallback; Ver. 37 has a confirmed working update path. Ver. 38 still requires checking the labels on actual hardware.
