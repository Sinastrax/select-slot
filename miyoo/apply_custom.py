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


# OnionOS owns physical POWER and its theme transitions when running its
# native runtime. SLOT must not blank the PWM on PowerTap before OnionOS can
# show whatever splash/shutdown image is provided by the selected theme.
# Keep SLOT's immediate save-state flush at press, without entering doze or
# doing a competing poweroff on release/hold. Native non-Onion use unchanged.
edit("crates/slot/src/app.rs", [
    ('''    pub fn apply(&mut self, action: Action) {
        self.track_held_dir(action);
        match action {''',
     '''    pub fn apply(&mut self, action: Action) {
        self.track_held_dir(action);
        // Under Onion, its keymon receives the same physical POWER event.
        // Let keymon own LCD blanking, active-theme artwork and suspend/wake.
        // In particular do not execute Slot's doze() -> PWM duty 0 before
        // Onion's bootScreen has a chance to render.
        // Only OnionOS gets POWER from its own keymon. Stock autoboot
        // also installs runtime.sh but has no Onion runtime/keymon.
        if self.root.as_ref().is_some_and(|r| {
            r.join(".tmp_update/runtime.sh").is_file()
                && r.join(".tmp_update/onionVersion/version.txt").is_file()
        }) {
            match action {
                Action::PowerPress => {
                    self.state_writer.flush();
                    self.flush_resume();
                    return;
                }
                Action::PowerTap => return, // OnionOS short-press suspend
                Action::PowerHold => {
                    // Initiate shutdown before OnionOS keymon's 0.5s
                    // deepsleep path can suspend us and delay power-off
                    // by its thirty-second fallback. We also exit the
                    // interactive Slot menu immediately.
                    self.menu_shutdown_onion = true;
                    self.begin_power_off();
                    self.act_at = self.now();
                    return;
                }
                _ => {}
            }
        }
        match action {'''),
])

# Return to Dean's original 0..9 brightness scale and hardware duty table.
# Existing Ver. 12–20 installations may contain brightness=10, 11 or 12.
# The inherited state parser rejects out-of-range brightness and discards the
# *entire* saved configuration; clamp only this one number to 9 instead.
edit("crates/slot-store/src/slot_state.rs", [
    ('''            "brightness" => brightness = Some(level(value, BRIGHTNESS_MAX)?),''',
     '''            // Accept former Miyoo boost levels without losing the rest of
            // slot.state (including resume/core/settings) on downgrade.
            "brightness" => brightness = Some(value.parse::<u8>().ok()?.min(BRIGHTNESS_MAX)),'''),
])

# Onion keymon is an independent backlight owner: it restores its own
# 0..10 level after standby, and while it believes MainUI is active it can
# rewrite brightness on key events. Notify its supported state-change hook when
# Slot launches as an app, then reapply Slot's saved level once on returning
# from a long process suspension. Never patch/stop keymon or alter Onion config.
edit("crates/slot/src/app.rs", [
    ('''        power.set_backlight(self.state.brightness);
        self.headphones = power.headphones();''',
     '''        power.set_backlight(self.state.brightness);
        // Onion keymon also writes this PWM. Tell it the active process
        // has changed so it does not keep applying MainUI brightness here.
        if self.root.as_ref().is_some_and(|r| r.join(".tmp_update/bin/keymon").is_file()) {
            let _ = std::fs::write("/tmp/state_changed", b"");
        }
        self.headphones = power.headphones();'''),
    ('''    fn copy_card_log(&self, power: &Power) {''',
     '''    pub fn restore_onion_backlight(&mut self) {
        // Called only after a sizeable process gap (standby/resume). Onion
        // keymon restores its own setting *before* resuming this process;
        // reapply the user's Slot level once after that handoff.
        if self.root.as_ref().is_some_and(|r| r.join(".tmp_update/bin/keymon").is_file()) {
            if let Some(power) = &mut self.power {
                power.set_backlight(self.state.brightness);
            }
        }
    }

    fn copy_card_log(&self, power: &Power) {'''),
])
edit("crates/slot/src/frontend.rs", [
    ('''        let dt = self.last.elapsed().as_secs_f32().min(MAX_DT);
        self.last = Instant::now();
        self.session.update(dt);''',
     '''        let elapsed = self.last.elapsed();
        if elapsed >= Duration::from_secs(1) {
            // Keymon may have replaced Slot's PWM while we were stopped.
            // Reapply once, not continuously and not on every game frame.
            self.session.app_mut().restore_onion_backlight();
        }
        let dt = elapsed.as_secs_f32().min(MAX_DT);
        self.last = Instant::now();
        self.session.update(dt);'''),
])

