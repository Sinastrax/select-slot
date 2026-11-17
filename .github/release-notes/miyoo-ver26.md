# select. slot. 1.8.1 Ver. 26 — Miyoo

**Standalone ARMv7 build for the Miyoo Mini family.** This release is independent of the H700/Anbernic firmware, which has a different upstream Slot version, hardware target and update channel. Ver. 26 is the project’s current user-confirmed working Miyoo reference.

## What's fixed in Ver. 26

- Corrected **B / Back** navigation in **Screen → Game Boy / Game Boy Color / Game Boy Advance**. Each system menu returns to the **Screen** menu, rather than jumping to the shelf.
- Retains the three independently saved scaling defaults (one per system), with individual game overrides taking priority.
- No unrelated runtime, display, brightness, menu-timer or power-handling changes compared with Ver. 25.

## Included features

- Game Boy, Game Boy Color, Game Boy Advance; GB/GBC: mGBA default with Gambatte available; GBA: gpSP default with mGBA available.
- Original, Integer, Aspect Fit, Fill/Crop and Full Stretch scaling; persisted per system and optionally per game.
- Shaders are **off**, with original unfiltered pixels. GB palettes and emulator-level color options are separate from display shaders.
- Original nine-step brightness menu (1–9), resume options, fast-forward, rewind, independent menu Screen Off / Power Off timers and native OnionOS power handoff.
- Offline installation; no Wi-Fi or online updater is required or provided.

## Download the ZIP for your installed firmware

| Asset | Use |
| --- | --- |
| **`select-slot-1.8.1-ver26-miyoo-onion-autoboot.zip`** | **OnionOS 4.3+** on compatible Mini/Mini Plus: direct SD-card-root extraction; launches Slot automatically from the OnionOS startup hook. Does not overwrite `.tmp_update/runtime.sh` or theme files. |
| **`select-slot-1.8.1-ver26-miyoo-stock-autoboot.zip`** | **Genuine stock Miyoo firmware ONLY:** direct SD-card-root extraction; provides the stock `.tmp_update/runtime.sh` boot hook to launch Slot. |
| **`select-slot-1.8.1-ver26-miyoo.zip`** | **App-only**, no startup hook. Preferred for manual launching or an uncertain/modified SD-card OS. |

Back up the SD card and extract **one** matching ZIP's contents to the **SD-card root**, including hidden directories. ROMs, BIOS files and personal saves are not included. The downloads each have a SHA-256 checksum.

> [!CAUTION]
> **Never install the Stock Autoboot ZIP onto OnionOS, Allium or another OS using its own `.tmp_update/runtime.sh`.** This ZIP contains the stock boot script and overwriting another OS's copy can prevent it from starting. Do not overwrite an existing runtime script on an unknown card.

## Compatibility and limits

- **GB/GBC/GBA only.** No NES, SNES, N64, PlayStation or other systems.
- **Miyoo and H700 builds cannot be interchanged.** The Miyoo port is based on Slot **1.8.1** and `deanmarano/slot-miyoo`; the H700 release uses Slot **1.16.0** and separate H700-specific source.
- **No H700 Authentic/Pocket shaders**, reflection effects, SGB shader modes or H700-only controls. Shaders were deliberately disabled for sharp unfiltered Miyoo rendering, particularly with Fit scaling.
- **No online updates** and no network connection needed. Upgrade by replacing files on the SD card, backing up `Config/`, `Saves/` and save states first.
- **Device/firmware coverage is limited.** The current setup has user-confirmed working behavior on an OnionOS Miyoo; stock-firmware/autoboot variants and other Mini/Plus/Flip hardware combinations are built and packaged but not all physically tested. Official OnionOS is for Mini/Mini Plus, **not Mini Flip**; choose a compatible stock/app route for the Flip.
- **Power integration depends on the installed OS.** OnionOS handles its own themes and standby/shutdown; its own sleep timer may override Slot's menu-only inactivity timers. Not all custom themes/firmware builds present the same artwork.
- **Emulator compatibility and performance are game- and model-dependent.** Alternative emulator cores may have incompatible save states; back up before changing cores. Avoid assuming the H700 software/feature set is present.
- **Integer vs Fit scaling:** Fit fills more screen space but is fractional at 640×480, so uneven physical pixel widths can be visible; shaders do not attempt to conceal shimmer.

## Provenance and integrity

The Ver. 26 ARMv7 compilation, archive structure and SHA-256 checks passed. This release republishes the **exact six existing Ver. 26 preview assets**, not a modified/newly rebuilt binary, from `miyoo-v1.8.1-ver26-preview.142.1` (source commit `db66797d5f21004dad34917d915b70bc5138aa3b`). Physical hardware has not been tested for *every* supported combination.

Source and installation details: [Miyoo port files](https://github.com/Sinastrax/select-slot/tree/feature/select-slot-miyoo-pwm-priority/miyoo) · [Miyoo installation guide](https://github.com/Sinastrax/select-slot/blob/feature/select-slot-miyoo-pwm-priority/miyoo/INSTALL.md) · [Original Miyoo port](https://github.com/deanmarano/slot-miyoo) · [Original Slot](https://github.com/slot-cfw/slot).

**This Miyoo release is not the H700 latest/OTA release.** H700 users should continue using [the H700 latest release](https://github.com/Sinastrax/select-slot/releases/latest).
