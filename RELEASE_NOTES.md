# select. slot. 1.16.0 Ver. 31

## Menus and in-game RetroAchievements

- **All-menu scrolling fix:** the main settings menu and every long quick-menu page, including GB/GBC/GBA, gameplay, RomM, shortcuts and the paused game menu, scroll before entering the footer. Original typography and six-row 480p viewport are retained.
- **In-game Achievements → Y Refresh:** force-read the active ROM's true MD5, reconnect to its registered RetroAchievements game, refresh the achievement definitions and unlock state. Keeps the game running, preserves its achievement hit counters, existing save RAM and offline award records.
- **Verified game connection:** show whether the exact ROM is unregistered, cached and offline, connecting, rejected, or has an accepted online session. A failed Rich Presence ping can no longer cancel an otherwise accepted achievement session; it retries separately.
- **Measured achievements:** show actual partial progress from rcheevos for achievements that define measurable goals. Already-completed milestones from an old save are not retroactively awarded.
- **Regression tests:** viewport safety for all pages, ROM rehash even against stale cached fingerprints, refresh save safety, and successful session reporting despite a failed presence ping.

**Unchanged:** existing manifest-based `System/` update cleanup, Wi-Fi behavior during play, mGBA performance governor, supported cores, shaders, color correction, scaling, bezels, credentials and existing save/RetroAchievements files.

### Compatibility
Anbernic H700 devices (RG34XXSP, RG35XXSP, RG35XX H). Full OTA package remains compatible; no ROMs or BIOS files included.
