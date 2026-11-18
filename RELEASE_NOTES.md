# select. slot. 1.16.0 Ver. 26

## Changes since Ver. 25

- **Fix RetroAchievements login saving when an existing configuration contains additional settings.** The on-device login editor under **Tools → RetroAchievements** now accepts and preserves compatible additional TOML fields instead of rejecting them.
- **Accurate error messages.** Invalid existing configurations are identified as such, rather than presenting every failure as an SD-card problem. Missing or unreadable files and genuine write errors are distinguished; only write failures advise checking the card. The device log records the underlying filesystem error without exposing credentials.
- **No destructive recovery.** Invalid TOML configurations are never silently replaced, keeping existing user settings intact.
- **Tests.** Added coverage for existing extra fields, invalid TOML and genuine file-access errors; existing on-device login tests remain enabled.

The on-device login **still requires a Slot restart** before the new credentials take effect. No changes to the single Wi-Fi On/Off switch, achievements, games, graphics, shaders, bezels, scaling or emulation cores.

H700 firmware; hardware retesting required to confirm the original user's save failure is resolved.
