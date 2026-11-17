# select. slot. 1.8.1 Ver. 21 — Miyoo Mini family

**Experimental, offline-capable Miyoo Mini / Mini Plus / Mini Flip application.** This is not the Anbernic H700 firmware. Built from the pinned [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo) ARMv7 port and Slot 1.8.1. Its releases are separate from the H700 update channel.

## Changes in Ver. 21

- **Brightness restored to the original 1–9 menu range.** Original Miyoo PWM steps and maximum duty are used; boost levels 10–12 and their experimental duty calculations have been removed.
- **Safe upgrade from Ver. 12–20:** If the previous saved brightness was 10, 11 or 12, it loads as 9. This avoids rejecting the entire `Config/slot.state` file, so the other settings and resume metadata remain readable. Older values of 1–9 are unchanged.
- **Theme-neutral OnionOS integration:** All POWER, sleep/wake and boot/shutdown presentation is left to OnionOS and whichever theme is selected. No theme name, theme image path, sprite, or theme-specific asset is referenced by the app. The app's POWER handler flushes saves and lets Onion's existing keymon handle the actual transition.
- **Shaders remain completely disabled**, including the in-game and system Shader rows, shader next/previous shortcuts and any old saved shader selection. Slot always asks for the original unfiltered software game renderer.

Nothing in Ver. 21 changes game scaling, emulator core choices, OnionOS files, themes, save-state format or the firmware of another device.

## Included features

| Area | Behavior |
| --- | --- |
| Games | Game Boy, Game Boy Color and Game Boy Advance |
| Default emulator | mGBA for GB/GBC; gpSP for GBA |
| Alternative emulator | Gambatte for GB/GBC; mGBA for GBA |
| Scaling | Original, Integer, Aspect Fit, Fill/Crop, Full Stretch, stored per game |
| Display | Unfiltered pixels only; game-core color-correction and palettes remain independent of rendering effects |
| Brightness | **1–9**, original Miyoo PWM curve; OnionOS's physical PWM interface has priority when OnionOS is present |
| Resume | Separate Resume on Power On and Resume on Insert |
| Power/theme | OnionOS owns physical POWER and selected theme; native keymon standby and shutdown handling |
| Saves | Existing ROMs, battery saves, save states and other config are preserved by the installer |

The original Miyoo frame-buffer orientation and the port's launcher remain untouched.

### OnionOS integration and theme compatibility

Under OnionOS, the app detects the installed Onion runtime instead of looking for any specific theme. Short POWER presses and shutdown transitions stay in the native OnionOS/keymon path. The app flushes its save data before yielding POWER, and uses OnionOS's documented state-change notification to avoid competing over the backlight; on return from a long process suspension it reapplies the selected Slot brightness once.

**Theme assets aren't copied, modified, chosen or hardcoded by Slot.** Whatever boot/shutdown presentation the *installed OnionOS version and selected theme* normally provide remains in OnionOS's control. A theme without a particular shutdown image cannot be made to display one by this patch. Physical display/standby behavior still needs checking on each Miyoo model.

The OnionOS PWM interface is preferred to unrelated backlight-class devices on the original Mini family, where such an interface may report changes that do not affect the LCD. On other firmware, the Miyoo port's normal backlight detection remains intact. Brightness levels themselves are restored to the original nine-step calibration.

### Menu inactivity controls

The **Menu Screen Off** and **Menu Power Off** features of the H700 fork are not yet ported. Unlike H700's standalone firmware, this build runs inside OnionOS, which also owns power handling. Directly duplicating H700's timer/shutdown calls could bypass selected-theme transitions or conflict with keymon. See the discussion in this project before introducing new timers; they are intentionally left disabled for this release.

### Offline-only update policy

**No in-app updater or Wi-Fi-dependent feature is included or planned for the Miyoo build.** Original Miyoo Mini units have no built-in Wi-Fi. Releases are downloaded on a separate device and installed from an SD card. Each successful experimental build is published to [the Miyoo GitHub prereleases](https://github.com/Sinastrax/select-slot/releases?q=miyoo) as a complete ZIP plus SHA-256 checksum. This does not affect the H700 OTA channel.

## Installation

1. Back up `Config/slot.state`, `Saves/`, any existing `System/slot` and other important SD-card content.
2. Download the full Miyoo ZIP from the matching experimental GitHub prerelease on a computer.
3. Extract the ZIP's **contents** into the SD-card root. There should be `System/slot`, `App/Slot/` and `Apps/slot.pak/` directly under the card root, not within another folder.
4. Start select. slot. from OnionOS. Set brightness between **1 and 9**.

**Optional autoboot:** `System/autoboot/onion-startup.sh` is packaged for manual use. It delegates to the port's original launcher; do not replace OnionOS's `.tmp_update/runtime.sh` or modify the current theme. See the comments in the script for the manual installation and removal paths.

The ZIP contains no ROMs or proprietary BIOS files. This release is built and packaged in CI but hardware behavior is not fully validated on every supported Miyoo model.

## Technical safeguards

Build checks verify that the shader-free frontend, hidden menu controls and no-op shortcuts remain in place. Ver. 21 checks the original brightness maximum is 9, the menu has 10 internal levels (0–9), the experimental PWM boost paths are absent and the prior brightness values are safely migrated. The existing OnionOS PWM selection and power/keymon coordination remain, but no theme-specific code is added.

[Original Slot](https://github.com/slot-cfw/slot) · [Miyoo port](https://github.com/deanmarano/slot-miyoo) · [select. slot.](https://github.com/Sinastrax/select-slot)
