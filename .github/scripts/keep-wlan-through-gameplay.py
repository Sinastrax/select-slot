#!/usr/bin/env python3
"""Ver.23: normal WLAN stays held during gameplay, with auto-reconnect.

Link play retains its explicit radio handoff, and explicit Wi-Fi Off,
sleep and shutdown still release the service. This runs AFTER Ver.22.
"""
from pathlib import Path

def replace_one(path, before, after):
    p=Path(path)
    s=p.read_text()
    n=s.count(before)
    if n!=1:
        raise SystemExit(f"{path}: expected one match, found {n}: {before[:100]!r}")
    p.write_text(s.replace(before,after,1))

replace_one("crates/slot/src/app.rs",
'''            // A game keeps a connection it already has, so RetroAchievements stay online, but
            // never starts one: a scan while playing can stall frames.
            return self.wifi_held
                && self.wifi_up()
                && !matches!(self.phase, Phase::Doze { .. })
                && !self.link_active()
                && !self.shutting_down()
                && !self.state.wifi_off;''',
'''            // Keep the normal infrastructure connection alive throughout
            // gameplay, including DHCP/association loss and reconnection.
            // Requiring wifi_up() here previously issued Cmd::Release as
            // soon as the IP disappeared, permanently stopping the service.
            // Saved networks can start/rejoin while a game is running, which
            // is also needed for online RetroAchievements.
            //
            // Link play owns the radio separately and explicitly releases
            // infrastructure Wi-Fi during its local multiplayer handoff.
            // Network scanning UI is still limited to the network menu.
            return (self.wifi_held || self.has_saved())
                && !matches!(self.phase, Phase::Doze { .. })
                && !self.link_active()
                && self.prejoin.is_none()
                && !self.shutting_down()
                && !self.state.wifi_off;''')

replace_one("crates/slot/tests/wifi_ui.rs",
'''fn a_game_releases_it() {
    let _g = serial();
    let (_d, mut a, log) = on_shelf();
    settle(&mut a);
    a.apply(Action::Insert);
    frames(&mut a, 2);
    assert_eq!(count(&log, "stop"), 1);
    assert!(!a.wifi().held);
}''',
'''fn a_game_keeps_wlan_active_for_online_features() {
    let _g = serial();
    let (_d, mut a, log) = on_shelf();
    settle(&mut a);
    assert!(a.wifi().held);
    a.apply(Action::Insert);
    frames(&mut a, 2);
    assert_eq!(count(&log, "stop"), 0);
    assert!(a.wifi().held);
}''')

with Path("crates/slot/tests/wifi_ui.rs").open("a") as out:
    out.write("""
#[test]
fn offline_game_starts_saved_wifi_instead_of_shutting_it_down() {
    let _g = serial();
    let (_d, mut a, log) = on_shelf();
    // The startup Wi-Fi settle delay has not elapsed yet.
    a.apply(Action::Insert);
    frames(&mut a, 2);
    assert_eq!(count(&log, "stop"), 0);
    settle(&mut a);
    assert!(a.wifi().held, "game must connect to saved Wi-Fi");
    assert_eq!(count(&log, "start"), 1);
    assert_eq!(count(&log, "stop"), 0);
}

#[test]
fn lost_ip_during_game_does_not_turn_off_wifi_or_on_eject() {
    let _g = serial();
    let fake = Fake::demo();
    let no_lease = fake.no_lease.clone();
    let (_d, mut a, log) = booted(true, fake);
    settle(&mut a);
    join_home(&mut a);
    assert!(a.wifi_up());
    a.apply(Action::Insert);
    frames(&mut a, 2);
    no_lease.store(true, std::sync::atomic::Ordering::SeqCst);
    settle(&mut a);
    assert!(!a.wifi_up());
    assert!(a.wifi().held, "lost DHCP lease must not release the WLAN service");
    assert_eq!(count(&log, "stop"), 0);
    a.apply(Action::Eject);
    frames(&mut a, 2);
    assert_eq!(count(&log, "stop"), 0);
    no_lease.store(false, std::sync::atomic::Ordering::SeqCst);
    settle(&mut a);
    assert!(a.wifi().held);
    assert!(a.wifi_up(), "returning to shelf must restore a saved connection");
}
""")
print("Ver.23 gameplay WLAN retention and reconnect regressions installed")
