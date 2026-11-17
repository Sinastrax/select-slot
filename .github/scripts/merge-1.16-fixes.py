#!/usr/bin/env python3
"""Resolve renderer API overlap between the v1.15 select. slot. patches and Slot v1.16.

Slot 1.16 moved FrameBlend/LCD response into ghost.rs. Keep that upstream
implementation while preserving our Authentic correction and fast-forward paths.
Fail loudly when expected merged source changes.
"""
from pathlib import Path

gfx = Path("crates/slot-gfx/src")
pipeline = gfx / "pipeline.rs"
p = pipeline.read_text()

old_enum = """/// How each new frame meets the ones before it, at the game's own size before any scaling.
/// Authentic draws its LCD response except during fast-forward.
#[derive(Copy, Clone, PartialEq, Eq, Debug, Default)]
pub enum FrameBlend {
    #[default]
    Off,
    /// Each frame half and half with the one before it.
    Mix,
    /// Authentic's LCD response for the screen in play: each pixel slow to change, slower
    /// while it turns lighter.
    Ghosting,
}

"""
assert p.count(old_enum) == 1, "Expected obsolete FrameBlend enum not found"
p = p.replace(old_enum, "", 1)

old = "    screen: Screen,\n    ghost: Ghost,"
new = "    screen: Screen,\n    lcd: Lcd,\n    ghost: Ghost,"
assert p.count(old) == 1, "GamePass LCD field context changed"
p = p.replace(old, new, 1)

old = "            screen: Screen::Gba,\n            ghost,"
new = "            screen: Screen::Gba,\n            lcd: Lcd::Gba,\n            ghost,"
assert p.count(old) == 1, "GamePass LCD default context changed"
p = p.replace(old, new, 1)

old = "    fn blend(&self) -> FrameBlend {"
new = """    fn response(&self) -> [f32; 2] {
        self.lcd.response()
    }

    fn blend(&self) -> FrameBlend {"""
assert p.count(old) == 1, "GamePass blend selector moved"
p = p.replace(old, new, 1)
pipeline.write_text(p)

fbo = gfx / "fbo.rs"
s = fbo.read_text()

# Keep only one set_frame_blend and cut_frame_blend method, with the
# newest upstream set_lcd method and our additional Authentic controls.
first = """    pub fn set_frame_blend(&mut self, blend: crate::FrameBlend) {
        self.game.set_blend(blend, &self.quad);
    }

    pub fn set_authentic_fast_forward"""
assert s.count(first) == 1, "Old frame-blend method moved"
s = s.replace(first, "    pub fn set_authentic_fast_forward", 1)

old_cut = """    /// The game's picture jumped (another game, a state load, a reset): blend nothing of
    /// what came before into the next frame.
    pub fn cut_frame_blend(&mut self) {
        self.game.cut();
    }

    pub fn set_authentic_colour_correction"""
assert s.count(old_cut) == 1, "Old frame-blend cut method moved"
s = s.replace(old_cut, "    pub fn set_authentic_colour_correction", 1)
assert s.count("pub fn set_frame_blend(") == 1
assert s.count("pub fn cut_frame_blend(") == 1
fbo.write_text(s)

menu = Path("crates/slot-ui/src/quick_menu.rs")
q = menu.read_text()
old_count = "pub const SYSTEM: [QuickRow; 8] = ["
assert q.count(old_count) == 1, "Upstream system settings layout changed"
q = q.replace(old_count, "pub const SYSTEM: [QuickRow; 9] = [", 1)
menu.write_text(q)

power = Path("crates/slot-power/src/power.rs")
p = power.read_text()
old = "    pub fn battery(&self) -> Option<Battery> {"
new = """    // Slot 1.16 bottom-panel control, retained alongside our menu-only idle blanking.
    pub fn set_bottom_backlight(&mut self, on: bool) {
        self.platform.set_bottom_backlight(on);
    }

    pub fn battery(&self) -> Option<Battery> {"""
assert p.count(old) == 1 and "pub fn set_bottom_backlight(" not in p
power.write_text(p.replace(old, new, 1))

app = Path("crates/slot/src/app.rs")
a = app.read_text()
old = "        let turbo_off = slot_store::legacy_turbo_off(root);\n"
assert a.count(old) == 1, "Removed upstream legacy turbo migration changed"
a = a.replace(old, "", 1)
old = """        if turbo_off {
            app.turbo_off_moves_to_controls(root);
        }
"""
assert a.count(old) == 1, "Removed upstream turbo migration block changed"
a = a.replace(old, "", 1)
app.write_text(a)

invite = Path("crates/slot/src/invite.rs")
i = invite.read_text()
old = "        Core::Gambatte => 3,"
new = """        Core::Gambatte => 3,
        // SameBoy was removed from select. slot.'s bundled emulator choices.
        // Do not incorrectly announce it as a playable link core.
        Core::Sameboy => 0,"""
assert i.count(old) == 1, "Slot 1.16 invite core mapping changed"
invite.write_text(i.replace(old, new, 1))

print("Integrated GPU blending, nickname, USB/dual-panel APIs and removed turbo setting")
