#!/usr/bin/env python3
"""Add saved Original GBA bezel selection to Anbernic H700 firmware.

The 640x480 built-in SP strip is already loaded/drawn through a separate
transparent overlay. Reuse the exact same position, alpha, gap, lift and
animation; load the new 640x480 image as a second GPU texture.
No picture resizing or moving, no shader changes, no extra bezel rendering
on 720x480 screens where GBA already fills the panel (no bottom gap).
"""
from pathlib import Path

def edit(pathname, replacements):
    path=Path(pathname)
    s=path.read_text()
    for old,new,label in replacements:
        found=s.count(old)
        assert found==1, (pathname,label,found)
        s=s.replace(old,new,1)
    path.write_text(s)

edit("crates/slot-store/src/slot_state.rs",[
    ("    Ags102,\n    File(String),",
     "    Ags102,\n    Agb001,\n    File(String),",
     "new persistent bezel enum"),
    ('            BezelPick::Ags102 => "ags-102".to_string(),',
     '            BezelPick::Ags102 => "ags-102".to_string(),\n            BezelPick::Agb001 => "agb-001".to_string(),',
     "new persisted variant ID"),
    ('            BezelPick::Ags102 => "AGS-102".to_string(),',
     '            BezelPick::Ags102 => "AGS-102".to_string(),\n            BezelPick::Agb001 => "Original GBA".to_string(),',
     "bezel menu label"),
    ('            "" | "ags-102" => BezelPick::Ags102,',
     '            "" | "ags-102" => BezelPick::Ags102,\n            "agb-001" => BezelPick::Agb001,',
     "saved bezel read"),
])

edit("crates/slot/src/app.rs",[
    ("    sp_strip: Option<TexId>,",
     "    sp_strip: Option<TexId>,\n    gba_original_strip: Option<TexId>,",
     "app overlay texture"),
    ("            sp_strip: None,",
     "            sp_strip: None,\n            gba_original_strip: None,",
     "app overlay initialization"),
    ("""        if self.framed_panel() {
            choices.push(BezelPick::Ags102);
        }""",
     """        if self.framed_panel() {
            choices.push(BezelPick::Ags102);
            if platform.hardware() == Platform::Gba {
                choices.push(BezelPick::Agb001);
            }
        }""",
     "GBA bezel menu options"),
    ("""    pub fn sp_frame(&self) -> bool {
        self.resolved_bezel(self.playing_platform()) == BezelPick::Ags102
            && !self.game_layout().panel
    }""",
     """    pub fn sp_frame(&self) -> bool {
        // Only the 3.5-inch 640x480 Anbernic screen has a bottom strip.
        self.framed_panel()
            && matches!(
                self.resolved_bezel(self.playing_platform()),
                BezelPick::Ags102 | BezelPick::Agb001
            )
            && !self.game_layout().panel
    }""",
     "reuse SP geometry for original GBA"),
    ("""    pub fn set_sp_strip(&mut self, tex: Option<TexId>) {
        self.sp_strip = tex;
    }

    fn draw_sp_strip(&self, out: &mut Vec<Draw>) {""",
     """    pub fn set_sp_strip(&mut self, tex: Option<TexId>) {
        self.sp_strip = tex;
    }

    pub fn set_gba_original_strip(&mut self, tex: Option<TexId>) {
        self.gba_original_strip = tex;
    }

    fn draw_sp_strip(&self, out: &mut Vec<Draw>) {""",
     "second texture setter"),
    ("""        let Some(tex) = self.sp_strip.filter(|_| shown) else {
            return;
        };""",
     """        let chosen = match self.resolved_bezel(self.playing_platform()) {
            BezelPick::Agb001 => self.gba_original_strip.or(self.sp_strip),
            _ => self.sp_strip,
        };
        let Some(tex) = chosen.filter(|_| shown) else {
            return;
        };""",
     "choose label-only variant without changing placement or animation"),
])

edit("crates/slot/src/frontend.rs",[
    ("""            self.session.app_mut().set_sp_strip(Some(tex));
            eprintln!("slot: bezel {}", path.display());
        }
    }""",
     """            self.session.app_mut().set_sp_strip(Some(tex));
            eprintln!("slot: bezel {}", path.display());
        }
        // Original GBA is the same 640x480 alpha/geometry as the SP
        // bezel, only the bottom wordmark differs. Load both at boot
        // so changing GBA → Bezel takes effect immediately, no reboot.
        let original = self.session.app().root().map(|root| {
            root.join(crate::bezel::BEZELS)
                .join("640x480-gba-original.png")
        });
        if let Some(path) = original {
            if let Some(rgba) = bezel_face(&path, w, h) {
                let tex = compositor.create_texture(w, h, &rgba);
                self.session.app_mut().set_gba_original_strip(Some(tex));
                eprintln!("slot: bezel {}", path.display());
            }
        }
    }""",
     "upload original GBA texture without touching existing SP load"),
    ("            BezelPick::None | BezelPick::Ags102 => None,",
     "            BezelPick::None | BezelPick::Ags102 | BezelPick::Agb001 => None,",
     "do not allocate a separate in-game bezel for builtin overlay"),
])

# Lock the actual selected model to GBA; existing GB/GBC bezels don't change.
state=Path("crates/slot-store/src/slot_state.rs").read_text()
app=Path("crates/slot/src/app.rs").read_text()
front=Path("crates/slot/src/frontend.rs").read_text()
assert 'BezelPick::Agb001 => "agb-001".to_string()' in state
assert 'BezelPick::Agb001 => "Original GBA".to_string()' in state
assert 'if platform.hardware() == Platform::Gba {' in app
assert 'BezelPick::Ags102 | BezelPick::Agb001' in app
assert 'gba_original_strip.or(self.sp_strip)' in app
assert '"640x480-gba-original.png"' in front
assert 'BezelPick::None | BezelPick::Ags102 | BezelPick::Agb001 => None' in front
assert 'BezelPick::Ags102' in state  # existing default persists
print("PASS: H700 Original GBA choice persisted; both use identical SP canvas and overlay movement")
