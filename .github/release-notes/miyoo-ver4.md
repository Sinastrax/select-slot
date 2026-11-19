# select. slot. 1.8.1 Ver. 4 — Miyoo

A focused user-interface update on top of the proven Ver. 3 mGBA/gpSP-only Miyoo configuration.

## New in Ver. 4

- **Restart in the settings menu:** a selectable Restart row immediately below About. The Miyoo version of Slot 1.8.1 has no separate System menu; this uses Slot's existing safe restart flow (settles saves and displays the normal restart transition). The original About-screen X-to-Restart action remains available.
- **Universal menu scrolling:** all quick-menu pages now use their available row viewport. Gameplay settings no longer run into the footer, and selected options stay on-screen. The existing three-row in-game Screen panel retains its own viewport.
- **Legible status text:** main settings and in-game menus use their own high-contrast clock and battery-percentage textures. The normal shelf appearance and theme-selected colors remain unchanged.
- **Visible build number:** the existing About sticker displays Version 1.8.1 Ver. 4.

## Retained

- mGBA for GB/GBC, gpSP default / mGBA optional for GBA; no Gambatte.
- Per-system and per-game scaling choices, Game Boy palettes, and original GBA / GBA SP lower bezels.
- Shader-free software rendering, original physical brightness 0–9, original PWM/OnionOS power behavior, themes (including BMO), stand-by and shutdown artwork.
- Offline-only installer, three separate app-only / OnionOS-autoboot / stock-autoboot packages and SHA-256 checksums.
- Existing ROMs, battery saves, saved scaling settings, game settings and state files are not reset.

## Installation

Back up the SD card and extract **one** matching ZIP to its root. The **OnionOS Autoboot** ZIP is for supported OnionOS Mini / Mini Plus configurations. Do not overwrite OnionOS's boot manager with the separate stock-firmware autoboot ZIP.

[Full Miyoo installation guide](https://github.com/Sinastrax/select-slot/blob/main/miyoo/INSTALL.md) · [Miyoo releases](https://github.com/Sinastrax/select-slot/releases)

Automated build/package validation is not a substitute for hardware verification.
