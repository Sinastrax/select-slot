# select. slot. 1.8.1 Ver. 2 — Miyoo

Miyoo Mini-family release with an additional **GBA** lower bezel, using existing artwork. The previously available GBA SP style and every other feature from Ver. 1 are preserved.

## New: GBA bottom bezel

In **Screen → GBA → Bezel**, choose:

- **GBA SP** — the existing SP lower bezel, unchanged and still the default.
- **GBA** — the original Game Boy Advance lettering on the **same-size** lower bezel.
- **None** — no lower bezel.

The GBA game picture and scaling stay at exactly the same size and position. Both bezel styles use the same pixel-for-pixel 640×480 transparency mask, so the opening, bottom-strip height and screen animation are unchanged.

**Artwork and credit:** The GBA option uses [mugwomp93's existing *Perfect GBA (no grid)*](https://github.com/chrizzo-hb/knulli-bezels/blob/75aa66c41548ebaa95f31d260d47eea2baab9d8a/default-knulli/systems/gba-4_3.png), via [KNULLI Bezels](https://github.com/chrizzo-hb/knulli-bezels), licensed under CC BY-SA 4.0. The original PNG was resized to 640×480, not redrawn. Attribution is included in the `System/licenses` directory.

## Included features

- Game Boy, Game Boy Color and Game Boy Advance; mGBA/Gambatte for GB/GBC, gpSP/mGBA for GBA.
- Independently saved scaling for GB, GBC and GBA, with per-game overrides.
- Original, Integer, Aspect Fit, Fill/Crop and Full Stretch modes.
- Resume settings, menu inactivity controls and OnionOS-compatible standby/shutdown.
- Unfiltered pixels with optional lower bezels. Shader rendering is disabled.
- Offline installation; no Wi-Fi or updater required.

## Pick one installation ZIP

| Package | Supported OS |
| --- | --- |
| `select-slot-1.8.1-ver2-miyoo-onion-autoboot.zip` | OnionOS 4.3+ on compatible Mini / Mini Plus; automatically starts Slot without replacing OnionOS runtime or theme |
| `select-slot-1.8.1-ver2-miyoo-stock-autoboot.zip` | **Genuine stock Miyoo firmware ONLY**; uses `.tmp_update/runtime.sh` for autostart |
| `select-slot-1.8.1-ver2-miyoo.zip` | App-only; does not install an autoboot script |

Back up the SD card, then extract the contents of **only one** matching ZIP to the SD root, including hidden directories.

> [!CAUTION]
> **Never install the stock autoboot ZIP over OnionOS, Allium or another SD-card OS using its own `.tmp_update/runtime.sh`.** Replacing that boot file can break startup.

## Compatibility and limitations

- Supports **GB, GBC, GBA only**, not NES/SNES/PlayStation/N64.
- Miyoo ARMv7 release is not compatible with Anbernic H700 builds, H700 shader features or H700 OTA.
- Display shaders and reflections from H700 are not included; fractional Aspect Fit can show uneven pixel spacing.
- OnionOS power management and active themes may take precedence over the Slot inactivity controls.
- Compatibility testing is limited to the user's Miyoo setup; other hardware / firmware and stock-autoboot combinations are not universally tested.
- No ROMs, BIOS images or personal saves are included. Emulator save states may not transfer between cores.
- SD-card/manual upgrades only.

Each ZIP has a SHA-256 checksum. The compiled firmware and package structure are checked in GitHub Actions; bezel shape identity is additionally verified pixel-for-pixel against the unchanged original SP PNG.

Source and install guide: [Miyoo source](https://github.com/Sinastrax/select-slot/tree/main/miyoo) · [Miyoo installation](https://github.com/Sinastrax/select-slot/blob/main/miyoo/INSTALL.md) · [H700 releases](https://github.com/Sinastrax/select-slot/releases/latest)

The newest Miyoo release replaces the preceding Miyoo release; H700 releases are independent.
