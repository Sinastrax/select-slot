#!/usr/bin/env python3
"""Keep the separate per-system Frame Blending row available in Authentic."""
from pathlib import Path

path = Path("crates/slot/src/app.rs")
source = path.read_text()
old = """        for (platform, rows) in [
            (
                Platform::Gba,
                &[QuickRow::GbaBlending][..],
            ),
            (
                Platform::Gbc,
                &[QuickRow::GbcBlending][..],
            ),
            (
                Platform::Gb,
                &[
                    QuickRow::GbBlending,
                    QuickRow::GbPalette,
                ][..],
            ),
        ] {
            if self.authentic(platform) {
                hidden.extend_from_slice(rows);
            }
        }
"""
new = """        // Keep the GB palette hidden on monochrome Authentic models.
        // Pocket Color and GBC reveal it again immediately below.
        if self.authentic(Platform::Gb) {
            hidden.push(QuickRow::GbPalette);
        }
"""
assert source.count(old) == 1, "Expected the Authentic per-system row filter"
source = source.replace(old, new, 1)
assert "QuickRow::GbaBlending" not in new
path.write_text(source)
print("Authentic retains the separate Game Boy, Color and Advance Frame Blending controls")
