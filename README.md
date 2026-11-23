# more. slot.

**A separate Slot build for adding systems beyond the original select.slot. versions.**

`more. slot.` is the separate UnsloT-based branch for adding systems beyond select.slot. More.slot Test 6 (`v1.16.0-more.6`) has been withdrawn after its update and installation failed. The OTA feed no longer points to Test 6. Test 5 remains an archived test build; neither build is a recommended recovery image. More.slot development is paused until the installation path and requested feature set are corrected. The stable select.slot release and OTA feed are separate and unchanged.

The Miyoo Mini port remains available as [select.slot. 1.8.1 Ver. 12](https://github.com/Sinastrax/select-slot/releases/tag/miyoo-v1.8.1-ver12).

## Target system

| System | Core | Controls | Display options | Hardware status |
| --- | --- | --- | --- | --- |
| Sega Game Gear (`.gg`) | Gearsystem (PicoDrive, Genesis Plus GX and SMS Plus available as alternatives) | D-pad, A, B, Select, Start, turbo | Per-system Authentic shader, color correction, scaling, bezel and frame blending | Hardware confirmation pending |

The default scale is **Fit**. The display menu keeps Game Gear settings separate from GB, GBC, and GBA settings. Game Gear games use their own cartridge silhouette and label area. **General → Cart Slot** selects the Game Gear bay artwork; the other systems keep their existing slot.

The first integration targets Anbernic H700 devices. It does not add Miyoo support. Game Gear offers its own Authentic LCD profile with optional color correction and frame blending. Custom bezels go in Bezels/GG.

## Testing and releases

The H700 workflow builds pull requests without publishing. Test 4 established the separate More.slot OTA feed; test releases are delivered through **Settings → System → Check for Updates**. A verified merge to `more-slot` publishes a prerelease and updates only the `more-slot` OTA manifest. It does not mark the build as latest or change the stable select.slot release or updater feed. See [the test OTA notes](MORE_OTA.md).

The first build is intended primarily for the Anbernic RG35XX-H. No device is marked tested until you report testing results. Each build includes source and license notices; check the bundled notices for the terms that apply to each core and asset.

## Port status

Test 6 was withdrawn and is not a valid test build. The known select.slot parity gaps remain listed in [the feature parity tracker](docs/FEATURE_PARITY.md). The next release must not be published until its OTA and installation paths work and the requested feature set is present and reviewed. The stable select.slot release and updater feed remain unchanged.

## Credits

More.slot's H700 distribution is based on [UnsloT](https://github.com/cloudwithax/unslot), which is a fork of [Slot](https://github.com/BrandonKowalski/slot) by Brandon T. Kowalski. The H700 base also builds on [BaseOS](https://github.com/pvaibhav/BaseOS) by pvaibhav. The full upstream attribution for interface artwork, bundled cores, shaders, bezels, fonts, sounds, apps, services, and other media is retained in [UnsloT's credits](https://github.com/cloudwithax/unslot#credits). The generated `System/licenses/` directory and `cores.manifest` in every build list the applicable licenses and exact bundled core revisions.

Additional More.slot sources:

- [SlotPlus Ultra](https://github.com/nelynes/slotPlus), Game Gear cartridge shell, interior, board, label geometry and bay artwork, adapted from commit `0e85ed2b82dd1baf57ac10139c25f58a2365c09e`. Changes and license are recorded in `System/licenses/gamegear-cartridge-art.txt`.
- [Gearsystem](https://github.com/drhelius/Gearsystem), Game Gear core.
- [PicoDrive](https://github.com/libretro/picodrive), [Genesis Plus GX](https://github.com/ekeeke/Genesis-Plus-GX), and [SMS Plus](https://github.com/libretro/smsplus-gx), selectable Sega cores.
- [mGBA](https://github.com/libretro/mgba), [gpSP](https://github.com/libretro/gpsp), [Gambatte](https://github.com/libretro/gambatte), and [ArmGBA](https://github.com/MagnominusGit/armGBA), Game Boy family cores shipped or retained for update compatibility.
- [Libretro GLSL Shaders](https://github.com/libretro/glsl-shaders), sources for Slot's screen shader ports.
- [Anbernic H700 Overlays](https://github.com/RighteousSavant/Anbernic-H700-Overlays) and the [Knulli bezel collection](https://github.com/chrizzo-hb/knulli-bezels), with individual bezel artists and licenses documented in the bundled notices.

The core list above identifies the More.slot-specific and Game Boy cores; the bundled `cores.manifest` is the complete inventory for the actual release package. This project does not include game ROMs or proprietary BIOS files.
