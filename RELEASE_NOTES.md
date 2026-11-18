# select. slot. 1.16.0 Ver. 32

## In-game RetroAchievements stability

- **Freeze prevention:** the Achievements screen renders only the six visible rows at a time. Sorting with X, scrolling and receiving new achievement data reuse existing GPU texture handles instead of allocating textures for an entire large game set on every interaction.
- **Badge and description reuse:** reusable texture slots remain allocated even when an achievement temporarily has no downloaded badge. Switching games and repeatedly reopening the page cannot grow the texture cache with each interaction.
- **Repeated Y presses:** requests to refresh the active ROM and RetroAchievements session are coalesced for a short interval, preventing bursts of repeated ROM hashing and online lookups.
- **Tests:** verify that achievement lists up to 500 entries remain restricted to six visible rows, including the current selection.

**Unchanged:** all ROMs, in-game saves, RetroAchievements offline awards and existing unlock history, mGBA, Wi-Fi behavior, shaders, scaling, device detection, and the original manifest-based `System/` updater. Existing save milestones do not become retroactive achievements.

### Compatibility
Anbernic H700 devices (RG34XXSP, RG35XXSP, RG35XX H). No ROMs or BIOS files included.
