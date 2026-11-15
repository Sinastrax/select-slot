# Slot. RG SP custom Authentic build

This repository contains a **source patch** for [pvaibhav's Slot. v1.15.3-pvaibhav.1](https://github.com/pvaibhav/slot). It is intended for the Anbernic RG SP (H700).

## Changes

- Authentic keeps its LCD ghosting during normal gameplay, but disables the additional frame blending when fast-forward is engaged.
- GB games gain **Game Boy Color** as an additional Authentic screen model, with selectable GB color palettes.
- The original calibrated panel profiles remain sourced from the same upstream release.

## Build

The [Build custom Slot H700](../../actions/workflows/build-h700.yml) workflow downloads the exact upstream tag, applies [the patch](patches/rgsp-authentic-gbc.patch), compiles for H700, verifies the SD2 card tree, and uploads the `slot-rgsp-custom-h700` artifact.

A successfully generated artifact contains `slot-rgsp-custom/`. **Copy the contents of that folder onto the existing Slot. SD2 card, not the containing folder**, after backing up the entire SD card. Do not use it until a workflow run has completed successfully. This remains an experimental, untested modification.

**No ROMs, saves, or personal files are stored in this repository.**

## SameBoy and individual Authentic color correction (experimental)

- GB/GBC cartridges can select **SameBoy (left)** or **Gambatte (right)** from the two-choice core picker. **mGBA remains available for GBA**.
- Earlier GB/GBC cartridge choices for mGBA are migrated to SameBoy. Back up `Config/selected_core.txt` before installing.
- Gambatte's existing Authentic/Pocket Color appearance and profile are retained. The alternate-core Authentic profile (previously used by mGBA for GB) is now used by SameBoy.
- SameBoy sets `sameboy_model=Super Game Boy` when the **Pocket SGB** model is selected, allowing supported GB games such as Pokémon Yellow to use SGB commands for in-game palettes. Close and reopen the game after selecting the model.
- SameBoy's custom border is disabled, so the same 160x144 pixel geometry remains compatible with the Pocket LCD shader. This is not an authentic SNES border display.
- **Color Correction** is available even when Authentic is selected, with independent on/off memory for every GB Authentic model (DMG, Pocket, Pocket Color, Pocket SGB, Light, GBC) **for Gambatte and SameBoy separately**, plus GBC Authentic and GBA Authentic. In a game, use **Quick Menu → Settings → Screen → Color Correction**.
- Default corrected appearance is **on**, preserving the prior Pocket Color profile. Disabling measured correction preserves the LCD pixel grid.
- The firmware package must contain **both** `System/slot` and `System/sameboy_libretro.so`.
- Always back up `System/slot`, `Config/slot.state`, `Config/selected_core.txt`, and saved games before installation. Save-state files are generally **not compatible between cores**.
- SameBoy's frame pacing, SGB visual output and performance on the physical H700 RG SP have not yet been verified.
- Firmware with SameBoy ARM64 and per-core correction persistence successfully built and SD-card tree validated: [GitHub Actions run 43761142559](https://github.com/Sinastrax/slot-rgsp-mod/actions/runs/43761142559).
