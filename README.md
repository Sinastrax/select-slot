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

## Core-specific GB screen profiles (2026-11-15)

- GB **Gambatte** retains its existing `shader_gb` and `gb_model` settings (e.g. Authentic / Pocket Color).
- GB **mGBA** stores `shader_gb_mgba` and `gb_model_mgba` independently (e.g. Authentic / Pocket SGB).
- The core is selected **per GB cartridge** with START on its shelf entry (left: mGBA; right: Gambatte). Changing the core does not change the other core's screen profile.
- Pocket SGB uses mGBA's SGB palette and applies GBC-style measured colour response while retaining the Pocket dot/gap geometry. It is a *deliberate hybrid*, not accurate original SGB hardware colorimetry.
- When GB/GBC games are running with mGBA, Slot requests the Performance CPU governor; power draw and temperature can rise, and full speed is not guaranteed.
- Back up `Config/slot.state` along with `System/slot` before testing. In-game saves remain shared and save states remain core-specific.
- Current device build: [Actions run 43749935909](https://github.com/Sinastrax/slot-rgsp-mod/actions/runs/43749935909). Build/SD-tree validation passed, physical RG SP tests still needed.
