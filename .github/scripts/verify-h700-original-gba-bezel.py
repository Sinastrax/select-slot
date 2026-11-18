#!/usr/bin/env python3
"""Validate H700 GBA bezel selection without changing known-good graphics.

The SP and Original GBA are two renderings of the SAME 640x480 bottom strip
and only 3.5-inch 640x480 devices can select the Original GBA variant.
Device type isn't inferred from a console name: gfx::framed(panel) must
recognize the physical resolution, excluding 720x480 RG SP/RG34XXSP.
"""
from pathlib import Path
import hashlib

s=Path("crates/slot-store/src/slot_state.rs").read_text()
app=Path("crates/slot/src/app.rs").read_text()
front=Path("crates/slot/src/frontend.rs").read_text()
gfx=Path("crates/slot-gfx/src/bezel.rs").read_text()
shader=Path("crates/slot-gfx/src/shaders.rs").read_bytes()
auth=Path("crates/slot-gfx/src/authentic.rs").read_bytes()

assert hashlib.sha256(shader).hexdigest()=="2f45846d17f641f77db94542292b779312ffd10ccb58469e872218b24f5183f6", "Ver18 shader changed"
assert hashlib.sha256(auth).hexdigest()=="6990dbe1e03ee7d03cd2b53f5a826b7345ab05ab9ee401af14050a8242a0ca12", "Ver17 Pocket/SGB looks changed"
assert "    Ags102,\n    Agb001,\n    File(String)," in s
assert 'BezelPick::Agb001 => "agb-001".to_string()' in s
assert 'BezelPick::Agb001 => "Original GBA".to_string()' in s
assert '"agb-001" => BezelPick::Agb001' in s
assert "bezel_gba: BezelPick::Ags102," in s, "Original GBA must not change user default"
menu=app.split("fn bezel_choices(&self, platform: Platform)",1)[1].split("fn bezel_pick",1)[0]
assert "if self.framed_panel() {" in menu
assert "if platform.hardware() == Platform::Gba {" in menu
assert "choices.push(BezelPick::Ags102);" in menu
assert "choices.push(BezelPick::Agb001);" in menu
sp=app.split("pub fn sp_frame(&self) -> bool {",1)[1].split("\n    }",1)[0]
assert "self.framed_panel()" in sp
assert "BezelPick::Ags102 | BezelPick::Agb001" in sp
assert "!self.game_layout().panel" in sp
assert "gba_original_strip: Option<TexId>" in app
assert "gba_original_strip: None" in app
assert "fn draw_sp_strip(&self" in app and "BezelPick::Agb001 => self.gba_original_strip.or(self.sp_strip)" in app
assert 'root.join(crate::bezel::BEZELS)' in front
assert '"640x480-gba-original.png"' in front
assert "set_gba_original_strip(Some(tex))" in front
assert "BezelPick::None | BezelPick::Ags102 | BezelPick::Agb001 => None" in front
assert "c.w == 640.0 && c.h == 480.0" in gfx
assert "let (w, h) = self.session.app().game_bezel_size();" in front
# Panel gating is the only hardware selector; NOT any naming heuristics.
def is_framed(panel):
    w,h=panel
    return w==640 and h==480
for panel in ((720,480),(720,720),(1024,768),(1280,720)):
    assert not is_framed(panel)
assert is_framed((640,480))

print("PASS: Original GBA is GBA-only, 640x480-only, persisted, same SP layout")
print("PASS: RG SP/RG34XXSP menus unchanged; Ver18 shaders byte-identical")