# Original Miyoo Mini / Mini Plus: OnionOS controls PWM directly, but Dean's
# power detector was designed around the Mini Flip and only picks PWM AFTER
# finding no class backlight and no dispdbg. If either older interface exists,
# the saved brightness selection may not reach the LCD backlight.
# On OnionOS ONLY, prefer its actual PWM channel when already exported.
# Preserve Dean's original priority and fallbacks for stock/Allium firmware.
edit("crates/slot-power/src/device.rs", [
    ('''        let backlight = match class {
            Some(dir) => Some(Backlight::Class(dir)),
            None => {
                let dbg = sysfs.join("kernel/debug/dispdbg");
                dbg.join("param")
                    .is_file()
                    .then_some(Backlight::Dispdbg(dbg))
                    .or_else(|| find_pwm(sysfs).map(Backlight::Pwm))
            }
        };''',
     '''        // Onion controls physical screen brightness through
        // /sys/class/pwm/pwmchip0/pwm0/duty_cycle. On original Mini units a
        // secondary display class or dispdbg may exist but isn't the actual
        // backlight. Prefer PWM only while running on the Onion card.
        let onion_pwm = root.join(".tmp_update/runtime.sh").is_file()
            .then(|| find_pwm(sysfs).map(Backlight::Pwm))
            .flatten();
        let backlight = onion_pwm.or_else(|| match class {
            Some(dir) => Some(Backlight::Class(dir)),
            None => {
                let dbg = sysfs.join("kernel/debug/dispdbg");
                dbg.join("param")
                    .is_file()
                    .then_some(Backlight::Dispdbg(dbg))
                    .or_else(|| find_pwm(sysfs).map(Backlight::Pwm))
            }
        });'''),
])
edit("crates/slot-power/tests/device.rs", [
    ('''#[test]
fn a_shorter_period_clamps_rather_than_failing() {''',
     '''#[test]
fn onion_prefers_real_pwm_over_other_reported_display_backlights() {
    let d = sysfs("255", "87");
    let pwm = d.path().join("class/pwm/pwmchip0/pwm0");
    fs::create_dir_all(&pwm).unwrap();
    fs::write(pwm.join("period"), "800\\n").unwrap();
    fs::write(pwm.join("duty_cycle"), "6\\n").unwrap();
    fs::write(pwm.join("enable"), "1\\n").unwrap();

    // Without Onion, keep Dean's existing class-first policy.
    let mut stock = platform(&d);
    stock.set_backlight(9);
    assert_eq!(brightness(&d), 255);
    assert_eq!(duty(&d), 6);

    // Once Onion's runtime is present, direct PWM is the real LCD backlight.
    let onion = d.path().join(".tmp_update");
    fs::create_dir_all(&onion).unwrap();
    fs::write(onion.join("runtime.sh"), "#!/bin/sh\\n").unwrap();
    let mut slot = DevicePlatform::probe(d.path(), d.path().to_path_buf());
    slot.set_backlight(9);
    assert_eq!(duty(&d), 112);
    // Class isn't touched by the Onion-specific correction.
    assert_eq!(brightness(&d), 255);
}

#[test]
fn extended_brightness_respects_live_onion_pwm_period() {'''),
])



