# select. slot. 1.8.1 Ver. 6 — Miyoo maintenance release

This release removes the unnecessary Restart feature from the **Miyoo** build and improves the reliability and maintainability of the ARMv7 port. The Anbernic H700 build is unaffected.

## Miyoo UI

- **No Restart option:** removed the Settings → Restart row, the About-screen X restart shortcut, and its right-hand footer legend. Neither a hardware reboot nor a process re-exec is invoked from those screens. The original Slot restart internals remain unreachable from the Miyoo UI; this avoids changing the shared base implementation.
- **Preserved:** universal menu scrolling, including Gameplay settings; high-contrast clock/battery text; the About sticker now reads **1.8.1 Ver. 6**.

## Firmware safety

- **Correct OnionOS detection:** only an actual OnionOS runtime **and** its `.tmp_update/onionVersion/version.txt` marker enable the Onion-specific PWM preference. A stock-firmware autoboot script named `.tmp_update/runtime.sh` alone no longer activates this path.
- Added a regression test for the stock-versus-OnionOS distinction.
- No change to the 0–9 physical brightness ladder, game renderer, mGBA/gpSP cores, save formats, OnionOS theme handling, standby or shutdown.

## Source and build cleanup

- Refactored the large Miyoo customization generator into **seven ordered feature modules** (emulators, OnionOS power, rendering, idle, scaling, bezels and UI). All modifications still use exact-match, fail-closed source patching and a permitted-file allowlist.
- Added a **single version configuration** (`miyoo/version.env`) for the ARMv7 port revision, Slot version and select. slot. Miyoo release version.
- Added **Python regression contracts** for menu scrolling, removal of Restart, core compatibility and firmware detection.
- Added **ARMv7/QEMU graphics and power tests** to continuous integration and the release workflow, beyond ordinary compilation and ZIP checking.
- Consolidated per-version publishing into one generic workflow. Retired Ver. 3/4/5 publisher YAMLs; the later GitHub release cleanup removed their superseded public download entries while preserving their Git tags and source history.
- Removed the unused OnionOS splash script. OnionOS continues to display its own active theme.
- Local repeat builds may opt into `bash miyoo/build.sh --clean`; the default still refuses to overwrite an existing local source checkout.

## Installation

The release includes distinct **OnionOS autoboot**, **genuine stock firmware autoboot**, and **app-only** ZIPs and checksums. Back up the SD card before extracting one suitable ZIP to its root, including hidden folders. **Never use the stock-autoboot ZIP over an OnionOS SD card.**

Existing ROMs, battery saves, save states, per-system/per-ROM scaling choices and Game Boy palettes are not intentionally reset. As before, legacy `gambatte` core values are **read as mGBA without rewriting the saved file**; Gambatte save states are not compatible with mGBA.

**Validation:** ARMv7 compilation, QEMU Rust tests, source regression contracts and package checksum/OS-isolation checks. Hardware testing is still needed to confirm behavior on each supported Miyoo model and operating system combination.

[Full Miyoo installation guide](https://github.com/Sinastrax/select-slot/blob/main/miyoo/INSTALL.md) · [Project README](https://github.com/Sinastrax/select-slot)
