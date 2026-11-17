# select. slot. 1.8.1 Ver. 20 — unfiltered Miyoo rendering

**Experimental ARMv7 Miyoo Mini / Mini Plus / Flip application, not H700 firmware.** This version is based on the pinned [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo) commit `d096bdb87f25f3aba62de6b40ef859b61d841e43` and Slot upstream 1.8.1.

## Automatic experimental downloads

Successful Miyoo builds on the development branch now publish a **GitHub prerelease** with a distinct `miyoo-v…-preview.RUN.ATTEMPT` tag. Each prerelease includes the complete card-root Miyoo ZIP and its SHA-256 checksum. Unlike temporary workflow artifacts, published release assets do not have the 30-day Actions artifact retention limit. Find them at [GitHub Releases](https://github.com/Sinastrax/select-slot/releases?q=miyoo).

The publishing job only runs after the build and package checks succeed and only for trusted branch pushes/manual builds; pull requests do not publish releases. Miyoo prereleases use `--prerelease --latest=false`, so the H700 stable release and OTA channel remain separate. Release publication does **not** establish hardware compatibility, frame-rate or shader accuracy.

## Ver. 20: disable shaders completely

The Miyoo build uses **only the original, unfiltered software rendering path** for GB, GBC and GBA. It no longer patches the graphics backend with LCD, Dot or Shimmerless effects. Both in-game and global Shader menu rows are hidden. Shader next/previous shortcuts do nothing, and the frontend always sets `ScreenEffect::None` even when an older saved configuration contains a shader selection. The existing config, saves and states are not deleted.

Existing **Aspect Fit, Integer, Original, Crop and Stretch scaling**, mGBA/gpSP core preferences, PWM brightness, OnionOS BMO standby and the source Miyoo display path are unchanged. This release does not affect the H700 firmware or its authentic shaders.

## Ver. 19: Shimmerless only (Miyoo CPU renderer)

The only selectable shader modes are **Off** (the original neutral, nearest-neighbour gameplay path) and **Shimmerless** for GB, GBC and GBA. LCD3x, Dot, Grid and Simpletex have been removed from the selectable lists because they either rendered poorly or were never implemented in this CPU port. Existing saved shader selections outside the new list revert to Off.

Shimmerless is a software port of the newer official Slot scaling method: for each output pixel it calculates the fractional native pixel coverage and blends at most two source pixels per axis. Horizontal source rows are cached across output scanlines to reduce repeated sampling on the Miyoo's CPU. The effect uses no LCD mask, no RGB tint and no brightness adjustment; the original Off path remains untouched. On the 640×480 Miyoo it is intended primarily for Aspect Fit scaling.

The build checks the menu choice tables, persisted name, HUD label, frontend routing and CPU renderer to prevent a recurrence of the missing-GB/GBC-menu issue. Compilation and package validation are automated, but real device image quality and frame-time still need to be evaluated. The user-confirmed mGBA brightness, OnionOS/BMO standby and separate H700 release channel remain untouched.

## Ver. 18: make Dot selectable for GB and GBC

The previous Ver. 17 built the software Dot renderer, but **GB and GBC were still restricted to their original shader selection list** (Off, LCD3x, Grid, Simpletex). Dot was only offered to GBA. Ver. 18 corrects the GB/GBC selection table, exposes Dot for all three platforms, and hides Grid/Simpletex because the Miyoo CPU renderer never implemented those modes. The selectable shaders are now **Off / LCD3x / Dot** on GB, GBC and GBA.

The build checks both shader choice tables, the live frontend-to-renderer mapping, and the Dot mask. Saved unsupported shader choices fall back to neutral Off. Existing mGBA/gpSP defaults, PWM brightness, OnionOS/BMO and Fit scaling remain unchanged. Visual and frame-rate results still require testing on a real Miyoo.

## Ver. 17: experimental Fit-aware software Dot

Dot now uses area-weighted coverage of each emulated source pixel across its actual destination pixel footprint in both axes. Horizontal and vertical masks are precomputed per output column/row using the original Miyoo CPU renderer, so fractional Fit scaling does not produce a naive repeating output-pixel mask. Dot is neutral RGB (no color tint), with a modest dot-gap luminance reduction and no artificial brightening beyond the original white signal. Off and LCD3x paths remain intact; no changes to mGBA/gpSP, PWM, Onion standby or BMO. Performance and visual fidelity require physical device verification.\n\n## Ver. 16: restore the original Miyoo emulator defaults\n\nThe GB/GBC default is restored from Gambatte to the original Miyoo mGBA, retaining gpSP for GBA. Gambatte remains optional for compatibility, rather than being mandatory. The original renderer, launcher, PWM implementation, Onion keymon coordination and working BMO handoff are kept. Existing per-game core choices may continue to override the default, so test using a title without an explicit Gambatte selection. This is an experimental core-path correction, not a proven cure for the physical darkness.\n\n## Ver. 15: actual hardware backlight priority on the original Mini

This release preserves the **working Ver. 14 OnionOS standby / BMO handoff**. The remaining problem was a dark game/display even when the new SLOT brightness scale reached level 12.

**What was verified from source:** SLOT's `Shader: Off` selects `ScreenEffect::None` in the unchanged Dean Miyoo renderer, so the LCD3x intensity mask is not applied. Gambatte's `gambatte_dark_filter_level` is explicitly `0`, and its color correction receives `disabled` when Off. This does **not** establish that every possible system display adjustment is neutral, but there is no code path that keeps SLOT's LCD3x filter active after Shader Off.

**More significant discovery:** Dean's original `DevicePlatform::probe()` checks `/sys/class/backlight` first, then `/sys/kernel/debug/dispdbg`, and only **last** the actual `/sys/class/pwm/pwmchip0/pwm0` device. This priority is appropriate for Dean's verified Mini Flip, but OnionOS controls backlight on original Mini/Mini Plus through the PWM device directly. If an alternative display interface exists on the original Mini, selecting it means SLOT's PWM boost code is never called, so 9/10/11/12 can look identically dark even though the menu and saved settings change.

**Targeted correction:** When the **OnionOS runtime** is present on the SD card *and* the PWM channel's `period` and `duty_cycle` nodes are available, prefer the physical Onion PWM channel over older class/dispdbg entries. On stock/Allium firmware, or if PWM is absent, retain Dean's original fallback order. No changes to the software renderer, color palettes, filtering, framebuffer, BMO theme, or OnionOS files. Original brightness levels 0–9 and extended 10–12 remain. An added source-level test simulates a system with both a class backlight and the PWM channel, verifying that the PWM output receives the requested levels only under Onion.

**Limit:** This is a code-grounded compatibility correction, not a physical measurement. The actual display result still requires testing on the Mini. If the dark screen persists, the next issue is likely external to the SLOT shader-Off path (such as another Onion display setting/driver), rather than just raising the brightness number again.

## BMO standby / shutdown artwork and the POWER-button conflict

The actual **BMO by forevertuesday** theme (OnionUI/Themes) includes `skin/extra/Screen_Off.png`, `skin/extra/Screen_Off_Save.png`, and `skin/extra/bootScreen.png`. Onion's `bootScreen End` and `End_Save` code renders those actual files into its framebuffer.

The preceding experimental SLOT application was also handling the physical POWER press. Slot's `doze()` calls `power.on_close()`, which immediately writes PWM brightness 0. Onion's theme program may draw its shutdown picture afterward, but a black backlight makes it **invisible**, even if the image is in the framebuffer. This is a real potential race, especially on long-power/shutdown transitions.

Ver. 14 delegates POWER events **exclusively to OnionOS's already running keymon** whenever Onion's runtime is detected, while immediately flushing SLOT's save on POWER press. This prevents SLOT from turning the screen black before Onion's artwork can render, and does not modify or overwrite BMO theme assets or OnionOS binaries. On non-Onion firmware the original SLOT POWER handling is preserved.

**Important distinction:** A *short POWER press into Onion standby* is handled by `keymon` and ordinarily simply blanks the LCD, whereas the `Screen_Off` and `Screen_Off_Save` pictures are called by Onion's explicit shutdown routines. This change preserves those shutdown pictures but does **not** invent a brand-new always-on standby display or guarantee an image remains lit while asleep. Test the usual BMO shutdown transition separately from short standby. The screen darkness during normal operation is a **separate and still unresolved** issue; PWM boost levels 10–12 remain available but are experimental.

## Why it exists

On the user's original Miyoo Mini, the entire image appears too dark even with Slot at its maximum value **9**. The original Dean Miyoo version previously looked correct on the same handheld, and the Ver. 9 and clean Ver. 11 repairs did not restore it. This release changes **real hardware PWM backlight brightness** and coordinates with OnionOS power management. It does not artificially brighten game colors, alter LCD3x, or apply gamma or screen filters.

## Brightness levels

Slot upstream saves and exposes `BRIGHTNESS_MAX=9`; Dean's PWM calibration writes fixed values `[0,5,7,11,16,23,34,49,72,112]`, where level 9 writes duty 112. The hardware PWM period on OnionOS is configurable and defaults to 800. Ver. 12:

- Leaves **all original levels 0–9 identical**.
- Extends settings, on-screen controls, and saved-state parsing to 12.
- At default 800 period, level **10 writes 160**, **11 writes 240**, and **12 writes 400** (20%, 30%, and 50% electrical PWM duty, respectively).
- At other PWM periods, levels 10–12 scale to 20%/30%/50% of the *actual* period, never dropping below level 9 and never exceeding the period. Example at period 400: levels 9,10,11,12 write 112,112,120,200. At period 100, the old level 9 already saturates the period, so extra levels **cannot** boost further.
- Keeps the original PWM logic for original levels 0–9; only a small code path for levels 10–12 is new. Normal framebuffer, image renderer and launcher remain the original Dean version.

This upper boost is **not validated for the original Mini's display durability**. Dean documented trying duty 400 on a **Mini Flip**, describing it as exceptionally bright; that is not a brightness/safety measurement on every Mini panel. Start with 10, then 11; use 12 only if necessary. Higher brightness can cause more power consumption, heat or display stress, and shorter battery life.

## OnionOS settings and interactions

**OnionOS has its own global hardware brightness (0–10)**. In [Onion's source](https://github.com/OnionUI/Onion/blob/main/src/common/system/display.h), `display_setBrightness(level)` writes an exponential PWM duty. Level 10 is about **100** at the standard period, slightly *lower* than Slot's original level 9 of 112. Onion and Slot control the **same** `/sys/class/pwm/pwmchip0/pwm0/duty_cycle` interface.

**Onion keymon restores its global brightness after suspend/wake**. It can also reassert that setting while it believes the MainUI is active. This build writes Onion's supported temporary `/tmp/state_changed` notification on Slot app startup (when the Onion keymon binary is present), then reapplies the saved Slot level **once after a long process-suspension gap**. It does **not** stop keymon, replace Onion's `runtime.sh`, edit global preferences, or continuously rewrite backlight hardware.

**PWM frequency:** OnionOS **Apps → Tweaks → Advanced → PWM frequency** offers 100–1000; **800 Hz (Default)** is the baseline used for the table above. It changes the sysfs `period`. Onion's documentation warns lower values can cause flicker, while the setting also affects audible buzzing. For a reproducible brightness comparison, use **800 Hz (Default)**. Do not assume "level 9" means the same effective duty ratio with other PWM frequencies.

**Other global display adjustments:** OnionOS has **Apps → Tweaks → Appearance → Blue light filter**, including an optional schedule. Its adjustment uses the hardware color-temperature interface and can change the entire visible picture independently of a game shader. The Miyoo's native **Settings → Display** controls (including Luminance, Hue, Saturation and Contrast) can also affect overall image luminance and contrast. These remain untouched. For checking backlight only, turn off blue-light filter and use your preferred known-good factory display settings.

**Sleep:** The BMO by forevertuesday theme, Onion's native boot/shutdown art, and keymon suspend/wake logic remain intact. No custom visual animation or screen-off timer is installed.

## Installation

1. Back up the card, especially `Config/slot.state`, `Saves/`, and any existing `System/slot`.
2. For Ver. 17 and later, download the Miyoo ZIP and checksum from the matching experimental GitHub prerelease. Older experimental versions may only have temporary GitHub Actions artifacts.
3. Extract **the contents of the inner ZIP** to the SD-card root. `System/slot`, `App/Slot/`, and `Apps/slot.pak/` must be at the card root, not inside a new folder.
4. Start **select. slot.**. In the SLOT **Brightness** menu or using mapped brightness shortcuts, choose 10 first and then 11 or 12 only if needed.
5. If brightness falls back after standby, the new automatic resume reapply should restore the selected SLOT level. If a change in OnionOS settings is pending, its keymon remains responsible for its own global value.

GB/GBC default core is the original Miyoo ARMv7 mGBA, with Gambatte still available as an optional alternative. GBA defaults to gpSP, with mGBA as the compatibility alternative. This restores the original port's preferred GB/GBC emulator path without replacing existing saves or affecting Onion/BMO. The display-darkness issue is not yet verified resolved on hardware. Existing palette and per-game scaling features (Original, Integer, Aspect Fit, Fill/Crop, Full Stretch) and separate Resume on Power On/Resume on Insert settings remain included. The framebuffer, LCD3x and hardware orientation remain the original Miyoo implementation. Menu-idle power timers, custom sleep animations, Authentic GLSL shaders and H700 OTA are not included.

## Build validation and limitations

The GitHub workflow compiles and packages this using Dean's original ARMv7 toolchain, checks ZIP integrity, verifies the original launcher is byte-identical and rejects custom framebuffer modifications. The source also includes unit tests for original and extended PWM at several OnionOS periods. Build success **does not prove the original Mini hardware brightness is fixed**. This is a separately branched, experimental preview, not merged into main or published as an OTA release.

Credits: [slot-cfw/slot](https://github.com/slot-cfw/slot), [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo), and [Sinastrax/select-slot](https://github.com/Sinastrax/select-slot). Upstream GPL-3.0-or-later and component licences apply; no ROMs or BIOS binaries are included.
