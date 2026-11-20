#!/usr/bin/env python3
"""Verify Authentic hides neither system-specific Frame Blending setting."""
from pathlib import Path

source = Path("crates/slot/src/app.rs").read_text()
start = source.index("fn hidden_rows_any_panel")
end = source.index("\n    pub fn lid_off_min", start + 1)
section = source[start:end]
assert "hidden.push(QuickRow::GbPalette);" in section
assert "QuickRow::GbaBlending" not in section
assert "QuickRow::GbcBlending" not in section
assert "QuickRow::GbBlending" not in section

start = source.index("pub fn in_game_hidden")
end = source.index("\n    pub fn", start + 1)
in_game = source[start:end]
assert "hidden.push(QuickRow::Palette);" in in_game
assert "hidden.extend([QuickRow::Blending, QuickRow::Palette]);" not in in_game
assert "hidden.push(QuickRow::Blending);" not in in_game

pipeline = Path("crates/slot-gfx/src/pipeline.rs").read_text()
assert "effective_blend(self.effect, self.authentic_fast_forward, self.blend)" in pipeline
assert "(ScreenEffect::Authentic, true) => FrameBlend::Off" in pipeline
assert "fn authentic_frame_blending_setting_is_used_and_fast_forward_forces_off()" in pipeline

repo = Path(__file__).resolve().parents[2]
catalog = (repo / "handheld-i18n/de.tsv").read_text().splitlines()
assert "Frame Blending\tBildmischung" in catalog

print("PASS: Authentic system and in-game Frame Blending is visible, adjustable, German-localized, and off during Authentic fast-forward")
