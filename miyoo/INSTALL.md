# select. slot. 1.8.1 Ver. 3 — Miyoo

**Offline ARMv7 build for the Miyoo Mini family**, based on [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo) and Slot **1.8.1**. This is a **different build from select. slot. for Anbernic H700**, which is based on Slot 1.16.0. Do not interchange their firmware files.

This release removes Gambatte and retains only the original Miyoo mGBA/gpSP cores. The verified screen geometry, scaling, original GBA and GBA SP bezels, inputs, PWM brightness (0–9), OnionOS theme and power handling remain unchanged.

## Features

| Area | Behavior |
| --- | --- |
| Games | Game Boy (GB), Game Boy Color (GBC), Game Boy Advance (GBA) |
| Core defaults | GB/GBC: mGBA; GBA: gpSP |
| Other core options | GB/GBC: no additional core; GBA: mGBA alternative to gpSP |
| Scaling | Original, Integer, Aspect Fit, Fill/Crop, Full Stretch |
| Scaling persistence | Independent defaults at **Screen → GB/GBC/GBA → Scaling**, saved in `Config/video_mode.txt`. In-game per-ROM overrides take priority |
| Screen / rendering | Original unfiltered software pixels; shader controls removed and previous shader choices ignored |
| GBA lower bezel | **Screen → GBA → Bezel**: None, **GBA SP** (existing style and retained default), or **GBA**. The new style uses existing original-GBA artwork with the same 640×480 transparency mask, display opening and position as SP |
| Menu Screen Off | Off, 1, 3, 5, 10, 15, 30 minutes; default 3; the first button press wakes without launching anything |
| Menu Power Off | Off, 1, 3, 5, 10, 15, 30 minutes; default 15 |
| Resume | Independent Resume on Power On and Resume on Insert settings |
| Themes and power | On OnionOS, uses the operating system's own POWER, standby and shutdown handling with its currently selected theme |
| Updates | **Manual SD-card installation only**; no Wi-Fi or in-app OTA updater |

Individual game scaling preferences and battery saves are kept independently of the global per-system defaults. Previously saved per-game core choices of `gambatte` now open with mGBA, rather than failing to load. This preserves other saved settings and ROM files. **Gambatte save states cannot be loaded by mGBA.** Use in-game battery saves for cross-core continuity.

An older `System/gambatte_libretro.so` and `System/licenses/gambatte-src.tar.gz` may remain on a card updated by extracting the new ZIP over the previous release. Those files are no longer referenced or included; optionally delete just those two old files after backing up your card. The installer does not automatically delete unknown user files.

## Choose exactly one installation package

| ZIP | Installed system | Result |
| --- | --- | --- |
| `select-slot-1.8.1-ver3-miyoo-onion-autoboot.zip` | **OnionOS 4.3+** on compatible Mini or Mini Plus | Starts select. slot. at boot through `.tmp_update/startup/select-slot.sh`, without replacing the OnionOS runtime or theme |
| `select-slot-1.8.1-ver3-miyoo-stock-autoboot.zip` | **Genuine stock Miyoo firmware only** | Starts select. slot. at boot using `.tmp_update/runtime.sh` |
| `select-slot-1.8.1-ver3-miyoo.zip` | App-only on compatible firmware | Adds Slot to the regular apps menu, without changing the startup sequence |

**Never extract the stock autoboot ZIP over OnionOS, Allium or another third-party SD-card operating system.** It contains a replacement `.tmp_update/runtime.sh`; overwriting another OS's existing boot script can stop the OS from starting. On an unknown or modified SD card use the **app-only** package instead.

### Installation

1. Back up the SD card, including `Config/`, `Saves/`, save states and the operating system's existing files.
2. Download **one** ZIP appropriate for the installed firmware. Extract its **contents** to the **root of the SD card**; include hidden folders such as `.tmp_update`. Do not create another directory around `System/` and `App/`.
3. Eject the card safely and boot the handheld. Autoboot packages launch Slot automatically; with app-only, launch Slot from the normal apps menu.

To disable OnionOS autoboot later, remove `.tmp_update/startup/select-slot.sh` or use the existing `.tmp_update/config/.skip-custom-slot-autoboot` skip flag. For stock firmware, back up and remove only a `.tmp_update/runtime.sh` file you know was installed by this package.

The **GBA** bezel uses the existing [*Perfect GBA (no grid)* artwork by mugwomp93](https://github.com/chrizzo-hb/knulli-bezels/blob/75aa66c41548ebaa95f31d260d47eea2baab9d8a/default-knulli/systems/gba-4_3.png), provided by the KNULLI Bezels collection under **CC BY-SA 4.0**. The artwork is resized to 640×480; the build checks that its transparency mask exactly matches Slot's original SP bezel. See `System/licenses/gba-original-bezel-credits.txt` for attribution and license details. The SP PNG remains unchanged, and the GBA Bezel selection persists in `Config/slot.state`.

## Compatibility and limitations

- **GB, GBC and GBA only.** No NES, SNES, N64, PS1 or other consoles.
- **Not an H700 build.** The Miyoo ARMv7 binaries, patches, emulator versions and file layouts are distinct from the Anbernic H700 ARM64 package. Never mix ZIPs or use the H700 updater for Miyoo.
- **No H700 Authentic or Pocket/SGB LCD shaders**, reflections or GPU visual effects. Shaders are intentionally absent; core palettes/color settings are still independent of shader rendering.
- **Aspect Fit is fractional on the 640×480 panel.** Some physical pixel columns/rows may have uneven widths; there is no shader smoothing or pixel simulation to hide this.
- **No online updater or Wi-Fi requirement.** Transfer release ZIPs using a computer/SD-card reader. Back up data before installing.
- **Not all device and firmware combinations are physically tested.** The user's OnionOS Miyoo setup is verified; the stock autoboot route, Mini Plus and Mini Flip setups may need device-specific verification. Official OnionOS supports the original Mini / Mini Plus, **not Mini Flip**. Allium compatibility is limited to supported app-launch arrangements, not OnionOS autoboot.
- **OS sleep, shutdown and theme behavior are firmware-dependent.** OnionOS's native timer can act before Slot's menu timers, and the active theme determines which boot/shutdown artwork is available. Slot does not modify any theme files.
- **Emulator performance is game-specific.** Save states are not interchangeable between mGBA and gpSP, and old Gambatte states are not compatible with the remaining cores. Back up before changing core selection.
- **No ROMs or proprietary BIOS files** are included.

## Source and reproducibility

The [Miyoo sources and patch scripts](https://github.com/Sinastrax/select-slot/tree/main/miyoo) build the selected Slot 1.8.1 ARMv7 port and verify the renderer, menu timers, scaling persistence and OS-specific startup packages. Each release includes a SHA-256 checksum. Build/package verification does not substitute for testing on every hardware model.

[select. slot. Miyoo Ver. 3 release](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver3) · [Original Slot](https://github.com/slot-cfw/slot) · [Miyoo port](https://github.com/deanmarano/slot-miyoo)
