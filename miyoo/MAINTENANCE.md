# select. slot. — Miyoo maintainer guide

The Miyoo firmware is separate from the Anbernic H700 builds and OTA channel. It uses Slot 1.8.1 from [deanmarano/slot-miyoo](https://github.com/deanmarano/slot-miyoo), at the pinned commit in [version.env](version.env). Do **not** apply H700 GLES2, framebuffer, shader, or ARM64 patches to the Miyoo build.

## Update and test

- **Version and port revision:** [version.env](version.env) is the single source used by both the build script and the release publisher. Increment `CUSTOM_VERSION` for a new user-facing release.
- **Local build:** `bash miyoo/build.sh`. A local source checkout already present at `.build/miyoo/slot-miyoo` causes the build to refuse an overwrite. Use `bash miyoo/build.sh --clean` only when you deliberately want to replace that generated clone; it does not touch firmware or SD cards.
- **Static regression suite:** `python3 -m unittest discover -s miyoo/tests -p 'test_*.py' -v`.
- **Generated patch regression suite:** after building, set `MIYOO_GENERATED_PATCH=.build/miyoo/slot-miyoo/patches/0028-select-miyoo-config.patch` and run the same tests.
- **ARMv7/QEMU tests:** `cd .build/miyoo/slot-miyoo && task test`. These exercise the graphics and power crate tests, including the stock-versus-OnionOS PWM selector, but are **not** substitutes for physical hardware validation.
- **CI:** `.github/workflows/build-miyoo.yml` compiles, runs both source-level and QEMU tests, checks the three OS-specific ZIPs and checksums, and uploads artifacts.
- **Publication:** `.github/workflows/publish-miyoo.yml` is the single release publisher. It uses [version.env](version.env) and the matching `.github/release-notes/miyoo-verN.md`. It publishes without deleting prior releases or changing which H700 release GitHub labels latest.

## Ordered patch modules

[miyoo/apply_custom.py](apply_custom.py) imports the following modules **in order** after configuring [custom/patcher.py](custom/patcher.py): `emulators`, `onion_power`, `rendering`, `idle`, `scaling`, `bezels`, `ui`.

Some modules modify the same Rust source. Do not reorder them casually: the generator uses exact one-match string replacements, computes the final unified diff per source path, and fails if any replacement or allowlisted-file check does not match. Changing a module should be followed by a clean build and the complete regression suite.

## Compatibility boundaries

- **Emulators:** mGBA only for GB/GBC; gpSP default and mGBA optional for GBA. Legacy `gambatte` selections are interpreted as mGBA; saved configuration files aren't rewritten by that alias.
- **Display:** original unfiltered CPU software rendering, no GPU shader backend. Preserve the original Mini/Mini Plus framebuffer path, the 0–9 PWM brightness ladder, the selected OnionOS theme and native keymon suspend/shutdown.
- **Firmware detection:** `.tmp_update/runtime.sh` alone is not proof of OnionOS; stock autoboot also contains that path. The OnionOS version marker is required by all Onion-specific behaviors.
- **No Restart UI:** the Settings Restart entry, About X handler and About legend are intentionally removed on Miyoo. Power Off and OnionOS-managed sleep remain independent.
- **Installers:** `*-onion-autoboot.zip` installs only an OnionOS startup script; `*-stock-autoboot.zip` installs the stock-only `.tmp_update/runtime.sh`; app-only must install neither. The stock ZIP must never be extracted on top of OnionOS.
- **Saves:** do not delete or rewrite the ROM, Saves, States or Config trees in a firmware update. Back up user files before switching emulator cores.

## Hardware checks that CI cannot prove

**The original Miyoo Mini is the regular physical test device.** Verify: normal Game Boy and Game Boy Advance playback with sound; save/load after shutting down; GB/GBC/GBA scaling persistence; the original GBA bezel; menu scrolling, About B/Menu navigation and the **absence of Restart**; screen brightness through all 0–9 levels; OnionOS active-theme standby/wake and shutdown; and applicable firmware boot layouts. The Mini Plus, Mini Flip and other firmware variants need separate hardware confirmation; testing the original Mini does not establish compatibility for them.
