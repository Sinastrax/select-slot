# Custom slot. 1.8.1 Ver. 10 — Miyoo

This is an **experimental ARMv7 app build** for the **original Miyoo Mini**, Miyoo Mini Plus, and Miyoo Mini Flip. It is **not H700 firmware** and does not replace the device OS.

## Installation

1. Back up the Miyoo SD card, especially any existing Slot saves, states and settings.
2. Download the `custom-slot-1.8.1-ver10-miyoo.zip` artifact from the **Build Custom slot Miyoo preview** GitHub Actions workflow, once it has passed.
3. Extract the **contents** of the ZIP at the SD-card root. The card should contain `System/slot`, `App/Slot/` and `Apps/slot.pak/` directly. Do not put them inside another folder.
4. Reinsert the card and reboot. Launch **Custom slot** from the Apps/App section of your existing launcher. Stock, Onion and Allium layouts are included in the base port.
5. Add extracted, uncompressed ROMs under `Games/GB/`, `Games/GBC/` and `Games/GBA/`. Supply your legally obtained GBA BIOS as `BIOS/gba_bios.bin`; neither ROMs nor BIOS images are distributed.

**Important:** This build uses the same `System/slot` path as Dean Marano's original port. Installing it **replaces that port's executable**, but does not reflash the firmware. It is not a side-by-side app install. The H700 release, which uses its own SD2 arrangement, must never be extracted onto a Miyoo card.

## Version and verified scope

- **Base:** [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo), pinned to commit `d096bdb87f25f3aba62de6b40ef859b61d841e43`.
- **Slot upstream:** `v1.8.1`, pinned by the Miyoo port; our format is **Custom slot. 1.8.1 Ver. 10**.
- **Device architecture:** ARMv7 with software framebuffer rendering, not the H700/aarch64 GPU backend.
- **Upstream testing:** The original Miyoo Mini on OnionOS 4.3.1, plus Mini Plus and Flip, were reported working by the port author. **This Custom slot variant is not hardware-tested.**
- **GB and GBC default core:** Gambatte, custom-built for the same ARMv7 hard-float toolchain. Existing explicit per-game mGBA selections may still load; mGBA is not the recommended core here.
- **GBA default core:** gpSP with its ARM dynamic recompiler. mGBA remains in the original GBA core picker for compatibility.
- **Scaling in game:** Pause / Quick Menu → Settings → Screen → **Scaling**. Options are Original, Integer, Aspect Fit, Fill/Crop, and Full Stretch, saved per game in `Config/video_mode.txt`. GB/GBC shoulder buttons cycle these modes when not remapped to a game action. GBA uses the menu, because L/R are gameplay buttons. Original 640×480 Miyoo GB integer fit is 3× = 480×432; GBA integer fit is 2× = 480×320.
- **Resume settings:** Separate **Resume on Power On** (default On) and **Resume on Insert** (default On), under Gameplay. Turning power-on resume Off keeps the previously selected cartridge on the shelf without launching it; manual insertion still has its own setting. Older `auto_load` values initialize the power-on setting.
- **Menu inactivity:** Under General, **Menu Screen Off** defaults to 3 min and **Menu Power Off** to 15 min. Each accepts Off, 1, 3, 5, 10, 15 or 30 minutes. Gameplay is excluded; the first button press after screen blanking wakes the backlight rather than triggering a menu item. Test actual power handling on your device.
- **Still not implemented:** Your H700 **Authentic** GB/GBC/GBA screen simulation (DMG/Pocket/Light/GBC/GBA, Pocket Color), independent Authentic display correction and ghosting. Existing LCD3x is **not the same as Authentic**. The Miyoo renderer is software-only; no GLSL H700 shaders were copied. SGB and mGBA SGB modes are **intentionally excluded**. H700-only hotkeys and OTA remain excluded.
- **Original Miyoo Mini has no Wi-Fi:** The H700 online updater therefore cannot simply be reused on it. Updating this preview requires copying the ZIP to the SD card.

This is an **experimental preview**. Earlier versions cross-compiled, but Ver. 9 has not yet been tested on physical Miyoo hardware. Do not describe the Authentic shader work as completed.

## Ver. 10 — remove Gambatte's forced fast display dimming

