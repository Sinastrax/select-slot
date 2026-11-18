# select. slot. 1.8.1 Ver. 3 — Miyoo

This release removes the unnecessary **Gambatte** emulator from the Miyoo Mini family build. It keeps the proven mGBA + gpSP setup and otherwise preserves Ver. 2's behavior.

### Changes
- **Game Boy / Game Boy Color:** mGBA is now the only available emulator core.
- **Game Boy Advance:** gpSP remains the default, with mGBA as the existing alternative.
- **Legacy selections:** a per-game `gambatte` core selection now resolves to mGBA instead of failing. ROMs, battery saves, color/palette choices, scaling and other preferences are not deleted or reset.
- **Smaller build:** Gambatte is no longer downloaded, compiled, listed in the core picker or included as a binary/source archive.
- **Preserved:** original 0–9 Miyoo brightness, OnionOS/BMO theme sleep and shutdown, autostart installer choices, unfiltered rendering, independent scaling, and original GBA/GBA SP bezels.

### Update notes
- The three packages are distinct: **OnionOS autoboot**, **genuine stock firmware autoboot**, and **app-only**. Extract *one* suitable ZIP to the SD-card root, after backing up saves/configuration. **Do not use the stock firmware package on OnionOS.**
- Existing Gambatte save states **cannot be loaded by mGBA**. For continuity use battery saves made by the game itself.
- An old Gambatte binary/source archive may remain on an SD card updated by overlaying the new release; it is no longer used and can be removed manually after a backup. The installer does not delete files automatically.
- No online updater or additional emulated systems are included.

**Hardware verification:** automated ARMv7 build and package tests are separate from testing on the user's Miyoo Mini; the latter remains a final confirmation.

[Installation guide](https://github.com/Sinastrax/select-slot/blob/main/miyoo/INSTALL.md) · [Project README](https://github.com/Sinastrax/select-slot)
