# select. slot. 1.16.0 Ver. 37 — On-device fixed shortcuts guide

An H700 interface-only update built on the **user-confirmed Ver. 36** firmware. The physical shortcuts themselves have **not** changed.

## New: fixed shortcut reference

Open **Controls → Fixed Shortcuts**. The reference is organized into **Global, In-Game, Shelf, Collections and Save States**. Each row shows an action beside its actual physical button or combination, including:

- All three mute gestures: **SELECT + VOL+**, **SELECT + VOL−**, and **VOL+ + VOL−**.
- MENU single-tap, double-tap and hold actions; **SELECT + MENU** for Link Play.
- Fast-forward double-tap latch (using the currently bound fast-forward key).
- GB/GBC L1/R1 stretch/restore behavior when the shoulders are not mapped to game inputs.
- POWER taps and holds, shelf hold actions, collection actions and save-state switcher navigation.

This is an **informational, read-only menu**. A, X, Y and left/right cannot reassign or clear any reference entry. The existing editable **Controls → Shortcuts** page remains exactly as before. Existing default gestures, custom settings and shortcut file formats are unchanged.

## Preserved from confirmed Ver. 36

- All emulator cores, screen shaders, Authentic GB/GBC/GBA modes, SGB visuals and scaling.
- German Pokémon Smaragd RetroAchievements unlocks, fast-forward tracking, popups and synchronization.
- In-game input processing, hardware button behavior, volume/mute timing, menu access, Link Play, Wi-Fi state and safe power handling.
- ROMs, save games, save states, RetroAchievements accounts and caches, and configuration files. No migrations or rescan.

## Testing and compatibility

The H700 pipeline tests the complete Rust suite (including guide navigation, read-only mapping invariants and viewport scrolling), GLES2 shader checks, OTA/update contracts, source branding, packaging and checksums. Automated tests do not replace hardware testing.

**H700 devices:** RG35XX H, RG35XXSP, RG34XXSP and other compatible Anbernic H700 units. **Not compatible with Miyoo Mini.** Keep the confirmed **Ver. 36** release as a fallback until Ver. 37 is tested on a device. No ROMs or proprietary BIOS files included.
