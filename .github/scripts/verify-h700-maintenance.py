#!/usr/bin/env python3
"""Fail-closed H700 build/release checks, independent of device hardware.

Keep legacy patches in exactly the sequence verified on physical H700 units.
Never let a maintenance build delete releases, force-move tags, or silently
reintroduce a superseded OTA publisher. This runs before the costly build.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".github"
SCRIPTS = GH / "scripts"
PATCHES = ROOT / "patches"
WORKFLOWS = GH / "workflows"

version = (GH / "ota-version.txt").read_text().strip()
assert re.fullmatch(r"1\.16\.0-rgsp\.[1-9]\d*", version), f"unexpected H700 OTA version: {version!r}"
assert "\n" not in version

source = (SCRIPTS / "h700-prepare.sh").read_text()
assert source.startswith("#!/usr/bin/env bash\n")
assert "set -euo pipefail\n" in source
assert "v1.15.3-pvaibhav.1.tar.gz" in source
assert "v1.16.0-pvaibhav.2.tar.gz" in source
assert "v1.16.0-pvaibhav.1.tar.gz" not in source
assert "git merge --no-edit --no-ff -X ours upstream-1.16" in source

# All references must resolve locally; an upstream refactor should be
# detected before launching a lengthy, artifact-producing firmware build.
python_tools = re.findall(r"python3 \.\./\.github/scripts/([a-z0-9._-]+\.py)", source)
assert len(python_tools) >= 45, f"Missing customization stages ({len(python_tools)})"
for name in python_tools:
    assert (SCRIPTS / name).is_file(), f"Missing required H700 patch tool: {name}"

static_patches = re.findall(r"git apply(?: --check)? \.\./patches/([a-z0-9._-]+\.patch)", source)
assert len(static_patches) >= 35, f"Missing base patch stages ({len(static_patches)})"
for name in static_patches:
    assert (PATCHES / name).is_file(), f"Missing H700 base patch: {name}"
for name in ("menu-idle-settings", "menu-idle-behavior", "menu-idle-timer"):
    assert (PATCHES / (name + ".patch")).is_file()

# Guard ordering, not just presence: these refinements have hard dependencies.
stages = [
    "git apply ../patches/select-authentic-gbc.patch",
    "python3 ../.github/scripts/merge-1.16-fixes.py",
    "python3 ../.github/scripts/restore-ver4-pocket-optics.py",
    "python3 ../.github/scripts/restore-sgb-pocket-whitepoint.py",
    "python3 ../.github/scripts/fix-gba-fit-lcd-intersections.py",
    "python3 ../.github/scripts/verify-gba-fit-lcd-intersections.py",
    "python3 ../.github/scripts/add-h700-original-gba-bezel.py",
    "python3 ../.github/scripts/verify-h700-original-gba-bezel.py",
    "python3 ../.github/scripts/optimize-authentic-pocket-sampling.py",
    "python3 ../.github/scripts/ra-config-migration-ver27.py",
    "python3 ../.github/scripts/ver30-menu.py",
    "python3 ../.github/scripts/fix-menu-overflow-all-pages.py",
    "python3 ../.github/scripts/ver31-device-nicknames.py",
    "python3 ../.github/scripts/ver34-achievements-every-frame.py",
    "python3 ../.github/scripts/ver35-indirect-memory-compat.py",
]
positions = [source.find(x) for x in stages]
assert all(v >= 0 for v in positions) and positions == sorted(positions), (
    "H700's hardware-verified patch sequence is missing or out of order"
)
assert source.count("python3 ../.github/scripts/ver35-indirect-memory-compat.py") == 1

build = (WORKFLOWS / "build-h700.yml").read_text()
assert "bash .github/scripts/h700-prepare.sh" in build
assert "python3 .github/scripts/verify-h700-maintenance.py" in build
prep = (SCRIPTS / "h700-prepare.sh").read_text()
assert "restore-known-good-authentic-texture-filter.py" in prep
assert (SCRIPTS / "restore-known-good-authentic-texture-filter.py").exists()
assert "cargo test -p slot-achievements -- --nocapture" in build
assert "cargo test -p slot-ui --lib menu_viewport_tests" in build
assert "cargo test -p slot --no-default-features --features device --lib hardware_nickname_regression" in build
assert "cargo test -p slot-gfx --lib authentic_blending_tests" in build
assert "cargo test -p slot --no-default-features --features device --test app authentic_trades_the_game_boys_colour_and_palette_rows_for_a_model" in build
assert "check-gles2-shader.py" in build
assert "verify-ota-publisher.py" in build
assert "needs: build-h700" in build
assert "refs/heads/main" in build and "refs/heads/integration/slot-1.16.0-armgba" in build
assert "SLOT_VERSION=\"$(cat ../.github/ota-version.txt)\"" in build
assert "version=\"$(cat ../.github/ota-version.txt)\"" in build
assert "sha256" in build and "versions.json" in build
assert "mgba-c758314a639aa0066e7b65a8341448181b73c804-source.tar.gz" in build
assert "armgba_libretro.so" in build
assert "armgba-src" in build
assert "gh release create" in build and "--latest" in build
assert "release-test-h700" not in build
assert "configure-h700-test-ota.py" not in build
assert "--latest" in build[build.find("release-h700:"):]
assert "gh release delete" not in build
assert "git/refs/tags/" not in build  # never force-move a published tag

# One audited publisher only: the old workflow_run path forced tags and
# deleted draft releases; the old release curation could DELETE Ver. 35.
for legacy in ("publish-ota-from-build.yml", "publish-ota-from-run.yml", "rebrand-releases.yml"):
    assert not (WORKFLOWS / legacy).exists(), f"Unsafe/stale H700 workflow remains: {legacy}"

print(
    f"PASS: H700 {version}: {len(static_patches)} literal patch references, "
    f"{len(python_tools)} ordered source stages, one non-destructive publisher"
)
