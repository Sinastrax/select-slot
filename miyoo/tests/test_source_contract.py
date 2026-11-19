"""Source-level regression checks for the select. slot. Miyoo port.

These checks complement (and do not replace) ARMv7/QEMU and device tests.
No network, SD card or connected handheld is needed.
"""
from pathlib import Path
import os
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]

def versions():
    pairs = {}
    for line in (ROOT / "version.env").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        pairs[key] = value
    return pairs


class MiyooSourceContract(unittest.TestCase):
    def test_single_version_source(self):
        info = versions()
        self.assertRegex(info["SLOT_VERSION"], r"^\d+\.\d+\.\d+$")
        self.assertRegex(info["CUSTOM_VERSION"], r"^[1-9]\d*$")
        self.assertRegex(info["PORT_COMMIT"], r"^[0-9a-f]{40}$")
        build = (ROOT / "build.sh").read_text()
        self.assertIn('. "$ROOT/miyoo/version.env"', build)
        self.assertIn('"$SLOT_VERSION" "$CUSTOM_VERSION"', build)
        self.assertNotIn('CUSTOM_VERSION="', build)

    def test_release_documents_match_single_version(self):
        info = versions()
        label = f'{info["SLOT_VERSION"]} Ver. {info["CUSTOM_VERSION"]}'
        tag = f'miyoo-v{info["SLOT_VERSION"]}-ver{info["CUSTOM_VERSION"]}'
        installation = (ROOT / "INSTALL.md").read_text()
        readme = (ROOT.parent / "README.md").read_text().split("## H700 features")[0]
        self.assertIn(label, installation)
        self.assertIn(label, readme)
        self.assertIn(tag, readme)
        self.assertNotIn("Settings → Restart", installation.split("## Features")[0])
        notes = ROOT.parent / ".github/release-notes" / f'miyoo-ver{info["CUSTOM_VERSION"]}.md'
        self.assertTrue(notes.is_file(), "current release notes must exist")

    def test_no_user_restart_paths(self):
        ui = (ROOT / "custom/ui.py").read_text()
        self.assertNotIn("QuickRow::Restart", ui)
        self.assertIn("Phase::About if action == Action::GbaDown(Btn::X)", ui)
        self.assertIn("'''        self.draw_side_legend(restart, true, link_legend_y(), out);", ui)
        self.assertNotIn("Command::new(\"reboot\")", ui)
        self.assertNotIn("Command::new(\"/lib/ld-linux-armhf.so.3\")", ui)

    def test_menu_settings_stay_bounded(self):
        ui = (ROOT / "custom/ui.py").read_text()
        self.assertIn("fn scrolls(page: &[QuickRow])", ui)
        self.assertIn("!page.is_empty()", ui)
        self.assertIn("menu_clock_tex", ui)
        self.assertIn("menu_battery_tex", ui)

    def test_onion_marker_distinguishes_stock_runtime(self):
        power = (ROOT / "custom/onion_power.py").read_text()
        self.assertIn('root.join(".tmp_update/runtime.sh").is_file()', power)
        self.assertIn('root.join(".tmp_update/onionVersion/version.txt").is_file()', power)
        self.assertIn("stock_runtime.set_backlight(9)", power)
        self.assertIn('onion.join("onionVersion/version.txt")', power)

    def test_gambatte_alias_preserves_old_game_settings(self):
        emu = (ROOT / "custom/emulators.py").read_text()
        self.assertIn('"gambatte" => Some(Core::Mgba)', emu)
        self.assertIn("Platform::Gb | Platform::Gbc => Core::Mgba", emu)
        self.assertIn("Platform::Gba => Core::Gpsp", emu)

    def test_output_patch_contract_when_provided(self):
        patch_path = os.environ.get("MIYOO_GENERATED_PATCH")
        if not patch_path:
            self.skipTest("generated patch available only in build CI")
        patch = Path(patch_path).read_text()
        self.assertIn('-            Phase::About if action == Action::GbaDown(Btn::X) => self.begin_restart(),', patch)
        self.assertIn("-        self.draw_side_legend(restart, true, link_legend_y(), out);", patch)
        self.assertIn("+    !page.is_empty()", patch)
        self.assertNotIn("+        QuickRow::Restart,", patch)
        info = versions()
        self.assertIn(
            f'+        version: "{info["SLOT_VERSION"]} Ver. {info["CUSTOM_VERSION"]}",',
            patch,
        )
        self.assertIn('onionVersion/version.txt', patch)
        self.assertNotIn('+        let _ = Command::new("reboot").status();', patch)


if __name__ == "__main__":
    unittest.main()
