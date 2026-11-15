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