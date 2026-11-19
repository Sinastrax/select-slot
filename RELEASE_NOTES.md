# select. slot. 1.16.0 Ver. 36 — H700 maintenance

A maintenance release of the Anbernic H700 firmware, based on the **user-confirmed Ver. 35 behavior**. No emulator, shader, RetroAchievements, menu or data-format feature was intentionally changed.

## What changed

- **Reproducible, auditable builds:** extracted the complete historical H700 upstream merge/patch sequence from an oversized GitHub Actions YAML step into `.github/scripts/h700-prepare.sh`. The source archives, ordered patches and all Ver. 35 transformations remain in exactly the same order.
- **Fail-closed release checks:** a new source contract verifies pinned upstream versions, every referenced patch tool, dependency-sensitive shader/RA patch ordering, package checksums and expected regression tests before building firmware.
- **Single safe publisher:** retired the duplicate post-build and manual release publishers and the obsolete release-curation workflow. The latter could otherwise delete later confirmed releases; an older publisher could force-move tags. The remaining publisher creates new releases only after a successful verified build, never overwrites an existing public release and explicitly maintains the H700 latest-release channel.
- **CI hygiene:** superseded same-branch H700 builds are cancelled to avoid racing expensive ARM jobs; shell syntax and publisher safety are verified early.
- **Repository cleanup:** removed the no-longer-used experimental WLAN source transformer and the separate old-mGBA comparison workflow. These deletions do not change the working Ver. 23 WLAN patch or the shipped stable older mGBA core.
- **Maintenance documentation:** added [H700_MAINTENANCE.md](https://github.com/Sinastrax/select-slot/blob/main/H700_MAINTENANCE.md) explaining the exact patch sequence, tests, installation boundaries and recommended device checks.

## Preserved from Ver. 35

- Verified RetroAchievements unlock tracking for **German Pokémon Smaragd**, including fast-forward tracking and safe indirect-memory handling, unlock notifications, login and online synchronization.
- GB/GBC Pocket Color and SGB effects, Authentic colors, corrected RG35XX H Fit scaling, GBA Authentic, GBA/GBA SP bezel selection.
- Wi-Fi gameplay retention, link play, per-system scaling, menu viewport scrolling, model nicknames, boot/update branding.
- Existing ROMs, settings, save states, battery saves, offline achievement caches and credentials. **No automatic rescan or migration**.
- The same H700 ARM64 device support and separately downloadable MPL-2.0 source archive for the bundled stable mGBA core.

## Testing

The release workflow must pass the complete H700 Rust test suite, GLES2 shader checks, OTA and ZIP checks, source/branding checks, and archive checksum verification. These automated checks cannot establish real-device screen appearance, Wi-Fi/link play, suspend or firmware upgrade behavior. Keep **Ver. 35** available as the already-confirmed device-tested fallback until this maintenance release is tested on H700 hardware.

**Compatibility:** Anbernic H700 systems such as RG34XXSP, RG35XXSP and RG35XX H. **Not a Miyoo Mini package.** No ROMs or BIOS files included.
