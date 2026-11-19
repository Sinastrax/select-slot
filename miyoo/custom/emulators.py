"""Miyoo custom patches: emulators; applied in exact build order."""
from .patcher import edit

# Only the two original Miyoo emulator cores remain: mGBA (GB/GBC and
# optional GBA), gpSP (default GBA). Gambatte was removed for Ver. 3.
# Migrate a previous per-game core="gambatte" choice to mGBA without changing
# the rest of that game's saved profile or loading Gambatte as a fallback.
edit("crates/slot-store/src/core.rs", [
    ('            "gpsp" => Some(Core::Gpsp),',
     '            "gpsp" => Some(Core::Gpsp),\n            "gambatte" => Some(Core::Mgba),'),
    ('            Platform::Gba | Platform::Gb | Platform::Gbc => Core::Mgba,',
     '            Platform::Gba => Core::Gpsp,\n            Platform::Gb | Platform::Gbc => Core::Mgba,'),
])

# Per-game scaling stored in Config/video_mode.txt.
edit("crates/slot/src/video_mode.rs", [
    ("    Actual,\n    Stretch,\n}", "    Actual,\n    Stretch,\n    Integer,\n    Aspect,\n    Fill,\n    FullStretch,\n}"),
    ('            VideoMode::Stretch => "stretch",',
     '            VideoMode::Stretch => "stretch",\n            VideoMode::Integer => "integer",\n            VideoMode::Aspect => "aspect",\n            VideoMode::Fill => "fill",\n            VideoMode::FullStretch => "full-stretch",'),
    ('            "stretch" => Some(VideoMode::Stretch),',
     '            "stretch" => Some(VideoMode::Stretch),\n            "integer" => Some(VideoMode::Integer),\n            "aspect" => Some(VideoMode::Aspect),\n            "fill" => Some(VideoMode::Fill),\n            "full-stretch" => Some(VideoMode::FullStretch),'),
    ('''    }
}

pub fn video_mode_for''',
     '''    }

    pub fn next(self) -> VideoMode {
        match self {
            VideoMode::Actual | VideoMode::FullStretch => VideoMode::Integer,
            VideoMode::Integer => VideoMode::Aspect,
            VideoMode::Aspect | VideoMode::Stretch => VideoMode::Fill,
            VideoMode::Fill => VideoMode::FullStretch,
        }
    }

    pub fn previous(self) -> VideoMode {
        match self {
            VideoMode::Actual | VideoMode::Integer => VideoMode::FullStretch,
            VideoMode::Aspect => VideoMode::Integer,
            VideoMode::Fill | VideoMode::Stretch => VideoMode::Aspect,
            VideoMode::FullStretch => VideoMode::Fill,
        }
    }
}

pub fn video_mode_for'''),
    ('''    if (w, h) == (SRC_W, SRC_H) {
        return fit_width(PICTURE);
    }
    match mode {
        // The frame, not just the game inside it: the console body is drawn
        // around this and its opening has to land on the picture, so both
        // scale together. See `backdrop::frame_in`.
        VideoMode::Actual => fit_width(PICTURE),
        // Stretch overflows the panel on purpose -- what hangs over the side
        // is paper, and clipping it is how the picture fills the height -- so
        // it is not fitted.
        VideoMode::Stretch => {
            let k = out_h() as f32 / h as f32;
            [SRC_W as f32 * k, SRC_H as f32 * k]
        }
    }''',
     '''    // Source texture is 240x160 even for 160x144 GB; scale both together.
    let native_w = w as f32;
    let native_h = h as f32;
    let panel_w = out_w() as f32;
    let panel_h = out_h() as f32;
    match mode {
        VideoMode::Actual => fit_width(PICTURE),
        VideoMode::Integer => {
            let k = (panel_w / native_w).min(panel_h / native_h).floor().max(1.0);
            [SRC_W as f32 * k, SRC_H as f32 * k]
        }
        VideoMode::Aspect | VideoMode::Stretch => {
            if (w, h) == (SRC_W, SRC_H) && mode == VideoMode::Stretch {
                return fit_width(PICTURE);
            }
            let k = (panel_w / native_w).min(panel_h / native_h);
            [SRC_W as f32 * k, SRC_H as f32 * k]
        }
        VideoMode::Fill => {
            let k = (panel_w / native_w).max(panel_h / native_h);
            [SRC_W as f32 * k, SRC_H as f32 * k]
        }
        VideoMode::FullStretch => [
            SRC_W as f32 * panel_w / native_w,
            SRC_H as f32 * panel_h / native_h,
        ],
    }'''),
])
edit("crates/slot/src/app.rs", [
    ("self.set_picture(VideoMode::Stretch)", "self.set_picture(self.video_mode.next())"),
    ("self.set_picture(VideoMode::Actual)", "self.set_picture(self.video_mode.previous())"),
])

