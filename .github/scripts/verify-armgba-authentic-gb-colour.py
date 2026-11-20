#!/usr/bin/env python3
"""Verify Pocket Color and SGB selections reach armGBA's Game Boy model."""
from pathlib import Path

core = Path("crates/slot/src/core.rs").read_text()
assert 'Some(GbColors::GbcAuto) => Some("Game Boy Color")' in core
assert 'Some(GbColors::SgbAuto) => Some("Game Boy")' in core
armgba = core.split("Core::Armgba => {", 1)[1].split("#[cfg(feature = \"nds\")]", 1)[0]
assert "armgba_palette_model(palette)" in armgba
assert 'core.set_option("armgba_gb_model", model);' in armgba
print("PASS: armGBA receives GBC hardware for Pocket Color and DMG/SGB mode for SGB")
