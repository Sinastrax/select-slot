# select. slot. — release history

There are two independent firmware lines: **Anbernic H700** (Slot 1.16.0) and **Miyoo Mini family** (Slot 1.8.1). The [Releases page](https://github.com/Sinastrax/select-slot/releases) intentionally keeps only meaningful stable milestones and rollback points. Intermediate development versions remain traceable through their original Git tags and merged pull requests; release records for obsolete trials were curated on 19 November 2026.

## Anbernic H700

| Version | Status / milestone | Release |
| --- | --- | --- |
| **Ver. 40** | **Current, RG35XX H hardware-tested stable** — compact non-overlapping Hotkey Guide | [Ver. 40](https://github.com/Sinastrax/select-slot/releases/tag/v1.16.0-rgsp.40) |
| Ver. 36 | Verified maintenance and reproducible OTA baseline | [Ver. 36](https://github.com/Sinastrax/select-slot/releases/tag/v1.16.0-rgsp.36) |
| Ver. 35 | German Pokémon Smaragd RetroAchievements indirect RAM-read fix | [Ver. 35](https://github.com/Sinastrax/select-slot/releases/tag/v1.16.0-rgsp.35) |
| Ver. 18 | GBA Authentic pixel-grid correction at fractional Fit | [Ver. 18](https://github.com/Sinastrax/select-slot/releases/tag/v1.16.0-rgsp.18) |
| Ver. 17 | Finalized Pocket Color and Pocket SGB white point / rendering | [Ver. 17](https://github.com/Sinastrax/select-slot/releases/tag/v1.16.0-rgsp.17) |
| Ver. 4 | Early user-verified Authentic color baseline | [Ver. 4](https://github.com/Sinastrax/select-slot/releases/tag/v1.16.0-rgsp.4) |
| 1.15.3 Ver. 3 | Legacy pre-1.16.0 release, corrected resume-on-power-on | [Legacy](https://github.com/Sinastrax/select-slot/releases/tag/v1.15.3-rgsp.3) |

**Ver. 40:** Removes unnecessary entries from the read-only Hotkey Guide, keeps only harder-to-discover controls, and fits separate label/value columns inside narrow 640×480 screens. It changes no actual button bindings, emulator behavior, or configuration. This was confirmed on RG35XX H.

**Ver. 36:** Extracted the exact ordered H700 patch pipeline, added early release-safety checks, removed unsafe duplicate publishers, retained the older mGBA core and its separately downloadable source, and introduced reproducible maintenance documentation.

**Ver. 35:** Corrected indirect-pointer handling in RetroAchievements to match official rcheevos client behavior without weakening direct-memory checks or resetting unrelated achievements.

**Ver. 18:** Corrected fractional GBA Authentic LCD gap intersections while preserving integer scaling and all previously verified Pocket Color/SGB rendering.

**Ver. 17:** Matched the Pocket SGB optical profile with Pocket Color, including the LCD-tinted white point while retaining SGB game palettes.

**Ver. 4:** Retained calibrated Authentic color response and restored natural LCD gap darkening when GBA color correction is Off.

## Miyoo Mini family

| Version | Status / milestone | Release |
| --- | --- | --- |
| **1.8.1 Ver. 6** | **Current stable Miyoo release** — corrected OnionOS/stock detection, no Restart UI, modular build/test pipeline | [Miyoo Ver. 6](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver6) |
| 1.8.1 Ver. 2 | Original GBA and GBA SP bottom-bezel choices | [Miyoo Ver. 2](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver2) |

Miyoo builds are **ARMv7 and installed from the SD card**, not interchangeable with H700 firmware or OTA packages. See [installation](miyoo/INSTALL.md).

## Intermediate H700 development history

These steps are part of the current complete H700 build, but intermediate release downloads were intentionally removed from the public Releases list. The original source changes remain in Git history.

### Ver. 36 — maintenance baseline

- **Build cleanup:** moved the pinned H700 upstream merge and exact historical patch sequence into a dedicated script; added strict patch-order and release-safety validation.
- **Release safety:** retired duplicate/stale OTA publishers, including an unsafe force-tag/draft-replacement path and a historical release-deletion workflow. Existing GitHub releases and tags are preserved.
- **No gameplay changes:** the user-confirmed Ver. 35 RetroAchievements fix, shaders, device recognition, GB/GBC/GBA scaling, emulators, saves and WLAN remain intact. [Maintenance and hardware-testing guide](H700_MAINTENANCE.md); Ver. 36 is the confirmed device-tested fallback.

### Ver. 35: rcheevos-compatible indirect memory handling

- Fixed the **unavailable indirect RAM read** found in the German Pokémon Smaragd device log. The old wrapper reset *all* achievements when any dynamic pointer briefly pointed outside available memory; official `rc_client` treats this as a zero-valued pointer read without resetting unrelated achievements.
- Direct memory-address validation remains strict: invalid static achievement addresses and reads crossing unmapped boundaries are rejected. Real achievement tracking still runs for every emulated frame, including fast-forward.
- Added regression tests for invalid pointers, independent awards, and direct unmapped reads; routine injected server warnings no longer flood logs.
- Existing game saves, core selection, color modes, device naming, and original System manifest updater are unchanged. The Pokémon Smaragd unlock popup was subsequently **confirmed working on real H700 hardware**.

### Ver. 34: reliable achievements during fast-forward

- **Evaluate every emulated frame**, including fast-forward steps not displayed on the LCD. The evaluator now runs immediately after the emulator frame instead of using an eight-frame RAM snapshot queue that could drop momentary achievement conditions.
- **Offline achievements still synchronize asynchronously.** The background worker handles unlock records and network requests, while live gameplay evaluates local achievement conditions. No ROM, saved game, account, or previous achievement history is reset.
- **Ignore zero-point server compatibility warning entries**, including the injected "Warning: Unknown Emulator", when counting the real achievement list.
- Regression-tested against a 360-frame burst with one qualifying frame; actual H700 hardware behavior and performance must still be checked. Previously missed milestones cannot be backdated automatically.

### Ver. 33: RetroAchievements tracking reliability

- Optional **Rich Presence memory errors** cannot erase legitimate achievement triggers or reset the game evaluator. Invalid gameplay memory still fails closed to prevent false awards.
- If tracking still misses an unlock, `Logs/slot.log` reports the first relevant issue per game: an unexposed memory address, an invalid Rich Presence read, or evaluator queue saturation. This separates server connection from actual RAM evaluation.
- Existing save data, offline awards, emulator and shader settings, online update manifest, and device nicknames are unchanged.

### Ver. 32: safer in-game Achievements browsing

- **Repeated X sorting and scrolling** now reuse a fixed pool of six visible achievement rows instead of accumulating GPU textures for all badges and labels. Descriptions and temporarily unavailable badges also keep reusable texture handles.
- **Repeated Y Refresh presses** are coalesced to avoid unnecessary repeated ROM hashing and network session requests. This does not alter save data or manufacture RetroAchievements unlocks.
- Large achievement sets are checked by a 500-entry viewport regression. Existing softcore tracking, session status, shaders, cores and the System updater remain unchanged.

### Ver. 31: menu scrolling and current-game RetroAchievements refresh

- **Hardware-correct default link-play nicknames:** use the BaseOS device identifier (e.g. `rg35xxh`) to distinguish RG35XX H from RG35XX SP. Any custom nickname remains unchanged.
- **Every long quick-menu page** now scrolls within the available rows rather than colliding with the footer, including the main settings list, GBA/GB/GBC display options and paused game menus.
- **In-game Achievements → Y Refresh** verifies the running ROM's MD5, requests a fresh online game session, updates cached definitions/unlocks and reports the actual connection stage. Saved progress and offline awards are never deleted.
- **Measured achievement progress** is read from the local rcheevos runtime where supported. Previously completed conditions are not auto-awarded from a save file.
- An accepted RetroAchievements game session is **not undone by a failing Rich Presence ping**. Wi-Fi behavior, the mGBA governor and the original `System/` update manifest are unchanged.

### In-game RetroAchievements and storage cleanup (Ver. 30)

- **In-game only:** open the existing paused game menu and select **Achievements**. Browse the current game's cached badges, descriptions, unlocked/locked state and point totals. A opens details; X changes between original and locked-first ordering; B goes back. No shelf achievement menu and no extra pause system.
- **Restart:** a selectable item immediately **below System** in the main settings list. The original About restart remains available.
- **Tools → Storage Cleanup:** Scan Storage reports optional old rotated logs and temporary cache files; Clean Detected Files requires a second explicit confirmation. No ROMs, saves, screenshots, settings, RetroAchievements history or unknown files are deleted. The `System/` updater continues to use the **original manifest-based cleanup**, unchanged.
- **Extra exclusions:** create `Config/cleanup-protected.txt`, one relative folder per line, to exclude additional paths such as `Cache/my-folder`. The scanner never follows symlinks.
- **Smaller firmware ZIP:** the exact modified MPL-2.0 mGBA source archive is published beside the firmware as a separate release asset. Installed devices retain the compiled mGBA core and a source/license notice; the firmware ZIP does not install the source archive. Previous on-card source bundles are removed by the existing `System/` update manifest.


## Early legacy history

## select. slot. 1.16.0 Ver. 1 (`v1.16.0-rgsp.1`)
- Integrated official Slot v1.16.0 and pvaibhav v1.16.0-pvaibhav.1.
- Added handwritten missing-art cartridge titles, multiplayer invitations/nicknames, USB-C audio playback and PNG overlays.
- Updated GPU frame blending across cores and removed the obsolete global Turbo Buttons toggle.
- Integrated select. slot.'s Authentic rendering controls with the new renderer.

## select. slot. 1.15.3 Ver. 3 (`v1.15.3-rgsp.3`)
- Fixed **Resume on Power On**: Off boots to the shelf without launching the previously played game.
- **Resume on Insert** remains independent.

## select. slot. 1.15.3 Ver. 2 (`v1.15.3-rgsp.2`)
- Added separate menu-only screen-off and shutdown inactivity timers, configurable under System.

## select. slot. 1.15.3 Ver. 1 (`v1.15.3-rgsp.1`)
- Added the custom GitHub update channel and complete OTA packages.