# Expose per-game scaling in the existing in-game Screen menu, including GBA
# (whose shoulder buttons must remain bound to the game).
edit("crates/slot-ui/src/quick_menu.rs", [
    ("    AutoLoad,\n}\n\nimpl QuickRow", "    AutoLoad,\n    Scaling,\n}\n\nimpl QuickRow"),
    ("pub const ALL: [QuickRow; 80]", "pub const ALL: [QuickRow; 81]"),
    ("        QuickRow::AutoLoad,\n    ];\n\n    pub const MAIN:",
     "        QuickRow::AutoLoad,\n        QuickRow::Scaling,\n    ];\n\n    pub const MAIN:"),
    ("pub const PLAY_SCREEN: [QuickRow; 6]", "pub const PLAY_SCREEN: [QuickRow; 7]"),
    ("        QuickRow::Shader,\n        QuickRow::Bezel,",
     "        QuickRow::Shader,\n        QuickRow::Scaling,\n        QuickRow::Bezel,"),
    ("QuickRow::Shader | QuickRow::ColourCorrection | QuickRow::Palette | QuickRow::Bezel => {",
     "QuickRow::Shader | QuickRow::Scaling | QuickRow::ColourCorrection | QuickRow::Palette | QuickRow::Bezel => {"),
    ('            QuickRow::AutoLoad => "Load State on Insert",',
     '            QuickRow::AutoLoad => "Load State on Insert",\n            QuickRow::Scaling => "Scaling",'),
    ("    Level9,\n}\n\nimpl QuickValue",
     "    Level9,\n    ScaleActual,\n    ScaleInteger,\n    ScaleAspect,\n    ScaleFill,\n    ScaleFull,\n}\n\nimpl QuickValue"),
    ("pub const ALL: [QuickValue; 33]", "pub const ALL: [QuickValue; 38]"),
    ("        QuickValue::Level9,\n    ];\n\n    pub const LEVELS:",
     "        QuickValue::Level9,\n        QuickValue::ScaleActual,\n        QuickValue::ScaleInteger,\n        QuickValue::ScaleAspect,\n        QuickValue::ScaleFill,\n        QuickValue::ScaleFull,\n    ];\n\n    pub const LEVELS:"),
    ('            QuickValue::Level9 => "9",',
     '            QuickValue::Level9 => "9",\n            QuickValue::ScaleActual => "Original",\n            QuickValue::ScaleInteger => "Integer",\n            QuickValue::ScaleAspect => "Aspect Fit",\n            QuickValue::ScaleFill => "Fill / Crop",\n            QuickValue::ScaleFull => "Full Stretch",'),
])
edit("crates/slot/src/app.rs", [
    ("            QuickRow::Brightness => Some(QuickValue::level(self.state.brightness)),",
     '''            QuickRow::Scaling => Some(match self.video_mode {
                VideoMode::Actual => QuickValue::ScaleActual,
                VideoMode::Integer => QuickValue::ScaleInteger,
                VideoMode::Stretch | VideoMode::Aspect => QuickValue::ScaleAspect,
                VideoMode::Fill => QuickValue::ScaleFill,
                VideoMode::FullStretch => QuickValue::ScaleFull,
            }),
            QuickRow::Brightness => Some(QuickValue::level(self.state.brightness)),'''),
    ('''        let row = self.playing_row(row);
        if let QuickRow::Brightness | QuickRow::BlueLight = row {''',
     '''        let row = self.playing_row(row);
        if row == QuickRow::Scaling {
            let to = if right { self.video_mode.next() } else { self.video_mode.previous() };
            self.set_picture(to);
            return;
        }
        if let QuickRow::Brightness | QuickRow::BlueLight = row {'''),
])


