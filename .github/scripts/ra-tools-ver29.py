#!/usr/bin/env python3
"""Ver.29: Tools > RetroAchievements: account, status, library, retry, indexing.

All service actions remain non-blocking. The account editor stays masked and
continues to apply login changes only after a restart.
"""
from pathlib import Path
import re

def change(path, before, after, why):
    p = Path(path)
    data = p.read_text()
    count = data.count(before)
    if count != 1:
        raise SystemExit(f"{path}: {why}: expected exactly one match, got {count}")
    p.write_text(data.replace(before, after, 1))
    print(f"Ver29 {path}: {why}")

menu="crates/slot-ui/src/quick_menu.rs"
change(menu,
'''    System,
    RetroAchievements,
}''',
'''    System,
    RetroAchievements,
    RaAccount,
    RaStatus,
    RaPrepare,
    RaRetry,
    RaBackground,
}''',
"submenu rows")
change(menu,
'''        QuickRow::System,
        QuickRow::RetroAchievements,
    ];''',
'''        QuickRow::System,
        QuickRow::RetroAchievements,
        QuickRow::RaAccount,
        QuickRow::RaStatus,
        QuickRow::RaPrepare,
        QuickRow::RaRetry,
        QuickRow::RaBackground,
    ];''',
"enum order mirrored by ALL")
p=Path(menu)
s=p.read_text()
m=re.search(r'(pub const ALL: \[QuickRow; )(\d+)( \+ cfg!\(feature = "nds"\) as usize\])',s)
if not m:
    raise SystemExit("Cannot update QuickRow ALL count")
s=s[:m.start(2)]+str(int(m.group(2))+5)+s[m.end(2):]
p.write_text(s)
change(menu,
'''    pub const ROMM: [QuickRow; 8] = [''',
'''    pub const RA: [QuickRow; 5] = [
        QuickRow::RaAccount,
        QuickRow::RaStatus,
        QuickRow::RaPrepare,
        QuickRow::RaRetry,
        QuickRow::RaBackground,
    ];

    pub const ROMM: [QuickRow; 8] = [''',
"dedicated RA submenu")
change(menu,
'''            QuickRow::RetroAchievements => &QuickRow::NETWORK,''',
'''            QuickRow::RetroAchievements => &QuickRow::NETWORK,
            QuickRow::RaAccount | QuickRow::RaStatus | QuickRow::RaPrepare
            | QuickRow::RaRetry | QuickRow::RaBackground => &QuickRow::RA,''',
"submenu navigation")
change(menu,
'''            QuickRow::RommProtocol => Some(QuickRow::Romm),''',
'''            QuickRow::RommProtocol => Some(QuickRow::Romm),
            QuickRow::RaAccount => Some(QuickRow::RetroAchievements),''',
"B returns to RA submenu")
change(menu,
'''            QuickRow::Romm => Some(QuickRow::ROMM[0]),''',
'''            QuickRow::Romm => Some(QuickRow::ROMM[0]),
            QuickRow::RetroAchievements => Some(QuickRow::RA[0]),''',
"open RA submenu")
change(menu,
'''            QuickRow::RetroAchievements => "RetroAchievements",''',
'''            QuickRow::RetroAchievements => "RetroAchievements",
            QuickRow::RaAccount => "Account",
            QuickRow::RaStatus => "Sync Status",
            QuickRow::RaPrepare => "Prepare Library",
            QuickRow::RaRetry => "Retry Failed Games",
            QuickRow::RaBackground => "Background Index",''',
"readable row names")
change(menu,
'''                | QuickRow::RetroAchievements
                | QuickRow::RommServer''',
'''                | QuickRow::RetroAchievements
                | QuickRow::RaAccount
                | QuickRow::RaStatus
                | QuickRow::RaPrepare
                | QuickRow::RaRetry
                | QuickRow::RaBackground
                | QuickRow::RommServer''',
"open or act on RA rows")

