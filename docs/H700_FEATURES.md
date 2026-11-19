# select. slot. — H700 feature reference

This page provides an expanded technical reference for the H700 features also summarized and described in the main [README](../README.md). It describes the **Anbernic H700** build only, based on **[Slot](https://github.com/slot-cfw/slot)** and **[pvaibhav/slot](https://github.com/pvaibhav/slot)** at the pinned `v1.16.0-pvaibhav.1` source. It must not be treated as Miyoo Mini documentation.

For how the game-focused frontend works in general, use the [official Slot guide](https://slot-cfw.fyi/). For original pvaibhav behavior and screenshots, see the [pvaibhav wiki](https://github.com/pvaibhav/slot/wiki). For the current supported version and release milestones, see the [changelog](../CHANGELOG.md).

The build deliberately preserves upstream behavior while making extra configuration and visual changes. Hardware-dependent features, such as higher panel refresh rates and analogue button mappings, are **not universal**. **Testing coverage:** Every H700 update and reported successful result is tested on all compatible regular H700 devices — **Anbernic RG SP, RG34XXSP and RG35XX H** — unless the maintainer explicitly states otherwise. Hardware-specific features are tested wherever supported. The separate ARMv7 releases are tested on the original Miyoo Mini. Current stable H700 release: [Ver. 40](https://github.com/Sinastrax/select-slot/releases/tag/v1.16.0-rgsp.40).

---

## Features inherited and added on H700

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

## What select. slot. adds

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

### Important improvements

- **RetroAchievements (Ver. 30–35):** reliable in-game tracking for German Pokémon Smaragd, safe indirect memory reads, progress and per-game refresh, offline caching, and achievement tracking during fast-forward. The achievement viewer reuses a fixed number of UI textures.
- **Better menus (Ver. 30–40):** universal menu scrolling, an in-game achievements viewer, safe storage cleanup, a standalone Restart menu entry, readable device names, and a hardware-tested, compact **Controls → Hotkey Guide** for less-obvious shortcuts.
- **Independent shader and scale settings:** verified Pocket Color/SGB and GBA Authentic Fit optimizations with the intended color-correction options.
- **Reliable distribution (Ver. 36):** pinned source patches, automated regression checks, and complete OTA builds with a separate mGBA source archive. Earlier public versions were curated to preserve meaningful rollback points.

For detailed per-version history and links to confirmed milestones, see the [changelog](../CHANGELOG.md). The current stable H700 build is **Ver. 40**, tested on all three compatible devices in the regular H700 lineup.

### Online updates

- **Custom update channel** from **Settings → System → Check for Updates**. Updates come from [this repository's releases](https://github.com/Sinastrax/select-slot/releases), not an upstream build.
- **Full releases only:** the updater downloads a complete H700 package, checks its size and SHA-256 checksum, then stages it for installation at restart.
- **Correctly branded OTA version text (Ver. 21).** The updater displays **1.16.0 Ver. 21** instead of the internal `v1.16.0-rgsp.21` identifier. The technical ZIP filename stays unchanged to preserve backwards-compatible OTA updates.
- **No forced background updates.** The user chooses whether to install. ROMs, saves and personal settings are not bundled in releases.

See [the online update guide](../ONLINE_UPDATES.md) for technical packaging and release procedures.

---

## More information

- [H700 installation and OTA updates](../ONLINE_UPDATES.md)
- [H700 build pipeline and device testing](../H700_MAINTENANCE.md)
- [Release milestones and change history](../CHANGELOG.md)
- [Miyoo-specific installation and limitations](../miyoo/INSTALL.md)

All screenshots of original Slot or pvaibhav's Authentic shaders in the main README are **upstream references**. They do not constitute screenshots of select. slot.'s newly added Pocket Color or Pocket SGB configurations.
