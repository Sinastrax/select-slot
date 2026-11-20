#!/usr/bin/env bash
# H700 source preparation for the pinned Slot v1.16.0 base.
# DO NOT reorder sequential historic patches: later hunks depend on earlier
# transformations. This script is the exact former inline CI build stage.
# Working directory: repository checkout root, not upstream/.
set -euo pipefail
curl -fsSL --retry 5 --retry-all-errors \
  "https://github.com/pvaibhav/slot/archive/refs/tags/v1.15.3-pvaibhav.1.tar.gz" \
  -o /tmp/base-slot.tar.gz
curl -fsSL --retry 5 --retry-all-errors \
  "https://github.com/pvaibhav/slot/archive/refs/tags/v1.16.0-pvaibhav.2.tar.gz" \
  -o /tmp/new-slot.tar.gz
mkdir upstream
tar -xzf /tmp/base-slot.tar.gz --strip-components=1 -C upstream
cd upstream
git init -q
git config user.email "select-slot@users.noreply.github.com"
git config user.name "select. slot. CI"
git add -A
git commit -qm "pvaibhav Slot v1.15.3 base"
git apply --check ../patches/select-authentic-gbc.patch
git apply ../patches/select-authentic-gbc.patch
git apply --check ../patches/pocket-color.patch
git apply ../patches/pocket-color.patch
git apply --check ../patches/pocket-color-gbc-correction.patch
git apply ../patches/pocket-color-gbc-correction.patch
git apply --check ../patches/sgb-pocket-pixel-separation.patch
git apply ../patches/sgb-pocket-pixel-separation.patch
git apply --check ../patches/core-specific-gb-screen-sgb-correction-performance.patch
git apply ../patches/core-specific-gb-screen-sgb-correction-performance.patch
git apply --check ../patches/sameboy-authentic-correction.patch
git apply ../patches/sameboy-authentic-correction.patch
git apply --check ../patches/sameboy-build-fixes.patch
git apply ../patches/sameboy-build-fixes.patch
git apply --check ../patches/per-core-authentic-color-correction.patch
git apply ../patches/per-core-authentic-color-correction.patch
git apply --check ../patches/color-transfer-only-gambatte-sgb-fix.patch
git apply ../patches/color-transfer-only-gambatte-sgb-fix.patch
git apply --check ../patches/restore-mgba-gb-and-disable-autoframeskip.patch
git apply ../patches/restore-mgba-gb-and-disable-autoframeskip.patch
git apply --check ../patches/mgba-drift-and-authentic-color-consistency.patch
git apply ../patches/mgba-drift-and-authentic-color-consistency.patch
git apply --check ../patches/mgba-native-pitch-neutral-authentic-white.patch
git apply ../patches/mgba-native-pitch-neutral-authentic-white.patch
git apply --check ../patches/mgba-audio-overflow-crossfade.patch
git apply ../patches/mgba-audio-overflow-crossfade.patch
git apply --check ../patches/authentic-color-response-only.patch
git apply ../patches/authentic-color-response-only.patch
git apply --check ../patches/mgba-gb-buffer-recovery.patch
git apply ../patches/mgba-gb-buffer-recovery.patch
git apply --check ../patches/rg34xxsp-extra-hotkeys.patch
git apply ../patches/rg34xxsp-extra-hotkeys.patch
git apply --check ../patches/select-online-updates.patch
git apply ../patches/select-online-updates.patch
for patch in menu-idle-settings menu-idle-behavior menu-idle-timer; do
  git apply --check "../patches/${patch}.patch"
  git apply "../patches/${patch}.patch"
