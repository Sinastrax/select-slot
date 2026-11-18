#!/usr/bin/env python3
"""Ver.25: RetroAchievements login via the built-in keyboard; restart required.

Existing RetroAchievements service remains a startup-only service. The UI never
displays previously saved passwords. Credentials are written atomically and
UI-created passwords are scrubbed after a successful login token is saved.
"""
from pathlib import Path

def repl(path, changes):
    p=Path(path)
    s=p.read_text()
    for before,after,name in changes:
        n=s.count(before)
        if n!=1:
            raise SystemExit(f"{path}: {name}: expected 1 match, got {n}")
        s=s.replace(before,after,1)
    p.write_text(s)
    print("Updated", path)

repl("crates/slot-ui/src/quick_menu.rs",[
("""    BatteryDisplay,
    System,
}""",
"""    BatteryDisplay,
    System,
    RetroAchievements,
}""","new enum row"),
("""pub const ALL: [QuickRow; 143 + cfg!(feature = "nds") as usize]""",
"""pub const ALL: [QuickRow; 144 + cfg!(feature = "nds") as usize]""","row array capacity"),
("""        QuickRow::BatteryDisplay,
        QuickRow::System,
    ];""",
"""        QuickRow::BatteryDisplay,
        QuickRow::System,
        QuickRow::RetroAchievements,
    ];""","row array entry"),
("""    pub const SYSTEM: [QuickRow; 7] = [
        QuickRow::Wifi,""",
"""    pub const SYSTEM: [QuickRow; 8] = [
        QuickRow::Wifi,
        QuickRow::RetroAchievements,""","system menu"),
("""            | QuickRow::Nickname => &QuickRow::SYSTEM,""",
"""            | QuickRow::Nickname
            | QuickRow::RetroAchievements => &QuickRow::SYSTEM,""","menu group"),
("""            QuickRow::Nickname => "Nickname",""",
"""            QuickRow::Nickname => "Nickname",
            QuickRow::RetroAchievements => "RetroAchievements",""","row label"),
("""                | QuickRow::Nickname
                | QuickRow::RommServer""",
"""                | QuickRow::Nickname
                | QuickRow::RetroAchievements
                | QuickRow::RommServer""","row opens"),
])

repl("crates/slot-ui/src/keyboard.rs", [
("""    help: bool,
    aim: Option<f32>,""",
"""    help: bool,
    aim: Option<f32>,
    masked: bool,""","mask field"),
("""            help: false,
            aim: None,
        }
    }

    pub fn layout""",
"""            help: false,
            aim: None,
            masked: false,
        }
    }

    /// Preserve the actual typed secret for submission; render only stars.
    pub fn masked(mut self) -> Self {
        self.masked = true;
        self
    }

    pub fn layout""","mask builder"),
("""pub fn keyboard_text_face(kb: &Keyboard) -> (UndoFace, Vec<f32>) {
    let typed = kb.text();""",
"""pub fn keyboard_text_face(kb: &Keyboard) -> (UndoFace, Vec<f32>) {
    let typed = if kb.masked {
        "*".repeat(kb.text.len())
    } else {
        kb.text()
    };""","mask display"),
])

repl("crates/slot-achievements/Cargo.toml", [
("""features = ["std", "parse", "serde"]""",
"""features = ["std", "parse", "serde", "display"]""","allow safe TOML credential serialization"),
])

