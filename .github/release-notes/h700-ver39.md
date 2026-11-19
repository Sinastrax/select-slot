# select. slot. 1.16.0 Ver. 39 — Source-verified Hotkey Guide

This H700 release corrects and expands the on-device reference for button shortcuts. It builds on Ver. 38 without changing a single physical shortcut or how inputs are processed.

## Improved read-only controls reference

Open **Controls → Hotkey Guide** (previously Fixed Shortcuts). The guide contains Global, In-Game, Shelf, Collections, Save States, and a new Recovery / Kid Mode category.

- **MENU twice** correctly identifies the **save-state viewer** (when saved states are available), rather than implying it opens the screenshot gallery. Holding MENU is identified as a multi-game exit gesture.
- **Fast-Forward** distinguishes holding the assigned key, tapping it twice to latch, pressing it again to exit a latch, and the **separately configurable FF Toggle** action. The displayed key always follows each current assignment. Unbound actions show NOT ASSIGNED.
- **Shelf and collections** display the current Favorite / Remove Recent button for holding, adding/removing games and moving collection entries. Hold-only actions require an ordinary single-button mapping; if rebound to a chord, the guide explains SINGLE KEY ONLY rather than falsely suggesting the chord can be held.
- **Game Boy / Game Boy Color** stretch/normal display shortcuts are qualified as available only when their shoulder buttons are free. Kid Mode restrictions still apply.
- **Link Play** is labeled as compatibility-dependent. Basic power actions continue to use their existing definitions.
- **Shelf** also lists tapping SELECT for Cart Studio and START for the emulator picker.
- **Recovery / Kid Mode** documents SELECT+START for conditional SD-card repair or About-screen restart, the START+SELECT+L2+R2 boot-held Kid Mode unlock, and MENU for leaving a game while Kid Mode is locked.

## Unchanged behavior

The guide is **read-only**. No modifications were made to the gesture state machine, evdev mappings, key timings, input bindings, default combinations, gameplay, UI shortcut editor, emulator cores, shaders, WLAN / Link Play operations, save data, RetroAchievements progress, OTA updater, or Miyoo Mini firmware. This is a full H700 firmware package, not a standalone documentation file.

## Verification

The H700 CI pipeline completed source transformation and formatting, Rust regression and navigation tests, OTA safety tests, GPU shader checks, cross-build, complete firmware packaging and archive checks. Physical readability and button behavior on RG35XX H / SP / RG34XXSP still require device testing. **Ver. 36 is the confirmed hardware-tested fallback**, and the Ver. 37 updater was confirmed working; Ver. 38 remains available as the previous released version.

**Supported:** compatible Anbernic H700 devices. **Not for Miyoo Mini.** No ROMs or proprietary BIOS files included.
