#!/usr/bin/env python3
"""Keep connected Wi-Fi across cartridge ejection and show branded OTA versions.

Only UI/connection lifecycle changes; never change archive URL, manifest key,
size, SHA-256, archive staging, emulator or shader code.
"""
from pathlib import Path

def edit(path, replacements):
    p=Path(path)
    data=p.read_text()
    for old,new,label in replacements:
        n=data.count(old)
        if n != 1:
            raise SystemExit(f"{path} {label}: wanted one match, got {n}")
        data=data.replace(old,new,1)
    p.write_text(data)
    print("Patched",path)

edit("crates/slot/src/update.rs", [
    (
'''pub fn newer(release: &str, running: &str) -> bool {''',
'''/// Friendly text for the OTA screen only. Never use this to name or fetch
/// release archives: existing updaters expect slot-v<technical>-h700.zip.
pub fn display_version(kind: Kind, version: &str) -> String {
    if kind == Kind::BaseOs {
        return format!("v{version}");
    }
    if let Some((upstream, suffix)) = version.split_once('-') {
        for prefix in ["rgsp.", "custom.", "select."] {
            if let Some(revision) = suffix.strip_prefix(prefix) {
                if !revision.is_empty() && revision.bytes().all(|b| b.is_ascii_digit()) {
                    return format!("{upstream} Ver. {revision}");
                }
            }
        }
    }
    format!("v{version}")
}

pub fn newer(release: &str, running: &str) -> bool {''',
    "human version display"
    )
])

edit("crates/slot/src/app.rs", [
    (
'''            UpdateState::UpToDate => (
                "slot is up to date".into(),
                format!("{running} is the latest version."),
            ),''',
'''            UpdateState::UpToDate => (
                "select. slot. is up to date".into(),
                format!(
                    "{} is the latest version.",
                    crate::update::display_version(Kind::Slot, running)
                ),
            ),''',
    "up-to-date branding"
    ),
    (
'''        .map(|r| (format!("v{}", r.running), format!("v{}", r.version)))
    }

    pub fn update_chosen''',
'''        .map(|r| (
            crate::update::display_version(r.kind, &r.running),
            crate::update::display_version(r.kind, &r.version),
        ))
    }

    pub fn update_chosen''',
    "version chip labels"
    ),
    (
'''            return self.wifi_held
                && self.wifi_up()
                && !matches!(self.phase, Phase::Doze { .. })''',
'''            // Keep an already-started Wi-Fi daemon alive even during
            // temporary association/DHCP loss. A game does not initiate Wi-Fi,
            // but it must not kill a connection that is recovering.
            return self.wifi_held
                && !matches!(self.phase, Phase::Doze { .. })''',
    "keep already held Wi-Fi across brief disconnections in games"
    ),
    (
'''            Phase::Shelf
                | Phase::QuickMenu { .. }
                | Phase::About''',
'''            Phase::Shelf
                // Keep Wi-Fi alive while a game cart is being pulled and
                // Slot returns to the shelf. Ejection must not call slotlink
                // wifi stop and kill wpa_supplicant/udhcpc.
                | Phase::Ejecting { .. }
                | Phase::QuickMenu { .. }
                | Phase::About''',
    "preserve connection during ejection"
    ),
])

edit("crates/slot/tests/update_ui.rs", [
    (
'''            "slot is up to date".into(),
            format!("{running} is the latest version.")''',
'''            "select. slot. is up to date".into(),
            format!(
                "{} is the latest version.",
                slot::update::display_version(Kind::Slot, running)
            )''',
    "OTA up to date test"
    ),
    (
'''        Some((format!("v{running}"), "v99.0.0".to_string()))''',
'''        Some((
            slot::update::display_version(Kind::Slot, running),
            "v99.0.0".to_string()
        ))''',
    "OTA chip label test"
    ),
    (
'''fn baseos() -> Release {''',
'''#[test]
fn select_slot_ota_labels_are_user_friendly_but_archive_urls_stay_original() {
    use slot::update::display_version;
    assert_eq!(display_version(Kind::Slot, "1.16.0-rgsp.20"), "1.16.0 Ver. 20");
    assert_eq!(display_version(Kind::Slot, "1.16.0-rgsp.21"), "1.16.0 Ver. 21");
    assert_eq!(display_version(Kind::Slot, "1.16.0-select.6"), "1.16.0 Ver. 6");
    assert_eq!(display_version(Kind::Slot, "1.16.0-custom.3"), "1.16.0 Ver. 3");
    assert_eq!(display_version(Kind::Slot, "1.16.0-pvaibhav.1"), "v1.16.0-pvaibhav.1");
    assert_eq!(display_version(Kind::BaseOs, "1.4.0"), "v1.4.0");
    let release = release();
    assert_eq!(release.url, "https://example.invalid/slot.zip");
}

fn baseos() -> Release {''',
    "OTA UI regression"
    ),
])

edit("crates/slot/tests/wifi_ui.rs", [
    (
'''#[test]
fn a_failed_hold_tries_again_after_a_minute()''',
'''#[test]
fn pulling_a_connected_game_cartridge_keeps_wifi_daemons_running() {
    let _g = serial();
    let (_d, mut a, log) = on_shelf();
    settle(&mut a);
    join_home(&mut a);
    assert!(a.wifi_up());
    a.apply(Action::Insert);
    frames(&mut a, 2);
    assert!(a.wifi().held);
    a.apply(Action::Eject);
    frames(&mut a, 2);
    assert!(a.wifi().held, "Wi-Fi was released during cartridge pull");
    settle(&mut a);
    assert!(a.wifi().held, "Wi-Fi was released on return to shelf");
    assert!(a.wifi_up());
    assert_eq!(count(&log, "stop"), 0, "slotlink wifi stop was called");
    assert_eq!(count(&log, "start"), 1, "unnecessary Wi-Fi restart");
}

#[test]
fn a_failed_hold_tries_again_after_a_minute()''',
    "cartridge eject connection retention regression"
    ),
])
