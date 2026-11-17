# Custom slot. 1.8.1 Ver. 2 — Miyoo

This is an **experimental ARMv7 app build** for the **original Miyoo Mini**, Miyoo Mini Plus, and Miyoo Mini Flip. It is **not H700 firmware** and does not replace the device OS.

## Installation

1. Back up the Miyoo SD card, especially any existing Slot saves, states and settings.
2. Download the `custom-slot-1.8.1-ver2-miyoo.zip` artifact from the **Build Custom slot Miyoo preview** GitHub Actions workflow, once it has passed.
3. Extract the **contents** of the ZIP at the SD-card root. The card should contain `System/slot`, `App/Slot/` and `Apps/slot.pak/` directly. Do not put them inside another folder.
4. Reinsert the card and reboot. Launch **Custom slot** from the Apps/App section of your existing launcher. Stock, Onion and Allium layouts are included in the base port.
5. Add extracted, uncompressed ROMs under `Games/GB/`, `Games/GBC/` and `Games/GBA/`. Supply your legally obtained GBA BIOS as `BIOS/gba_bios.bin`; neither ROMs nor BIOS images are distributed.

**Important:** This build uses the same `System/slot` path as Dean Marano's original port. Installing it **replaces that port's executable**, but does not reflash the firmware. It is not a side-by-side app install. The H700 release, which uses its own SD2 arrangement, must never be extracted onto a Miyoo card.

## Version and verified scope

- **Base:** [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo), pinned to commit `d096bdb87f25f3aba62de6b40ef859b61d841e43`.
- **Slot upstream:** `v1.8.1`, pinned by the Miyoo port; our format is **Custom slot. 1.8.1 Ver. 2**.
- **Device architecture:** ARMv7 with software framebuffer rendering, not the H700/aarch64 GPU backend.
- **Upstream testing:** The original Miyoo Mini on OnionOS 4.3.1, plus Mini Plus and Flip, were reported working by the port author. **This Custom slot variant is not hardware-tested.**
- **GB and GBC default core:** Gambatte, custom-built for the same ARMv7 hard-float toolchain. Existing explicit per-game mGBA selections may still load; mGBA is not the recommended core here.
- **GBA default core:** gpSP with its ARM dynamic recompiler. mGBA remains in the original GBA core picker for compatibility.
- **Scaling in game:** Pause / Quick Menu → Settings → Screen → **Scaling**. Options are Original, Integer, Aspect Fit, Fill/Crop, and Full Stretch, saved per game in `Config/video_mode.txt`. GB/GBC shoulder buttons cycle these modes when not remapped to a game action. GBA uses the menu, because L/R are gameplay buttons. Original 640×480 Miyoo GB integer fit is 3× = 480×432; GBA integer fit is 2× = 480×320.
- **Resume settings:** Separate **Resume on Power On** (default On) and **Resume on Insert** (default On), under Gameplay. Turning power-on resume Off keeps the previously selected cartridge on the shelf without launching it; manual insertion still has its own setting. Older `auto_load` values initialize the power-on setting.
- **Menu inactivity:** Under General, **Menu Screen Off** defaults to 3 min and **Menu Power Off** to 15 min. Each accepts Off, 1, 3, 5, 10, 15 or 30 minutes. Gameplay is excluded; the first button press after screen blanking wakes the backlight rather than triggering a menu item. Test actual power handling on your device.
- **Still not implemented:** Your H700 **Authentic** GB/GBC/GBA screen simulation (DMG/Pocket/Light/GBC/GBA, Pocket Color), independent Authentic display correction and ghosting. Existing LCD3x is **not the same as Authentic**. The Miyoo renderer is software-only; no GLSL H700 shaders were copied. SGB and mGBA SGB modes are **intentionally excluded**. H700-only hotkeys and OTA remain excluded.
- **Original Miyoo Mini has no Wi-Fi:** The H700 online updater therefore cannot simply be reused on it. Updating this preview requires copying the ZIP to the SD card.

This is an **experimental preview**. GitHub Actions successfully cross-compiled and packaged the core, scaling, and system changes, but no Custom slot Miyoo hardware or frame-time test has been performed. Do not describe the Authentic shader work as completed.

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
git clone https://github.com/Sinastrax/slot-rgsp-mod.git
cd slot-rgsp-mod
git checkout feature/custom-slot-miyoo-mini
bash miyoo/build.sh
```

The script clones the pinned Miyoo port, keeps its upstream submodule and hardware patches, adds the Miyoo-compatible custom patch, builds using that port's Docker ARMv7 toolchain and produces a separate ZIP + SHA-256 checksum under `.build/miyoo/`. It does not modify the H700 patches or build workflow.

## Credits and source obligations

- Original Slot by [Brandon Kowalski / slot-cfw](https://github.com/slot-cfw/slot).
- Miyoo hardware port by [deanmarano](https://github.com/deanmarano/slot-miyoo), including its CPU rasterizer, hardware support, toolchain and launcher.
- Additional Custom slot changes by [Sinastrax](https://github.com/Sinastrax/slot-rgsp-mod).

This work inherits Slot's **GPL-3.0-or-later** obligations. Distributed ZIPs preserve upstream licence and core-source materials. No proprietary ROMs or BIOS files are included.
