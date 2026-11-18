# select. slot. 1.16.0 Ver. 35

## RetroAchievements: correct handling of indirect memory reads

The original bug was identified from an actual H700 Pokémon Smaragd-Edition (German) session log. The game launched through mGBA, frame-by-frame tracking ran (including fast-forward), but the achievement evaluator reported **"out-of-range achievement RAM read; award suppressed for safety."**

- **Root cause:** select. slot.'s custom rcheevos wrapper reset *all* achievement progress when a dynamic pointer-chain read temporarily left mapped RAM. Official RetroAchievements `rc_client_peek` treats an unavailable pointer-chain read as zero without resetting unrelated achievements.
- **Fix:** after validating static achievement memory addresses, an unmapped indirect pointer-chain lookup follows the official client behavior. Other achievements retain hit counts and can unlock normally.
- **Safety:** static memory reads are still checked against real emulated RAM. A multi-byte direct read crossing into unavailable memory still fails closed; unsupported direct addresses are not treated as zero.
- **Regression tests:** an independent achievement must trigger alongside an invalid pointer chain; direct invalid reads must not fabricate achievements; the legacy Game Boy pointer-hole test now matches official `rc_client` semantics.
- **Diagnostics:** the first unavailable indirect address is logged once per game, and routine filtered server compatibility warnings no longer flood `slot.log`.

Ver. 34's every-emulated-frame tracking, including fast-forward, remains in place. No existing ROMs, saves, shader settings, online account details, game progress, hardware nicknames, or System manifest behavior are changed. Previously missed milestones are not automatically backdated.

**Validation:** automated CI and build results are separate from real-device confirmation. Test a *new* eligible event in Smaragd after installing. An existing milestone completed while tracking was broken cannot necessarily be awarded retroactively.

### Compatibility
Anbernic H700 devices (RG34XXSP, RG35XXSP, RG35XX H). No ROMs or BIOS files included.

Implementation references: [official rcheevos rc_client source](https://github.com/RetroAchievements/rcheevos/blob/master/src/rc_client.c), [select. slot. source](https://github.com/Sinastrax/select-slot).
