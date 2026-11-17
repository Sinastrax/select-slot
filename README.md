# Slot. RG SP custom Authentic build

Custom modifications based on [pvaibhav's Slot. v1.15.3-pvaibhav.1](https://github.com/pvaibhav/slot) for the Anbernic **RG SP (H700)**.

## Latest: Gambatte + mGBA restored (experimental)

The current [H700 build](../../actions/runs/43764469607) restores the original two GB/GBC emulator choices: **mGBA on the left**, **Gambatte on the right**. For GBA, the choices remain mGBA and gpSP.

- Previously saved GB/GBC choices marked `sameboy` are interpreted as mGBA. Existing Gambatte choices stay Gambatte.
- Gambatte and mGBA have separate GB Authentic screen-model and color-correction profiles, including **Pocket Color** and **Pocket SGB**.
- Pocket Color retains the Pocket-style separated LCD dots, shadows and GBC-style colors.
- Pocket SGB on mGBA uses **Super Game Boy hardware**, with borders disabled, and supports the dynamic game-specific SGB color commands (where the game and core support them). Close and reopen a game after selecting Pocket SGB.
- Authentic ghosting is disabled during fast-forward and retained at regular speed.
- **mGBA GB/GBC automatic frameskip is now disabled**. Slot. previously forced `mgba_frameskip=auto`; this build explicitly sets `disabled` for GB/GBC, matching the bundled mGBA core's default. The GBA mGBA settings are unchanged.
- This frameskip change is a **targeted performance experiment**, not an established fix. mGBA SGB emulation can still be demanding; frame pacing and audio sync remain unverified on the physical device.
- The SameBoy experiment is **retired from the UI and the build package**, because it performed badly on the device. The source retains some dormant SameBoy integration code for the moment.

## Authentic color correction

When the RGB color-correction switch is off, the LCD grid, pixel gaps, shadows, grain, and glass rendering remain active. Turning it off bypasses the measured color-response conversion where applicable.

- **Pocket Color, Pocket SGB, GBC and GBA Authentic:** per-model correction setting (on/off).
- **DMG, original Pocket and Light:** their panel tint is part of the screen simulation, not a separate RGB correction; it is not stripped away by the switch.
- GB correction flags are stored independently for Gambatte and mGBA.
- Select a model, then use **Quick Menu → Settings → Screen → Color Correction**.

## Install to SD2

Back up `System/slot`, `System/mgba_libretro.so`, `Config/slot.state`, `Config/selected_core.txt`, and your saved games and states.

A release/build artifact contains a `slot-rgsp-custom/` directory. **Copy the contents of that directory to the root of SD2, not the directory itself.** A minimal upgrade ZIP can contain only `System/slot` and `System/mgba_libretro.so`, which can be merged with the existing `System` folder.

Do not load save states produced by another emulator core. In-game battery saves are different from save states and are generally more portable, but back them up regardless.

The [GitHub Actions workflow](.github/workflows/build-h700.yml) downloads the exact upstream tag, applies the patches in order, builds the ARM64 firmware and validates the device file tree. The build can complete successfully even if a runtime performance issue remains.

**No ROMs, games, personal saves or other copyrighted game content are included in this repository.**

## History

Earlier experiments integrated SameBoy and developed the Pocket Color/Pocket SGB hybrid shaders. Their patch history remains in `patches/`; the **current firmware selects mGBA and Gambatte**. Previously successful test artifacts are recorded in the GitHub Actions run history.


## Current diagnostic: mGBA audio-queue drift and Authentic correction (2026-11-15)

- Latest firmware: [successful ARM64 H700 build 43765871771](https://github.com/Sinastrax/slot-rgsp-mod/actions/runs/43765871771).
- On physical RG SP, mGBA was reported to start smoothly, develop hiccups, temporarily recover on fast-forward, and get worse when automatic frameskip was disabled. Disabling rewind and Authentic ghosting did not solve it.
- The previous `mgba_frameskip=disabled` experiment is therefore **reverted to `auto`** for GB/GBC.
- Slot.'s audio ring buffers up to ~8 game frames and `push_blocking` may wait up to 50ms when full. mGBA GB/GBC now uses a wider **queue-dependent** audio drift correction (max ±5% instead of ±0.5%), without changing other cores' audio response. This is a hypothesis-driven test: **not yet a confirmed performance fix**.
- The uncorrected RGB path for GBC/GBA Authentic now maps source values into the *same panel dark/light range* as corrected values before the common sparkle, LCD grid, pixel gaps, and glass pass. Corrected-on rendering remains unchanged. Monochrome Authentic models retain their historical physical LCD panel tint.
- Update-only ZIP replaces **only `System/slot`** on SD2. Back up your existing executable and configuration, plus saves, before installing.
- Compare a full normal-speed play session with Pocket Color versus Pocket SGB; check audio pitch/crackling and whether temporary fast-forward resets are still needed. The hardware behavior is currently unverified.


## Latest test: native-pitch mGBA audio and neutral Authentic whites

[H700 build 43767324185](https://github.com/Sinastrax/slot-rgsp-mod/actions/runs/43767324185) passed patching, Rust formatting, ARM64 compilation, device tree validation and artifact upload.

- Previous ±5% mGBA GB/GBC resampler drift correction produced smooth video but audibly wrong music/audio. New test returns to the normal ±0.5% resampler limit.
- For GB/GBC **mGBA only**, audio pushes no longer block the emulation thread when the ring fills: stale samples are dropped from the queue instead. This preserves nominal sample playback pitch but can occasionally click or skip sound. Gambatte and GBA behavior are unchanged.
- With Authentic **Color Correction Off**, Pocket Color/Pocket SGB use neutral reflector white, and GBC/GBA shader branches use neutral (0,0,0) grid/black instead of calibrated panel tint. Pixel-gap geometry, grain, glass and LCD response timings are not changed. With correction **On**, the established calibrated/tinted look is unchanged.
- The supplied minimal update contains only `System/slot`. Back up the old executable, `Config/slot.state`, and saves before replacing it.
- **Physical hardware testing is required.** If sound clicks persist, the queue's overflow counters need measurement instead of increasing the resampler pitch deviation again.

## Online updates (custom release channel)

The original Slot **Settings → System → Check for Updates** interface is retained, but the
`rgsp-online-updates.patch` routes future downloads to this repository's own GitHub Releases,
**not** to the unmodified upstream or pvaibhav firmware. The updater verifies release size and
SHA-256, stages the complete `System/` folder and installs on restart.

Release ZIPs are built from all current patches, replace upstream's mGBA with the verified older
core `c758314a639aa0066e7b65a8341448181b73c804`, and retain the standard licenses and
source records. This is a **complete-build-only** release channel; an incomplete zip must never
be published as an online update.

**One manual installation** of an OTA-enabled full build is necessary to switch older firmware
to our release channel. Releases are not offered until the matching firmware version has actually
been published on GitHub. See [ONLINE_UPDATES.md](ONLINE_UPDATES.md) for the update and release process.
