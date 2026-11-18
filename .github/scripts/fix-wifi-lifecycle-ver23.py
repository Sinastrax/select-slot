#!/usr/bin/env python3
"""Ver. 23: correct root Wi-Fi teardown rather than hiding the ejection symptom.

Patch after Ver. 21 and Ver. 22 source transformations. This patch touches
only App Wi-Fi/radio policy and Wi-Fi regression tests. Shader, scaling, OTA,
emulator and radio shell scripts are unchanged.
"""
from pathlib import Path

def edit(path, pairs):
    path = Path(path)
    source = path.read_text()
    for before, after, what in pairs:
        count = source.count(before)
        if count != 1:
            raise SystemExit(
                f"{path}: {what}: expected 1 matching section, got {count}"
            )
        source = source.replace(before, after, 1)
    path.write_text(source)
    print(f"Updated {path}")

edit("crates/slot/src/app.rs", [
    (
'''    pub fn end_link(&mut self) {
        let live = self.link.is_some();
        self.ble_off();
        self.end_switch();
        self.join_target = None;
        self.link = None;
        self.link_player = None;
        self.sync_link_badge();
        self.radio_bye = Some(self.now() + RADIO_BYE_MS);
        if !live {
            self.radio_down();
        }
    }''',
'''    pub fn end_link(&mut self) {
        let live = self.link.is_some();
        // Plain game ejection also invokes end_link(). The previous code
        // always sent RadioJob::Down when no link was live. On H700, "link
        // down" runs link_clear -> wifi_stop, killing normal wpa_supplicant
        // and udhcpc even though the Wi-Fi worker still believes it is held.
        // Only perform radio teardown when a real link session or an
        // in-flight link transfer has actually borrowed the radio.
        let borrowed = live
            || self.starting.is_some()
            || self.prejoin.is_some()
            || self.link_core.is_some()
            || self.link_kind_once.is_some()
            || self.join_target.is_some()
            || self.radio_bye.is_some();
        self.ble_off();
        self.end_switch();
        self.join_target = None;
        self.link = None;
        self.link_player = None;
        self.sync_link_badge();
        if borrowed {
            self.radio_bye = Some(self.now() + RADIO_BYE_MS);
            // The link's Down job runs asynchronously, and stops wlan0's
            // supplicant. Let it finish before the normal network attempts
            // to reconnect (the ordinary Wi-Fi settle period adds 2s).
            self.wifi_wanted_at = Some(self.now() + 2_500);
            if !live {
                self.radio_down();
            }
        }
    }''',
    "avoid link radio teardown on ordinary cart ejection"
    ),
    (
'''        if self.seated_cart().is_some() {
            // Keep an already-connected Wi-Fi service alive during a brief
            // DHCP/association outage; do not keep an offline, never-connected
            // radio running just because gameplay began.
            return self.wifi_held
                && (self.wifi_up() || self.wifi_was_up)
                && !matches!(self.phase, Phase::Doze { .. })
                && !self.link_active()
                && !self.shutting_down()
                && !self.state.wifi_off;
        }''',
'''        if self.seated_cart().is_some() {
            // RetroAchievements uses Internet access during ordinary game
            // play. The user-enabled Wi-Fi service must survive game launch
            // and temporary association/DHCP loss. Checking wifi_up() here
            // makes a connection still starting up get deliberately killed.
            // Real link play is different: it borrows wlan0/wlan1 for a
            // direct softAP/STA connection, so infrastructure Wi-Fi must be
            // released until the link ends.
            return (self.wifi_held || self.has_saved())
                && !matches!(self.phase, Phase::Doze { .. })
                && !self.link_active()
                && self.starting.is_none()
                && self.prejoin.is_none()
                && self.reload.is_none()
                && self.link_reload.is_none()
                && self.link_kind_once.is_none()
                && self.join_later.is_none()
                && !self.shutting_down()
                && !self.state.wifi_off;
        }''',
    "retain Wi-Fi in ordinary gameplay including pending DHCP"
    ),
    (
'''        if matches!(self.phase, Phase::Ejecting { .. }) {
            return !self.state.wifi_off
                && !self.link_active()
                && self.prejoin.is_none()
                && !self.shutting_down()
                && (self.wifi_held || self.has_saved());
        }''',
'''        if matches!(self.phase, Phase::Ejecting { .. }) {
            return !self.state.wifi_off
                && !self.link_active()
                && self.starting.is_none()
                && self.prejoin.is_none()
                && self.reload.is_none()
                && self.link_reload.is_none()
                && !self.shutting_down()
                && (self.wifi_held || self.has_saved());
        }''',
    "avoid reconnect during an in-progress link teardown"
    ),
])

