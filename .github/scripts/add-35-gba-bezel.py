#!/usr/bin/env python3
"""Add a second, identically positioned GBA lower bezel on 640x480 H700 panels.

Run after all existing upstream merge and shader fixes. Do not modify any
shader/color/performance source. A separate packaging step installs the
pre-existing, attributed Perfect GBA artwork.
"""
from pathlib import Path


def edit(path: str, pairs: list[tuple[str, str]]) -> None:
    p = Path(path)
    original = p.read_text()
    out = original
    for old, new in pairs:
        if out.count(old) != 1:
            raise SystemExit(
                f"{path}: wanted exactly one occurrence of {old[:110]!r}; "
                f"found {out.count(old)}"
            )
        out = out.replace(old, new, 1)
    if original == out:
        raise SystemExit(f"{path}: no changes")
    p.write_text(out)
    print(f"Added 35-screen GBA bezel support: {path}")


edit("crates/slot-store/src/slot_state.rs", [
    ('''    Ags102,
    File(String),
}

impl BezelPick''',
     '''    Ags102,
    /// Original horizontal GBA artwork, using the SP bezel's screen opening.
    Agb001,
    File(String),
}

impl BezelPick'''),
    ('''            BezelPick::Ags102 => "ags-102".to_string(),
            BezelPick::File(name)''',
     '''            BezelPick::Ags102 => "ags-102".to_string(),
            BezelPick::Agb001 => "agb-001".to_string(),
            BezelPick::File(name)'''),
    ('''            BezelPick::Ags102 => "AGS-102".to_string(),
            BezelPick::File(name)''',
     '''            BezelPick::Ags102 => "AGS-102".to_string(),
            BezelPick::Agb001 => "GBA".to_string(),
            BezelPick::File(name)'''),
    ('''            "" | "ags-102" => BezelPick::Ags102,
            other => BezelPick::File(other.to_string()),''',
     '''            "" | "ags-102" => BezelPick::Ags102,
            "agb-001" => BezelPick::Agb001,
            other => BezelPick::File(other.to_string()),'''),
])

edit("crates/slot/src/bezel.rs", [
    ('''pub const GAME_BEZELS: &str = "Bezels";

pub fn list''',
     '''pub const GAME_BEZELS: &str = "Bezels";

/// The alternate original-GBA lower strip is intentionally exclusive to the
/// 3.5-inch 640x480 H700 layout. It must never appear on 720x480 RG34 screens,
/// larger 4:3 panels, or GB/GBC pages.
pub fn original_gba_available(panel: (u32, u32), platform: Platform) -> bool {
    panel == (640, 480) && platform.hardware() == Platform::Gba
}

pub fn list'''),
])

