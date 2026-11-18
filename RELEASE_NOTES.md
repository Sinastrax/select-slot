# select. slot. 1.16.0 Ver. 34

## RetroAchievements: every-frame tracking during fast-forward

- **Every emulated frame is evaluated, including fast-forward frames that are never shown on screen.** Achievements are checked immediately after the emulator advances, using its current memory; they no longer depend on an eight-frame RAM-snapshot queue that can overflow and silently lose short-lived conditions.
- **Awards remain asynchronous and durable.** Only triggered achievement events are sent to the background worker. Existing offline award storage, subsequent server submission, and achievement notifications remain separate from emulator execution.
- **Lifecycle safety:** game loads, resets, manual save-state loads, and link-play transitions synchronize or reset the runtime as appropriate. Game saves, ROMs, account configuration, and previous unlock records are unchanged.
- **Server warning filtering:** an injected zero-point 'Warning: Unknown Emulator' entry is no longer displayed as a real game achievement, matching official rcheevos client treatment. This does not by itself solve Softcore tracking.
- **Regression coverage:** test a single qualifying frame in a 360-frame fast-forward burst and ensure the unlock reaches the offline ledger; preserve no-blocking and non-fabricated-award tests.

**Important:** Previously missed achievements are not automatically credited, and functional testing on actual hardware is still required. Fast-forward should no longer cause missing tracking frames; performance remains subject to device testing.

### Compatibility
Anbernic H700 devices (RG34XXSP, RG35XXSP, RG35XX H). No ROMs or BIOS files included.

**Unchanged:** shaders, color correction, per-system scaling, Wi-Fi behavior, firmware branding, device nicknames, and the original manifest-based `System/` update cleanup.