# Separate Power On resume from manual insertion, matching the H700 setting.
# Backward compatibility: existing auto_load value seeds resume_power_on once.
edit("crates/slot-store/src/slot_state.rs", [
    ("    pub auto_load: bool,\n    pub eject_save: bool,",
     "    pub auto_load: bool,\n    pub resume_power_on: bool,\n    pub eject_save: bool,"),
    ("            auto_load: true,\n            eject_save: true,",
     "            auto_load: true,\n            resume_power_on: true,\n            eject_save: true,"),
    ('    text.push_str(&format!("auto_load={}\\n", s.auto_load as u8));',
     '    text.push_str(&format!("auto_load={}\\n", s.auto_load as u8));\n    text.push_str(&format!("resume_power_on={}\\n", s.resume_power_on as u8));'),
    ("    let mut auto_load = None;\n    let mut eject_save = None;",
     "    let mut auto_load = None;\n    let mut resume_power_on = None;\n    let mut eject_save = None;"),
    ('            "auto_load" => auto_load = flag(value),',
     '            "auto_load" => auto_load = flag(value),\n            "resume_power_on" => resume_power_on = flag(value),'),
    ("        auto_load: auto_load.unwrap_or(fallback.auto_load),",
     "        auto_load: auto_load.unwrap_or(fallback.auto_load),\n        resume_power_on: resume_power_on.or(auto_load).unwrap_or(fallback.resume_power_on),"),
])
edit("crates/slot/src/app.rs", [
    ('''                if self.state.auto_load {
                    self.insert(false);''',
     '''                if self.state.resume_power_on {
                    self.insert(false);'''),
    ("            QuickRow::AutoLoad => Some(QuickValue::flag(self.state.auto_load)),",
     "            QuickRow::AutoLoad => Some(QuickValue::flag(self.state.auto_load)),\n            QuickRow::ResumePowerOn => Some(QuickValue::flag(self.state.resume_power_on)),"),
    ("            QuickRow::AutoLoad => s.auto_load = !s.auto_load,",
     "            QuickRow::AutoLoad => s.auto_load = !s.auto_load,\n            QuickRow::ResumePowerOn => s.resume_power_on = !s.resume_power_on,"),
])
edit("crates/slot-ui/src/quick_menu.rs", [
    ("    Scaling,\n}\n\nimpl QuickRow", "    Scaling,\n    ResumePowerOn,\n}\n\nimpl QuickRow"),
    ("pub const ALL: [QuickRow; 81]", "pub const ALL: [QuickRow; 82]"),
    ("        QuickRow::Scaling,\n    ];\n\n    pub const MAIN:",
     "        QuickRow::Scaling,\n        QuickRow::ResumePowerOn,\n    ];\n\n    pub const MAIN:"),
    ("pub const GAME: [QuickRow; 8]", "pub const GAME: [QuickRow; 9]"),
    ("        QuickRow::AutoLoad,\n        QuickRow::EjectSave,",
     "        QuickRow::AutoLoad,\n        QuickRow::ResumePowerOn,\n        QuickRow::EjectSave,"),
    ("            | QuickRow::AutoLoad\n            | QuickRow::EjectSave => &QuickRow::GAME,",
     "            | QuickRow::AutoLoad\n            | QuickRow::ResumePowerOn\n            | QuickRow::EjectSave => &QuickRow::GAME,"),
    ('            QuickRow::AutoLoad => "Load State on Insert",',
     '            QuickRow::AutoLoad => "Resume on Insert",\n            QuickRow::ResumePowerOn => "Resume on Power On",'),
])


# The scaling and resume settings also have to appear in exhaustive legacy
# action handlers; unlike the removed power/idle rows these need no
# additional system hooks or timer callbacks.
edit("crates/slot/src/app.rs", [
    ('''            | QuickRow::AutoLoad
            | QuickRow::EjectSave''',
     '''            | QuickRow::AutoLoad
            | QuickRow::Scaling
            | QuickRow::ResumePowerOn
            | QuickRow::EjectSave'''),
    ('''            | QuickRow::LidOff => return,''',
     '''            | QuickRow::LidOff
            | QuickRow::Scaling => return,'''),
])