# Miyoo-specific shader removal. Both menus hide the selector, shortcut
# cycling is inert and the frontend always selects the original unfiltered
# CPU path. Old shader names remain readable in the saved configuration,
# but are ignored for rendering; no user data or saves are deleted.
edit("crates/slot/src/app.rs", [
    ('''    pub fn in_game_hidden(&self) -> Vec<QuickRow> {
        let no_bezel = self.playing_platform() == Platform::Gba && !self.framed_panel();
        let mut hidden = Vec::new();''',
     '''    pub fn in_game_hidden(&self) -> Vec<QuickRow> {
        let no_bezel = self.playing_platform() == Platform::Gba && !self.framed_panel();
        // The shaders are intentionally disabled for this Miyoo build.
        let mut hidden = vec![
            QuickRow::Shader, QuickRow::GbaShader,
            QuickRow::GbShader, QuickRow::GbcShader,
        ];'''),
    ('''        let mut hidden = Vec::new();
        if !own {
            hidden.push(QuickRow::WallpaperTint);''',
     '''        // Remove the shader row from every system's quick settings.
        let mut hidden = vec![
            QuickRow::Shader, QuickRow::GbaShader,
            QuickRow::GbShader, QuickRow::GbcShader,
        ];
        if !own {
            hidden.push(QuickRow::WallpaperTint);'''),
    ('''    pub fn screen_shader(&self) -> Shader {
        match self.playing_platform() {
            Platform::Gba => self.state.shader_gba,
            Platform::Gb => self.state.shader_gb,
            Platform::Gbc => self.state.shader_gbc,
        }
    }''',
     '''    pub fn screen_shader(&self) -> Shader {
        // Force the unfiltered picture even for pre-existing saved choices.
        Shader::Off
    }'''),
    ('''    fn step_shader(&mut self, right: bool) {
        if !matches!(self.phase, Phase::Inserting { .. } | Phase::Playing { .. }) {
            return;
        }
        let (shader, choices) = match self.playing_platform() {
            Platform::Gba => (&mut self.state.shader_gba, &Shader::GBA[..]),
            Platform::Gb => (&mut self.state.shader_gb, &Shader::GB[..]),
            Platform::Gbc => (&mut self.state.shader_gbc, &Shader::GB[..]),
        };
        *shader = shader.step(choices, right);
        let said = match *shader {
            Shader::Off => Toast::ShaderOff,
            Shader::Lcd3x => Toast::ShaderLcd3x,
            Shader::Grid => Toast::ShaderGrid,
            Shader::Dot => Toast::ShaderDot,
            Shader::Simpletex => Toast::ShaderSimpletex,
        };
        self.persist();
        self.hud.toast(said, self.now());
    }''',
     '''    fn step_shader(&mut self, _right: bool) {
        // Ignore existing next/previous shader shortcuts as well.
    }'''),
])
edit("crates/slot/src/frontend.rs", [
    ('''        compositor.set_screen_effect(match self.session.app().screen_shader() {
            slot_store::Shader::Off => ScreenEffect::None,
            slot_store::Shader::Lcd3x => ScreenEffect::Lcd3x,
            slot_store::Shader::Grid => ScreenEffect::Grid,
            slot_store::Shader::Dot => ScreenEffect::Dot,
            slot_store::Shader::Simpletex => ScreenEffect::Simpletex,
        });''',
     '''        // No shader or software effect can be selected on Miyoo.
        // Keep the original unfiltered renderer for every platform.
        compositor.set_screen_effect(ScreenEffect::None);'''),
])
edit("crates/slot-store/src/slot_state.rs", [
    ('''            shader_gba: Shader::Grid,
            shader_gb: Shader::Simpletex,
            shader_gbc: Shader::Simpletex,''',
     '''            shader_gba: Shader::Off,
            shader_gb: Shader::Off,
            shader_gbc: Shader::Off,'''),
])