The custom Gambatte option path forced `gambatte_gbc_color_correction_mode=fast`, a documented mode that darkens and desaturates colors when GBC correction is enabled. This release restores the core's **accurate** mode, without forcing color correction on; `Colour Correction: Off` stays uncorrected. The independent Gambatte dark-filter level is explicitly held at 0. It does not alter PWM/backlight, which has the original Miyoo port's range (max 112; OnionOS normally reaches about 100 with an 800 ns period), nor does it alter the BMO theme or LCD3x renderer. This is a focused image-processing correction, not a proven fix for physical backlight dimness.

## Ver. 9 — one-time recovery of brightness overwritten by Ver. 5

Ver. 5 imported OnionOS brightness into Slot's `brightness` setting (whose range is different). The modified value could be saved in `Config/slot.state`. Ver. 8 restored the original brightness initialization code, but continued to read the changed saved value.

Ver. 9 restores the original Miyoo Slot default **5/9** on the **first OnionOS launch only**, and **only if** Slot's saved brightness is below 5. It saves that repaired level and creates a small one-time marker `Config/.select-slot-miyoo-brightness-restored`. From then on, any brightness setting selected in Slot is respected, including lower levels. Existing saved settings 5–9, stock firmware and Allium remain unchanged. No screen shaders, brightness tables, framebuffer orientation, Onion files or BMO assets are modified. This directly addresses the persistent-state regression without requiring diagnostics.

The Gambatte integration also now stops sending mGBA-only palette commands during the loading/ready path, and skips an unsupported Gambatte frameskip option. These fixes address actual warnings in the earlier logs, but **have not been demonstrated to resolve screen brightness on hardware**.

## Ver. 8 — targeted rollback to known-good Miyoo behavior

The user's original Dean Miyoo Slot was bright; the darkness began after the Custom slot additions. This version **reverts the fork's brightness import** and calls the original Miyoo backlight routine with Slot's own saved brightness. The original PWM table is not modified. The additional menu-only screen-off/power-off timers are bypassed **when Onion keymon is managing the display**, so that fork-specific timer cannot dim the entire screen and fight Onion's sleep routine. The controls remain implemented for non-Onion use.

When Onion keymon is running, POWER is handled by Onion. The fork no longer runs an extra **blocking state flush** on POWER-down, which could race Onion's process suspension. Slot's normal periodic save behavior remains. **OnionOS Power single press must be configured as Standby rather than Shutdown** in Apps → Tweaks → Button shortcuts.

For **BMO by forevertuesday**, OnionOS itself continues using the selected theme's `skin/extra/bootScreen.png` on boot and `Screen_Off.png` / `Screen_Off_Save.png` during shutdown. The theme does **not** provide separate sleep/wake animation assets; Onion keymon's standby is primarily backlight and process suspension. We do not replace theme artwork or modify Onion's daemon.

Build validation does not establish a successful hardware fix.

## Ver. 7 — brightness and sleep investigation

Dean's original Miyoo Slot had normal brightness on the user's physical Mini. Darkening began after the Custom slot changes, so **do not change Dean's upstream PWM calibration** without device measurements.

The previous Onion-specific brightness and POWER changes were never enabled by their original launcher condition: the script checked for `.tmp_update/onionVersion/version.txt`, which is not part of the official OnionOS source tree. Ver. 7 checks `.tmp_update/runtime.sh` instead, preserving Onion's own runtime and keymon. The original 180° framebuffer rotation has also been restored; the 0° change caused a real upside-down screen regression.

**Important:** The custom menu screen-off timer is also an added backlight-control path. Brightness and POWER behavior still need original-Mini testing; a successful cross-build does not prove either is fixed.
## OnionOS BMO theme, sleep and screen behavior (Ver. 4)

The verified Onion theme repository includes **BMO by forevertuesday**, **BMO Noire by forevertuesday**, and **BMO by OjninJo**. Each theme provides `skin/extra/bootScreen.png`, `Screen_Off.png`, and `Screen_Off_Save.png`; none provides an independent Sleep/Wake asset. All themes remain untouched on the SD card.

