<div align="center">

<img src="https://raw.githubusercontent.com/slot-cfw/slot/main/.github/resources/hero.webp" width="100%" alt="The original Slot cartridge-shelf artwork">

# select. slot.

**A personal take on Slot for Game Boy, Game Boy Color and Game Boy Advance.**

[**Download for Anbernic H700**](https://github.com/Sinastrax/select-slot/releases/latest) · [**Download for Miyoo Mini**](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver10) · [**Release history**](CHANGELOG.md) · [**Original Slot guide**](https://slot-cfw.fyi/) · [**Original Slot Discord**](https://discord.gg/NYRWsSuPUu)

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
| Current build | **1.16.0 Ver. 46** | **1.8.1 Ver. 10** |
| Handhelds | RG SP / RG34XXSP / RG35XX H and other compatible H700 models | Miyoo Mini, Mini Plus and Mini Flip, subject to firmware support |
| Rendering | GPU, including Authentic and custom LCD styles | Software rendering; no H700 LCD shaders |
| Game cores | GB/GBC: Gambatte or mGBA; GBA: gpSP or mGBA | GB/GBC: mGBA; GBA: gpSP or mGBA |
| Updates | Wi-Fi / in-app OTA updates | Manual SD-card installation only |
| Download | [**Latest H700 release**](https://github.com/Sinastrax/select-slot/releases/latest) | [**Miyoo Ver. 10 release**](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver10) |

## Device compatibility

The H700 device list follows [original Slot](https://github.com/slot-cfw/slot#supported-devices) and [pvaibhav's fork](https://github.com/pvaibhav/slot#supported-devices). The Miyoo device list follows [Dean Marano's port](https://github.com/deanmarano/slot-miyoo). An upstream-supported device is **not automatically verified with select. slot.**

| Device | Build | Supported since (upstream) | select. slot. testing |
| --- | --- | --- | --- |
| **Anbernic RG SP** | H700 | Original Slot | **Every applicable update** |
| **Anbernic RG34XXSP** | H700 | Slot 1.4.0 | **Every applicable update** |
| **Anbernic RG35XX H** | H700 | Slot 1.7.0 | **Every applicable update** |
| Anbernic RG34XX | H700 | Slot 1.4.0 | Upstream-supported; not personally tested |
| Anbernic RG35XXSP | H700 | Slot 1.5.0 | Upstream-supported; not personally tested |
| Anbernic RG35XX Plus | H700 | Slot 1.5.0 | Upstream-supported; not personally tested |
| Anbernic RG35XX Pro | H700 | Slot 1.15.0 | Upstream-supported; not personally tested |
| Anbernic RG28XX | H700 | Slot 1.6.0 | Upstream-supported; not personally tested |
| **Miyoo Mini (original)** | Miyoo | Miyoo port of Slot 1.8.1 | **Every applicable update** |
| Miyoo Mini Plus | Miyoo | Miyoo port of Slot 1.8.1 | Port-supported; not personally tested |
| Miyoo Mini Flip | Miyoo | Miyoo port of Slot 1.8.1 | Port-supported; not personally tested |

**Testing convention:** When a result is reported as working, it applies to **every compatible device in the regular four-device test lineup**, unless an exception is explicitly stated. Device-only features are tested only where the hardware supports them. The Miyoo models also require a compatible firmware and appropriate installer; see [Miyoo compatibility and installation](miyoo/INSTALL.md).

## What original Slot includes

select. slot. keeps the cartridge-oriented experience created for **[original Slot](https://github.com/slot-cfw/slot)**. These are **upstream features**, not features developed by select. slot.

### Shelf, cartridges and organization

- **Cartridge shelf / carousel:** browse GB, GBC and GBA games like physical carts; original cart styles, labels, cartridge animations and the core-picker presentation.
- **Favorites, Recents and collections:** organize games across systems; add, reorder and move collections. A separate GB Advance Video shelf is supported by the original H700 frontend.
- **Cart Studio:** customize cartridge shells, finishes and labels, including fetching art where network services are available. Games without downloaded artwork can display handwritten names on their carts.
- **Themes and wallpapers:** dark/light appearance, per-shelf or random backgrounds, tinting, and personally supplied wallpapers.
- **Custom assets:** system bezels, splash/boot logos, cartridge labels, game guides, and PNG overlays. Overlays can cover a game or tile repeatedly.
- **Original RomM integration** for connecting to a configured RomM game library on supported network-enabled Slot builds.
- **Optional Gamebit web interface (H700):** manage games, saves, state files, artwork, guides, bezels, wallpapers, BIOS and other SD-card files over Wi-Fi from a phone or computer. This was created by Slot.

### Gameplay, controls and convenience

- **Game Boy, Game Boy Color and Game Boy Advance** support, with core choice on eligible systems; per-game emulator selections where supported.
- **Battery saves, save states, rewind and automatic save/resume**. Resume on Insert and Resume on Power On are independently configurable. A state viewer and recent save/load undo are included.
- **Fast-forward and turbo:** configurable fast-forward rates, hold/toggle behavior, and configurable Turbo A and Turbo B mappings.
- **Screenshots and game guides:** capture in-game images, browse screenshots and use a text guide named for the game.
- **Per-system screen controls:** scaling, stretch, basic shaders such as LCD/Grid/Dot, palettes, color correction, mixing/ghosting, contrast, saturation and blue-light adjustments. The visual options differ across hardware and emulator cores.
- **Kid Mode:** limits the shelf and controls for younger players; the 1.16.0 upstream release also provides nicknames and clearer invitations for Kid Mode link play.
- **Direct wireless link play on supported H700 devices**, rumble for appropriate cartridges, city-based real-time clocks, and the mGBA Boktai solar sensor.
- **Remappable controls and context-sensitive shortcuts**, lid/sleep behavior and hardware brightness/volume management; USB-C audio adapters are supported by upstream Slot 1.16.0 on compatible hardware.
- **Network features on H700:** Wi-Fi setup, time synchronization, online artwork fetching, and the original firmware update interface.

Official documentation: [Slot tour](https://slot-cfw.fyi/tour/), [controls](https://slot-cfw.fyi/guide/controls/), [screen settings](https://slot-cfw.fyi/guide/screen/), [customization](https://slot-cfw.fyi/guide/customizing/), [collections](https://slot-cfw.fyi/guide/collections/) and [Gamebit](https://slot-cfw.fyi/guide/gamebit/). The Miyoo build uses Dean Marano's adapted ARMv7 software renderer; not every H700 feature exists there.

## What pvaibhav's H700 fork adds

The H700 version of select. slot. is based on **[pvaibhav/slot](https://github.com/pvaibhav/slot)**, at `v1.16.0-pvaibhav.1`. It inherits these enhancements, including some changes that later became standard upstream Slot features:

- **Authentic LCD shaders** for Game Boy, Pocket, Light, Game Boy Color and GBA. The original reflective LCD models simulate screen colors, pixel structure, reflections, glass and ghosting, with an independent Reflection setting.
- **Measured panel color calibration** for compatible RG SP and RG34XXSP hardware, including calibrated gamma and white-point adjustments.
- **Automatic 120 Hz** on compatible RG SP, RG34XXSP and RG34XX panel variants. Other revisions keep their normal refresh rates. It is not enabled universally.
- **CPU scaling and performance policies** tailored to the running game/core; suitable GB/GBC workloads can save power, while mGBA GBA can run at a faster governor for consistent timing.
- **GPU Frame Blending** became part of original Slot 1.16.0; the original pvaibhav changes are credited for bringing blending/ghosting across Gambatte, gpSP and mGBA.
- **Persistent Wi-Fi while playing**, so online RetroAchievements sessions can stay connected without scanning for a new network during an emulated frame.
- **RetroAchievements** for GB/GBC/GBA, with connected sessions, softcore unlocks, Rich Presence, cached offline achievements and subsequent synchronization. Trophy seals can mark games prepared for offline achievements.
- **mGBA cheats:** optional `Cheats.pack` or appropriately named RetroArch `.cht` files in the corresponding `Cheats/` subfolder. This is not available in Gambatte.
- **Cartridge label packs:** optional `Artwork.pack` provides a large set of offline labels without needing a live image fetch.
- **Fork-based updates:** select. slot. keeps the idea of a fork-specific OTA release channel, but redirects it to its **own** H700 releases rather than downloading pvaibhav's firmware.

Detailed upstream references: [Authentic shaders](https://github.com/pvaibhav/slot/wiki/Authentic-shader), [panel calibration](https://github.com/pvaibhav/slot/wiki/Panel-colour-calibration), [120 Hz](https://github.com/pvaibhav/slot/wiki/120-Hz-and-run-ahead), [CPU and battery](https://github.com/pvaibhav/slot/wiki/CPU-speed-and-battery), [RetroAchievements](https://github.com/pvaibhav/slot/wiki/RetroAchievements), [cheats](https://github.com/pvaibhav/slot/wiki/Cheats) and [updates](https://github.com/pvaibhav/slot/wiki/Updates-and-releases).

### Optional H700 resource packs from pvaibhav

| Pack | What it does |
| --- | --- |
| [**Artwork.pack**](https://github.com/pvaibhav/slot/releases/download/v1.16.0-pvaibhav.1/Artwork.pack) | Put in `Labels/` for predownloaded artwork. |
| [**Cheats.pack**](https://github.com/pvaibhav/slot/releases/download/v1.16.0-pvaibhav.1/Cheats.pack) | Put in `Cheats/` for mGBA-compatible cheats. |

These packs are published by **pvaibhav**, not supplied as parts of select. slot.'s firmware ZIP.

## What select. slot. adds

Everything below is **on top of** the respective upstream project. The custom H700 and Miyoo changes are not interchangeable.

### Anbernic H700 — select. slot. additions

These are the **custom changes in the H700 build**, on top of upstream Slot and pvaibhav's improvements. Everything listed here is retained in complete **H700** release builds.

#### Game Boy visuals and color

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

#### Emulation and audio

- **Three supported cores:** mGBA and Gambatte for GB/GBC, and mGBA and gpSP for GBA.
- **Pinned older mGBA core.** Our complete H700 build uses the older mGBA revision `c758314a639aa0066e7b65a8341448181b73c804` rather than replacing it with a newer experimental core. Its modified corresponding source is supplied as a separate asset alongside each firmware release.
- **GB/GBC mGBA performance and audio changes.** Core-specific CPU governor selection, audio-ring overflow handling with short crossfades, buffer recovery, and pitch-neutral drift behavior. Gambatte and GBA playback are not modified by the mGBA-only audio path.
- **SameBoy is not bundled.** Experimental SameBoy work was retired after unfavorable performance; the supported GB/GBC choices remain mGBA and Gambatte.

#### Controls and handheld behavior

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

#### Important improvements

- **RetroAchievements (Ver. 30–35):** reliable in-game tracking for German Pokémon Smaragd, safe indirect memory reads, progress and per-game refresh, offline caching, and achievement tracking during fast-forward. The achievement viewer reuses a fixed number of UI textures.
- **Long list names (Ver. 46):** The selected cheat or achievement name scrolls horizontally when it exceeds its column.
- **Better menus (Ver. 30–40):** universal menu scrolling, an in-game achievements viewer, safe storage cleanup, a standalone Restart menu entry, readable device names, and a hardware-tested, compact **Controls → Hotkey Guide** for less-obvious shortcuts.
- **Independent shader and scale settings:** verified Pocket Color/SGB and GBA Authentic Fit optimizations with the intended color-correction options.
- **Reliable distribution (Ver. 36):** pinned source patches, automated regression checks, and complete OTA builds with a separate mGBA source archive. Earlier public versions were curated to preserve meaningful rollback points.

For detailed per-version history and links to confirmed milestones, see the [changelog](CHANGELOG.md). Ver. 41 adds one-shot Shift and Caps Lock to the H700 keyboard. Press Shift or SELECT once for one character, twice for Caps Lock, and again to unlock. The Shift key has a white background behind the arrow after one press and displays **CAPS** while locked. Ver. 40 was tested on all three regular H700 devices.

Choose **Deutsch** under **Settings → General → Language**, then restart Slot. The German interface includes settings, controls, help, dialogs and status messages. To switch back, choose **English** under **Einstellungen → Allgemein → Sprache** and restart. Game content and user-entered names keep their original language.

#### Online updates

- **Custom update channel** from **Settings → System → Check for Updates**. Updates come from [this repository's releases](https://github.com/Sinastrax/select-slot/releases), not an upstream build.
- **Full releases only:** the updater downloads a complete H700 package, checks its size and SHA-256 checksum, then stages it for installation at restart.
- **Correctly branded OTA version text (Ver. 21).** The updater displays **1.16.0 Ver. 21** instead of the internal `v1.16.0-rgsp.21` identifier. The technical ZIP filename stays unchanged to preserve backwards-compatible OTA updates.
- **No forced background updates.** The user chooses whether to install. ROMs, saves and personal settings are not bundled in releases.

See [the online update guide](ONLINE_UPDATES.md) for technical packaging and release procedures.

### Miyoo Mini family — port and select. slot. changes

The Miyoo version is derived from [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo), **not** from the H700 codebase. Dean's port implements the CPU software renderer, framebuffer and panel handling, ARMv7 emulator cores, buttons, audio, battery and power integration. Its shelf, game states, rewind and optional physical-console bezels build upon the original Slot interface.

select. slot.'s **Miyoo Ver. 6** adds independent GB/GBC/GBA scaling defaults, per-game scaling overrides, mGBA as the only GB/GBC core, GBA/GBA SP bottom-bezel choices, menu overflow fixes, improved clock/battery contrast, 0–9 brightness handling, native OnionOS sleep/theme handoff and removal of the Miyoo Restart UI. Three installer packages are provided: OnionOS autoboot, genuine-stock autoboot and app-only.

#### Miyoo feature and behavior reference

| Area | Behavior |
| --- | --- |
| Games | Game Boy (GB), Game Boy Color (GBC), Game Boy Advance (GBA) |
| Core defaults | GB/GBC: mGBA; GBA: gpSP |
| Other core options | GB/GBC: no additional core; GBA: mGBA alternative to gpSP |
| Scaling | Original, Integer, Aspect Fit, Fill/Crop, Full Stretch |
| Scaling persistence | Independent defaults at **Screen → GB/GBC/GBA → Scaling**, saved in `Config/video_mode.txt`. In-game per-ROM overrides take priority |
| Screen / rendering | Original unfiltered software pixels; shader controls removed and previous shader choices ignored |
| GBA lower bezel | **Screen → GBA → Bezel**: None, **GBA SP** (existing style and retained default), or **GBA**. The new style uses existing original-GBA artwork with the same 640×480 transparency mask, display opening and position as SP |
| Restart | **Not offered on Miyoo.** The Settings entry and About X action/legend were removed. Use normal shutdown and power-on when a new session is needed |
| Scrolling | All long menu pages, including Gameplay settings, stay within a visible six-row viewport; the in-game Screen panel retains its three-row viewport |
| Menu readability | High-contrast clock and battery percentage in both main settings and in-game quick menus; normal shelf colors unchanged |
| About | Shows **Version 1.8.1 Ver. 10** in the existing sticker layout; B/Menu returns to settings |
| Menu Screen Off | Off, 1, 3, 5, 10, 15, 30 minutes; default 3; the first button press wakes without launching anything |
| Menu Power Off | Off, 1, 3, 5, 10, 15, 30 minutes; default 15 |
| Resume | Independent Resume on Power On and Resume on Insert settings |
| Themes and power | On OnionOS, uses the operating system's own POWER, standby and shutdown handling with its currently selected theme |
| Updates | **Manual SD-card installation only**; no Wi-Fi or in-app OTA updater |

Individual game scaling preferences and battery saves are kept independently of the global per-system defaults. Previously saved per-game core choices of `gambatte` are **interpreted as mGBA at load time**, rather than failing to load. This does not rewrite or delete the old core-selection file and preserves other settings and ROMs. **Gambatte save states cannot be loaded by mGBA.** Use in-game battery saves for cross-core continuity.

An older `System/gambatte_libretro.so` and `System/licenses/gambatte-src.tar.gz` may remain on a card updated by extracting the new ZIP over the previous release. Those files are no longer referenced or included; optionally delete just those two old files after backing up your card. The installer does not automatically delete unknown user files.

**Miyoo-specific limitations:** The 32-bit CPU renderer has no H700 Authentic/Pocket Color/SGB shader stack; there is no Wi-Fi OTA updater. The original Miyoo Mini also has no Wi-Fi hardware. Link-play code in the original port was not demonstrated working; do not assume multiplayer link compatibility. Save states from Gambatte are incompatible with mGBA, and gpSP states cannot be freely exchanged with mGBA. Always back up saves before switching cores. Original Mini testing does not establish Mini Plus or Flip firmware compatibility.

For the actual ZIPs, OnionOS/stock installation boundaries and boot-safety warning, see [Miyoo installation](miyoo/INSTALL.md) and [Miyoo maintenance](miyoo/MAINTENANCE.md).

## A look at Slot

The distinctive cartridge shelf, core picker and overall interface were designed upstream. These are **original Slot** examples, not screenshots of new select. slot. features.

<p align="center">
<img src="https://raw.githubusercontent.com/slot-cfw/slot/main/.github/resources/screenshots/carousel.gif" width="48%" alt="Original Slot cartridge shelf">
<img src="https://raw.githubusercontent.com/slot-cfw/slot/main/.github/resources/screenshots/core-picker.gif" width="48%" alt="Original Slot emulator picker">
</p>

<p align="center">
<img src="https://raw.githubusercontent.com/slot-cfw/slot/main/.github/resources/screenshots/link.gif" width="96%" alt="Original Slot H700 link-play demonstration">
</p>


The following **Authentic LCD shader** examples come from pvaibhav's fork. select. slot.'s additional Pocket Color and Pocket SGB configurations are not shown here.

These are original upstream screenshots, not newly captured select. slot. screens.

<p align="center">
<img src="https://raw.githubusercontent.com/pvaibhav/slot/pvaibhav-improvements/.github/resources/screenshots/authentic-gb.png" width="32%" alt="pvaibhav Authentic Game Boy">
<img src="https://raw.githubusercontent.com/pvaibhav/slot/pvaibhav-improvements/.github/resources/screenshots/authentic-gbc.png" width="32%" alt="pvaibhav Authentic Game Boy Color">
<img src="https://raw.githubusercontent.com/pvaibhav/slot/pvaibhav-improvements/.github/resources/screenshots/authentic-gba.png" width="32%" alt="pvaibhav Authentic Game Boy Advance">
</p>


### Miyoo software-rendered interface (original port)

The following images are from [Dean Marano's Miyoo port](https://github.com/deanmarano/slot-miyoo), not select. slot. device captures.

<p align="center">
<img src="https://raw.githubusercontent.com/deanmarano/slot-miyoo/main/docs/shelf.png" width="48%" alt="Original Miyoo port shelf">
<img src="https://raw.githubusercontent.com/deanmarano/slot-miyoo/main/docs/bezel.png" width="48%" alt="Original Miyoo port bezel">
</p>

## Basic controls

Button bindings can be remapped and depend on the handheld. These are common upstream actions; for the exact current mappings, use [Slot's controls guide](https://slot-cfw.fyi/guide/controls/) or **Controls → Hotkey Guide** on the H700 version.

| Action | Typical control |
| --- | --- |
| Browse the shelf | Left / Right |
| Switch shelves or systems | Shoulder buttons |
| Favorite or unfavorite | Y |
| Insert/resume a cartridge | A |
| Open available emulator picker | START |
| Open settings / quick menu | Tap MENU |
| Return to shelf / eject | Hold MENU |
| Open save-state switcher | Double-tap MENU |
| Fast-forward and rewind | Assigned Fast-Forward / Rewind controls |
| Save or load states, take screenshots | Assigned shortcuts |
| GB/GBC picture stretch | L1 / R1 when not used by the game |

## Installation

### Anbernic H700

1. Set up a compatible [BaseOS](https://github.com/pvaibhav/BaseOS) and SD2 card following the [original Slot installation guide](https://slot-cfw.fyi/).
2. Back up your saves, save states and `Config/` directory.
3. Download the [latest full H700 ZIP](https://github.com/Sinastrax/select-slot/releases/latest). Copy the **contents of its device folder** to the root of SD2, so the executable is at `System/slot`.
4. Restart. Subsequent select. slot. updates are available under **Settings → System → Check for Updates**, once the custom update channel is installed.

The update package is a complete firmware build, not a standalone patch or a replacement for BaseOS. [Read the full update details](ONLINE_UPDATES.md).

### Miyoo Mini / Mini Plus / Mini Flip

Download **one** package from [Miyoo Ver. 10](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver10):

| Package | Use it for |
| --- | --- |
| **OnionOS autoboot** | Compatible original Mini / Mini Plus setups running OnionOS 4.3+ |
| **Stock autoboot** | Genuine Miyoo stock firmware only |
| **App-only** | Manual launch; safest when the installed OS or boot integration is uncertain |

Back up the SD card and extract the chosen ZIP's **contents** to the card root, including hidden folders. **Do not install the stock-autoboot ZIP over OnionOS, Allium or another OS using `.tmp_update/runtime.sh`**. Official OnionOS does not support the Mini Flip; use an appropriate supported firmware and installation method.

[Full Miyoo installation instructions](miyoo/INSTALL.md)


### H700 configuration and optional files

After setting up Wi-Fi in Slot, **Tools → RetroAchievements** allows on-device login on the H700 build. Existing `Config/retroachievements.toml` configurations are still recognized, with a one-time compatibility migration where needed. The emulator takes effect after a restart.

For cartridge artwork without a network download, use the [pvaibhav Artwork.pack](https://github.com/pvaibhav/slot/releases/download/v1.16.0-pvaibhav.1/Artwork.pack) in `Labels/`. For mGBA cheats, use the corresponding [Cheats.pack](https://github.com/pvaibhav/slot/releases/download/v1.16.0-pvaibhav.1/Cheats.pack) in `Cheats/`.

H700 firmware updates use a **complete manifest-controlled System update** with size/SHA-256 verification. User ROMs, saves and personal configurations outside managed System files are not part of the release. See [online updates](ONLINE_UPDATES.md). SHA-256 from the same download site is an integrity check, not an independently signed package.

## Release versions and update cadence

- **Anbernic H700:** [1.16.0 Ver. 46](https://github.com/Sinastrax/select-slot/releases/tag/v1.16.0-rgsp.46) adds horizontal scrolling for long cheat and achievement names. [Ver. 36](https://github.com/Sinastrax/select-slot/releases/tag/v1.16.0-rgsp.36) is a tested fallback; other retained milestone releases are catalogued in the [changelog](CHANGELOG.md).
- **Miyoo:** [1.8.1 Ver. 10](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver10) is the separate current ARMv7 release, installed manually from SD.
- **Technical version labels** (such as `v1.16.0-rgsp.40`) remain for compatibility with earlier H700 update installations. The public firmware name is **select. slot.**.
- **Release cadence:** unlike pvaibhav's automated upstream sync, select. slot. does not claim a daily automatic upstream release schedule. New firmware versions are kept separate from documentation-only edits.

## Source and building

| Component | H700 build | Miyoo build |
| --- | --- | --- |
| Upstream | pvaibhav/slot 1.16.0 with ordered historical patches | Dean Marano's ARMv7 Slot 1.8.1 port |
| Customization scripts | [H700 source preparation](.github/scripts/h700-prepare.sh) | [Miyoo patch generator](miyoo/apply_custom.py) |
| Build workflow | [H700 CI](.github/workflows/build-h700.yml) | [Miyoo CI](.github/workflows/build-miyoo.yml) |
| Local build guidance | [H700 maintenance](H700_MAINTENANCE.md) | [Miyoo build script](miyoo/build.sh) and [maintenance](miyoo/MAINTENANCE.md) |
| Deliverables | Full firmware, `versions.json`, separate modified mGBA source | Onion/stock/app ZIPs and SHA-256 files |

H700 patches are **ordered build inputs**. Earlier stages must not be deleted solely because later stages refine them. CI verifies buildability and many functional contracts; every applicable firmware update is also tested on the compatible devices identified in the compatibility table above.

## Documentation

| Resource | Contents |
| --- | --- |
| [Official Slot guide](https://slot-cfw.fyi/) | Basic shelf, controls, game launching, link play and customization |
| [pvaibhav's Slot wiki](https://github.com/pvaibhav/slot/wiki) | Original Authentic shaders, calibration, RetroAchievements, power and performance features |
| [H700 feature reference](docs/H700_FEATURES.md) | Detailed list of inherited and custom H700 features |
| [Release history](CHANGELOG.md) | Stable milestones, changes and rollback versions |
| [H700 maintenance guide](H700_MAINTENANCE.md) | Pinned sources, build verification and hardware checks |
| [Miyoo installation](miyoo/INSTALL.md) | Package selection, SD-card layout, saves and firmware limitations |

## AI disclosure and project relationship

Original Slot and pvaibhav each disclose AI-assisted work in their own repositories. select. slot.'s source patches and integration tooling likewise use **AI assistance**, with development decisions, source verification, automated checks and regular handheld testing maintained for this customization.

This repository does not claim ownership of the original interface or artworks and is not an official continuation, release channel, or GitHub-linked fork of the upstream projects. The separate Anbernic and Miyoo source foundations are credited directly. Support questions about select. slot. changes should be directed to this repository rather than to the upstream maintainers.

## Credits and license

**Original Slot:** [Brandon Kowalski](https://github.com/slot-cfw/slot) created Slot and its guide. The cartridge-inspired interface and artwork are credited to their original creators, including [Markus](https://github.com/MarkusMaribu).

**H700 base and features:** [pvaibhav/slot](https://github.com/pvaibhav/slot) provides the enhanced H700 fork, Authentic LCD shaders and measured panel calibration, performance and RetroAchievements features. [BaseOS](https://github.com/pvaibhav/BaseOS) is maintained separately.

**Miyoo port:** [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo) developed the software-rendered ARMv7 port on which the Miyoo build depends.

**Additional software and assets:** mGBA, gpSP, Gambatte, bezels and shader components retain their original credits and licensing. The optional GBA bezel uses existing artwork credited to [mugwomp93 / KNULLI Bezels](https://github.com/chrizzo-hb/knulli-bezels). Source modifications in this repository were developed with AI assistance and verified using automated checks and device testing.

The Slot-derived frontend is distributed under [GPL-3.0](LICENSE); applicable third-party licenses and emulator source notices are provided with the firmware. **No game ROMs or proprietary BIOS files are distributed.**

If this customization is useful, please also support and credit the creators of [original Slot](https://github.com/slot-cfw/slot), [pvaibhav's fork](https://github.com/pvaibhav/slot) and [Dean Marano's port](https://github.com/deanmarano/slot-miyoo).