# Menu-only inactivity controls, adapted for OnionOS. Keep menu timers
# independent from OnionOS's own sleep setting, and never intercept POWER.
edit("crates/slot-store/src/slot_state.rs", [
    ('''    pub lid_off_min: Option<u8>,
    pub bezel_gba: BezelPick,''',
     '''    pub lid_off_min: Option<u8>,
    pub menu_screen_off_min: u8,
    pub menu_power_off_min: u8,
    pub bezel_gba: BezelPick,'''),
    ('''            lid_off_min: None,
            bezel_gba: BezelPick::Ags102,''',
     '''            lid_off_min: None,
            menu_screen_off_min: 3,
            menu_power_off_min: 15,
            bezel_gba: BezelPick::Ags102,'''),
    ('''    if let Some(min) = s.lid_off_min {
        text.push_str(&format!("lid_off_min={min}\\n"));
    }
    text.push_str(&format!("bezel_gba={}\\n", s.bezel_gba.key()));''',
     '''    if let Some(min) = s.lid_off_min {
        text.push_str(&format!("lid_off_min={min}\\n"));
    }
    text.push_str(&format!("menu_screen_off_min={}\\n", s.menu_screen_off_min));
    text.push_str(&format!("menu_power_off_min={}\\n", s.menu_power_off_min));
    text.push_str(&format!("bezel_gba={}\\n", s.bezel_gba.key()));'''),
    ('''    let mut lid_off_min = None;
    let mut bezel_gba = None;''',
     '''    let mut lid_off_min = None;
    let mut menu_screen_off_min = None;
    let mut menu_power_off_min = None;
    let mut bezel_gba = None;'''),
    ('''            "lid_off_min" => lid_off_min = value.parse().ok().filter(|m| LID_OFF_MIN.contains(m)),
            "bezel_gba"''',
     '''            "lid_off_min" => lid_off_min = value.parse().ok().filter(|m| LID_OFF_MIN.contains(m)),
            "menu_screen_off_min" => {
                menu_screen_off_min = value.parse::<u8>().ok().filter(|m| [0, 1, 3, 5, 10, 15, 30].contains(m))
            }
            "menu_power_off_min" => {
                menu_power_off_min = value.parse::<u8>().ok().filter(|m| [0, 1, 3, 5, 10, 15, 30].contains(m))
            }
            "bezel_gba"'''),
    ('''        lid_off_min,
        bezel_gba: bezel_gba.unwrap_or(fallback.bezel_gba),''',
     '''        lid_off_min,
        menu_screen_off_min: menu_screen_off_min.unwrap_or(fallback.menu_screen_off_min),
        menu_power_off_min: menu_power_off_min.unwrap_or(fallback.menu_power_off_min),
        bezel_gba: bezel_gba.unwrap_or(fallback.bezel_gba),'''),
])
edit("crates/slot-ui/src/quick_menu.rs", [
    ('''    ResumePowerOn,
}

impl QuickRow''',
     '''    ResumePowerOn,
    MenuScreenOff,
    MenuPowerOff,
}

impl QuickRow'''),
    ('''    pub const ALL: [QuickRow; 82]''', '''    pub const ALL: [QuickRow; 84]'''),
    ('''        QuickRow::ResumePowerOn,
    ];

    pub const MAIN:''',
     '''        QuickRow::ResumePowerOn,
        QuickRow::MenuScreenOff,
        QuickRow::MenuPowerOff,
    ];

    pub const MAIN:'''),
    ('''    pub const GENERAL: [QuickRow; 7]''', '''    pub const GENERAL: [QuickRow; 9]'''),
    ('''        QuickRow::LidOff,
        QuickRow::DateTime,''',
     '''        QuickRow::LidOff,
        QuickRow::MenuScreenOff,
        QuickRow::MenuPowerOff,
        QuickRow::DateTime,'''),
    ('''            | QuickRow::LidOff => &QuickRow::GENERAL,''',
     '''            | QuickRow::LidOff
            | QuickRow::MenuScreenOff
            | QuickRow::MenuPowerOff => &QuickRow::GENERAL,'''),
    ('''            QuickRow::LidOff => "Lid Power Off",''',
     '''            QuickRow::LidOff => "Lid Power Off",
            QuickRow::MenuScreenOff => "Menu Screen Off",
            QuickRow::MenuPowerOff => "Menu Power Off",'''),
])


# Blank only the physical backlight for idle menus. Keep the remembered level
# intact: the first input restores exactly the user's chosen 1..9 setting.
edit("crates/slot-power/src/power.rs", [
    ('''    pub fn set_backlight(&mut self, step: u8) {
        self.level = step;
        if !self.closed {
            self.platform.set_backlight(step);
        }
    }

    pub fn battery''',
     '''    pub fn set_backlight(&mut self, step: u8) {
        self.level = step;
        if !self.closed {
            self.platform.set_backlight(step);
        }
    }

    /// Menu-only blanking must not overwrite the saved physical PWM level.
    pub fn set_idle_blank(&mut self, blank: bool) {
        if !self.closed {
            self.platform.set_backlight(if blank { 0 } else { self.level });
        }
    }

    pub fn battery'''),
])

