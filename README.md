# more. slot.

**A separate Slot build for adding systems beyond the original select.slot. versions.**

`more. slot.` starts with Sega Game Gear. This branch is based on the prepared select.slot. H700 source and keeps the established shelf, game launch, save, settings, and online-update infrastructure while adding Game Gear as a distinct system. It does not change the existing select.slot. or Miyoo builds.

## Current work

| System | Core | Controls | Display options | Hardware status |
| --- | --- | --- | --- | --- |
| Sega Game Gear (`.gg`) | PicoDrive | D-pad, A, B, Select, Start, turbo | Per-system shader, scale, overlay, bezel, frame blending | Integrated in source; not yet built or tested on hardware |

The default scale is **Fit**. The display menu keeps Game Gear settings separate from GB, GBC, and GBA settings. Game Gear games use a separate cartridge silhouette, label position, shell branding, and clear-shell shadow/backing on the shelf.

The first integration targets Anbernic H700 devices. It does not add Miyoo support. Shaders and bezels use Slot's existing rendering and asset paths; no Game Gear-specific LCD shader or bezel artwork is included yet.

## Testing and releases

The H700 workflow publishes `more. slot.` builds as GitHub prereleases for testing. It does not mark them as latest and does not change the stable select.slot release or updater feed. The first test build must be installed manually; after that, only this build's isolated test feed can deliver later `more. slot.` updates through **Settings → System → Check for Updates**. See [the test OTA notes](MORE_OTA.md).

The first build is intended primarily for the Anbernic RG35XX-H. No device is marked tested until you report testing results. PicoDrive's license prohibits commercial use; each downloadable build includes the pinned source and required notices.

## Credits

- [Slot](https://github.com/slot-cfw/slot), by Brandon Kowalski
- [pvaibhav's H700 Slot fork](https://github.com/pvaibhav/slot)
- [PicoDrive libretro core](https://github.com/libretro/picodrive), plus its separately pinned build dependencies

The included source and core notices are authoritative for the bundled emulator's terms. This project does not include game ROMs or proprietary BIOS files.