# Retain the neutral GB palette Off choice, distinct from automatic colors.
# Off remains the default on mGBA, without any Gambatte dependency.
edit("crates/slot-store/src/gb_palette.rs", [
    ('''pub enum GbColors {
    Auto,
    Palette(GbPalette),
}''',
     '''pub enum GbColors {
    Off,
    Auto,
    Palette(GbPalette),
}'''),
    ('''        std::iter::once(GbColors::Auto).chain(GbPalette::all().map(GbColors::Palette))''',
     '''        [GbColors::Off, GbColors::Auto]
            .into_iter()
            .chain(GbPalette::all().map(GbColors::Palette))'''),
    ('''            GbColors::Auto => 0,
            GbColors::Palette(p) => p.index() + 1,''',
     '''            GbColors::Off => 0,
            GbColors::Auto => 1,
            GbColors::Palette(p) => p.index() + 2,'''),
    ('''            GbColors::Auto => GbColors::Palette(GbPalette(0)),
            GbColors::Palette(p) if p.index() + 1 == GbPalette::COUNT => GbColors::Auto,''',
     '''            GbColors::Off => GbColors::Auto,
            GbColors::Auto => GbColors::Palette(GbPalette(0)),
            GbColors::Palette(p) if p.index() + 1 == GbPalette::COUNT => GbColors::Off,'''),
    ('''            GbColors::Auto => GbColors::Palette(GbPalette((GbPalette::COUNT - 1) as u8)),
            GbColors::Palette(p) if p.index() == 0 => GbColors::Auto,''',
     '''            GbColors::Off => GbColors::Palette(GbPalette((GbPalette::COUNT - 1) as u8)),
            GbColors::Auto => GbColors::Off,
            GbColors::Palette(p) if p.index() == 0 => GbColors::Auto,'''),
    ('''    pub fn label(self) -> &'static str {
        match self {
            GbColors::Auto => "Auto",''',
     '''    pub fn label(self) -> &'static str {
        match self {
            GbColors::Off => "Off",
            GbColors::Auto => "Auto",'''),
    ('''    pub fn core_name(self) -> &'static str {
        match self {
            GbColors::Auto => "Auto",''',
     '''    pub fn core_name(self) -> &'static str {
        match self {
            GbColors::Off => "Off",
            GbColors::Auto => "Auto",'''),
])
edit("crates/slot-store/src/slot_state.rs", [
    ('''    pub gb_palettes: bool,
    pub gb_palette: GbPalette,''',
     '''    pub gb_palettes: bool,
    pub gb_colors_off: bool,
    pub gb_palette: GbPalette,'''),
    ('''    pub fn gb_colors(&self) -> GbColors {
        match self.gb_palettes {
            true => GbColors::Palette(self.gb_palette),
            false => GbColors::Auto,
        }
    }

    pub fn set_gb_colors(&mut self, to: GbColors) {
        match to {
            GbColors::Auto => self.gb_palettes = false,
            GbColors::Palette(p) => {
                self.gb_palettes = true;
                self.gb_palette = p;
            }
        }
    }''',
     '''    pub fn gb_colors(&self) -> GbColors {
        if self.gb_colors_off {
            GbColors::Off
        } else if self.gb_palettes {
            GbColors::Palette(self.gb_palette)
        } else {
            GbColors::Auto
        }
    }

    pub fn set_gb_colors(&mut self, to: GbColors) {
        match to {
            GbColors::Off => {
                self.gb_colors_off = true;
                self.gb_palettes = false;
            }
            GbColors::Auto => {
                self.gb_colors_off = false;
                self.gb_palettes = false;
            }
            GbColors::Palette(p) => {
                self.gb_colors_off = false;
                self.gb_palettes = true;
                self.gb_palette = p;
            }
        }
    }'''),
    ('''            gb_palettes: false,
            gb_palette: GbPalette::DEFAULT,''',
     '''            gb_palettes: false,
            gb_colors_off: true,
            gb_palette: GbPalette::DEFAULT,'''),
    ('''    text.push_str(&format!(
        "colour_correction_gbc={}\\n",''',
     '''    text.push_str(&format!("gb_colors_off={}\\n", s.gb_colors_off as u8));
    text.push_str(&format!(
        "colour_correction_gbc={}\\n",'''),
    ('''    let mut gb_palettes = None;
    let mut gb_palette = None;''',
     '''    let mut gb_palettes = None;
    let mut gb_colors_off = None;
    let mut gb_palette = None;'''),
    ('''            "gb_palettes" => gb_palettes = flag(value),''',
     '''            "gb_palettes" => gb_palettes = flag(value),
            "gb_colors_off" => gb_colors_off = flag(value),'''),
    ('''        gb_palettes: gb_palettes.unwrap_or(fallback.gb_palettes),
        gb_palette: gb_palette.unwrap_or(fallback.gb_palette),''',
     '''        gb_palettes: gb_palettes.unwrap_or(fallback.gb_palettes),
        // Preserve selected palettes from existing Slot installations.
        // Older Auto setups migrate to neutral Off.
        gb_colors_off: gb_colors_off.unwrap_or(!gb_palettes.unwrap_or(false)),
        gb_palette: gb_palette.unwrap_or(fallback.gb_palette),'''),
])