edit("crates/slot/src/app.rs", [
    ('''    sp_strip: Option<TexId>,
    eject_overlay: f32,''',
     '''    sp_strip: Option<TexId>,
    gba_strip: Option<TexId>,
    eject_overlay: f32,'''),
    ('''            sp_strip: None,
            eject_overlay: 0.0,''',
     '''            sp_strip: None,
            gba_strip: None,
            eject_overlay: 0.0,'''),
    ('''        if self.framed_panel() {
            choices.push(BezelPick::Ags102);
        }
        let scale = self.resolved_scale(platform);''',
     '''        if self.framed_panel() {
            choices.push(BezelPick::Ags102);
            if crate::bezel::original_gba_available(self.panel, platform) {
                choices.push(BezelPick::Agb001);
            }
        }
        let scale = self.resolved_scale(platform);'''),
    ('''    fn bezel_pick(&mut self, platform: Platform) -> &mut BezelPick {''',
     '''    /// Give only the GBA SP choice its GBA-specific name. The GB/GBC AGS-102
    /// labels and all pre-existing saved values remain untouched.
    pub fn bezel_label(&self, platform: Platform) -> String {
        let pick = self.resolved_bezel(platform);
        match (platform.hardware(), &pick) {
            (Platform::Gba, BezelPick::Ags102) => "GBA SP".to_string(),
            _ => pick.label(),
        }
    }

    fn bezel_pick(&mut self, platform: Platform) -> &mut BezelPick {'''),
    ('''    pub fn sp_frame(&self) -> bool {
        self.resolved_bezel(self.playing_platform()) == BezelPick::Ags102
            && !self.game_layout().panel
    }''',
     '''    pub fn sp_frame(&self) -> bool {
        // Both GBA silhouettes have the identical 640x480 screen opening and
        // *must* use the same lift and top-aligned picture geometry.
        matches!(
            self.resolved_bezel(self.playing_platform()),
            BezelPick::Ags102 | BezelPick::Agb001
        ) && !self.game_layout().panel
    }'''),
    ('''    pub fn set_sp_strip(&mut self, tex: Option<TexId>) {
        self.sp_strip = tex;
    }

    fn draw_sp_strip''',
     '''    pub fn set_sp_strip(&mut self, tex: Option<TexId>) {
        self.sp_strip = tex;
    }

    pub fn set_gba_strip(&mut self, tex: Option<TexId>) {
        self.gba_strip = tex;
    }

    fn draw_sp_strip'''),
    ('''        let Some(tex) = self.sp_strip.filter(|_| shown) else {
            return;
        };
        let canvas''',
     '''        let pick = self.resolved_bezel(self.playing_platform());
        let selected = if pick == BezelPick::Agb001 {
            self.gba_strip.or(self.sp_strip)
        } else {
            self.sp_strip
        };
        let Some(tex) = selected.filter(|_| shown) else {
            return;
        };
        let canvas'''),
])

edit("crates/slot/src/frontend.rs", [
    ('''            self.session.app_mut().set_sp_strip(Some(tex));
            eprintln!("slot: bezel {}", path.display());
        }
    }

    pub fn render''',
     '''            self.session.app_mut().set_sp_strip(Some(tex));
            eprintln!("slot: bezel {}", path.display());
        }
        // The alternate uses the exact SP strip's display coordinates. Load
        // it only on the 640x480 panel; no RG34XXSP/GBC/GB layout changes.
        if panel == (640, 480) {
            if let Some(root) = self.session.app().root() {
                let path = root.join("System/bezels/gba-original.png");
                if let Some(rgba) = bezel_face(&path, w, h) {
                    let tex = compositor.create_texture(w, h, &rgba);
                    self.session.app_mut().set_gba_strip(Some(tex));
                }
            }
        }
    }

    pub fn render'''),
    ('''            BezelPick::None | BezelPick::Ags102 => None,''',
     '''            BezelPick::None | BezelPick::Ags102 | BezelPick::Agb001 => None,'''),
    ('''        let label = app.resolved_bezel(platform).label();''',
     '''        let label = app.bezel_label(platform);'''),
])

edit("crates/slot/tests/bezel.rs", [
    ('''use slot::bezel::{pick, BEZELS};''',
     '''use slot::bezel::{original_gba_available, pick, BEZELS};'''),
    ('''#[test]
fn the_panel_takes_the_bezel_named_for_its_size()''',
     '''#[test]
fn original_gba_only_on_35_screen_and_only_for_gba() {
    use slot_store::{BezelPick, Platform};
    assert!(original_gba_available((640, 480), Platform::Gba));
    assert!(original_gba_available((640, 480), Platform::Gbav));
    for panel in [(720, 480), (1024, 768), (1280, 960), (640, 400)] {
        assert!(!original_gba_available(panel, Platform::Gba));
    }
    for platform in [Platform::Gb, Platform::Gbc] {
        assert!(!original_gba_available((640, 480), platform));
    }
    assert_eq!(BezelPick::parse("agb-001"), BezelPick::Agb001);
    assert_eq!(BezelPick::Agb001.key(), "agb-001");
    assert_eq!(BezelPick::Agb001.label(), "GBA");
    assert_eq!(BezelPick::Ags102.key(), "ags-102");
}

#[test]
fn the_panel_takes_the_bezel_named_for_its_size()'''),
])
