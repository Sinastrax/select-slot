# select. slot. 1.16.0 Ver. 27

## Changes since Ver. 26

- **Automatic RetroAchievements TOML migration.** On the first boot after updating, the firmware reads and interprets the existing `Config/retroachievements.toml` and rewrites it once in a normalized, supported format—no manual editing required.
- **Account data preserved.** The migration retains your username, login token, pending password, enabled/disabled setting, on-device login marker, and other compatible configuration values.
- **Verified, safe write.** The rewritten data is parsed again and checked for consistency before an atomic write; if the original file is unreadable or malformed, it is not overwritten. Future-schema files are left alone, and already-migrated files are not rewritten.
- **Achievement progress untouched.** Saved game data, offline achievements, unlock caches and account history under `Saves/RetroAchievements` are never modified by the migration.
- **Regression tests.** Tests cover preservation of login information and extra settings, single-run migration, malformed-file protection, future schema and saved unlock isolation.

Existing **Tools → RetroAchievements** menu login, masked password entry and **restart required** behavior are unchanged. Migration normalizes configuration; it cannot repair a genuinely read-only or damaged SD card. TOML comments may not survive normalization, but meaningful setting values are preserved.

H700 firmware. Physical-device verification of the reported login-save error remains necessary.