done
git apply --check ../patches/resume-power-on-do-not-autolaunch.patch
git apply ../patches/resume-power-on-do-not-autolaunch.patch
echo "All verified select. slot. v1.15.3 patches applied"
git add -A
git commit -qm "select. slot. verified v1.15.3 changes"
git branch custom-prev
git checkout -qb upstream-1.16 HEAD~1
# Restore the exact new upstream checkout on an ancestor-linked branch.
find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
tar -xzf /tmp/new-slot.tar.gz --strip-components=1 -C .
git add -A
git commit -qm "pvaibhav Slot v1.16.0 source"
git checkout -q custom-prev
git merge --no-edit --no-ff -X ours upstream-1.16
# Merge conflicts in removed files must never be silently accepted.
test -z "$(git diff --name-only --diff-filter=U)"
git show upstream-1.16:CHANGELOG.md | grep -q '1.16.0'
git diff --stat HEAD~1 HEAD | tail -25
echo "Merged latest upstream with our previous complete custom modifications"
python3 ../.github/scripts/merge-1.16-fixes.py
python3 ../.github/scripts/fix-authentic-colour-reflection.py
python3 ../.github/scripts/fix-fit-lcd-sampling.py
python3 ../.github/scripts/verify-fit-lcd-sampling.py
# Validate the exact merged shader against OpenGL ES 2.0, not only Rust syntax.
# glslang-tools is installed in the next step after apt metadata setup.
python3 ../.github/scripts/verify-authentic-colour.py
python3 ../.github/scripts/reduce-fit-vertical-stripes.py
python3 ../.github/scripts/verify-fit-vertical-stripes.py
python3 ../.github/scripts/fix-rg35xxh-dot-grid-sgb.py
python3 ../.github/scripts/verify-rg35xxh-dot-grid-sgb.py
# Build the LCD grid in source-pixel space, and bypass expensive
# Pocket ink rendering on the dedicated mGBA/Gambatte SGB path.
python3 ../.github/scripts/fix-fit-reference-sgb-fastpath.py
python3 ../.github/scripts/verify-fit-reference-sgb-fastpath.py
# Native Game Boy Pocket ink must use fractional gap coverage at Fit.
python3 ../.github/scripts/fix-pocket-fit-ink-coverage.py
python3 ../.github/scripts/verify-pocket-fit-ink-coverage.py
# SGB must draw through Pocket Color's exact optical LCD pipeline.
python3 ../.github/scripts/fix-pocket-sgb-parity.py
python3 ../.github/scripts/verify-pocket-sgb-parity.py
# SGB RGB pixels must retain their palette chroma; only the real
# Pocket geometry may blend into the reflector at LCD dot gaps.
python3 ../.github/scripts/fix-mgba-sgb-optical-chroma.py
python3 ../.github/scripts/verify-mgba-sgb-optical-chroma.py
# Match Pocket Color's entire reflector/ink response, not just
# its physical gap outline; also render synthetic palette-swap
# frames and compare optical contrast at Integer and Fit scales.
python3 ../.github/scripts/fix-pocket-sgb-full-optics.py
python3 ../.github/scripts/verify-pocket-sgb-full-optics.py
# After all experimental shader transitions, restore exactly the
# PRE-RG35XX H Ver. 4 optical raster path for both color Pocket modes.
# Existing Fit work for mono/standard shaders stays independent.
python3 ../.github/scripts/restore-ver4-pocket-optics.py
python3 ../.github/scripts/verify-restored-pocket-optics.py
# Replicate the user-verified live switch: an already-running
# mGBA SGB game looks right when the GPU profile is Pocket Color.
# Both screens now return literally the same Look / shader path.
# Keep mGBA SGB hardware and palettes unchanged.
python3 ../.github/scripts/alias-sgb-to-pocket-color-renderer.py
python3 ../.github/scripts/verify-sgb-pocket-color-renderer-alias.py
# Final palette routing fix: color Auto is not a forced DMG
# palette; SGB uses SGB source colors, not GBC correction.
# This executes AFTER all historical shader transformations.
python3 ../.github/scripts/repair-pocket-rgb-source-and-correction.py
python3 ../.github/scripts/verify-pocket-rgb-source-and-correction.py
# Hardware feedback: SGB colors and LCD pixels are right, but the
# SNES correction left whites nearly pure white. Keep *all* Ver. 16
# RGB source and LCD code; apply exact Pocket Color GPU Look last.
python3 ../.github/scripts/restore-sgb-pocket-whitepoint.py
python3 ../.github/scripts/verify-sgb-pocket-whitepoint.py
# GBA-only Authentic correction for RG35XX H's fractional 2.67x
# Fit scaling. Applied LAST; all verified Pocket/SGG output
# and standard GBA Dot/Grid/LCD color effects remain unchanged.
python3 ../.github/scripts/fix-gba-fit-lcd-intersections.py
python3 ../.github/scripts/verify-gba-fit-lcd-intersections.py
# H700 GBA-only bottom bezel option: 3.5-inch 640x480 screens.
# Separate image with original alpha and SP placement. No shader edits.
python3 ../.github/scripts/add-h700-original-gba-bezel.py
python3 ../.github/scripts/verify-h700-original-gba-bezel.py
# Preserve the connection when pulling a cart, present branded OTA
# versions, and keep the shelf clock legible over the built-in dark
# wallpaper. Leave archive names, checksums and shaders unchanged.
python3 ../.github/scripts/fix-ota-label-wifi-eject.py
# Exact menu-corner light-theme texture fix, Wi-Fi Ejecting phase
# handling, and GBA's missing visible 2x Scale choice on 720x480.
# No color shader or optical raster changes.
python3 ../.github/scripts/fix-menu-status-wifi-eject-gba-scale.py
# Root Wi-Fi fix: ordinary cartridge ejection must never emit a
# link radio Down job. Preserve enabled Wi-Fi during normal games,
# while giving it to direct-console link play only when requested.
python3 ../.github/scripts/fix-wifi-lifecycle-ver23.py
# RetroAchievements launch indicator uses confirmed RA sessions and cached
# offline readiness, without changing the Wi-Fi On/Off radio policy.
python3 ../.github/scripts/ra-game-connection-ver24.py
python3 ../.github/scripts/ra-launch-banner-ver24.py
# Ver.25: RA login via masked on-device keyboard, applied on restart.
python3 ../.github/scripts/ra-menu-login-ver25.py
python3 ../.github/scripts/ra-menu-login-tests-ver25.py
# Ver.26: preserve compatible existing RA settings and show accurate save errors.
python3 ../.github/scripts/ra-login-save-ver26.py
# Ver.27: migrate pre-existing RA config on first boot; preserve account data.
python3 ../.github/scripts/ra-config-migration-ver27.py
# Ver.29: opt-in RA indexing, reliable negative caching and actionable Tools UI.
python3 ../.github/scripts/ra-library-ver29.py
python3 ../.github/scripts/ra-tools-ver29.py
python3 ../.github/scripts/ra-badges-ver29.py
python3 ../.github/scripts/ra-tests-ver29.py
# Ver.30: direct restart, active-game achievement viewer and protected cleanup.
python3 ../.github/scripts/ver30-menu.py
python3 ../.github/scripts/ver30-achievements.py
python3 ../.github/scripts/ver30-cleanup.py
# Shared row viewport: scroll all long quick-menu pages, protect footer.
python3 ../.github/scripts/fix-menu-overflow-all-pages.py
# Ver.31: per-game RA refresh, session/presence separation and measured progress.
python3 ../.github/scripts/ver31-ra-network.py
python3 ../.github/scripts/ver31-ra-viewer.py
python3 ../.github/scripts/ver31-ra-ui-efficiency.py
python3 ../.github/scripts/ver31-ra-tests.py
# BaseOS target fixes RG35XX H's default link nickname on 640x480 panels.
python3 ../.github/scripts/ver31-device-nicknames.py
# Ver.32: repeated X/Y presses render only six reusable achievement rows.
python3 ../.github/scripts/ver32-achievement-stability.py
# Ver.33: invalid Rich Presence cannot cancel achievement unlocks.
python3 ../.github/scripts/ver33-ra-tracking-reliability.py
# Ver.34: every emulated frame is evaluated, including fast-forward.
python3 ../.github/scripts/ver34-achievements-every-frame.py
# Match official rc_client: injected server warnings are not achievements.
python3 ../.github/scripts/ver34-ra-server-warning-filter.py
# Ver.35: use official rcheevos indirect-pointer invalid-read behavior.
python3 ../.github/scripts/ver35-indirect-memory-compat.py
# UI-only reference to built-in controls; no input or shortcut remapping.
python3 ../.github/scripts/readonly-shortcut-guide-ver37.py
# Ver38: plain-language labels and a display-only effective FF shortcut.
python3 ../.github/scripts/clarify-fixed-shortcuts-ver38.py
# Ver.39: verified, read-only instructions for contextual and remappable gestures.
python3 ../.github/scripts/source-verified-hotkey-guide-ver39.py
# Ver.40: only obscure shortcuts shown; guide-only text layout cannot collide.
python3 ../.github/scripts/compact-hotkey-guide-ver40.py
# Shared H700 on-screen keyboard: one-shot Shift, double-press Caps Lock.
python3 ../.github/scripts/keyboard-one-shot-caps-lock-ver41.py
# Refresh keyboard key textures when one-shot Shift becomes Caps Lock.
git apply ../patches/keyboard-caps-indicator.patch
# Keep long names readable in the cheat and achievement lists.
git apply ../patches/scroll-cheat-achievement-names.patch
# Reserve top chrome and header space in the in-game achievement list.
git apply ../patches/achievement-header-viewport.patch