# Timers count on the shelf and in the shelf Quick Menu only, never during
# gameplay, cartridge transitions, capture, links, shutdown or core selection.
# A native OnionOS idle suspend may take priority. We do not disable keymon,
# touch its settings, or create the stay_awake override.
edit("crates/slot/src/app.rs", [
    ('''    clock: f64,
    power: Option<Power>,
    dozed_at: Millis,''',
     '''    clock: f64,
    menu_idle_at: Millis,
    menu_screen_blanked: bool,
    menu_shutdown_onion: bool,
    power: Option<Power>,
    dozed_at: Millis,'''),
    ('''            clock: 0.0,
            power: None,
            dozed_at: 0,''',
     '''            clock: 0.0,
            menu_idle_at: 0,
            menu_screen_blanked: false,
            menu_shutdown_onion: false,
            power: None,
            dozed_at: 0,'''),
    ('''            QuickRow::LidOff => QuickValue::LID_OFF
                .into_iter()
                .find(|v| v.minutes() == Some(self.lid_off_min())),''',
     '''            QuickRow::LidOff => QuickValue::LID_OFF
                .into_iter()
                .find(|v| v.minutes() == Some(self.lid_off_min())),
            QuickRow::MenuScreenOff | QuickRow::MenuPowerOff => {
                let min = if row == QuickRow::MenuScreenOff {
                    self.state.menu_screen_off_min
                } else {
                    self.state.menu_power_off_min
                };
                Some(match min {
                    1 => QuickValue::Min1,
                    3 => QuickValue::Min3,
                    5 => QuickValue::Min5,
                    10 => QuickValue::Min10,
                    15 => QuickValue::Min15,
                    30 => QuickValue::Min30,
                    _ => QuickValue::Off,
                })
            },'''),
    ('''        if row == QuickRow::LidOff {
            let n = LID_OFF_MIN.len();''',
     '''        if matches!(row, QuickRow::MenuScreenOff | QuickRow::MenuPowerOff) {
            const CHOICES: [u8; 7] = [0, 1, 3, 5, 10, 15, 30];
            let current = if row == QuickRow::MenuScreenOff {
                self.state.menu_screen_off_min
            } else {
                self.state.menu_power_off_min
            };
            let at = CHOICES.iter().position(|m| *m == current).unwrap_or(0);
            let n = CHOICES.len();
            let to = CHOICES[if right { (at + 1) % n } else { (at + n - 1) % n }];
            if row == QuickRow::MenuScreenOff {
                self.state.menu_screen_off_min = to;
            } else {
                self.state.menu_power_off_min = to;
            }
            self.menu_idle_at = self.now();
            self.persist();
            return;
        }
        if row == QuickRow::LidOff {
            let n = LID_OFF_MIN.len();'''),
    ('''            | QuickRow::LidOff
            | QuickRow::Scaling => return,''',
     '''            | QuickRow::LidOff
            | QuickRow::Scaling
            | QuickRow::MenuScreenOff
            | QuickRow::MenuPowerOff => return,'''),
    ('''            | QuickRow::LidOff => {}
        }
    }

    fn change_setting''',
     '''            | QuickRow::LidOff
            | QuickRow::MenuScreenOff
            | QuickRow::MenuPowerOff => {}
        }
    }

    fn change_setting'''),
    ('''    pub fn apply(&mut self, action: Action) {
        self.track_held_dir(action);''',
     '''    pub fn apply(&mut self, action: Action) {
        // The first intentional button press only wakes a dark menu.
        // POWER and lid transitions always belong to the device/OnionOS.
        if self.menu_screen_blanked {
            match action {
                Action::GbaUp(_) | Action::MenuChordUp(_) | Action::PowerOff => return,
                Action::PowerPress | Action::PowerTap | Action::PowerHold
                | Action::LidOpen | Action::LidClose => {}
                _ => {
                    self.menu_screen_blanked = false;
                    if let Some(power) = &mut self.power {
                        power.set_idle_blank(false);
                    }
                    self.menu_idle_at = self.now();
                    self.held_dir = None;
                    return;
                }
            }
        }
        // No menu activity accumulates while an emulator is running.
        if !matches!(action, Action::GbaUp(_) | Action::MenuChordUp(_) | Action::PowerOff) {
            self.menu_idle_at = self.now();
        }
        self.track_held_dir(action);'''),
    ('''    fn timers(&mut self) {
        self.play_hold();
        self.repeat_held_dir();''',
     '''    fn tick_menu_idle(&mut self) {
        let allowed = matches!(self.phase, Phase::Shelf | Phase::QuickMenu { .. })
            && !self.shutting_down()
            && self.core_picker.is_none()
            && self.capture.is_none()
            && self.starting.is_none()
            && !self.link_active();
        if !allowed {
            if self.menu_screen_blanked {
                self.menu_screen_blanked = false;
                if let Some(power) = &mut self.power {
                    power.set_idle_blank(false);
                }
            }
            self.menu_idle_at = self.now();
            return;
        }
        let elapsed = self.now().saturating_sub(self.menu_idle_at);
        let off = self.state.menu_power_off_min;
        if off != 0 && elapsed >= u64::from(off) * 60_000 {
            // Restore backlight BEFORE the active OnionOS theme is displayed.
            if self.menu_screen_blanked {
                self.menu_screen_blanked = false;
                if let Some(power) = &mut self.power {
                    power.set_idle_blank(false);
                }
            }
            self.menu_idle_at = self.now();
            // Stock firmware autoboot also uses .tmp_update/runtime.sh;
            // that file alone is NOT evidence of OnionOS. Its complete
            // runtime additionally ships bin/ and script/ directories.
            self.menu_shutdown_onion = self.root.as_ref().is_some_and(|root| {
                root.join(".tmp_update/runtime.sh").is_file()
                    && root.join(".tmp_update/onionVersion/version.txt").is_file()
            });
            self.begin_power_off();
            return;
        }
        let blank = self.state.menu_screen_off_min;
        if blank != 0 && elapsed >= u64::from(blank) * 60_000 && !self.menu_screen_blanked {
            if let Some(power) = &mut self.power {
                power.set_idle_blank(true);
                self.menu_screen_blanked = true;
            }
        }
    }

    fn timers(&mut self) {
        self.play_hold();
        self.repeat_held_dir();
        self.tick_menu_idle();'''),
    ('''    pub fn poweroff(&mut self) {
        self.settle_saves();
        if let Some(power) = &mut self.power {
            power.poweroff();
        }
    }''',
     '''    pub fn poweroff(&mut self) {
        self.settle_saves();
        if self.menu_shutdown_onion {
            // The official OnionOS runtime's check_off_order() sees this
            // after our app returns, renders the selected theme's End screen,
            // runs its shutdown hooks and invokes its own shutdown utility.
            // We deliberately do NOT invoke the hardware poweroff here.
            if std::fs::write("/tmp/.offOrder", b"").is_ok() {
                std::process::exit(0);
            }
            eprintln!("slot: cannot request OnionOS shutdown; using device fallback");
        }
        if let Some(power) = &mut self.power {
            power.poweroff();
        }
    }'''),
    ('''        if self.root.as_ref().is_some_and(|r| r.join(".tmp_update/bin/keymon").is_file()) {
            if let Some(power) = &mut self.power {
                power.set_backlight(self.state.brightness);
            }
        }''',
     '''        if !self.menu_screen_blanked
            && self.root.as_ref().is_some_and(|r| r.join(".tmp_update/bin/keymon").is_file()) {
            if let Some(power) = &mut self.power {
                power.set_backlight(self.state.brightness);
            }
        }'''),
])


