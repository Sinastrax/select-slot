# more. slot.

**A separate Slot build for adding systems beyond the original select.slot. versions.**

`more. slot.` is the separate UnsloT-based branch for adding systems beyond select.slot. Test 5 was an incomplete Game Gear evaluation build. Test 6 is being prepared with the select.slot feature port; its implementation and hardware package are still under review. Track exact parity in [the feature parity tracker](docs/FEATURE_PARITY.md). It does not change the existing select.slot. or Miyoo builds.

The Miyoo Mini port remains available as [select.slot. 1.8.1 Ver. 12](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver12).

## Current work

| System | Core | Controls | Display options | Hardware status |
| --- | --- | --- | --- | --- |
| Sega Game Gear (`.gg`) | PicoDrive | D-pad, A, B, Select, Start, turbo | Per-system shader, scale, overlay, bezel, frame blending | Hardware confirmation pending |

The default scale is **Fit**. The display menu keeps Game Gear settings separate from GB, GBC, and GBA settings. Game Gear games use a separate cartridge silhouette, label position, shell branding, and clear-shell shadow/backing on the shelf.

The first integration targets Anbernic H700 devices. It does not add Miyoo support. Game Gear offers its own Authentic LCD profile with optional color correction and frame blending. Custom bezels go in Bezels/GG.

## Testing and releases

The H700 workflow builds pull requests without publishing. Test 4 established the separate More.slot OTA feed; each later test release advances that feed through **Settings → System → Check for Updates**. A verified merge to `more-slot` publishes a prerelease and updates only the `more-slot` OTA manifest. It does not mark the build as latest or change the stable select.slot release or updater feed. See [the test OTA notes](MORE_OTA.md).

The first build is intended primarily for the Anbernic RG35XX-H. No device is marked tested until you report testing results. PicoDrive's license prohibits commercial use; each downloadable build includes the pinned source and required notices.

## Port status

Test 5 was an incomplete Game Gear evaluation build. Test 6 remains an unpublished candidate until the parity tracker’s release gate is cleared and the H700 package passes GitHub Actions. The More.slot OTA feed can only update more.slot test builds; select.slot stable releases remain separate.

## Credits

- [Slot](https://github.com/slot-cfw/slot), by Brandon Kowalski
- [pvaibhav's H700 Slot fork](https://github.com/pvaibhav/slot)
- [PicoDrive libretro core](https://github.com/libretro/picodrive), plus its separately pinned build dependencies

The included source and core notices are authoritative for the bundled emulator's terms. This project does not include game ROMs or proprietary BIOS files.
