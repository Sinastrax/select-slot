# select. slot. — Anbernic H700 maintainer guide

The H700 firmware and Miyoo firmware are **different products**. The current **user-tested H700 stable release is select. slot. 1.16.0 Ver. 40**, with Ver. 36 retained as an older verified fallback. These builds preserve the Ver. 35 RetroAchievements indirect-memory fix, GB/GBC/GBA rendering, hardware nicknames, system scaling, and OTA updates. Never port Miyoo's 32-bit renderer, PWM settings, or mGBA-only default into this ARM64 build without device-specific testing.

## H700 source and patch order

- **Pinned source:** [pvaibhav/slot](https://github.com/pvaibhav/slot) at the `v1.15.3-pvaibhav.1` patch base, merged onto the exact `v1.16.0-pvaibhav.1` release. Both upstream archives are selected in [h700-prepare.sh](.github/scripts/h700-prepare.sh).
- **Historical patches:** the existing [patches](patches/) directory is an **ordered input to the build**, not a bag of independent or obsolete files. Some earlier experiments are deliberately superseded by later stages; the final Ver. 35 result is user-verified. Removing apparently redundant patches can break the merge or change output.
- **Customization entry point:** [h700-prepare.sh](.github/scripts/h700-prepare.sh) reproduces the **original, exact** sequence previously embedded inline in the Actions workflow. It applies verified base patches, merges sources, then runs the existing narrowly targeted Python transformations and visual/regression verifiers in order.
- **Release version:** [.github/ota-version.txt](.github/ota-version.txt) is the sole active H700 version source. The generated `versions.json` and firmware ZIP use it directly.
- **Automated source contract:** [verify-h700-maintenance.py](.github/scripts/verify-h700-maintenance.py) fails early if upstream versions, required patch scripts, the ordering of sensitive shader/RA modifications, critical test jobs, checksum controls, or publication rules drift unexpectedly.

## Build, verification and release flow

The only active H700 build/publisher is [.github/workflows/build-h700.yml](.github/workflows/build-h700.yml). Commits affecting H700 scripts, patches, branding, workflow or OTA version trigger it; manual dispatch can build without publishing. The build:

1. Checks shell syntax and H700 maintenance/publisher safety contracts.
2. Retrieves pinned source archives, applies/merges every ordered patch, and uploads merged source for inspection.
3. Runs GLES2 shader validation, Rust formatting, OTA safety tests, Wi-Fi and link behavior tests, complete RetroAchievements tests, hardware nickname tests and menu viewport tests.
4. Brands boot/update assets, cross-builds the complete H700 filesystem, verifies the original GBA bezel, and installs the tested older mGBA core with the matching MPL-2.0 source archive.
5. Checks the installation tree, packages the complete full-firmware ZIP and hashes it into `versions.json`.
6. Publishes a new H700 release **only after the build succeeds** and only if that tag does not already have a release. Existing public releases, source tags, and assets are never overwritten. The latest H700 release is explicitly marked latest.

The old manual `publish-ota-from-run.yml`, post-build `publish-ota-from-build.yml`, and historical `rebrand-releases.yml` were retired because they duplicated publication, allowed unsafe tag rewriting, or contained obsolete deletion criteria tied to Ver. 24. The experimental old-core comparison workflow was also retired. **The one-time release curation removed 17 superseded release records but preserved all technical Git tags, the nine retained milestones, their assets, and the OTA latest channel.**

## What must be preserved

- **RetroAchievements:** verified German Pokémon Smaragd recognition, valid unlock popup, synchronization, and every-emulated-frame tracking including fast-forward; never relax static memory bounds or reset unrelated achievements on invalid indirect pointers.
- **Display:** the verified Pocket Color/SGB shared optical rendering and white point, core-specific GB color correction, shader reflections, RG35XX H Fit scaling, GBA Authentic fractional scaling and GBA/GBA SP bezel choices.
- **Hardware/OS:** separate RG35XX H and SP recognition/nicknames, per-system scaling in `Config`, normal WLAN retained during gameplay, link-play radio handoff, B-button menu navigation, standby and safe shutdown.
- **Data:** `System/` update manifests, ROMs, saves, achievements and credentials must not be rewritten or removed during maintenance. Retained release assets must never be automatically overwritten or deleted.
- **Miyoo isolation:** the H700 compiler and publisher must never modify the Miyoo 1.8.1 releases.

## Hardware acceptance checks

Automated tests cannot prove GPU display fidelity or real-world radio/power behavior. On RG35XX H, RG35XXSP and RG34XXSP (when available), test: GB Pocket Color and actual SGB modes and palette changes; Authentic GBA at Fit and Integer; independent per-system scaling after restart; overlay/restart/update branding; GB/GBC/GBA save/load; WLAN and link behavior; RetroAchievements progress and unlock popup; correct device nickname; and a complete OTA update. **Ver. 40 is confirmed working on RG35XX H, including the compact Hotkey Guide. Ver. 36 remains available as an older verified fallback.**

## Hotkey guide validation (Ver. 40)

Controls → Hotkey Guide is presentation-only. Ver. 40 deliberately hides obvious or duplicated functions: basic volume/power buttons, ordinary MENU tap, editable hold/toggle Fast-Forward and basic save-state viewer navigation. Verify the less-obvious features still listed: SELECT+either volume button and simultaneous volume mute, MENU double-tap for saved states, MENU hold, Link Play, double-tap Fast-Forward latch, free GB/GBC L1/R1 resizing, shelf and collection hold gestures with currently configured buttons, and conditional SD repair/Kid Mode startup unlock. The guide's label and key textures scale independently to avoid horizontal overlap on 640-pixel panels; **all other settings pages remain unchanged**. No input engine, shortcut timing, config file, save data or editable Shortcuts editor may be modified.
