"""Miyoo custom patches: onion_power; applied in exact build order."""
from .patcher import edit

# OnionOS owns physical POWER and its theme transitions when running its
# native runtime. SLOT must not blank the PWM on PowerTap before OnionOS can
# show whatever splash/shutdown image is provided by the selected theme.
# Queue a save on press without blocking the input loop. A short press belongs
# to Onion; a hold requests the themed shutdown after pending writes settle.
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
                    self.queue_onion_resume_save();
                    return;
                }
                Action::PowerTap => return, // OnionOS short-press suspend
                Action::PowerHold => {
                    // Initiate shutdown before OnionOS keymon's 0.5s
                    // deepsleep path can suspend us and delay power-off
                    // by its thirty-second fallback. We also exit the
                    // interactive Slot menu immediately.
                    eprintln!("slot: POWER hold; requesting OnionOS shutdown");
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
        let onion_runtime = root.join(".tmp_update/runtime.sh").is_file()
            && root.join(".tmp_update/onionVersion/version.txt").is_file();
        let onion_pwm = onion_runtime.then(|| find_pwm(sysfs).map(Backlight::Pwm)).flatten();
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

    // Stock autoboot also contains runtime.sh. It must retain the stock
    // backlight path, not accidentally activate Onion-specific PWM.
    let onion = d.path().join(".tmp_update");
    fs::create_dir_all(&onion).unwrap();
    fs::write(onion.join("runtime.sh"), "#!/bin/sh\\n").unwrap();
    let mut stock_runtime = DevicePlatform::probe(d.path(), d.path().to_path_buf());
    stock_runtime.set_backlight(9);
    assert_eq!(duty(&d), 6);

    // The full OnionOS version marker is required to prefer direct PWM.
    let version = onion.join("onionVersion/version.txt");
    fs::create_dir_all(version.parent().unwrap()).unwrap();
    fs::write(&version, "4.3.1\\n").unwrap();
    let mut slot = DevicePlatform::probe(d.path(), d.path().to_path_buf());
    slot.set_backlight(9);
    assert_eq!(duty(&d), 112);
    // Class isn't touched by the Onion-specific correction.
    assert_eq!(brightness(&d), 255);
}

#[test]
fn extended_brightness_respects_live_onion_pwm_period() {'''),
])




# Taking the core snapshot and writing it can both block while playing. Keep
# them on the save worker so the main loop can recognize the same key hold.
edit("crates/slot/src/persist.rs", [
    ('''pub trait Snapshot {
''', '''pub trait Snapshot {
    fn background_snapshot(&self) -> Option<Box<dyn Snapshot + Send>> {
        None
    }

'''),
])
edit("crates/slot/src/emu.rs", [
    ('''impl Snapshot for EmuSnapshot {
''', '''impl Snapshot for EmuSnapshot {
    fn background_snapshot(&self) -> Option<Box<dyn Snapshot + Send>> {
        Some(Box::new(self.clone()))
    }

'''),
])
edit("crates/slot/src/app.rs", [
    ('''    pub fn flush_resume(&mut self) {''',
     '''    fn queue_onion_resume_save(&mut self) {
        let (Some(root), Some(snapshot), Some(cart)) = (
            &self.root,
            self.snapshot.as_ref().and_then(|snapshot| snapshot.background_snapshot()),
            self.seated(),
        ) else {
            return;
        };
        let (root, platform, core, cart) =
            (root.clone(), self.platform, self.core, cart.to_owned());
        self.autosave_at = self.now() + AUTOSAVE_MS;
        let previous = self.pending_save.take();
        let failing = self.card_writes.clone();
        self.pending_save = Some(std::thread::spawn(move || {
            if let Some(previous) = previous {
                let _ = previous.join();
            }
            let Some(state) = snapshot.state() else {
                eprintln!("slot: power save: the core gave up no state");
                return;
            };
            let (state, sav) = trusted_write(snapshot.as_ref(), state, "power save");
            let written = persist::flush(
                &root, platform, core, &cart, state.as_deref(), sav.as_deref(),
            );
            if let Err(error) = &written {
                eprintln!("slot: power save: {error}");
            }
            failing.wrote("power save", &written);
        }));
    }

    pub fn flush_resume(&mut self) {'''),
])

# A busy frame can deliver release before the periodic hold check.
# Classify the held time before clearing the press and emit a hold only once.
edit("crates/slot-input/src/gesture.rs", [
    ('''            Btn::Power => self.power_up(),''',
     '''            Btn::Power => self.power_up(now),'''),
    ('''    fn power_up(&mut self) -> Vec<Action> {
        let held = self.power_hold_fired;
        self.power_down_at = None;
        self.power_hold_fired = false;
        vec![if held {
            Action::PowerOff
        } else {
            Action::PowerTap
        }]
    }''',
     '''    fn power_up(&mut self, now: Millis) -> Vec<Action> {
        let held_for = self.power_down_at.take()
            .map_or(0, |since| now.saturating_sub(since));
        if std::mem::take(&mut self.power_hold_fired) {
            vec![Action::PowerOff]
        } else if held_for >= POWER_HOLD_MS {
            vec![Action::PowerHold, Action::PowerOff]
        } else {
            vec![Action::PowerTap]
        }
    }'''),
])

edit("crates/slot-input/tests/gesture.rs", [
    ('''#[test]
fn a_press_just_short_of_the_threshold_is_a_lock() {''',
     '''#[test]
fn power_release_still_registers_a_hold_if_the_frame_missed_the_tick() {
    let mut g = gestures();
    let down = 100;
    assert_eq!(g.feed(Down(Btn::Power), down), vec![PowerPress]);
    assert_eq!(
        g.feed(Up(Btn::Power), down + POWER_HOLD_MS + 20),
        vec![PowerHold, PowerOff],
    );
    assert!(g.tick(down + POWER_HOLD_MS + 50).is_empty());
}

#[test]
fn a_press_just_short_of_the_threshold_is_a_lock() {'''),
])