app="crates/slot/src/app.rs"
change(app,
'''pub struct App {
    phase: Phase,''',
'''pub struct App {
    phase: Phase,
    ra_action: Option<slot_achievements::LibraryAction>,
    ra_overview: Option<slot_achievements::Overview>,''',
"store live worker status and requested command")
change(app,
'''            phase: Phase::Shelf,
            shelves,''',
'''            phase: Phase::Shelf,
            ra_action: None,
            ra_overview: None,
            shelves,''',
"init RA app state")
change(app,
'''    pub fn quick_menu(&self) -> Option<QuickRow> {''',
'''    pub fn set_achievement_overview(&mut self, overview: slot_achievements::Overview) {
        self.ra_overview = Some(overview);
    }

    pub fn take_achievement_action(&mut self) -> Option<slot_achievements::LibraryAction> {
        self.ra_action.take()
    }

    pub fn quick_menu(&self) -> Option<QuickRow> {''',
"relay nonblocking RA requests to service")
change(app,
'''            QuickRow::WifiPower => Some(QuickValue::flag(!self.state.wifi_off)),''',
'''            QuickRow::WifiPower => Some(QuickValue::flag(!self.state.wifi_off)),
            QuickRow::RaBackground => Some(QuickValue::flag(
                self.ra_overview.is_some_and(|status| status.index_library)
            )),''',
"background index toggle value")
change(app,
'''            | QuickRow::RetroAchievements
            | QuickRow::RommPort''',
'''            | QuickRow::RetroAchievements
            | QuickRow::RaAccount
            | QuickRow::RaStatus
            | QuickRow::RaPrepare
            | QuickRow::RaRetry
            | QuickRow::RommPort''',
"no synthetic value on action rows")
change(app,
'''    RaInvalidCredentials,''',
'''    RaInvalidCredentials,
    RaStatus,
    RaQueued,
    RaRetryQueued,
    RaNoFailures,
    RaNotConfigured,''',
"RA status and feedback notices")
change(app,
'''            QuickRow::RetroAchievements => {
                let user = self.root.as_deref()''',
'''            QuickRow::RaAccount => {
                let user = self.root.as_deref()''',
"move login editor into Account")
change(app,
'''            QuickRow::RommStatus | QuickRow::RommPairedServer => {}''',
'''            QuickRow::RommStatus | QuickRow::RommPairedServer => {}
            QuickRow::RaStatus => self.set_update(Some(UpdateState::Notice(NetNotice::RaStatus))),
            QuickRow::RaPrepare => {
                if self.ra_overview.is_some_and(|status| status.state != slot_achievements::SyncStatus::Disabled) {
                    self.ra_action = Some(slot_achievements::LibraryAction::Prepare);
                    self.set_update(Some(UpdateState::Notice(NetNotice::RaQueued)));
                } else {
                    self.set_update(Some(UpdateState::Notice(NetNotice::RaNotConfigured)));
                }
            }
            QuickRow::RaRetry => {
                if self.ra_overview.is_some_and(|status| status.failed_roms > 0) {
                    self.ra_action = Some(slot_achievements::LibraryAction::RetryFailed);
                    self.set_update(Some(UpdateState::Notice(NetNotice::RaRetryQueued)));
                } else {
                    self.set_update(Some(UpdateState::Notice(NetNotice::RaNoFailures)));
                }
            }
            QuickRow::RaBackground => self.toggle_ra_index(),''',
"status, prepare and retry actions")
change(app,
'''            | QuickRow::Romm
            | QuickRow::Wifi
            | QuickRow::Controls''',
'''            | QuickRow::Romm
            | QuickRow::RetroAchievements
            | QuickRow::Wifi
            | QuickRow::Controls''',
"open RA submenu instead of keyboard")
change(app,
'''    fn change_setting(&mut self, row: QuickRow, right: bool) {
        match row {''',
'''    fn toggle_ra_index(&mut self) {
        let enabled = !self.ra_overview.is_some_and(|status| status.index_library);
        let result = self.root.as_deref()
            .ok_or("Missing SD card")
            .and_then(|root| slot_achievements::set_library_index(root, enabled));
        match result {
            Ok(()) => {
                if let Some(overview) = &mut self.ra_overview {
                    overview.index_library = enabled;
                }
                self.ra_action = Some(slot_achievements::LibraryAction::SetIndex(enabled));
            }
            Err(_) => self.set_update(Some(UpdateState::Notice(NetNotice::RaSaveFailed))),
        }
    }

    fn change_setting(&mut self, row: QuickRow, right: bool) {
        if row == QuickRow::RaBackground {
            return self.toggle_ra_index();
        }
        match row {''',
"persist index toggle and notify worker")
change(app,
'''            | QuickRow::RommDisconnect
            | QuickRow::Nickname
            | QuickRow::RetroAchievements
            | QuickRow::Server => return,''',
'''            | QuickRow::RommDisconnect
            | QuickRow::RaAccount
            | QuickRow::RaStatus
            | QuickRow::RaPrepare
            | QuickRow::RaRetry
            | QuickRow::RaBackground
            | QuickRow::RetroAchievements
            | QuickRow::Nickname
            | QuickRow::Server => return,''',
"settings exhaustive match")
change(app,
'''            UpdateState::Notice(NetNotice::RaInvalidCredentials) => (
                "Invalid login entry".into(),
                "Check the username and password length.".into(),
            ),''',
'''            UpdateState::Notice(NetNotice::RaInvalidCredentials) => (
                "Invalid login entry".into(),
                "Check the username and password length.".into(),
            ),
            UpdateState::Notice(NetNotice::RaStatus) => {
                let detail = match self.ra_overview {
                    Some(status) => {
                        let state = match status.state {
                            slot_achievements::SyncStatus::Disabled => "Not configured",
                            slot_achievements::SyncStatus::Syncing => "Syncing",
                            slot_achievements::SyncStatus::Ready => "Ready",
                            slot_achievements::SyncStatus::Offline => "Offline / retrying",
                            slot_achievements::SyncStatus::Attention => "Needs attention",
                        };
                        format!("{state}; {} failed ROMs; {}",
                            status.failed_roms,
                            status.progress.map_or("No scan".into(), |p| format!("{p}%")))
                    }
                    None => "Checking service".into(),
                };
                ("RetroAchievements".into(), detail)
            }
            UpdateState::Notice(NetNotice::RaQueued) => (
                "Preparing library".into(),
                "Checks pending games while idle with the lid open.".into(),
            ),
            UpdateState::Notice(NetNotice::RaRetryQueued) => (
                "Retrying failed games".into(),
                "Pending failed ROMs have been queued again.".into(),
            ),
            UpdateState::Notice(NetNotice::RaNoFailures) => (
                "No failed games".into(),
                "Nothing is currently marked for retry.".into(),
            ),
            UpdateState::Notice(NetNotice::RaNotConfigured) => (
                "RetroAchievements disabled".into(),
                "Configure your account and restart first.".into(),
            ),''',
"clear diagnostic text")

sess="crates/slot/src/session.rs"
change(sess,
'''    pub fn update(&mut self, dt: f32) {
        self.bridge_link(|app| app.update(dt));
        let up = self.app.wifi_up();''',
'''    pub fn update(&mut self, dt: f32) {
        self.app.set_achievement_overview(self.achievements.overview());
        self.bridge_link(|app| app.update(dt));
        if let Some(action) = self.app.take_achievement_action() {
            self.achievements.request_library(action);
        }
        let awake = !matches!(self.app.phase(), Phase::Doze { .. });
        self.achievements.set_activity(awake, self.emu.is_some());
        let up = self.app.wifi_up();''',
"service receives requests and observes sleep/gameplay")
