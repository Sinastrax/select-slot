# select. slot. 1.16.0 Ver. 33

## RetroAchievements: accurate unlock tracking

- **Rich Presence isolation:** Optional activity text can no longer cancel an otherwise valid achievement award or reset the game's achievement state when it reads unavailable RAM.
- **Safety preserved:** An invalid memory read during the achievement evaluation itself still suppresses that frame's awards rather than treating unknown RAM as zero.
- **Targeted diagnostics:** Logs report the first occurrence per game of invalid achievement memory reads, missing memory required by a definition, invalid Rich Presence reads, or an overloaded frame queue. This helps distinguish a connected RetroAchievements session from actually evaluating game RAM.
- **Regression tests:** a legitimate achievement must trigger even when optional Rich Presence uses an inaccessible RAM address; an achievement using unavailable RAM must not be falsely awarded.

Existing ROMs, saves, offline unlock history, RetroAchievements account settings, game detection, shaders, scaling, power features, device nicknames, Wi-Fi behavior and original manifest-based System updater are unchanged.

**Note:** A previously missed in-game milestone will not be fabricated or silently reawarded. The fix addresses a verified isolation defect, but individual games still require real-device validation.

### Compatibility
Anbernic H700 devices (RG34XXSP, RG35XXSP, RG35XX H). No ROMs or BIOS files included.