# Ver. 25: separate, persisted GB / GBC / GBA scaling defaults in
# Screen -> Game Boy / Game Boy Color / Game Boy Advance.
# Per-ROM scaling stays the highest priority. The old Ver.24 'default' key
# remains a *read-only* fallback for users who installed that release.
edit("crates/slot/src/video_mode.rs", [
    ('''pub fn video_mode_for(root: &Path, stem: &str) -> VideoMode {
    ini::value(root, VIDEO_MODE_FILE, stem)
        .as_deref()
        .and_then(VideoMode::parse)
        .unwrap_or_default()
}''',
     '''fn platform_default_key(platform: Platform) -> &'static str {
    match platform {
        Platform::Gb => "default_gb",
        Platform::Gbc => "default_gbc",
        Platform::Gba => "default_gba",
    }
}

pub fn default_video_mode(root: &Path, platform: Platform) -> VideoMode {
    ini::value(root, VIDEO_MODE_FILE, platform_default_key(platform))
        .as_deref()
        .and_then(VideoMode::parse)
        // Preserve the old Ver. 24 global default until each system is
        // configured explicitly. Never overwrite or delete per-ROM values.
        .or_else(|| ini::value(root, VIDEO_MODE_FILE, "default")
            .as_deref()
            .and_then(VideoMode::parse))
        .unwrap_or(VideoMode::Actual)
}

pub fn write_default_video_mode(root: &Path, platform: Platform, mode: VideoMode) -> std::io::Result<()> {
    ini::write(root, VIDEO_MODE_FILE, platform_default_key(platform), mode.as_str())
}

pub fn video_mode_for(root: &Path, stem: &str, platform: Platform) -> VideoMode {
    ini::value(root, VIDEO_MODE_FILE, stem)
        .as_deref()
        .and_then(VideoMode::parse)
        .unwrap_or_else(|| default_video_mode(root, platform))
}'''),
])
edit("crates/slot/src/session.rs", [
    ('''            .set_video_mode(crate::video_mode::video_mode_for(&self.root, stem));''',
     '''            .set_video_mode(crate::video_mode::video_mode_for(&self.root, stem, platform));'''),
])
edit("crates/slot-ui/src/quick_menu.rs", [
    ('''    MenuPowerOff,
}

impl QuickRow''',
     '''    MenuPowerOff,
    GbaScaling,
    GbScaling,
    GbcScaling,
}

impl QuickRow'''),
    ('''    pub const ALL: [QuickRow; 84]''', '''    pub const ALL: [QuickRow; 87]'''),
    ('''        QuickRow::MenuPowerOff,
    ];

    pub const MAIN:''',
     '''        QuickRow::MenuPowerOff,
        QuickRow::GbaScaling,
        QuickRow::GbScaling,
        QuickRow::GbcScaling,
    ];

    pub const MAIN:'''),
    ('''    pub const SCREEN_GBA: [QuickRow; 3] = [
        QuickRow::GbaShader,
        QuickRow::GbaColourCorrection,
        QuickRow::GbaBezel,
    ];''',
     '''    pub const SCREEN_GBA: [QuickRow; 4] = [
        QuickRow::GbaScaling,
        QuickRow::GbaShader,
        QuickRow::GbaColourCorrection,
        QuickRow::GbaBezel,
    ];'''),
    ('''    pub const SCREEN_GBC: [QuickRow; 3] = [
        QuickRow::GbcShader,
        QuickRow::GbcColourCorrection,
        QuickRow::GbcBezel,
    ];''',
     '''    pub const SCREEN_GBC: [QuickRow; 4] = [
        QuickRow::GbcScaling,
        QuickRow::GbcShader,
        QuickRow::GbcColourCorrection,
        QuickRow::GbcBezel,
    ];'''),
    ('''    pub const SCREEN_GB: [QuickRow; 4] = [
        QuickRow::GbShader,
        QuickRow::GbColourCorrection,
        QuickRow::GbPalette,
        QuickRow::GbBezel,
    ];''',
     '''    pub const SCREEN_GB: [QuickRow; 5] = [
        QuickRow::GbScaling,
        QuickRow::GbShader,
        QuickRow::GbColourCorrection,
        QuickRow::GbPalette,
        QuickRow::GbBezel,
    ];'''),
    ('''            QuickRow::GbaShader | QuickRow::GbaColourCorrection | QuickRow::GbaBezel => {
                &QuickRow::SCREEN_GBA
            }''',
     '''            QuickRow::GbaShader | QuickRow::GbaColourCorrection | QuickRow::GbaBezel
            | QuickRow::GbaScaling => {
                &QuickRow::SCREEN_GBA
            }'''),
    ('''            QuickRow::GbcShader | QuickRow::GbcColourCorrection | QuickRow::GbcBezel => {
                &QuickRow::SCREEN_GBC
            }''',
     '''            QuickRow::GbcShader | QuickRow::GbcColourCorrection | QuickRow::GbcBezel
            | QuickRow::GbcScaling => {
                &QuickRow::SCREEN_GBC
            }'''),
    ('''            | QuickRow::GbBezel => &QuickRow::SCREEN_GB,''',
     '''            | QuickRow::GbBezel
            | QuickRow::GbScaling => &QuickRow::SCREEN_GB,'''),
    ('''            QuickRow::MenuPowerOff => "Menu Power Off",''',
     '''            QuickRow::MenuPowerOff => "Menu Power Off",
            QuickRow::GbaScaling | QuickRow::GbScaling | QuickRow::GbcScaling => "Scaling",'''),
])
edit("crates/slot/src/app.rs", [
    ('''            QuickRow::Scaling => Some(match self.video_mode {
                VideoMode::Actual => QuickValue::ScaleActual,''',
     '''            QuickRow::GbaScaling | QuickRow::GbScaling | QuickRow::GbcScaling => {
                let platform = match row {
                    QuickRow::GbaScaling => Platform::Gba,
                    QuickRow::GbcScaling => Platform::Gbc,
                    _ => Platform::Gb,
                };
                let mode = self.root.as_deref()
                    .map(|root| video_mode::default_video_mode(root, platform))
                    .unwrap_or(VideoMode::Actual);
                Some(match mode {
                    VideoMode::Actual => QuickValue::ScaleActual,
                    VideoMode::Integer => QuickValue::ScaleInteger,
                    VideoMode::Stretch | VideoMode::Aspect => QuickValue::ScaleAspect,
                    VideoMode::Fill => QuickValue::ScaleFill,
                    VideoMode::FullStretch => QuickValue::ScaleFull,
                })
            },
            QuickRow::Scaling => Some(match self.video_mode {
                VideoMode::Actual => QuickValue::ScaleActual,'''),
    ('''        if row == QuickRow::Scaling {
            let to = if right { self.video_mode.next() } else { self.video_mode.previous() };
            self.set_picture(to);
            return;
        }''',
     '''        if matches!(row, QuickRow::GbaScaling | QuickRow::GbScaling | QuickRow::GbcScaling) {
            if let Some(root) = &self.root {
                let platform = match row {
                    QuickRow::GbaScaling => Platform::Gba,
                    QuickRow::GbcScaling => Platform::Gbc,
                    _ => Platform::Gb,
                };
                let now = video_mode::default_video_mode(root, platform);
                let to = if right { now.next() } else { now.previous() };
                let written = video_mode::write_default_video_mode(root, platform, to);
                if let Err(e) = &written {
                    eprintln!("slot: video: cannot save system scaling: {e}");
                }
                self.card_writes.wrote("video_mode.txt", &written);
            }
            return;
        }
        if row == QuickRow::Scaling {
            let to = if right { self.video_mode.next() } else { self.video_mode.previous() };
            self.set_picture(to);
            return;
        }'''),
    ('''            | QuickRow::MenuPowerOff => {}
        }
    }

    fn change_setting''',
     '''            | QuickRow::MenuPowerOff
            | QuickRow::GbaScaling
            | QuickRow::GbScaling
            | QuickRow::GbcScaling => {}
        }
    }

    fn change_setting'''),
    ('''            | QuickRow::MenuPowerOff => return,''',
     '''            | QuickRow::MenuPowerOff
            | QuickRow::GbaScaling
            | QuickRow::GbScaling
            | QuickRow::GbcScaling => return,'''),
])

