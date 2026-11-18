<div align="center">

<img src="https://raw.githubusercontent.com/slot-cfw/slot/main/.github/resources/hero.webp" width="100%" alt="slot — Game Boy-centric custom firmware for Anbernic H700 handhelds">

[![H700](https://img.shields.io/badge/H700-Latest%20release-238636?style=for-the-badge)](https://github.com/Sinastrax/select-slot/releases/latest)
[![Miyoo](https://img.shields.io/badge/Miyoo-1.8.1%20Ver.%202-238636?style=for-the-badge)](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver2)
[![Original slot](https://img.shields.io/badge/Original-slot-555?style=for-the-badge)](https://github.com/slot-cfw/slot)
[![pvaibhav's fork](https://img.shields.io/badge/Based%20on-pvaibhav%2Fslot-555?style=for-the-badge)](https://github.com/pvaibhav/slot)
[![Guide](https://img.shields.io/badge/Guide-slot--cfw.fyi-555?style=for-the-badge)](https://slot-cfw.fyi)

</div>

---

# What is select. slot.?

**select. slot.** is a noncommercial, modified version of [Slot](https://github.com/slot-cfw/slot), the Game Boy-centric frontend created by **Brandon Kowalski**. It has **separate, non-interchangeable builds** for Anbernic H700 handhelds (based on [pvaibhav's enhanced fork](https://github.com/pvaibhav/slot)) and the Miyoo Mini family (based on [deanmarano's ARMv7 port](https://github.com/deanmarano/slot-miyoo)).

The **H700 build** uses **`v1.16.0-pvaibhav.1`** and adds independent GB/GBC shaders, Pocket Color and Super Game Boy modes, per-core color correction, custom input mappings, performance/audio changes, online updates, and menu power management.

Its name is **select. slot.**, not RGSP: the H700 build is intended for other compatible handhelds as well. Both builds support **Game Boy, Game Boy Color and Game Boy Advance**, not NES, SNES, PS1 or N64. Their emulators, display paths and available extras differ; the features below labeled H700 must **not** be assumed to exist in the Miyoo version.

> [!IMPORTANT]
> Use extracted ROM files, not `.zip` or `.7z` archives. Games and proprietary BIOS files are **not** included.

## Choose a build

| Build | Version / download | Hardware and updates |
| --- | --- | --- |
| **Anbernic H700** | [Latest H700 release](https://github.com/Sinastrax/select-slot/releases/latest) | H700 ARM64; BaseOS/SD2 installation; its own [OTA update channel](ONLINE_UPDATES.md) and H700-specific Authentic shader features |
| **Miyoo Mini family** | **[select. slot. 1.8.1 Ver. 2 — Miyoo](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver2)** | ARMv7; standalone SD-card build for compatible Miyoo Mini/Mini Plus/Mini Flip setups; **offline installation only** |

**Do not install an H700 ZIP on a Miyoo or a Miyoo ZIP on an Anbernic H700 device.** The two releases are built from different source versions and are not compatible.

### Miyoo Mini / Mini Plus / Mini Flip — Ver. 2

The Miyoo version is based on [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo) and **Slot 1.8.1**, not the H700 version's Slot 1.16.0/pvaibhav build. **Ver. 2** retains the working Miyoo configuration and adds the original-GBA bottom bezel option.

It includes GB/GBC/GBA emulation (mGBA/Gambatte for GB/GBC; gpSP/mGBA for GBA), **independent persisted scaling defaults for GB, GBC and GBA**, optional per-game scaling overrides, Original/Integer/Aspect Fit/Fill-Crop/Full Stretch modes, resume settings and independent menu Screen Off/Power Off timers. Display shaders are deliberately **disabled**.

Under **Screen → GBA → Bezel**, choose **GBA**, the existing **GBA SP** bezel, or **None**. The GBA option uses mugwomp93's existing CC BY-SA *Perfect GBA* artwork, resized to exactly the same 640×480 bottom-strip opening as Slot's SP bezel. It does not change shader settings, display size or scaling.

Choose **one** complete ZIP; back up the SD card, then extract the contents at its root, including hidden folders:

| Download | Intended firmware | What it installs |
| --- | --- | --- |
| **[OnionOS Autoboot ZIP](https://github.com/Sinastrax/select-slot/releases/download/miyoo-v1.8.1-ver2/select-slot-1.8.1-ver2-miyoo-onion-autoboot.zip)** | **OnionOS 4.3+** on supported Mini / Mini Plus | Automatically launches Slot from `.tmp_update/startup/select-slot.sh`, without replacing OnionOS's boot manager or active theme |
| **[Stock Firmware Autoboot ZIP](https://github.com/Sinastrax/select-slot/releases/download/miyoo-v1.8.1-ver2/select-slot-1.8.1-ver2-miyoo-stock-autoboot.zip)** | **Genuine stock Miyoo firmware only** | Automatically launches Slot using stock's `.tmp_update/runtime.sh` |
| **[App-only ZIP](https://github.com/Sinastrax/select-slot/releases/download/miyoo-v1.8.1-ver2/select-slot-1.8.1-ver2-miyoo.zip)** | Manual launch; safest for uncertain/modified firmware | Installs the Slot app **without** any startup hook |

> [!CAUTION]
> **Never install the Stock Firmware Autoboot ZIP over OnionOS, Allium or another SD-card OS that already uses `.tmp_update/runtime.sh`.** It can overwrite that operating system's boot script. Always back up your card and use only the matching ZIP.

#### Miyoo limitations and compatibility boundaries

- **Only GB, GBC and GBA** are supported. No other console systems are included.
- **No H700 Authentic/Pocket/SGB shaders, reflections or H700-specific controls.** Miyoo renders unfiltered software pixels; the shader menu is intentionally absent. **Aspect Fit is fractional at 640×480**, so some irregular pixel widths/shimmer are unavoidable without a visual trade-off.
- **No online updater and no Wi-Fi dependency.** Install new releases by SD card. Battery saves, settings and save states should be backed up before upgrades.
- **Hardware/firmware support is not universal.** The current OnionOS Miyoo setup has been confirmed working by the project user, but not every stock-firmware/model/autoboot combination is physically tested. Official OnionOS is for Mini/Mini Plus, **not Mini Flip**; choose an appropriate compatible alternative for the Flip. Allium should use app-only unless its launcher is verified.
- **OS power management still takes priority.** OnionOS manages theme artwork, suspend and shutdown, and its native idle timer may act before Slot's menu timers. Other OS builds can handle these transitions differently.
- **Core choice and game performance vary.** mGBA/Gambatte/gpSP save states are not guaranteed interchangeable. Different Miyoo variants may have different performance and input hardware. ROMs, proprietary BIOS files and user saves are not in the downloads.

[**Miyoo full release and SHA-256 files**](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver2) · [Miyoo installation notes](miyoo/INSTALL.md) · [Miyoo build source](miyoo/)

---

## H700 features (Slot 1.16.0)

The following feature descriptions, screenshots, online update instructions and Anbernic device list refer to the **H700 build** unless explicitly stated otherwise.

## Inherited in Slot 1.16.0

select. slot. now incorporates the latest [official Slot v1.16.0](https://github.com/slot-cfw/slot/releases/tag/v1.16.0) and [pvaibhav v1.16.0](https://github.com/pvaibhav/slot/releases/tag/v1.16.0-pvaibhav.1), including:

- Handwritten cartridge titles whenever label artwork is missing.
- Kid Mode link-play invitations and player nicknames, with clearer multiplayer prompts.
- GPU frame blending available across mGBA, gpSP and Gambatte.
- Custom PNG overlays, with tiled and full-frame display options.
- USB-C audio adapter playback when connected.
- Turbo configured using the Turbo A / Turbo B control mappings instead of a separate Turbo Buttons toggle.
- The upstream screenshot gallery thumbnail fix.

These are **upstream improvements**. The separate section below documents our own additional changes.

## What this fork adds

These are the **custom changes in the H700 build**, on top of upstream Slot and pvaibhav's improvements. Everything listed here is retained in complete **H700** release builds.

### Game Boy visuals and color

- **Authentic GB/GBC/GBA shaders.** Extended Authentic rendering with model-specific LCD pixel separation, shadowing, ghosting and reflector response.
- **Game Boy Color appearance for original Game Boy games.** Additional Authentic color presentation beyond the original monochrome models.
- **Pocket Color.** Pocket-style LCD dot spacing and shadows with Game Boy Color-style color output.
- **Pocket Color & Pocket SGB (mGBA).** Both use the **same entire Pocket Color LCD display profile**: dot separation, glass, pixel shadows, persistence, reflector and, with **Color Correction On**, its calibrated olive-gray white point (RGB approximately 134/140/122) and GBC LCD color response. Their *emulated color sources* stay distinct: Pocket Color uses mGBA in Game Boy Color mode with automatic GBC palettes; Pocket SGB uses mGBA in Super Game Boy mode with actual SGB palettes. **Color Correction Off** retains each emulator's original source RGB (including neutral whites) while preserving the LCD dot shader. This models **SGB game colors through the Pocket Color screen**, intentionally not an authentic SNES television response.
- **Independent settings for Gambatte and mGBA.** GB/GBC screen appearance and color-correction behavior can differ by emulator core without interfering with the other.
- **Separate color-correction switches.** Keep the Authentic pixel grid, reflections and visual treatment while disabling the calibrated RGB color transfer. Monochrome LCD tint remains part of the model simulation.
- **Fast-forward adjustments.** Authentic LCD ghosting is suppressed during fast-forward and restored for normal play.
- **Fit-scaled LCD pixels on 640×480 devices.** Authentic's pixel-gap width is taken from the nearest integer-sized native-pixel reference grid (for example, 3×), then integrated over each actual Fit output pixel; LCD brightness compensation uses the same reference grid. DMG/Pocket/Light/Pocket Color/**Pocket SGB** share fractional-area ink-gap coverage and their original LCD shadow effects. Standard LCD keeps its area-integrated subpixel stripes, while Grid calculates coverage of intersecting bands. Exact integer-sized Authentic pixels are preserved; fractional Fit still necessarily softens some edges.
- **GBA Authentic on RG35XX H Fit (Ver. 18).** At 240×160 → 640×427 (~2.67×), partially covered GBA LCD row/column gaps now combine by their actual area union rather than losing intersection coverage to `max()`. Matching calibrated cell compensation preserves the existing GBA color-response curve and corrected brightness; Color Correction Off still leaves unboosted source colors with the Authentic pixel grid. Original integer scaling remains pixel-for-pixel unchanged. GBA Dot, Grid and LCD already had fractional Fit processing and retain it without further changes. Pocket Color and Pocket SGB keep their verified Ver. 17 appearance.
- **GBA scaling on 720×480 screens (Ver. 22).** Under **Screen → Game Boy Advance → Scale**, **Integer** provides a centered **2× (480×320)** image; **Fit** retains the original **3× (720×480)** image. The choice is saved in the GBA settings and does not alter GB/GBC sizing, Authentic/Pocket shaders, or color correction.
- **GBA / GBA SP bezel choice on 640×480 Anbernic screens (Ver. 20).** Under **Screen → Game Boy Advance → Bezel**, choose **None**, **GBA** (original horizontal Game Boy Advance artwork) or **GBA SP** (the existing AGS-102 strip). The new GBA bezel uses mugwomp93's already-authored *Perfect GBA* artwork, which has a pixel-identical transparency mask to Slot's original AGS-102 image. It retains the same screen placement, bezel size and slide animation. The selection is saved; GBA SP remains the default. The extra GBA choice is available **only at exactly 640×480**, including RG35XX H, not on 720×480 RG SP / RG34XXSP or other resolutions. No shader, scaling or core changes. Existing custom bezels still work; attribution and CC BY-SA 4.0 licensing are included in the firmware.

### Emulation and audio

- **Three supported cores:** mGBA and Gambatte for GB/GBC, and mGBA and gpSP for GBA.
- **Pinned older mGBA core.** Our complete H700 build uses the older mGBA revision `c758314a639aa0066e7b65a8341448181b73c804` rather than replacing it with a newer experimental core. Its modified corresponding source is supplied as a separate asset alongside each firmware release.
- **GB/GBC mGBA performance and audio changes.** Core-specific CPU governor selection, audio-ring overflow handling with short crossfades, buffer recovery, and pitch-neutral drift behavior. Gambatte and GBA playback are not modified by the mGBA-only audio path.
- **SameBoy is not bundled.** Experimental SameBoy work was retired after unfavorable performance; the supported GB/GBC choices remain mGBA and Gambatte.

### Controls and handheld behavior

- **Extra hotkey buttons:** L3, R3, and right-stick up/down/left/right on devices that have those controls.
- **Corrected right-stick axis mapping** for H700 handheld input, including the RG34XXSP layout.
- **Menu Screen Off** under **Settings → System**: turns off the display backlight after menu inactivity, default **3 minutes**.
- **Menu Power Off** under **Settings → System**: gracefully shuts down after menu inactivity, default **15 minutes**. Each timer is independently adjustable to **Off, 1, 3, 5, 10, 15 or 30 minutes**.
- **Menu-only inactivity detection.** Active gameplay is excluded, and a button press wakes an idled, dark screen without accidentally launching a game. Active background operations are excluded.
- **Automatic RetroAchievements config migration (Ver. 27).** On startup, select. slot. reads any existing `Config/retroachievements.toml` and performs a one-time, validated, atomic migration. It preserves the account name, token, any pending password, enabled state, UI-login marker, and compatible additional configuration fields. It never touches `Saves/RetroAchievements/` or offline achievement history. A malformed/unreadable configuration is never overwritten, and later startups skip already-migrated files. TOML comments/formatting may be normalized during the one-time rewrite; the actual settings remain intact. No SD card editing required.
- **RetroAchievements login save compatibility (Ver. 26).** Existing optional fields in `Config/retroachievements.toml` are preserved rather than rejected during on-device login. Malformed configurations are not overwritten. The Tools login now distinguishes invalid or unreadable configurations from real SD-card write failures, and the latter are recorded in `Logs/slot.log` without revealing credentials. Existing masked keyboard, restart-required login, Wi-Fi controls, achievement popups and emulator/shader behavior remain unchanged.
- **RetroAchievements on-device login (Ver. 25).** Use **Tools → RetroAchievements** to enter a username and a masked password with the existing on-screen keyboard. Slot saves the login configuration securely on the card and displays **Restart Slot for the login to take effect**; there is deliberately no hot account switch. On a successful subsequent login, the password entered through this menu is cleared after the token is persisted. Existing manually configured RetroAchievements accounts remain compatible.
- **RetroAchievements launch status (Ver. 24).** A silent, short banner when a game launches reports **Connected** only after a verified RetroAchievements game session, **Offline ready** when local achievement definitions are cached and the connection is unavailable, **Connecting** while checking the server, **No offline cache yet** if the game has not been prepared, or **Off** if RetroAchievements is disabled. The banner updates if connection is established during launch. Existing earned-achievement popups with cached badges, names, points and sound are unchanged. The Wi-Fi interface keeps its single On/Off switch, with no additional modes.
- **Reliable Wi-Fi through games and cartridge removal (Ver. 23).** Fixed the real shutdown source: ordinary ejection was incorrectly issuing the **link-play radio Down** command, and its script also killed home Wi-Fi. Normal games now keep enabled WLAN running while RetroAchievements are online, including during initial DHCP/reconnection, with no unnecessary shutdown on ejection. **Real wireless link play** temporarily borrows the radio for a direct softAP/STA connection, then automatically restores the saved home network afterward. Wi-Fi Off, sleep and power-off still release the radio normally.
- **Light-mode clock and battery percentage (Ver. 22).** Status text at the top of quick menus, including in-game menus, uses independent bright HUD text textures so both the **time** and **battery percentage** remain visible against the dark menu background. The existing shelf footer and wallpaper-specific colors remain untouched.
- **Corrected Resume on Power On.** **On** starts the last game and loads its resume state; **Off** boots to the shelf with that game selected but not running. **Resume on Insert** stays independent for manual launches.

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

### Online updates

- **Custom update channel** from **Settings → System → Check for Updates**. Updates come from [this repository's releases](https://github.com/Sinastrax/select-slot/releases), not an upstream build.
- **Full releases only:** the updater downloads a complete H700 package, checks its size and SHA-256 checksum, then stages it for installation at restart.
- **Correctly branded OTA version text (Ver. 21).** The updater displays **1.16.0 Ver. 21** instead of the internal `v1.16.0-rgsp.21` identifier. The technical ZIP filename stays unchanged to preserve backwards-compatible OTA updates.
- **No forced background updates.** The user chooses whether to install. ROMs, saves and personal settings are not bundled in releases.

See [ONLINE_UPDATES.md](ONLINE_UPDATES.md) for technical packaging and release procedures.

## How to install (H700)

1. Install a compatible [BaseOS](https://github.com/pvaibhav/BaseOS) setup for your handheld and prepare the SD2 card following the [original Slot guide](https://slot-cfw.fyi).
2. Back up saves, save states, and `Config/` before upgrading.
3. Download the **latest full H700 ZIP** from [Releases](https://github.com/Sinastrax/select-slot/releases/latest).
4. Extract the contents of the included device folder to the **root of SD2**, so `System/slot` is in the SD2 `System` directory. Do not copy the containing device folder itself.
5. Restart the handheld. Once running a select. slot. build with online updates, subsequent updates are available under **Settings → System → Check for Updates**.

Do not interchange save states made by different emulator cores; in-game battery saves and emulator save states have different compatibility requirements.

## Versions and release notes

The H700 and Miyoo versions are independent. The **[Miyoo Ver. 2 official release](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver2)** is deliberately not marked as the H700 `latest` release and is not part of H700 OTA. The full Miyoo requirements and limitations are above.


Release titles follow **select. slot. 1.16.0 Ver. 9**: the upstream Slot version appears immediately after the project name, followed by the custom revision number. For compatibility with existing OTA installations, Ver. 9 retains the technical version `1.16.0-rgsp.9` and tag `v1.16.0-rgsp.9`. Future functional versions increment the revision and include complete firmware updates; renaming alone does not generate a new release.

**[Latest release](https://github.com/Sinastrax/select-slot/releases/latest)** · **[Changes in the latest version](RELEASE_NOTES.md)**

Release notes list **only the additions and fixes since the previous release**, rather than repeating the complete feature list. This README is the permanent place for the full feature overview.

The [build workflow](.github/workflows/build-h700.yml) pins the pvaibhav base, applies our patches and builds a reproducible H700 device package. The firmware may run on other H700 devices, but not every feature or device has been physically tested.

---

# What does it look like?

The original cartridge carousel and core picker remain part of select. slot. The **Authentic examples** below are courtesy of [pvaibhav's fork](https://github.com/pvaibhav/slot); the carousel and link examples come from the [original Slot](https://github.com/slot-cfw/slot). These are visual references, not new captures of the custom Pocket Color or Pocket SGB modes.

<p align="center">
<img src="https://raw.githubusercontent.com/pvaibhav/slot/pvaibhav-improvements/.github/resources/screenshots/authentic-gb.png" width="32%" alt="pvaibhav Authentic Game Boy shader">
<img src="https://raw.githubusercontent.com/pvaibhav/slot/pvaibhav-improvements/.github/resources/screenshots/authentic-gbc.png" width="32%" alt="pvaibhav Authentic Game Boy Color shader">
<img src="https://raw.githubusercontent.com/pvaibhav/slot/pvaibhav-improvements/.github/resources/screenshots/authentic-gba.png" width="32%" alt="pvaibhav Authentic Game Boy Advance shader">
</p>
<p align="center">GB · GBC · GBA — inherited Authentic shader examples</p>

<p align="center">
<img src="https://raw.githubusercontent.com/slot-cfw/slot/main/.github/resources/screenshots/carousel.gif" width="48%" alt="Original Slot cartridge carousel">
<img src="https://raw.githubusercontent.com/slot-cfw/slot/main/.github/resources/screenshots/core-picker.gif" width="48%" alt="Original Slot core picker">
</p>

<p align="center">
<img src="https://raw.githubusercontent.com/slot-cfw/slot/main/.github/resources/screenshots/link.gif" width="96.5%" alt="Original Slot Game Boy link demonstration">
</p>

---

# Supported devices

select. slot. builds the same **H700 ARM64 device package** as its Slot base. The underlying frontend supports these devices:

| Device | Supported by Slot | Custom build hardware verification |
|---|---|---|
| Anbernic RG SP | Yes | Tested |
| Anbernic RG35XXSP | Yes | Not tested |
| Anbernic RG34XXSP | Yes | Tested |
| Anbernic RG34XX | Yes | Not tested |
| Anbernic RG35XX H | Yes | Tested |
| Anbernic RG35XX Plus | Yes | Not tested |
| Anbernic RG35XX Pro | Yes | Not tested |
| Anbernic RG28XX | Yes | Not tested |

This is **not an RGSP-exclusive firmware**. Device-specific controls such as L3/R3 and analog stick directions only appear where the hardware provides them.

---

# Credits and licensing

- **Original Slot:** [slot-cfw/slot](https://github.com/slot-cfw/slot), created by **Brandon Kowalski**. The original artwork and interface are credited to their respective authors, including [Markus](https://github.com/MarkusMaribu). The original guide is at [slot-cfw.fyi](https://slot-cfw.fyi).
- **Miyoo ARMv7 port:** [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo), used for the separate Mini family build. Its firmware integration and other changes remain credited to Dean Marano and their upstream contributors.
- **Enhanced Slot base:** [pvaibhav/slot](https://github.com/pvaibhav/slot), including its performance, Authentic shader, CPU scaling and other improvements. Its [wiki](https://github.com/pvaibhav/slot/wiki) documents many inherited features.
- **select. slot.:** the patches, build scripts and other changes maintained in this repository. Source modifications were developed with AI assistance and reviewed through automated builds and device testing.
- **Emulator and third-party assets:** mGBA, gpSP, Gambatte, shader sources, bezels and other third-party parts keep their own copyright and license conditions. The device build includes the applicable files in `System/licenses/`.

The Slot-derived frontend is distributed under the **GPL-3.0** terms in [LICENSE](LICENSE). This is a **noncommercial customization**; no proprietary game ROMs or BIOS dumps are distributed.

---

If you enjoy select. slot., please also support and credit the creators of [Slot](https://github.com/slot-cfw/slot) and [pvaibhav's fork](https://github.com/pvaibhav/slot).
