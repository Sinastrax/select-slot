# select. slot. 1.8.1 Ver. 5 — Miyoo

## Fix: Restart now relaunches Slot instead of turning off the original Mini

Ver. 4's Restart menu option called the upstream Linux hardware `reboot` path. On the original Miyoo Mini this can **power off the device rather than restart it**.

Ver. 5 changes **both** the Settings → Restart entry and the existing About-screen X restart shortcut to relaunch select. slot. itself inside the running firmware session:

- Save/state writer is settled before restarting, as before.
- Replaces the current Slot process using the native ARMv7 dynamic loader (`/lib/ld-linux-armhf.so.3`) and the same `System/slot` binary. It does **not** launch a second concurrent Slot.
- Keeps the existing launcher environment, OnionOS services, theme, keymon, audio and framebuffer ownership model; does not touch OS power, suspend or shutdown scripts.
- Open descriptors are marked close-on-exec so the relaunched frontend initializes devices afresh. Existing redirected logs remain available.
- If relaunch is unavailable, records an error and returns control to the launcher instead of powering down the device.

The visible menu label remains **Restart**. On Miyoo, it now refers to restarting the Slot frontend—not rebooting the device hardware.

## Retained from Ver. 4

- Universal menu scrolling, including Gameplay settings
- High-contrast clock and battery text in the main settings and in-game menus
- Version shown in About (now Ver. 5)
- GB/GBC: mGBA only; GBA: gpSP default or mGBA alternative
- Existing scaling, palette preferences, GBA/GBA SP bezels
- Native OnionOS theme/sleep/shutdown handling, BMO standby, 0–9 brightness, shader-free rendering
- Original SD-card app-only, OnionOS autoboot and stock-autoboot install choices; no Wi-Fi or OTA required

**Installation:** Back up your SD card and extract one ZIP appropriate for your installed firmware to the card root. On OnionOS use the OnionOS autoboot ZIP, never the stock firmware autoboot ZIP.

**Validation:** ARMv7 firmware compilation and package verification check the new restart path. Physical Miyoo Mini testing remains necessary to verify the end-to-end behavior.

[Miyoo installation guide](https://github.com/Sinastrax/select-slot/blob/main/miyoo/INSTALL.md) · [Project README](https://github.com/Sinastrax/select-slot)
