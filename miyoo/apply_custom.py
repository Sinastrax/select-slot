#!/usr/bin/env python3
"""Create a Miyoo-only patch after Dean's device patches, without touching H700.
Runs against the already patched upstream checkout. Exact replacements fail closed.
"""
from pathlib import Path
from difflib import unified_diff
import sys

src = Path(sys.argv[1])
dest = Path(sys.argv[2])
changes = {}
desired = {}

def edit(path, operations):
    file = src / path
    original = file.read_text()
    new = desired.get(path, original)
    for before, after in operations:
        count = new.count(before)
        if count != 1:
            raise RuntimeError(f"{path}: expected exactly one match, found {count}: {before[:100]!r}")
        new = new.replace(before, after, 1)
    diff = "".join(unified_diff(
        original.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"a/{path}", tofile=f"b/{path}", n=4
    ))
    if not diff:
        raise RuntimeError(f"{path}: no changes")
    desired[path] = new
    changes[path] = diff

edit("crates/slot-store/src/core.rs", [
    ("    Gpsp,\n}", "    Gpsp,\n    Gambatte,\n}"),
    ('            Core::Gpsp => "gpsp",', '            Core::Gpsp => "gpsp",\n            Core::Gambatte => "gambatte",'),
    ('            Core::Gpsp => "gpSP",', '            Core::Gpsp => "gpSP",\n            Core::Gambatte => "Gambatte",'),
    ('            "gpsp" => Some(Core::Gpsp),', '            "gpsp" => Some(Core::Gpsp),\n            "gambatte" => Some(Core::Gambatte),'),
    ('            Core::Gpsp => platform == Platform::Gba,',
     '            Core::Gpsp => platform == Platform::Gba,\n            Core::Gambatte => platform != Platform::Gba,'),
    ('            Platform::Gba | Platform::Gb | Platform::Gbc => Core::Mgba,',
     '            Platform::Gba => Core::Gpsp,\n            Platform::Gb | Platform::Gbc => Core::Gambatte,'),
])
# Keep the classic two-chip GBA picker unchanged. GB/GBC now default to Gambatte.
# mGBA remains available for explicit legacy selections; no SGB mode is added.

