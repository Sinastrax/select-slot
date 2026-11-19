"""Miyoo custom patches: idle; applied in exact build order."""
from .patcher import edit

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


