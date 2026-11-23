# more. slot.

**A separate Slot build for adding systems beyond the original select.slot. versions.**

`more. slot.` is the separate UnsloT-based branch for adding systems beyond select.slot. More.slot Test 6 (`v1.16.0-more.6`) has been withdrawn after its update and installation failed. The OTA feed no longer points to Test 6. Test 5 remains an archived test build; neither build is a recommended recovery image. More.slot development is paused until the installation path and requested feature set are corrected. The stable select.slot release and OTA feed are separate and unchanged.

The Miyoo Mini port remains available as [select.slot. 1.8.1 Ver. 12](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver12).

## Current work

| System | Core | Controls | Display options | Hardware status |
| --- | --- | --- | --- | --- |
| Sega Game Gear (`.gg`) | Gearsystem (PicoDrive, Genesis Plus GX and SMS Plus available as alternatives) | D-pad, A, B, Select, Start, turbo | Per-system Authentic shader, color correction, scaling, bezel and frame blending | Hardware confirmation pending |

The default scale is **Fit**. The display menu keeps Game Gear settings separate from GB, GBC, and GBA settings. Game Gear games use their own cartridge silhouette and label area. **General → Cart Slot** selects the Game Gear bay artwork; the other systems keep their existing shelf slot.

The first integration targets Anbernic H700 devices. It does not add Miyoo support. Game Gear offers its own Authentic LCD profile with optional color correction and frame blending. Custom bezels go in Bezels/GG.

## Testing and releases

The H700 workflow builds pull requests without publishing. Test 4 established the separate More.slot OTA feed; test releases are delivered through **Settings → System → Check for Updates**. A verified merge to `more-slot` publishes a prerelease and updates only the `more-slot` OTA manifest. It does not mark the build as latest or change the stable select.slot release or updater feed. See [the test OTA notes](MORE_OTA.md).

The first build is intended primarily for the Anbernic RG35XX-H. No device is marked tested until you report testing results. PicoDrive's license prohibits commercial use; each downloadable build includes the pinned source and required notices.

## Port status

Test 6 was withdrawn and is not a valid test build. The known select.slot parity gaps remain listed in [the feature parity tracker](docs/FEATURE_PARITY.md). The next release must not be published until its OTA and installation paths work and the requested feature set is present and reviewed. The stable select.slot release and updater feed remain unchanged.

## Credits

- [Slot](https://github.com/slot-cfw/slot), by Brandon Kowalski
- [pvaibhav's H700 Slot fork](https://github.com/pvaibhav/slot)
- [SlotPlus Ultra](https://github.com/nelynes/slotPlus), for the adapted Game Gear cartridge and bay artwork (GPL-3; see `System/licenses/gamegear-cartridge-art.txt` in the build)
- [Gearsystem](https://github.com/drhelius/Gearsystem), the default Game Gear core
- [PicoDrive libretro core](https://github.com/libretro/picodrive), plus its separately pinned build dependencies

The included source and core notices are authoritative for the bundled emulator's terms. This project does not include game ROMs or proprietary BIOS files.