edit("crates/slot/src/core.rs", [
    ('        Core::Gpsp => Some((\n            "gpsp_color_correction",',
     '        Core::Gambatte => Some((\n            "gambatte_gbc_color_correction",\n            if on { "GBC only" } else { "disabled" },\n        )),\n        Core::Gpsp => Some((\n            "gpsp_color_correction",'),
    ('    if which == Core::Gpsp {\n        core.set_option("gpsp_serial", serial);',
     '''    if which == Core::Gambatte {
        // Do not request SGB palettes or emulate SGB hardware. GB titles may
        // use the chosen built-in palette; GBC titles supply their own colors.
        match palette {
            Some(slot_store::GbColors::Palette(p)) => {
                let name = match p.label() {
                    "DMG Green" => "GB - DMG",
                    "GB Pocket" => "GB - Pocket",
                    "GB Light" => "GB - Light",
                    "Grayscale" => "GBC - Grayscale",
                    "GBC Brown" => "GBC - Brown",
                    "GBC Red" => "GBC - Red",
                    "GBC Dark Brown" => "GBC - Dark Brown",
                    "GBC Blue" => "GBC - Blue",
                    "GBC Dark Blue" => "GBC - Dark Blue",
                    "GBC Green" => "GBC - Green",
                    "GBC Dark Green" => "GBC - Dark Green",
                    other if other.starts_with("GBC ") => "GBC - Grayscale",
                    _ => "GB - DMG",
                };
                core.set_option("gambatte_gb_colorization", "internal");
                core.set_option("gambatte_gb_internal_palette", name);
            }
            Some(slot_store::GbColors::Auto) => core.set_option("gambatte_gb_colorization", "GBC"),
            Some(slot_store::GbColors::Off) | None => core.set_option("gambatte_gb_colorization", "disabled"),
        }
        if let Some((key, value)) = colour_option(which, platform, colour) {
            core.set_option(key, value);
        }
        core.set_option("gambatte_gbc_color_correction_mode", "fast");
    }
    if which == Core::Gpsp {
        core.set_option("gpsp_serial", serial);'''),
])
# Update palette changes live for Gambatte rather than writing mGBA options to it.
edit("crates/slot/src/session.rs", [
    ('                emu.set_option("mgba_gb_colors", p.core_name());',
     '''                match self.app.core() {
                    slot_store::Core::Gambatte => {
                        // Gambatte options are core-specific. Reopen on a
                        // palette change to ensure the new core settings apply.
                        if let slot_store::GbColors::Palette(palette) = p {
                            let name = match palette.label() {
                                "DMG Green" => "GB - DMG",
                                "GB Pocket" => "GB - Pocket",
                                "GB Light" => "GB - Light",
                                "Grayscale" => "GBC - Grayscale",
                                "GBC Brown" => "GBC - Brown",
                                "GBC Red" => "GBC - Red",
                                "GBC Dark Brown" => "GBC - Dark Brown",
                                "GBC Blue" => "GBC - Blue",
                                "GBC Dark Blue" => "GBC - Dark Blue",
                                "GBC Green" => "GBC - Green",
                                "GBC Dark Green" => "GBC - Dark Green",
                                _ => "GB - DMG",
                            };
                            emu.set_option("gambatte_gb_colorization", "internal");
                            emu.set_option("gambatte_gb_internal_palette", name);
                        } else if p == slot_store::GbColors::Auto {
                            emu.set_option("gambatte_gb_colorization", "GBC");
                        } else {
                            emu.set_option("gambatte_gb_colorization", "disabled");
                        }
                    }
                    _ => emu.set_option("mgba_gb_colors", p.core_name()),
                }'''),
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

# Menu-only screen blank and shutdown timers. Live gameplay is excluded.
edit("crates/slot-store/src/slot_state.rs", [
    ("pub const LID_OFF_MIN: [u8; 6] = [1, 3, 5, 10, 15, 30];",
     "pub const LID_OFF_MIN: [u8; 6] = [1, 3, 5, 10, 15, 30];\npub const MENU_IDLE_MINUTES: [u8; 7] = [0, 1, 3, 5, 10, 15, 30];"),
    ("    pub lid_off_min: Option<u8>,\n    pub bezel_gba: BezelPick,",
     "    pub lid_off_min: Option<u8>,\n    pub menu_screen_off_min: u8,\n    pub menu_power_off_min: u8,\n    pub bezel_gba: BezelPick,"),
    ("            lid_off_min: None,\n            bezel_gba: BezelPick::Ags102,",
     "            lid_off_min: None,\n            menu_screen_off_min: 3,\n            menu_power_off_min: 15,\n            bezel_gba: BezelPick::Ags102,"),
    ('    text.push_str(&format!("auto_load={}\\n", s.auto_load as u8));',
     '    text.push_str(&format!("auto_load={}\\n", s.auto_load as u8));\n    text.push_str(&format!("menu_screen_off_min={}\\n", s.menu_screen_off_min));\n    text.push_str(&format!("menu_power_off_min={}\\n", s.menu_power_off_min));'),
    ("    let mut lid_off_min = None;\n    let mut bezel_gba = None;",
     "    let mut lid_off_min = None;\n    let mut menu_screen_off_min = None;\n    let mut menu_power_off_min = None;\n    let mut bezel_gba = None;"),
    ('            "lid_off_min" => lid_off_min = value.parse().ok().filter(|m| LID_OFF_MIN.contains(m)),',
     '            "lid_off_min" => lid_off_min = value.parse().ok().filter(|m| LID_OFF_MIN.contains(m)),\n            "menu_screen_off_min" => menu_screen_off_min = value.parse().ok().filter(|m| MENU_IDLE_MINUTES.contains(m)),\n            "menu_power_off_min" => menu_power_off_min = value.parse().ok().filter(|m| MENU_IDLE_MINUTES.contains(m)),'),
    ("        lid_off_min,\n        bezel_gba: bezel_gba.unwrap_or(fallback.bezel_gba),",
     "        lid_off_min,\n        menu_screen_off_min: menu_screen_off_min.unwrap_or(fallback.menu_screen_off_min),\n        menu_power_off_min: menu_power_off_min.unwrap_or(fallback.menu_power_off_min),\n        bezel_gba: bezel_gba.unwrap_or(fallback.bezel_gba),"),
])
edit("crates/slot-ui/src/quick_menu.rs", [
    ("    ResumePowerOn,\n}\n\nimpl QuickRow",
     "    ResumePowerOn,\n    MenuScreenOff,\n    MenuPowerOff,\n}\n\nimpl QuickRow"),
    ("pub const ALL: [QuickRow; 82]", "pub const ALL: [QuickRow; 84]"),
    ("        QuickRow::ResumePowerOn,\n    ];\n\n    pub const MAIN:",
     "        QuickRow::ResumePowerOn,\n        QuickRow::MenuScreenOff,\n        QuickRow::MenuPowerOff,\n    ];\n\n    pub const MAIN:"),
    ("pub const GENERAL: [QuickRow; 7]", "pub const GENERAL: [QuickRow; 9]"),
    ("        QuickRow::LidOff,\n        QuickRow::DateTime,",
     "        QuickRow::LidOff,\n        QuickRow::MenuScreenOff,\n        QuickRow::MenuPowerOff,\n        QuickRow::DateTime,"),
    ("            | QuickRow::LidOff => &QuickRow::GENERAL,",
     "            | QuickRow::LidOff\n            | QuickRow::MenuScreenOff\n            | QuickRow::MenuPowerOff => &QuickRow::GENERAL,"),
    ('            QuickRow::LidOff => "Lid Power Off",',
     '            QuickRow::LidOff => "Lid Power Off",\n            QuickRow::MenuScreenOff => "Menu Screen Off",\n            QuickRow::MenuPowerOff => "Menu Power Off",'),
])
edit("crates/slot/src/app.rs", [
    ("    power: Option<Power>,\n    dozed_at: Millis,",
     "    power: Option<Power>,\n    menu_last_input: Millis,\n    menu_screen_blanked: bool,\n    dozed_at: Millis,"),
    ("            power: None,\n            dozed_at: 0,",
     "            power: None,\n            menu_last_input: 0,\n            menu_screen_blanked: false,\n            dozed_at: 0,"),
    ("    fn timers(&mut self) {\n        self.play_hold();",
     "    fn timers(&mut self) {\n        self.tick_menu_idle();\n        self.play_hold();"),
    ("    pub fn apply(&mut self, action: Action) {\n        self.track_held_dir(action);",
     '''    pub fn apply(&mut self, action: Action) {
        // Physical releases are not wake actions. The first press while
        // blanked wakes the screen but does not activate menu selections.
        if !matches!(action, Action::GbaUp(_) | Action::MenuChordUp(_) | Action::PowerOff | Action::LidClose) {
            self.menu_last_input = self.now();
            if self.menu_screen_blanked {
                self.menu_screen_blanked = false;
                if let Some(power) = &mut self.power {
                    power.set_backlight(self.state.brightness);
                }
                return;
            }
        }
        self.track_held_dir(action);'''),
    ("    fn timers(&mut self) {",
     '''    fn tick_menu_idle(&mut self) {
        let now = self.now();
        let allowed = matches!(self.phase, Phase::Shelf | Phase::QuickMenu { .. })
            && self.game_menu.is_none()
            && self.core_picker.is_none()
            && !self.powering_off
            && !self.card_writes.failing();
        if !allowed {
            self.menu_last_input = now;
            if self.menu_screen_blanked {
                self.menu_screen_blanked = false;
                if let Some(power) = &mut self.power {
                    power.set_backlight(self.state.brightness);
                }
            }
            return;
        }
        let elapsed = now.saturating_sub(self.menu_last_input);
        let off = self.state.menu_power_off_min as u64 * 60_000;
        if off != 0 && elapsed >= off {
            self.menu_last_input = now;
            self.poweroff();
            return;
        }
        let blank = self.state.menu_screen_off_min as u64 * 60_000;
        if blank != 0 && elapsed >= blank && !self.menu_screen_blanked {
            self.menu_screen_blanked = true;
            if let Some(power) = &mut self.power {
                power.set_backlight(0);
            }
        }
    }

    fn timers(&mut self) {'''),
    ("            QuickRow::LidOff => QuickValue::LID_OFF",
     '''            QuickRow::MenuScreenOff | QuickRow::MenuPowerOff => {
                let n = if row == QuickRow::MenuScreenOff {
                    self.state.menu_screen_off_min
                } else {
                    self.state.menu_power_off_min
                };
                Some(match n {
                    1 => QuickValue::Min1,
                    3 => QuickValue::Min3,
                    5 => QuickValue::Min5,
                    10 => QuickValue::Min10,
                    15 => QuickValue::Min15,
                    30 => QuickValue::Min30,
                    _ => QuickValue::Off,
                })
            }
            QuickRow::LidOff => QuickValue::LID_OFF'''),
    ("        if row == QuickRow::LidOff {\n",
     '''        if matches!(row, QuickRow::MenuScreenOff | QuickRow::MenuPowerOff) {
            let values = [0u8, 1, 3, 5, 10, 15, 30];
            let from = if row == QuickRow::MenuScreenOff {
                self.state.menu_screen_off_min
            } else {
                self.state.menu_power_off_min
            };
            let at = values.iter().position(|m| *m == from).unwrap_or(0);
            let next = values[if right { (at + 1) % values.len() } else { (at + values.len() - 1) % values.len() }];
            if row == QuickRow::MenuScreenOff {
                self.state.menu_screen_off_min = next;
                if next == 0 && self.menu_screen_blanked {
                    self.menu_screen_blanked = false;
                    if let Some(power) = &mut self.power {
                        power.set_backlight(self.state.brightness);
                    }
                }
            } else {
                self.state.menu_power_off_min = next;
            }
            self.menu_last_input = self.now();
            self.persist();
            return;
        }
        if row == QuickRow::LidOff {
'''),
])

# Newly added QuickRow variants must be exhaustively handled in the legacy
# source's two action dispatch matches. Their real behavior is above.
edit("crates/slot/src/app.rs", [
    ('''            | QuickRow::AutoLoad
            | QuickRow::EjectSave''',
     '''            | QuickRow::AutoLoad
            | QuickRow::Scaling
            | QuickRow::ResumePowerOn
            | QuickRow::MenuScreenOff
            | QuickRow::MenuPowerOff
            | QuickRow::EjectSave'''),
    ('''            | QuickRow::LidOff => return,''',
     '''            | QuickRow::LidOff
            | QuickRow::Scaling
            | QuickRow::MenuScreenOff
            | QuickRow::MenuPowerOff => return,'''),
])

# Gambatte "Auto" applies an automatic GBC palette even with filters Off.
# Keep Auto available but add a genuinely neutral Off and default to Off.
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

# OnionOS theme transitions: only when launched under OnionOS (environment
# exported by the packaged launcher). Boot is already drawn by Onion before
# its startup scripts; shutdown/sleep/wake reuse Onion's existing renderer.
# The script lives on SD, never overwrites .tmp_update/runtime.sh or keymon.
edit("crates/slot/src/app.rs", [
    ('''    pub fn poweroff(&mut self) {
        self.settle_saves();
        if let Some(power) = &mut self.power {
            power.poweroff();
        }
    }''',
     '''    fn onion_splash(&self, transition: &str) {
        if std::env::var_os("SLOT_ONION_VISUALS").is_none() {
            return;
        }
        let Some(root) = self.root() else { return; };
        let script = root.join("System/onion-splash.sh");
        if !script.is_file() { return; }
        let _ = std::process::Command::new("sh")
            .arg(script)
            .arg(transition)
            .status();
        // The renderer returns immediately on the Mini. A brief hold keeps
        // the theme visible before the display blanks or Slot redraws.
        if transition != "shutdown" {
            std::thread::sleep(std::time::Duration::from_millis(300));
        }
    }

    pub fn poweroff(&mut self) {
        self.settle_saves();
        // Do not turn the screen back on merely for an idle sleep timeout.
        // A direct power-off while awake should show Onion's End_Save art.
        if !matches!(self.phase, Phase::Doze { .. }) {
            if self.menu_screen_blanked {
                if let Some(power) = &mut self.power {
                    power.set_backlight(self.state.brightness);
                }
            }
            self.onion_splash("shutdown");
        }
        if let Some(power) = &mut self.power {
            power.poweroff();
        }
    }'''),
    ('''        self.radio.ask(RadioJob::Cool);
        if let Some(power) = &mut self.power {
            power.on_close();
        }
    }

    fn wake(&mut self)''',
     '''        self.radio.ask(RadioJob::Cool);
        // Slot has already flushed its resume snapshot. Show the themed
        // "saving/off" screen before the LCD backlight is disabled.
        self.onion_splash("sleep");
        if let Some(power) = &mut self.power {
            power.on_close();
        }
    }

    fn wake(&mut self)'''),
    ('''        if let Some(power) = &mut self.power {
            power.on_open();
        }
    }

    pub fn on_doze_timeout''',
     '''        if let Some(power) = &mut self.power {
            power.on_open();
        }
        // Reuse Onion's Boot artwork; the normal Slot frame resumes after.
        self.onion_splash("wake");
    }

    pub fn on_doze_timeout'''),
])

# OnionOS starts keymon before running its startup hooks. When present,
# keymon alone owns POWER/suspend/wake. Slot saves on the key-down edge
# (before Onion suspends it on key release), but must never enter a competing
# doze, redraw a splash or force shutdown in response to that same key.
# Stock firmware / Allium continue to use Slot's original POWER path.
edit("crates/slot/src/app.rs", [
    ('''        // Physical releases are not wake actions. The first press while
        // blanked wakes the screen but does not activate menu selections.''',
     '''        // POWER goes to Onion's keymon as well as this input queue. Never
        // race its display-off / suspend / wake actions when Onion is in charge.
        if std::env::var_os("SLOT_ONION_POWER_OWNER").is_some() {
            match action {
                Action::PowerPress => {
                    // The release may cause Onion to SIGSTOP Slot immediately.
                    self.state_writer.flush();
                    self.flush_resume();
                    return;
                }
                Action::PowerTap | Action::PowerHold => return,
                _ => {}
            }
        }
        // Physical releases are not wake actions. The first press while
        // blanked wakes the screen but does not activate menu selections.'''),
])

# OnionOS owns a device-wide brightness preference (0..10) through
# /customer/app/jsonval. Slot v1.8.1 instead defaults to its own level 5.
# Respect Onion's preference on entry: before Slot writes the PWM backlight
# the first time, import the level. Existing Slot controls remain usable.
# The UI brightness field is 1..9: convert Onion 10 -> Slot 9.
edit("crates/slot/src/app.rs", [
    ('''    pub fn set_power(&mut self, mut power: Power) {
        power.set_backlight(self.state.brightness);''',
     '''    pub fn set_power(&mut self, mut power: Power) {
        if let Ok(level) = std::env::var("SLOT_ONION_BRIGHTNESS") {
            if let Ok(level) = level.parse::<u8>() {
                if level <= 10 {
                    self.state.brightness = level.clamp(1, 9);
                }
            }
        }
        power.set_backlight(self.state.brightness);'''),
])

# Protect the known-good original Miyoo backlight behavior. Onion's keymon
# owns LCD blanking during suspend and wake, so the fork's new menu-idle
# timer must not set raw backlight PWM on Onion. Do not alter Dean's PWM
# brightness table; the separate Onion brightness import is reverted below.
edit("crates/slot/src/app.rs", [
    ('''    fn tick_menu_idle(&mut self) {
        let now = self.now();''',
     '''    fn tick_menu_idle(&mut self) {
        let now = self.now();
        // Onion keymon is the display/backlight owner for this app.
        // Never blank PWM from the fork's optional menu timer.
        if std::env::var_os("SLOT_ONION_POWER_OWNER").is_some() {
            self.menu_last_input = now;
            return;
        }'''),
    ('''                Action::PowerPress => {
                    // The release may cause Onion to SIGSTOP Slot immediately.
                    self.state_writer.flush();
                    self.flush_resume();
                    return;
                }''',
     '''                // Onion's keymon handles POWER and may SIGSTOP this process
                // on button release. A synchronous save/flush here can be
                // interrupted mid-write. Rely on normal Slot autosaves,
                // and do not block the keymon handoff.
                Action::PowerPress => return,'''),
    ('''    pub fn set_power(&mut self, mut power: Power) {
        if let Ok(level) = std::env::var("SLOT_ONION_BRIGHTNESS") {
            if let Ok(level) = level.parse::<u8>() {
                if level <= 10 {
                    self.state.brightness = level.clamp(1, 9);
                }
            }
        }
        power.set_backlight(self.state.brightness);''',
     '''    pub fn set_power(&mut self, mut power: Power) {
        // Restore Dean's previously working original Miyoo brightness path.
        // Do not translate another frontend's brightness here: Slot's own
        // stored setting and PWM calibration already worked on this panel.
        power.set_backlight(self.state.brightness);'''),
])

# A software renderer cannot use the H700 GLSL effects; Authentic is deferred
# pending a measured LUT/lookup-table implementation. Do not fake it.

parts = []
for path, diff in changes.items():
    parts.append(f"diff --git a/{path} b/{path}\n{diff}")
dest.write_text("".join(parts))
print(f"Generated {dest}: {len(changes)} Miyoo-only source files")
