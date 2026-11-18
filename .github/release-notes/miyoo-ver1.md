# select. slot. 1.8.1 Ver. 1 — Miyoo

The **first official select. slot. release for the Miyoo Mini family**. This is the same user-confirmed working feature set as the last development build, rebuilt and versioned **Ver. 1** throughout the ZIPs and version metadata. Miyoo releases are independent from the H700/Anbernic builds.

## Features

- GB/GBC/GBA support. Default cores: **mGBA** (GB/GBC) and **gpSP** (GBA); alternative Gambatte/mGBA options.
- **Separate persistent Scaling** under **Screen → GB, GBC or GBA**: Original, Integer, Aspect Fit, Fill/Crop and Full Stretch. Saved per system, with optional per-game overrides.
- Correct **B / Back** navigation from all three system Screen pages.
- Original **1–9 brightness levels**, resume options, quick-menu timers and OnionOS-compatible sleep and shutdown handling.
- Unfiltered display: all shaders intentionally disabled.
- **Offline only**; no network or in-app updater needed.

## Download exactly one ZIP

| Asset | For |
| --- | --- |
| **`select-slot-1.8.1-ver1-miyoo-onion-autoboot.zip`** | **OnionOS 4.3+ (Mini/Mini Plus)**: copy to SD card root; starts automatically using OnionOS's startup hook. Preserves its own runtime and current theme. |
| **`select-slot-1.8.1-ver1-miyoo-stock-autoboot.zip`** | **Genuine stock Miyoo firmware ONLY**: includes `.tmp_update/runtime.sh` to start Slot automatically. |
| **`select-slot-1.8.1-ver1-miyoo.zip`** | **App-only**, no autoboot. Appropriate for manually launching or uncertain firmware setups. |

Back up your SD card and extract **one** ZIP's contents directly to the SD-card root. Preserve hidden folders such as `.tmp_update`. Each ZIP has an accompanying SHA-256 checksum.

> [!CAUTION]
> **Never install Stock Autoboot over OnionOS, Allium or any operating system with its own `.tmp_update/runtime.sh`.** Overwriting that script can prevent the installed system from booting.

## Known limits

- Supports **Game Boy, Game Boy Color and Game Boy Advance only**; no NES/SNES/PS1/N64.
- **Not compatible with H700 devices, H700 OTA updates or H700-specific Authentic/Pocket/SGB shaders**. Miyoo renders unfiltered software pixels.
- Fractional Fit scaling may create uneven physical pixel widths or shimmer. No shader filter is applied to hide this.
- **No Wi-Fi features or OTA updater**. Further releases must be installed manually via SD card.
- **Physical firmware/model testing is limited.** The project user's OnionOS Miyoo is confirmed working; stock autoboot, Mini Plus, Mini Flip and other firmware configurations are not all verified. Official OnionOS does not support the Flip.
- The installed OS controls power behavior, shutdown/theme artwork and its own idle timer; OS timer actions can take precedence over Slot's menu timers.
- Save states from different emulator cores are not necessarily interchangeable. ROMs, BIOS dumps, and user saves are not distributed.

## Code and credits

Based on [original Slot](https://github.com/slot-cfw/slot) and [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo). Sources and build instructions: [Miyoo directory](https://github.com/Sinastrax/select-slot/tree/main/miyoo). H700 releases remain separate at [the H700 latest-release link](https://github.com/Sinastrax/select-slot/releases/latest).

This is the **only published Miyoo release**; development previews and older Miyoo versions are withdrawn after this package is validated.