repl("crates/slot-achievements/src/storage.rs", [
("""#[derive(Clone, Deserialize, Default)]
#[serde(default, deny_unknown_fields)]
pub(crate) struct Config {
    pub enabled: bool,
    pub username: String,
    pub token: String,
    pub password: String,
}""",
"""#[derive(Clone, Serialize, Deserialize, Default)]
#[serde(default, deny_unknown_fields)]
pub(crate) struct Config {
    pub enabled: bool,
    pub username: String,
    pub token: String,
    pub password: String,
    // Only login entries made using Slot's keyboard are auto-scrubbed.
    pub ui_login: bool,
}""","UI provisioned credentials marker"),
("""#[derive(Clone, Serialize, Deserialize)]
pub(crate) struct Auth {""",
"""/// Stage credentials on SD for the next startup; never perform an in-place
/// account switch while the achievement workers still own the old account.
pub(crate) fn configure_login(root: &Path, username: &str, password: &str) -> Result<(), &'static str> {
    let username = username.trim();
    if username.is_empty() || username.len() > 128 || password.len() > 256 {
        return Err("Invalid RetroAchievements credentials");
    }
    let path = root.join("Config/retroachievements.toml");
    let mut config = Config::read(&path).unwrap_or_default();
    if !config.username.eq_ignore_ascii_case(username) {
        config.token.clear();
        config.password.clear();
    }
    let has_remembered = {
        let account = format!("{:x}", md5::compute(username.to_lowercase()));
        root.join("Saves/RetroAchievements").join(account).join("auth.json").exists()
    };
    if password.is_empty() && config.token.is_empty()
        && config.password.is_empty() && !has_remembered
    {
        return Err("Password needed for this account");
    }
    if !password.is_empty() {
        config.password = password.into();
        config.token.clear();
    }
    config.enabled = true;
    config.username = username.into();
    config.ui_login = true;
    let text = toml::to_string(&config).map_err(|_| "Cannot serialize RA login")?;
    std::fs::create_dir_all(path.parent().ok_or("Missing config directory")?)
        .map_err(|_| "Cannot create RA config")?;
    slot_store::atomic_write(&path, text.as_bytes()).map_err(|_| "Cannot save RA login")?;
    protect(&path);
    Ok(())
}

/// Once the worker has durably remembered the token, discard passwords entered
/// with the menu. Do not alter hand-edited configuration files.
pub(crate) fn scrub_ui_password(root: &Path, username: &str, password: &str) {
    if password.is_empty() {
        return;
    }
    let path = root.join("Config/retroachievements.toml");
    let Ok(mut config) = Config::read(&path) else { return };
    if !config.ui_login || config.username != username || config.password != password {
        return;
    }
    config.password.clear();
    if let Ok(text) = toml::to_string(&config) {
        if slot_store::atomic_write(&path, text.as_bytes()).is_ok() {
            protect(&path);
        }
    }
}

fn protect(path: &Path) {
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let _ = std::fs::set_permissions(path, std::fs::Permissions::from_mode(0o600));
    }
    #[cfg(not(unix))]
    let _ = path;
}

#[derive(Clone, Serialize, Deserialize)]
pub(crate) struct Auth {""","create and scrub UI credentials"),
])

repl("crates/slot-achievements/src/lib.rs",[
("""pub use badges::{load_badge, BadgeImage};
pub use ready::Readiness;""",
"""pub use badges::{load_badge, BadgeImage};
pub use ready::Readiness;

/// UI login credentials are staged for restart; the running session is not changed.
pub fn configure_login(root: &std::path::Path, username: &str, password: &str) -> Result<(), &'static str> {
    storage::configure_login(root, username, password)
}

pub fn configured_username(root: &std::path::Path) -> Option<String> {
    storage::Config::read(&root.join("Config/retroachievements.toml"))
        .ok()
        .map(|c| c.username)
        .filter(|s| !s.is_empty())
}""","public minimal account UI API"),
])

repl("crates/slot-achievements/src/network.rs",[
("""                storage::write(&dir.join("auth.json"), &logged_in).map_err(|_| Failure::Invalid)?;
                auth = Some(logged_in);
                verified = true;""",
"""                storage::write(&dir.join("auth.json"), &logged_in).map_err(|_| Failure::Invalid)?;
                // Only after the token is durably on disk, scrub a password
                // staged from the on-device login menu.
                storage::scrub_ui_password(&root, &config.username, &config.password);
                auth = Some(logged_in);
                verified = true;""","remove UI-entered password after token is saved"),
])