# OnionOS keymon starts its own shutdown/deepsleep at about 0.5s of POWER
# hold, before Slot's upstream 1000ms PowerHold event. Shorten the Miyoo
# gesture specifically, so a deliberate hold can flush, mark shutdown and
# exit before keymon suspends the app. Quick taps still belong to OnionOS.
edit("crates/slot-input/src/gesture.rs", [
    ('''pub const POWER_HOLD_MS: Millis = 1000;''',
     '''pub const POWER_HOLD_MS: Millis = 350;'''),
])

# Ver. 24: shutting down is a terminal state, not an active menu. Ignore all
# controller actions once shutdown begins (including repeated power/menu
# actions). Slot's own shutdown overlay remains available for stock firmware.
# On OnionOS hand control to the runtime immediately for its selected theme's
# Screen_Off image instead of allowing another interactive frame.
edit("crates/slot/src/app.rs", [
    ('''    pub fn apply(&mut self, action: Action) {
        // The first intentional button press only wakes a dark menu.''',
     '''    pub fn apply(&mut self, action: Action) {
        // Shutdown means no new menu, game, or controller actions.
        if self.shutting_down() {
            return;
        }
        // The first intentional button press only wakes a dark menu.'''),
    ('''            self.begin_power_off();
            return;
        }
        let blank = self.state.menu_screen_off_min;''',
     '''            self.begin_power_off();
            // Fast shutdown: no interactive delay. OnionOS will present the
            // active theme's shutdown image once Slot relinquishes the FB.
            if self.menu_shutdown_onion {
                self.act_at = self.now();
            }
            return;
        }
        let blank = self.state.menu_screen_off_min;'''),
])
# Ver. 26: the GB/GBC/GBA Screen submenus now begin with Scaling rather
# than Shader. QuickRow::parent() identifies its menu by its FIRST row.
# Update the three parent keys so B returns to Screen instead of Shelf.
# Neither input handling nor any other navigation or scaling logic changes.
edit("crates/slot-ui/src/quick_menu.rs", [
    ('''            QuickRow::GbaShader => Some(QuickRow::ScreenGba),
            QuickRow::GbcShader => Some(QuickRow::ScreenGbc),
            QuickRow::GbShader => Some(QuickRow::ScreenGb),''',
     '''            QuickRow::GbaScaling => Some(QuickRow::ScreenGba),
            QuickRow::GbcScaling => Some(QuickRow::ScreenGbc),
            QuickRow::GbScaling => Some(QuickRow::ScreenGb),'''),
])

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
# Invariants: keep PWM brightness untouched. The only power-layer addition is
# menu-only backlight blank/restore, preserving the stored brightness level.
# Never patch the frame-buffer, keymon, theme files or OnionOS runtime.
allowed = {
    "crates/slot-store/src/core.rs",
    "crates/slot-store/src/slot_state.rs",
    "crates/slot-store/src/gb_palette.rs",
    "crates/slot/src/session.rs",
    "crates/slot/src/video_mode.rs",
    "crates/slot/src/session.rs",
    "crates/slot/src/app.rs",
    "crates/slot-ui/src/quick_menu.rs",
    "crates/slot-power/src/device.rs",
    "crates/slot-power/src/power.rs",
    "crates/slot-power/tests/device.rs",
    "crates/slot/src/frontend.rs",
    "crates/slot-input/src/gesture.rs",
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
print(f"Miyoo no-shader preview: {len(changes)} sources, original mGBA, CPU rendering and PWM preserved")
