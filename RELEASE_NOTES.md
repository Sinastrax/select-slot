# select. slot. 1.16.0 Ver. 29

## RetroAchievements improvements

- **Tools → RetroAchievements:** dedicated Account, Sync Status, Prepare Library, Retry Failed Games, and Background Index controls.
- **Game-first activation:** the currently launched game's achievements remain available regardless of full-library indexing.
- **Optional full-library indexing:** automatic library-wide preparation is disabled by default; switch on Background Index or use Prepare Library to run it manually.
- **Regional ROMs without achievements:** confirmed unmatched hashes are cached as valid results, marked ready and not repeatedly queried until the cache expires.
- **Quiet background recovery:** unreadable ROMs are tracked individually for Retry Failed Games rather than leaving a persistent orange warning for the entire shelf.
- **Badge download retry:** a temporary badge failure no longer makes the global sync state an actionable error.
- **Respect handheld use:** background ROM hashing and badge prefetch pause during gameplay; new network work pauses while the lid is closed.
- **Account and achievements preserved:** existing credentials, authenticated tokens, unlock history and offline caches are not reset by this update.

The sync-status screen distinguishes ready, syncing, offline/retrying, and action-required states and shows the count of failed ROMs.

**H700 only** (RG34XXSP, RG35XXSP, RG35XX H). No changes to Miyoo firmware, shaders, emulators, scaling, or screen settings.

### Notes
Automatic background indexing is now opt-in. Existing caches remain available. RetroAchievements server acceptance of offline unlocks is not guaranteed; launch an online session for supported games.

