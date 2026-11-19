"""Miyoo custom patches: scaling; applied in exact build order."""
from .patcher import edit

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

