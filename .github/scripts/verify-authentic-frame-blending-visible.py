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
print("PASS: Authentic has no system filter hiding separate Frame Blending")
