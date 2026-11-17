<div align="center">

<img src="https://raw.githubusercontent.com/slot-cfw/slot/main/.github/resources/hero.webp" width="100%" alt="slot — Game Boy-centric custom firmware for Anbernic H700 handhelds">

[![Download](https://img.shields.io/badge/Download-Latest%20release-238636?style=for-the-badge)](https://github.com/Sinastrax/select-slot/releases/latest)
[![Original slot](https://img.shields.io/badge/Original-slot-555?style=for-the-badge)](https://github.com/slot-cfw/slot)
[![pvaibhav's fork](https://img.shields.io/badge/Based%20on-pvaibhav%2Fslot-555?style=for-the-badge)](https://github.com/pvaibhav/slot)
[![Guide](https://img.shields.io/badge/Guide-slot--cfw.fyi-555?style=for-the-badge)](https://slot-cfw.fyi)

</div>

---

# What is Custom slot?

**Custom slot** is a noncommercial, modified build of [slot](https://github.com/slot-cfw/slot), the Game Boy-centric frontend created by **Brandon Kowalski**, based on [pvaibhav's enhanced fork](https://github.com/pvaibhav/slot).

The **H700 edition** builds on **`v1.15.3-pvaibhav.1`** and adds independent GB/GBC shaders, Pocket Color and Super Game Boy modes, per-core color correction, custom input mappings, performance/audio changes, online updates, and menu power management.

Its name is **Custom slot**, not RGSP: the H700 build is intended for other compatible handhelds as well. The H700 and experimental Miyoo editions focus on **Game Boy, Game Boy Color and Game Boy Advance**, not NES, SNES, PS1 or N64.

> [!IMPORTANT]
> Use extracted ROM files, not `.zip` or `.7z` archives. Games and proprietary BIOS files are **not** included.

## Miyoo Mini edition (experimental)

A separate **ARMv7 / software-rendered** build targets the **original Miyoo Mini**, Miyoo Mini Plus and Miyoo Mini Flip. It is based on [deanmarano's Miyoo port](https://github.com/deanmarano/slot-miyoo) rather than the H700/aarch64 build. The port author has tested the original Mini with OnionOS 4.3.1; **our custom build has not yet been tested on hardware**.

- **Preview name:** Custom slot. 1.8.1 Ver. 5 (Miyoo). The Slot upstream is v1.8.1, pinned by Dean's port.
- **Emulators:** **Gambatte for GB/GBC** and **gpSP for GBA**, both ARMv7. mGBA remains optional for compatibility but Super Game Boy hardware/border modes are not included.
- **Scaling:** Original, true integer scaling, aspect fit, fill/crop and full stretch. Select under the in-game **Settings → Screen → Scaling** menu; options persist per game. GB/GBC shoulder buttons cycle choices if not used by the game.
- **System:** Independent **Resume on Power On** and **Resume on Insert**, with the earlier auto-start bug fixed; **Menu Screen Off** and **Menu Power Off** timers default to 3 and 15 minutes respectively and exclude gameplay.
- **Authentic display effects are NOT YET PORTED:** DMG, Pocket, Light, GBC, GBA and Pocket Color Authentic shaders require a real CPU software-rendering implementation. The Miyoo's LCD3x is not equivalent. The advanced H700 per-model correction, ghosting, extra hotkeys and OTA have not been ported. SGB is deliberately out of scope.
- **Validation:** A full GitHub Actions ARMv7 cross-build and ZIP verification passed; the enhanced preview has **not** been tested on physical Miyoo hardware.
- **OnionOS autoboot:** optional startup script provided at `System/autoboot/onion-startup.sh`. Copy to `.tmp_update/startup/custom-slot.sh` to enter Custom slot on power-on while preserving Onion's `runtime.sh`. Removing the file restores the normal boot. Not enabled by default; hardware testing pending.
- **OnionOS power and BMO theme:** native Onion boot splash remains unchanged; Slot-driven shutdown uses the active theme's `Screen_Off_Save`. When Onion `keymon` is active, it exclusively owns POWER sleep/wake and display blanking; Slot saves on key-down but no longer competes with Onion's suspend sequence. BMO themes have no separate sleep/wake assets. Ver. 4 also fixes accidental 180° Flip framebuffer rotation on the original Mini / Mini Plus. This integration is hardware-untested.
- **OnionOS brightness:** Slot no longer replaces Onion's user-configured brightness with its own default of level 5 on startup. The launcher reads `/customer/app/jsonval brightness`, initializes Slot's 1–9 display control from that setting, and retains in-game brightness adjustment. Validated in CI only; original Mini physical screen testing is required.
- **Delivery:** an independent, manually triggered or CI-built experimental ZIP that installs as an app on the Miyoo SD card. The original Miyoo Mini has no Wi-Fi, so it does not support the H700 OTA workflow.
- **Platform separation:** this edition never uses the H700 SD2 firmware package, and the Miyoo build does not modify the H700 build.

**[Miyoo installation, changes and credits](miyoo/INSTALL.md)** · **[Miyoo preview build workflow](.github/workflows/build-miyoo.yml)**

---

## H700 edition: what this fork adds

These are the **H700-specific custom changes**, on top of both upstream Slot and pvaibhav's improvements. Everything listed here is retained in complete H700 release builds. **Do not assume these features are available in the experimental Miyoo edition.**

### Game Boy visuals and color

- **Authentic GB/GBC/GBA shaders.** Extended Authentic rendering with model-specific LCD pixel separation, shadowing, ghosting and reflector response.
- **Game Boy Color appearance for original Game Boy games.** Additional Authentic color presentation beyond the original monochrome models.
- **Pocket Color.** Pocket-style LCD dot spacing and shadows with Game Boy Color-style color output.
- **Pocket SGB (Super Game Boy).** Runs compatible GB titles with mGBA's Super Game Boy hardware behavior and supports the games' dynamic SGB palettes. SGB borders are disabled for the handheld display.
- **Independent settings for Gambatte and mGBA.** GB/GBC screen appearance and color-correction behavior can differ by emulator core without interfering with the other.
- **Separate color-correction switches.** Keep the Authentic pixel grid, reflections and visual treatment while disabling the calibrated RGB color transfer. Monochrome LCD tint remains part of the model simulation.
- **Fast-forward adjustments.** Authentic LCD ghosting is suppressed during fast-forward and restored for normal play.

### Emulation and audio

- **Three supported cores:** mGBA and Gambatte for GB/GBC, and mGBA and gpSP for GBA.
- **Pinned older mGBA core.** Our complete H700 build uses the older mGBA revision `c758314a639aa0066e7b65a8341448181b73c804` rather than replacing it with a newer experimental core. Its corresponding source is packaged.
- **GB/GBC mGBA performance and audio changes.** Core-specific CPU governor selection, audio-ring overflow handling with short crossfades, buffer recovery, and pitch-neutral drift behavior. Gambatte and GBA playback are not modified by the mGBA-only audio path.
- **SameBoy is not bundled.** Experimental SameBoy work was retired after unfavorable performance; the supported GB/GBC choices remain mGBA and Gambatte.

### Controls and handheld behavior

- **Extra hotkey buttons:** L3, R3, and right-stick up/down/left/right on devices that have those controls.
- **Corrected right-stick axis mapping** for H700 handheld input, including the RG34XXSP layout.
- **Menu Screen Off** under **Settings → System**: turns off the display backlight after menu inactivity, default **3 minutes**.
- **Menu Power Off** under **Settings → System**: gracefully shuts down after menu inactivity, default **15 minutes**. Each timer is independently adjustable to **Off, 1, 3, 5, 10, 15 or 30 minutes**.
- **Menu-only inactivity detection.** Active gameplay is excluded, and a button press wakes an idled, dark screen without accidentally launching a game. Active background operations are excluded.
- **Corrected Resume on Power On.** **On** starts the last game and loads its resume state; **Off** boots to the shelf with that game selected but not running. **Resume on Insert** stays independent for manual launches.

### Online updates

- **Custom update channel** from **Settings → System → Check for Updates**. Updates come from [this repository's releases](https://github.com/Sinastrax/select-slot/releases), not an upstream build.
- **Full releases only:** the updater downloads a complete H700 package, checks its size and SHA-256 checksum, then stages it for installation at restart.
- **No forced background updates.** The user chooses whether to install. ROMs, saves and personal settings are not bundled in releases.

See [ONLINE_UPDATES.md](ONLINE_UPDATES.md) for technical packaging and release procedures.

## How to install

1. Install a compatible [BaseOS](https://github.com/pvaibhav/BaseOS) setup for your handheld and prepare the SD2 card following the [original Slot guide](https://slot-cfw.fyi).
2. Back up saves, save states, and `Config/` before upgrading.
3. Download the **latest full H700 ZIP** from [Releases](https://github.com/Sinastrax/select-slot/releases/latest).
4. Extract the contents of the included device folder to the **root of SD2**, so `System/slot` is in the SD2 `System` directory. Do not copy the containing device folder itself.
5. Restart the handheld. Once running a Custom slot build with online updates, subsequent updates are available under **Settings → System → Check for Updates**.

Do not interchange save states made by different emulator cores; in-game battery saves and emulator save states have different compatibility requirements.

## Versions and release notes

Releases are titled **Custom slot. Ver. 1.15.3.1**, **Custom slot. Ver. 1.15.3.2**, etc. Technical release tags and ZIP filenames retain their original version suffixes for update compatibility. The product name is not repeated in the version number.

**[Latest release](https://github.com/Sinastrax/select-slot/releases/latest)** · **[Changes in the latest version](RELEASE_NOTES.md)**

Release notes list **only the additions and fixes since the previous release**, rather than repeating the complete feature list. This README is the permanent place for the full feature overview.

The [build workflow](.github/workflows/build-h700.yml) pins the pvaibhav base, applies our patches and builds a reproducible H700 device package. The firmware may run on other H700 devices, but not every feature or device has been physically tested.

---

# What does it look like?

The original cartridge carousel and core picker remain part of Custom slot. The **Authentic examples** below are courtesy of [pvaibhav's fork](https://github.com/pvaibhav/slot); the carousel and link examples come from the [original Slot](https://github.com/slot-cfw/slot). These are visual references, not new captures of the custom Pocket Color or Pocket SGB modes.

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

# Supported H700 devices

Custom slot builds the same **H700 ARM64 device package** as its Slot base. The underlying frontend supports these devices:

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
- **Enhanced Slot base:** [pvaibhav/slot](https://github.com/pvaibhav/slot), including its performance, Authentic shader, CPU scaling and other improvements. Its [wiki](https://github.com/pvaibhav/slot/wiki) documents many inherited features.
- **Custom slot:** the patches, build scripts and other changes maintained in this repository. Source modifications were developed with AI assistance and reviewed through automated builds and device testing.
- **Emulator and third-party assets:** mGBA, gpSP, Gambatte, shader sources, bezels and other third-party parts keep their own copyright and license conditions. The device build includes the applicable files in `System/licenses/`.

The Slot-derived frontend is distributed under the **GPL-3.0** terms in [LICENSE](LICENSE). This is a **noncommercial customization**; no proprietary game ROMs or BIOS dumps are distributed.

---

If you enjoy Custom slot, please also support and credit the creators of [Slot](https://github.com/slot-cfw/slot) and [pvaibhav's fork](https://github.com/pvaibhav/slot).
