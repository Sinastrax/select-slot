"""Miyoo custom patches: onion_power; applied in exact build order."""
from .patcher import edit

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



