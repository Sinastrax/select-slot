# Custom slot. 1.8.1 Ver. 1 — Miyoo

This is an **experimental ARMv7 app build** for the **original Miyoo Mini**, Miyoo Mini Plus, and Miyoo Mini Flip. It is **not H700 firmware** and does not replace the device OS.

## Installation

1. Back up the Miyoo SD card, especially any existing Slot saves, states and settings.
2. Download the `custom-slot-1.8.1-ver1-miyoo.zip` artifact from the **Build Custom slot Miyoo preview** GitHub Actions workflow, once it has passed.
3. Extract the **contents** of the ZIP at the SD-card root. The card should contain `System/slot`, `App/Slot/` and `Apps/slot.pak/` directly. Do not put them inside another folder.
4. Reinsert the card and reboot. Launch **Custom slot** from the Apps/App section of your existing launcher. Stock, Onion and Allium layouts are included in the base port.
5. Add extracted, uncompressed ROMs under `Games/GB/`, `Games/GBC/` and `Games/GBA/`. Supply your legally obtained GBA BIOS as `BIOS/gba_bios.bin`; neither ROMs nor BIOS images are distributed.

**Important:** This build uses the same `System/slot` path as Dean Marano's original port. Installing it **replaces that port's executable**, but does not reflash the firmware. It is not a side-by-side app install. The H700 release, which uses its own SD2 arrangement, must never be extracted onto a Miyoo card.

## Version and verified scope

- **Base:** [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo), pinned to commit `d096bdb87f25f3aba62de6b40ef859b61d841e43`.
- **Slot upstream:** `v1.8.1`, pinned by the Miyoo port; our format is **Custom slot. 1.8.1 Ver. 1**.
- **Device architecture:** ARMv7 with software framebuffer rendering, not the H700/aarch64 GPU backend.
- **Upstream testing:** The original Miyoo Mini on OnionOS 4.3.1, plus Mini Plus and Flip, were reported working by the port author. **This Custom slot variant is not hardware-tested.**
- **Custom behavior added here:** `Auto Load: Off` no longer automatically inserts the remembered game during startup; it leaves the cartridge selected on the shelf. With `Auto Load: On`, the normal automatic state-loading path remains in place.
- **Not yet ported:** H700-specific Authentic shaders, Pocket Color/SGB modes, Gambatte selection, per-core color correction, new hotkeys, idle timers, separate Resume on Power On / Resume on Insert toggles, and the H700 update menu. They cannot be claimed as working on the CPU-only Miyoo renderer.
- **Original Miyoo Mini has no Wi-Fi:** The H700 online updater therefore cannot simply be reused on it. Updating this preview requires copying the ZIP to the SD card.

This is a preview intended to establish a working baseline before porting more user-facing changes. A successful CI cross-build is not proof of correct on-device visuals, audio, battery reporting or performance.

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
