# select. slot. 1.16.0 Ver. 40 — Compact Hotkey Guide

An H700 interface-only update in response to RG35XX H hardware feedback on Ver. 39: the reference contained too many obvious actions and long labels collided with their button legends.

## What changed

- The **Controls → Hotkey Guide** now lists only hard-to-discover actions. Basic volume, power, normal MENU, editable FF Toggle and basic save-state navigation are no longer repeated.
- Redundant mute entries and GB/GBC resize instructions are consolidated: SELECT + either volume button, both volume buttons together, and L1/R1 resizing when those buttons are not assigned to a game.
- More concise labels for double MENU, long MENU, Link Play, double-tap Fast-Forward latch, shelf hold gestures, collection editing, SD-card repair and Kid Mode startup recovery.
- **Two-column text layout fixed** for the guide only: the left action label is limited to a width share and both labels and button legends can scale below the ordinary settings minimum. This prevents horizontal collision at RG35XX H's 640x480 display resolution.
- The currently assigned fast-forward and collection controls are still displayed where relevant. Hidden entries remain in source for compatibility but are omitted from the on-device guide.

## Unchanged

Every actual button mapping, gesture/timing, shortcut editor, input handling, power/wireless/Link Play behavior, emulator core, shader, RetroAchievements feature, save state, configuration file, artwork, update mechanism and Miyoo release is unchanged.

## Validation

Full H700 CI passed source preparation, shader and OTA checks, Rust regression suite (including synthetic 640-, 720- and 800-pixel guide column checks), device compilation, core restoration, firmware packaging and archive validation. This does **not** establish visual fidelity on hardware; inspect the on-device guide after updating.

**Compatibility:** Anbernic H700 devices including RG35XX H, RG35XXSP and RG34XXSP; not Miyoo Mini. **Ver. 39 remains available** as the previous release, and Ver. 36 is the confirmed pre-guide stable fallback.