edit("crates/slot/tests/wifi_ui.rs", [
    (
'''#[test]
fn a_game_releases_it() {
    let _g = serial();
    let (_d, mut a, log) = on_shelf();
    settle(&mut a);
    a.apply(Action::Insert);
    frames(&mut a, 2);
    assert_eq!(count(&log, "stop"), 1);
    assert!(!a.wifi().held);
}''',
'''#[test]
fn a_game_keeps_enabled_wifi_even_before_dhcp_completes() {
    let _g = serial();
    let fake = Fake::demo();
    let no_lease = fake.no_lease.clone();
    no_lease.store(true, std::sync::atomic::Ordering::SeqCst);
    let (_d, mut a, log) = booted(true, fake);
    settle(&mut a);
    assert!(a.wifi().held);
    assert!(!a.wifi_up());
    a.apply(Action::Insert);
    frames(&mut a, 2);
    assert_eq!(count(&log, "stop"), 0, "game launch stopped pending Wi-Fi");
    assert!(a.wifi().held);
    no_lease.store(false, std::sync::atomic::Ordering::SeqCst);
    settle(&mut a);
    assert!(a.wifi_up(), "network did not finish joining during gameplay");
    assert_eq!(count(&log, "start"), 1);
}''',
    "replace outdated intentional-Wi-Fi-stop expectation"
    ),
])

with Path("crates/slot/tests/wifi_ui.rs").open("a") as out:
    out.write("""
#[derive(Clone, Default)]
struct EjectRadioLog(std::sync::Arc<std::sync::Mutex<Vec<slot::link_radio::RadioJob>>>);

impl slot::link_radio::RadioJobs for EjectRadioLog {
    fn ask(&mut self, job: slot::link_radio::RadioJob) {
        self.0.lock().unwrap().push(job);
    }

    fn warmed(&self) -> bool {
        false
    }
}

impl EjectRadioLog {
    fn jobs(&self) -> Vec<slot::link_radio::RadioJob> {
        self.0.lock().unwrap().clone()
    }
}

#[test]
fn ejecting_an_ordinary_game_does_not_run_link_down_or_stop_wifi() {
    use slot::link_radio::RadioJob;
    let _g = serial();
    let (_d, mut a, log) = on_shelf();
    let radio = EjectRadioLog::default();
    a.set_radio_jobs(Box::new(radio.clone()));
    settle(&mut a);
    join_home(&mut a);
    a.apply(Action::Insert);
    frames(&mut a, 2);
    assert_eq!(count(&log, "stop"), 0);
    a.apply(Action::Eject);
    frames(&mut a, 2);
    assert!(matches!(a.phase(), Phase::Ejecting { .. }));
    assert!(a.wifi().held);
    assert!(!radio.jobs().contains(&RadioJob::Down),
        "normal cart removal sent link down, which stops wlan0 in slotlink.sh");
    assert_eq!(count(&log, "stop"), 0);
    settle(&mut a);
    assert!(a.wifi_up());
    assert_eq!(count(&log, "start"), 1, "unnecessary Wi-Fi restart");
}

#[test]
fn true_link_play_borrows_the_radio_and_rejoins_afterwards() {
    use slot::link_radio::RadioJob;
    let _g = serial();
    let (_d, mut a, log) = on_shelf();
    let radio = EjectRadioLog::default();
    a.set_radio_jobs(Box::new(radio.clone()));
    settle(&mut a);
    join_home(&mut a);
    a.apply(Action::Insert);
    frames(&mut a, 2);
    a.begin_link(0);
    frames(&mut a, 2);
    assert!(!a.wifi().held, "home Wi-Fi must yield to the link's softAP/STA");
    assert_eq!(count(&log, "stop"), 1);
    a.end_link();
    // End the real session and allow asynchronous link-radio teardown.
    a.tick_ms(a.now() + slot::app::RADIO_BYE_MS + 1);
    assert!(radio.jobs().contains(&RadioJob::Down),
        "actual link play must still shut down the link radio");
    for _ in 0..9 {
        a.tick_ms(a.now() + 1_000);
    }
    assert!(a.wifi().held, "home Wi-Fi must reconnect after link play");
    assert_eq!(count(&log, "start"), 2);
}
""")

print("Added true link-down (RadioJob) and gameplay Wi-Fi lifecycle regression tests")
