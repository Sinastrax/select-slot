"""Miyoo custom patches: bezels; applied in exact build order."""
from .patcher import edit

# Original horizontal GBA bottom strip: exactly the SP bezel's 640x480
# silhouette/opening and rendering path, with only the lower lettering changed.
# The existing AGS-102 option remains the default and is not modified.
edit("crates/slot-store/src/slot_state.rs", [
    ('''    Ags102,
    File(String),
}

impl BezelPick''',
     '''    Ags102,
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
     '''            BezelPick::Ags102 => "GBA SP".to_string(),
            BezelPick::Agb001 => "GBA".to_string(),
            BezelPick::File(name)'''),
    ('''            "" | "ags-102" => BezelPick::Ags102,
            other => BezelPick::File(other.to_string()),''',
     '''            "" | "ags-102" => BezelPick::Ags102,
            "agb-001" => BezelPick::Agb001,
            other => BezelPick::File(other.to_string()),'''),
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
        choices.extend''',
     '''        if self.framed_panel() {
            choices.push(BezelPick::Ags102);
            if platform == Platform::Gba {
                choices.push(BezelPick::Agb001);
            }
        }
        choices.extend'''),
    ('''    pub fn sp_frame(&self) -> bool {
        self.resolved_bezel(self.playing_platform()) == BezelPick::Ags102
    }''',
     '''    pub fn sp_frame(&self) -> bool {
        // The original-GBA strip uses the *same* picture position and
        // transparent opening as the current SP strip.
        matches!(self.resolved_bezel(self.playing_platform()),
            BezelPick::Ags102 | BezelPick::Agb001)
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
     '''        let chosen = if self.resolved_bezel(self.playing_platform()) == BezelPick::Agb001 {
            self.gba_strip.or(self.sp_strip)
        } else {
            self.sp_strip
        };
        let Some(tex) = chosen.filter(|_| shown) else {
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
        // Load the alternate lower lettering *once*. It uses exactly the
        // same texture coordinates, dimensions and static-surround caching
        // as the pre-existing SP bezel.
        let gba_path = self.session.app().root()
            .map(|root| root.join("System/bezels/gba-original.png"));
        if let Some(path) = gba_path {
            if let Some(rgba) = bezel_face(&path, panel.0, panel.1) {
                let tex = compositor.create_texture(panel.0, panel.1, &rgba);
                self.session.app_mut().set_gba_strip(Some(tex));
            }
        }
    }

    pub fn render'''),
    ('''            BezelPick::None | BezelPick::Ags102 => None,''',
     '''            BezelPick::None | BezelPick::Ags102 | BezelPick::Agb001 => None,'''),
])

