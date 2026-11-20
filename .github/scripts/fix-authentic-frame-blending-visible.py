#!/usr/bin/env python3
"""Restore upstream Authentic Frame Blending behavior after the source merge."""
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
new = """        for (platform, rows) in [
            (Platform::Gba, &[QuickRow::GbaColourCorrection][..]),
            (Platform::Gbc, &[QuickRow::GbcColourCorrection][..]),
            (
                Platform::Gb,
                &[QuickRow::GbColourCorrection, QuickRow::GbPalette][..],
            ),
        ] {
            if self.authentic(platform) {
                hidden.extend_from_slice(rows);
            }
        }
"""
if source.count(old) == 1:
    source = source.replace(old, new, 1)
else:
    palette_only = """        // Keep the GB palette hidden on monochrome Authentic models.
        // Pocket Color and GBC reveal it again immediately below.
        if self.authentic(Platform::Gb) {
            hidden.push(QuickRow::GbPalette);
        }
"""
    if source.count(palette_only) == 1:
        source = source.replace(palette_only, new, 1)
    else:
        assert source.count(new) == 1, "Expected the Authentic per-system row filter"
assert "QuickRow::GbaBlending" not in new

# The in-game Screen page has one context-sensitive row. It already reads and
# writes the playing platform's independent setting, so keep it visible for
# Authentic too; hiding it made the new per-system Authentic value impossible
# to reach while a game was running.
old = """        if self.authentic(platform) {
            // Color correction remains selectable for every Authentic screen.
            hidden.extend([QuickRow::Blending, QuickRow::Palette]);
        }
"""
new = """        if self.authentic(platform) {
            // Keep the system-only colour and palette controls out of the
            // in-game panel. Frame Blending stays available here.
            hidden.extend([QuickRow::ColourCorrection, QuickRow::Palette]);
        }
"""
if source.count(old) == 1:
    source = source.replace(old, new, 1)
else:
    intermediate = """        if self.authentic(platform) {
            // Keep the system-only colour and palette controls out of the
            // in-game panel. Frame Blending stays available here.
            hidden.extend([QuickRow::ColourCorrection, QuickRow::Palette]);
        }
"""
    earlier_intermediate = """        if self.authentic(platform) {
            // Color correction and Frame Blending remain independently
            // selectable for every Authentic screen.
            hidden.push(QuickRow::Palette);
        }
"""
    if source.count(intermediate) == 1:
        pass
    elif source.count(earlier_intermediate) == 1:
        source = source.replace(earlier_intermediate, intermediate, 1)
    else:
        assert source.count(new) == 1, "Expected the Authentic in-game screen filter"
path.write_text(source)

# The Authentic pipeline previously forced Ghosting at all times, ignoring
# the setting. Preserve the LCD ghost response by default, but honor Off/Mix/
# Ghosting; the established fast-forward override remains unconditionally Off.
pipeline = Path("crates/slot-gfx/src/pipeline.rs")
gpu = pipeline.read_text()
old = """    fn blend(&self) -> FrameBlend {
        match self.effect {
            ScreenEffect::Authentic if self.authentic_fast_forward => FrameBlend::Off,
            ScreenEffect::Authentic => FrameBlend::Ghosting,
            _ => self.blend,
        }
    }
"""
new = """    fn blend(&self) -> FrameBlend {
        effective_blend(self.effect, self.authentic_fast_forward, self.blend)
    }
"""
# Add a pure helper adjacent to the pipeline type so this behavior can be
# tested without initializing the handheld GPU.
helper = """fn effective_blend(
    effect: ScreenEffect,
    fast_forward: bool,
    configured: FrameBlend,
) -> FrameBlend {
    match (effect, fast_forward) {
        (ScreenEffect::Authentic, true) => FrameBlend::Off,
        _ => configured,
    }
}

#[cfg(test)]
mod authentic_blending_tests {
    use super::{effective_blend, FrameBlend, ScreenEffect};

    #[test]
    fn authentic_frame_blending_setting_is_used_and_fast_forward_forces_off() {
        assert_eq!(
            effective_blend(ScreenEffect::Authentic, false, FrameBlend::Off),
            FrameBlend::Off
        );
        assert_eq!(
            effective_blend(ScreenEffect::Authentic, false, FrameBlend::Mix),
            FrameBlend::Mix
        );
        assert_eq!(
            effective_blend(ScreenEffect::Authentic, false, FrameBlend::Ghosting),
            FrameBlend::Ghosting
        );
        assert_eq!(
            effective_blend(ScreenEffect::Authentic, true, FrameBlend::Ghosting),
            FrameBlend::Off
        );
        assert_eq!(
            effective_blend(ScreenEffect::None, true, FrameBlend::Mix),
            FrameBlend::Mix
        );
    }
}

"""
if gpu.count(old) == 1:
    gpu = gpu.replace(old, new, 1)
else:
    assert gpu.count(new) == 1, "Expected the Authentic fast-forward blend selector"
assert gpu.count("pub struct GamePass {") == 1, "Expected the pipeline struct"
anchor = "pub struct GamePass {"
if "fn effective_blend(" not in gpu:
    gpu = gpu.replace(anchor, helper + anchor, 1)
else:
    assert "(ScreenEffect::Authentic, true) => FrameBlend::Off" in gpu
pipeline.write_text(gpu)

# Keep the existing Authentic visibility test aligned with the intended UI.
tests = Path("crates/slot/tests/app.rs")
test_source = tests.read_text()
assert "assert!(!in_game.contains(&QuickRow::Blending));" in test_source
assert "assert!(!settings.contains(&QuickRow::GbBlending));" in test_source
old = "use slot_store::{GbColors, GbPalette, Platform, Shader};"
new = "use slot_store::{GbColors, Platform, Shader};"
if test_source.count(old) == 1:
    test_source = test_source.replace(old, new, 1)
else:
    assert test_source.count(new) == 1, "Expected Authentic Game Boy test imports"
old = "GbColors::Palette(GbPalette::GRAYSCALE)"
new = "GbColors::SgbAuto"
if test_source.count(old) == 1:
    test_source = test_source.replace(old, new, 1)
else:
    assert test_source.count(new) >= 1, "Expected current Authentic SGB model assertion"
tests.write_text(test_source)
print("Authentic Frame Blending is visible and honors its setting; fast-forward forces it off")