repl("crates/slot/src/app.rs", [
("""pub enum KeyboardFor {
    Password { ssid: String, hidden: bool },""",
"""pub enum KeyboardFor {
    Password { ssid: String, hidden: bool },
    RaUsername,
    RaPassword { username: String },""","RA keyboard tasks"),
("""enum NetNotice {
    Password,""",
"""enum NetNotice {
    Password,
    RaRestart,
    RaPasswordNeeded,
    RaSaveFailed,""","restart and error notices"),
("""            | QuickRow::Nickname
            | QuickRow::RommPort""",
"""            | QuickRow::Nickname
            | QuickRow::RetroAchievements
            | QuickRow::RommPort""","quick value no extra value"),
("""            QuickRow::WifiPower => self.set_wifi_off(!self.state.wifi_off),
            QuickRow::Networks => self.open_networks(),""",
"""            QuickRow::WifiPower => self.set_wifi_off(!self.state.wifi_off),
            QuickRow::Networks => self.open_networks(),
            QuickRow::RetroAchievements => {
                let user = self.root.as_deref()
                    .and_then(slot_achievements::configured_username)
                    .unwrap_or_default();
                self.open_keyboard(
                    "RetroAchievements Username",
                    Some("Changes apply after restart"),
                    KeyboardFor::RaUsername,
                    slot_ui::Layout::General,
                    &user,
                );
            },""","open username"),
("""            | QuickRow::Nickname
            | QuickRow::Server => return,""",
"""            | QuickRow::Nickname
            | QuickRow::RetroAchievements
            | QuickRow::Server => return,""","settings match exhaustive"),
("""        let kb = slot_ui::Keyboard::new(layout, title, subtitle, text);
        self.keyboard = Some((kb, task));""",
"""        let kb = slot_ui::Keyboard::new(layout, title, subtitle, text);
        let kb = if matches!(task, KeyboardFor::RaPassword { .. }) {
            kb.masked()
        } else {
            kb
        };
        self.keyboard = Some((kb, task));""","mask entered RA password"),
("""            KeyboardFor::CollectionName => self.name_collection(text),""",
"""            KeyboardFor::CollectionName => self.name_collection(text),
            KeyboardFor::RaUsername => {
                let username = text.trim();
                if username.is_empty() {
                    if let Some((kb, _)) = &mut self.keyboard {
                        kb.refuse("Enter a username");
                    }
                    return;
                }
                self.open_keyboard(
                    "RetroAchievements Password",
                    Some("Leave blank for a saved account"),
                    KeyboardFor::RaPassword { username: username.into() },
                    slot_ui::Layout::General,
                    "",
                );
            }
            KeyboardFor::RaPassword { username } => {
                let result = self.root.as_deref()
                    .ok_or("No card root")
                    .and_then(|root| slot_achievements::configure_login(root, &username, &text));
                self.keyboard = None;
                let notice = match result {
                    Ok(()) => NetNotice::RaRestart,
                    Err("Password needed for this account") => NetNotice::RaPasswordNeeded,
                    Err(_) => NetNotice::RaSaveFailed,
                };
                self.set_update(Some(UpdateState::Notice(notice)));
            },""","stage and warn; no hot reload"),
("""            UpdateState::Notice(NetNotice::Password) => ("Invalid Password".into(), String::new()),""",
"""            UpdateState::Notice(NetNotice::Password) => ("Invalid Password".into(), String::new()),
            UpdateState::Notice(NetNotice::RaRestart) => (
                "RetroAchievements saved".into(),
                "Restart Slot for the login to take effect.".into(),
            ),
            UpdateState::Notice(NetNotice::RaPasswordNeeded) => (
                "Enter a password".into(),
                "No saved login token exists for this account.".into(),
            ),
            UpdateState::Notice(NetNotice::RaSaveFailed) => (
                "Could not save login".into(),
                "Check the SD card and try again.".into(),
            ),""","restart warning screen"),
])
print("RetroAchievements login staged in System menu; no live account switching")
