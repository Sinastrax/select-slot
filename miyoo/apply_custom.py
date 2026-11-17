#!/usr/bin/env python3
"""Miyoo rebuild: apply *only* emulator, palette, scaling and resume changes.

Runs against dean-marano's pinned, freshly patched original slot-miyoo tree.
No changes to the original Miyoo framebuffer, compositor, brightness, PWM,
power management, sleep/wake, launcher, display settings or panel calibration.
Every replacement must match exactly once or the build fails closed.
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

# Isolated GB/GBC Gambatte + GBA gpSP defaults; untouched original framebuffer.
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
        // Gambatte's "fast" correction deliberately darkens and desaturates.
        // Preserve the upstream accurate correction when enabled; Off stays Off.
        core.set_option("gambatte_gbc_color_correction_mode", "accurate");
        core.set_option("gambatte_dark_filter_level", "0");
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


# Two mGBA-only calls in the original Miyoo Slot remain outside the core
# opening routine. The first is already adapted above; the second runs while
# an emulator becomes ready and otherwise repeatedly sends mGBA options to
# Gambatte (visible in user-provided slot.log.1). Skip mGBA-only setup there.
# Gambatte's palette is set at opening and its live updates use its own API.
edit("crates/slot/src/session.rs", [
    ('''                if let (true, Some(emu)) = (self.app.palette_live(), &self.emu) {
                    emu.set_option("mgba_gb_colors", self.app.gb_colors().core_name());
                }''',
     '''                if let (true, Some(emu)) = (self.app.palette_live(), &self.emu) {
                    if self.app.core() == slot_store::Core::Mgba {
                        emu.set_option("mgba_gb_colors", self.app.gb_colors().core_name());
                    }
                }'''),
])

# Gambatte has no `gambatte_frameskip` core option. Do not send a nonexistent
# option at startup; the existing mGBA and gpSP setup remains untouched.
edit("crates/slot/src/core.rs", [
    ('''    core.set_option(&format!("{}_frameskip", which.as_str()), "auto");''',
     '''    if which != Core::Gambatte {
        core.set_option(&format!("{}_frameskip", which.as_str()), "auto");
    }'''),
])


# Miyoo-only physical brightness extension, requested after the clean Ver. 11
# display rebuild remained too dim at SLOT level 9. This does NOT alter the
# framebuffer, LCD3x effects, OnionOS files, or the original 1..9 PWM rungs.
# OnionOS can change the PWM period in Tweaks; new rungs are fractions of the
# live period and never reduce brightness below the original level-9 rung.
edit("crates/slot-store/src/slot_state.rs", [
    ("pub const BRIGHTNESS_MAX: u8 = 9;", "pub const BRIGHTNESS_MAX: u8 = 12;"),
])
edit("crates/slot-ui/src/quick_menu.rs", [
    ('''    Level9,
    ScaleActual,''',
     '''    Level9,
    Level10,
    Level11,
    Level12,
    ScaleActual,'''),
    ('''    pub const ALL: [QuickValue; 38]''',
     '''    pub const ALL: [QuickValue; 41]'''),
    ('''        QuickValue::Level9,
        QuickValue::ScaleActual,''',
     '''        QuickValue::Level9,
        QuickValue::Level10,
        QuickValue::Level11,
        QuickValue::Level12,
        QuickValue::ScaleActual,'''),
    ('''    pub const LEVELS: [QuickValue; 10]''',
     '''    pub const LEVELS: [QuickValue; 13]'''),
    ('''        QuickValue::Level9,
    ];

    pub const LID_OFF:''',
     '''        QuickValue::Level9,
        QuickValue::Level10,
        QuickValue::Level11,
        QuickValue::Level12,
    ];

    pub const LID_OFF:'''),
    ('''            QuickValue::Level9 => "9",''',
     '''            QuickValue::Level9 => "9",
            QuickValue::Level10 => "10",
            QuickValue::Level11 => "11",
            QuickValue::Level12 => "12",'''),
])
edit("crates/slot-power/src/device.rs", [
    ('''            Some(Backlight::Pwm(_)) => PWM_STEPS[TOP_STEP as usize],''',
     '''            Some(Backlight::Pwm(dir)) => {
                // Max UI brightness is now 50% of this panel's PWM period.
                // Include the old level-9 duty if Onion uses a shorter period.
                let period = read_number(&dir.join("period")).unwrap_or(800);
                (period / 2).max(PWM_STEPS[TOP_STEP as usize].min(period))
            },'''),
    ('''                let duty = PWM_STEPS[step as usize].min(cap);''',
     '''                let duty = if step <= TOP_STEP as u8 {
                    // Preserve all of Dean's original levels 0..9 exactly.
                    PWM_STEPS[step as usize].min(cap)
                } else {
                    // OnionOS allows 100..1000 as the PWM period (800
                    // by default), and restores its own brightness on wake.
                    // The old absolute-value table only covered 0..9.
                    // 10/11/12 target 20%/30%/50% duty of the *live*
                    // period, without exceeding the sysfs maximum.
                    let period = if cap == u32::MAX { 800 } else { cap };
                    let percent: u32 = match step {
                        10 => 20,
                        11 => 30,
                        _ => 50,
                    };
                    let scaled = ((period as u64 * percent as u64 + 50) / 100) as u32;
                    scaled.max(PWM_STEPS[TOP_STEP as usize].min(cap)).min(cap)
                };'''),
])
# Unit tests for 800 (Onion default), 400 (custom frequency), 100 (short).
edit("crates/slot-power/tests/device.rs", [
    ('''#[test]
fn a_shorter_period_clamps_rather_than_failing() {''',
     '''#[test]
fn extended_brightness_respects_live_onion_pwm_period() {
    let d = pwm_sysfs("800");
    let mut p = platform(&d);
    for (step, expected) in [(9, 112), (10, 160), (11, 240), (12, 400)] {
        p.set_backlight(step);
        assert_eq!(duty(&d), expected, "800 period step {step}");
    }
    let period = d.path().join("class/pwm/pwmchip0/pwm0/period");
    fs::write(&period, "400\\n").unwrap();
    for (step, expected) in [(9, 112), (10, 112), (11, 120), (12, 200)] {
        p.set_backlight(step);
        assert_eq!(duty(&d), expected, "400 period step {step}");
    }
    fs::write(&period, "100\\n").unwrap();
    for step in [9, 10, 11, 12] {
        p.set_backlight(step);
        assert_eq!(duty(&d), 100, "100 period saturated at step {step}");
    }
}

#[test]
fn a_shorter_period_clamps_rather_than_failing() {'''),
])

# Invariants: only allow the two explicit PWM backlight edits above in
# slot-power; framebuffer and compositor source stay original. Launcher,
# keymon, theme, screen-off / power lifecycle paths are never patched.
allowed = {
    "crates/slot-store/src/core.rs",
    "crates/slot-store/src/slot_state.rs",
    "crates/slot-store/src/gb_palette.rs",
    "crates/slot/src/core.rs",
    "crates/slot/src/session.rs",
    "crates/slot/src/video_mode.rs",
    "crates/slot/src/app.rs",
    "crates/slot-ui/src/quick_menu.rs",
    "crates/slot-power/src/device.rs",
    "crates/slot-power/tests/device.rs",
}
if set(changes) != allowed:
    raise RuntimeError(f"rebuild source changed unexpected paths: {sorted(set(changes) ^ allowed)}")
# Ignore unified diff context; check only changed lines, not unchanged neighbors.
for path, diff in changes.items():
    for line in diff.splitlines():
        if not (line.startswith("+") or line.startswith("-")) or line.startswith(("+++", "---")):
            continue
        if any(term in line for term in (
            "SLOT_ONION_",
            "blue_light_gain", "onion_splash",
            "fn sleep(", "fn wake(", "fn doze(",
        )):
            raise RuntimeError(f"forbidden brightness/power patch in {path}: {line}")

parts = []
for path, diff in changes.items():
    parts.append(f"diff --git a/{path} b/{path}\n{diff}")
dest.write_text("".join(parts))
print(f"Miyoo extended brightness: {len(changes)} sources, original framebuffer and power lifecycle preserved")