| Event | Behavior when Onion keymon is running |
|---|---|
| Boot | Onion itself renders your current BMO `bootScreen.png`, before the optional Custom slot startup hook |
| POWER tap to sleep | **Onion keymon exclusively** suspends Slot, controls the display/backlight and restores the session; Slot does **not** run an additional synchronous save flush or enter a conflicting doze on POWER-down |
| POWER tap to wake | **Onion keymon exclusively** restores display and resumes Slot; no additional Slot redraw of a boot image |
| Shutdown started by Slot | Slot finishes saves, then calls Onion's existing `bootScreen End_Save` renderer to display the current theme's `Screen_Off_Save.png` |
| Onion-managed forced/long-press shutdown | Onion handles it; Slot does not duplicate the transition |

**There are no built-in themed sleep/wake splash animations in Onion's `keymon`.** Previous Ver. 3 attempted to draw them from Slot simultaneously with Onion's suspend logic; that was unsafe and could leave the screen or input in a bad state. Ver. 4 prioritizes a working POWER sleep/wake over an unverified BMO animation. To get BMO artwork **on** sleep/wake when Onion owns the button, a separately tested Onion keymon integration is necessary; the theme files themselves cannot implement it.

**Display orientation:** Ver. 5 incorrectly selected 0° on the user's original Mini. Ver. 7 restores the original 180° setting.

**Historical note (Ver. 5, reverted in Ver. 8):** An attempt to synchronize OnionOS brightness (0–10) with Slot's saved level (0–9) introduced a persistent-state regression. Ver. 9 repairs saved values below 5 once, while keeping the original Miyoo PWM calibration.


`.tmp_update/runtime.sh`, Onion's theme, and its `keymon` executable are **not modified**. The optional `.tmp_update/config/.skip-custom-slot-splashes` flag disables only Slot-triggered shutdown artwork, not Onion's normal native boot display.

## Boot directly into Custom slot on OnionOS 4.3

**Optional, not enabled by the ZIP.** This uses Onion's documented startup-script hook and preserves OnionOS and its existing `.tmp_update/runtime.sh`. It has been inspected against Onion 4.3's startup code but **has not been device-tested with Custom slot**.

1. Install and manually launch Custom slot once to check that it works, especially audio.
2. In Onion, go to **Apps → Tweaks → System → Startup → Auto-resume last game → Off**, avoiding competition with Onion's existing last-game resume.
3. On the SD card, copy `System/autoboot/onion-startup.sh` to `.tmp_update/startup/custom-slot.sh`. Create the `.tmp_update/startup` folder if it is absent. Keep the original file as the reusable template.
4. Restart. Onion initializes its screen/audio/system, launches Custom slot via its standard wrapper and waits for it to exit. When Slot exits, Onion's normal MainUI startup continues.

**Do not copy the stock-firmware** `System/autoboot/runtime.sh` **over Onion's** `.tmp_update/runtime.sh`. That would replace Onion's boot manager and can prevent the OS from loading normally.

**Disable autoboot:** power off, put the card in a PC, delete or rename only `.tmp_update/startup/custom-slot.sh`. Alternatively, create an empty `.tmp_update/config/.skip-custom-slot-autoboot` file; remove it to restore autoboot. Neither action deletes saves or changes the firmware.

**Stock Miyoo firmware** instead supports the original port's separate `System/autoboot/runtime.sh` approach; that file is **not for OnionOS or Allium**.

## Building

Requires Git, Docker, go-task, Python 3 and standard ZIP tools:

```bash
git clone https://github.com/Sinastrax/select-slot.git
cd select-slot
git checkout feature/custom-slot-miyoo-mini
bash miyoo/build.sh
```

The script clones the pinned Miyoo port, keeps its upstream submodule and hardware patches, adds the Miyoo-compatible custom patch, builds using that port's Docker ARMv7 toolchain and produces a separate ZIP + SHA-256 checksum under `.build/miyoo/`. It does not modify the H700 patches or build workflow.

## Credits and source obligations

- Original Slot by [Brandon Kowalski / slot-cfw](https://github.com/slot-cfw/slot).
- Miyoo hardware port by [deanmarano](https://github.com/deanmarano/slot-miyoo), including its CPU rasterizer, hardware support, toolchain and launcher.
- Additional Custom slot changes by [Sinastrax](https://github.com/Sinastrax/slot-rgsp-mod).

This work inherits Slot's **GPL-3.0-or-later** obligations. Distributed ZIPs preserve upstream licence and core-source materials. No proprietary ROMs or BIOS files are included.
