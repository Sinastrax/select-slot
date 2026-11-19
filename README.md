<div align="center">

<img src="https://raw.githubusercontent.com/slot-cfw/slot/main/.github/resources/hero.webp" width="100%" alt="The original Slot cartridge-shelf artwork">

# select. slot.

**A personal take on Slot for Game Boy, Game Boy Color and Game Boy Advance.**

[**Download for Anbernic H700**](https://github.com/Sinastrax/select-slot/releases/latest) · [**Download for Miyoo Mini**](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver6) · [**Release history**](CHANGELOG.md) · [**Original Slot guide**](https://slot-cfw.fyi/)

</div>

> [!IMPORTANT]
> **Choose the build for your hardware.** The Anbernic and Miyoo versions use different architectures, emulators and installation methods. They are not interchangeable. Only uncompressed GB/GBC/GBA ROMs are supported; no games or proprietary BIOS files are included.

## What is select. slot.?

**select. slot.** is an independently maintained customization of [Slot](https://github.com/slot-cfw/slot), Brandon Kowalski's cartridge-inspired Game Boy frontend. Rather than replacing Slot's interface, it keeps the familiar shelf and adapts the experience with additional display options, emulator choices and everyday usability fixes.

It combines two **separate** builds:

- **Anbernic H700:** based on [pvaibhav's enhanced Slot fork](https://github.com/pvaibhav/slot) at `v1.16.0-pvaibhav.1`. This is the version with Authentic LCD rendering, additional Pocket Color / SGB visuals, RetroAchievements improvements, and custom online updates.
- **Miyoo Mini family:** based on [Dean Marano's ARMv7 port](https://github.com/deanmarano/slot-miyoo) of Slot 1.8.1. This uses a **software renderer without the H700 Authentic shaders**, and is installed from an SD card.

This repository is not an official Slot release or currently a GitHub-linked fork. The upstream projects and artwork remain credited below.

## Choose a build

| | **Anbernic H700** | **Miyoo Mini family** |
| --- | --- | --- |
| Current build | **1.16.0 Ver. 40** | **1.8.1 Ver. 6** |
| Handhelds | RG SP / RG34XXSP / RG35XX H and other compatible H700 models | Miyoo Mini, Mini Plus and Mini Flip, subject to firmware support |
| Rendering | GPU, including Authentic and custom LCD styles | Software rendering; no H700 LCD shaders |
| Game cores | GB/GBC: Gambatte or mGBA; GBA: gpSP or mGBA | GB/GBC: mGBA; GBA: gpSP or mGBA |
| Updates | Wi-Fi / in-app OTA updates | Manual SD-card installation only |
| Download | [**Latest H700 release**](https://github.com/Sinastrax/select-slot/releases/latest) | [**Miyoo Ver. 6 release**](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver6) |

**Hardware testing:** Every update and reported successful result is tested on **each compatible device in the regular test lineup**, unless explicitly stated otherwise. For the H700 build, those devices are **Anbernic RG SP, RG34XXSP and RG35XX H**; for the separate Miyoo build, it is the **original Miyoo Mini**. Device-specific features are tested on the devices that support them. Other models, including Miyoo Mini Plus and Mini Flip, are not part of this confirmation.

## What it adds

### Anbernic H700

- **Pocket Color and Pocket SGB** display modes, plus refined GB/GBC/GBA Authentic LCD rendering. Pocket SGB uses mGBA's Super Game Boy palettes with the Pocket Color display treatment. Color correction can be controlled separately from the LCD effect.
- **Better scaling and appearance:** corrected pixel separation at fractional Fit resolutions, independent per-system display settings, and a choice of **GBA** or **GBA SP** bottom bezels on 640×480 devices.
- **RetroAchievements improvements:** on-device login, a status indicator, an in-game achievement browser and refresh, offline progress/sync support, and fixes for tracking during fast-forward and certain indirect-memory reads. German Pokémon Smaragd achievement unlocks have been tested on hardware.
- **More reliable handheld controls:** hardware-specific device identification, persistent Wi-Fi during normal gameplay, menu scrolling, screen-off and shutdown timers, and a compact read-only **Hotkey Guide** for lesser-known combinations.
- **Verified release pipeline:** full-firmware OTA packages, pinned emulator sources, and checks for the update manifest, shaders, save-data boundaries and core compatibility.

Features such as the cartridge shelf, link play, base system controls, panel calibration, higher refresh rates on compatible screens, CPU scaling, cheats and the original Authentic LCD models come from **Slot and/or pvaibhav's fork**, not from select. slot. See the [complete H700 feature reference](docs/H700_FEATURES.md) for the distinction and technical details.

### Miyoo Mini family

- Independent scaling preferences for GB, GBC and GBA; optional per-game scaling overrides.
- mGBA for GB/GBC, with gpSP or mGBA for GBA; the original **GBA / GBA SP** lower-bezel choice.
- Compact scrolling menus, readable clock and battery information, 0–9 brightness levels and menu idle controls.
- Separate OnionOS, genuine-stock and app-only packages. On OnionOS, the operating system remains responsible for its theme, standby and shutdown.

**Limitations:** No H700 GPU shaders or in-app online updater. Emulator save states do not necessarily transfer between cores; back up battery saves and settings before switching. Read the [Miyoo installation and compatibility notes](miyoo/INSTALL.md) before choosing a ZIP.

## A look at Slot

The distinctive cartridge shelf, core picker and overall interface were designed upstream. These are **original Slot** examples, not screenshots of new select. slot. features.

<p align="center">
<img src="https://raw.githubusercontent.com/slot-cfw/slot/main/.github/resources/screenshots/carousel.gif" width="48%" alt="Original Slot cartridge shelf">
<img src="https://raw.githubusercontent.com/slot-cfw/slot/main/.github/resources/screenshots/core-picker.gif" width="48%" alt="Original Slot emulator picker">
</p>

The following **Authentic LCD shader** examples come from pvaibhav's fork. select. slot.'s additional Pocket Color and Pocket SGB configurations are not shown here.

<p align="center">
<img src="https://raw.githubusercontent.com/pvaibhav/slot/pvaibhav-improvements/.github/resources/screenshots/authentic-gb.png" width="32%" alt="pvaibhav Authentic Game Boy">
<img src="https://raw.githubusercontent.com/pvaibhav/slot/pvaibhav-improvements/.github/resources/screenshots/authentic-gbc.png" width="32%" alt="pvaibhav Authentic Game Boy Color">
<img src="https://raw.githubusercontent.com/pvaibhav/slot/pvaibhav-improvements/.github/resources/screenshots/authentic-gba.png" width="32%" alt="pvaibhav Authentic Game Boy Advance">
</p>

## Installation

### Anbernic H700

1. Set up a compatible [BaseOS](https://github.com/pvaibhav/BaseOS) and SD2 card following the [original Slot installation guide](https://slot-cfw.fyi/).
2. Back up your saves, save states and `Config/` directory.
3. Download the [latest full H700 ZIP](https://github.com/Sinastrax/select-slot/releases/latest). Copy the **contents of its device folder** to the root of SD2, so the executable is at `System/slot`.
4. Restart. Subsequent select. slot. updates are available under **Settings → System → Check for Updates**, once the custom update channel is installed.

The update package is a complete firmware build, not a standalone patch or a replacement for BaseOS. [Read the full update details](ONLINE_UPDATES.md).

### Miyoo Mini / Mini Plus / Mini Flip

Download **one** package from [Miyoo Ver. 6](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver6):

| Package | Use it for |
| --- | --- |
| **OnionOS autoboot** | Compatible original Mini / Mini Plus setups running OnionOS 4.3+ |
| **Stock autoboot** | Genuine Miyoo stock firmware only |
| **App-only** | Manual launch; safest when the installed OS or boot integration is uncertain |

Back up the SD card and extract the chosen ZIP's **contents** to the card root, including hidden folders. **Do not install the stock-autoboot ZIP over OnionOS, Allium or another OS using `.tmp_update/runtime.sh`**. Official OnionOS does not support the Mini Flip; use an appropriate supported firmware and installation method.

[Full Miyoo installation instructions](miyoo/INSTALL.md)

## Documentation

| Resource | Contents |
| --- | --- |
| [Official Slot guide](https://slot-cfw.fyi/) | Basic shelf, controls, game launching, link play and customization |
| [pvaibhav's Slot wiki](https://github.com/pvaibhav/slot/wiki) | Original Authentic shaders, calibration, RetroAchievements, power and performance features |
| [H700 feature reference](docs/H700_FEATURES.md) | Detailed list of inherited and custom H700 features |
| [Release history](CHANGELOG.md) | Stable milestones, changes and rollback versions |
| [H700 maintenance guide](H700_MAINTENANCE.md) | Pinned sources, build verification and hardware checks |
| [Miyoo installation](miyoo/INSTALL.md) | Package selection, SD-card layout, saves and firmware limitations |

## Credits and license

**Original Slot:** [Brandon Kowalski](https://github.com/slot-cfw/slot) created Slot and its guide. The cartridge-inspired interface and artwork are credited to their original creators, including [Markus](https://github.com/MarkusMaribu).

**H700 base and features:** [pvaibhav/slot](https://github.com/pvaibhav/slot) provides the enhanced H700 fork, Authentic LCD shaders and measured panel calibration, performance and RetroAchievements features. [BaseOS](https://github.com/pvaibhav/BaseOS) is maintained separately.

**Miyoo port:** [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo) developed the software-rendered ARMv7 port on which the Miyoo build depends.

**Additional software and assets:** mGBA, gpSP, Gambatte, bezels and shader components retain their original credits and licensing. The optional GBA bezel uses existing artwork credited to [mugwomp93 / KNULLI Bezels](https://github.com/chrizzo-hb/knulli-bezels). Source modifications in this repository were developed with AI assistance and verified using automated checks and device testing.

The Slot-derived frontend is distributed under [GPL-3.0](LICENSE); applicable third-party licenses and emulator source notices are provided with the firmware. **No game ROMs or proprietary BIOS files are distributed.**
