#!/usr/bin/env python3
"""Ver.26: accept older RetroAchievements config extensions and report save failures accurately.

Do not overwrite malformed configuration files, lose extra settings or reveal
passwords in the logs. Save success still requires an atomic verified card write.
"""
from pathlib import Path

def patch(path,changes):
    p=Path(path)
    s=p.read_text()
    for before,after,why in changes:
        n=s.count(before)
        if n!=1:
            raise SystemExit(f"{path}: {why}: expected one match, got {n}")
        s=s.replace(before,after,1)
    p.write_text(s)
    print("Patched",path)

patch("crates/slot-achievements/src/storage.rs",[
    (
'''#[serde(default, deny_unknown_fields)]
pub(crate) struct Config {
    pub enabled: bool,
    pub username: String,
    pub token: String,
    pub password: String,
    // Only login entries made using Slot's keyboard are auto-scrubbed.
    pub ui_login: bool,
}''',
'''#[serde(default)]
pub(crate) struct Config {
    pub enabled: bool,
    pub username: String,
    pub token: String,
    pub password: String,
    // Only login entries made using Slot's keyboard are auto-scrubbed.
    pub ui_login: bool,
    // A pre-existing user config may contain additional options from a
    // different build. Preserve them instead of refusing to save the login.
    #[serde(flatten)]
    pub extra: BTreeMap<String, toml::Value>,
}''',
    "preserve legacy configuration fields"
    ),
    (
'''    let mut config = if path.exists() {
        Config::read(&path).map_err(|_| "Cannot read existing achievement config")?
    } else {
        Config::default()
    };''',
'''    let mut config = if path.exists() {
        // Refuse to replace a malformed or unreadable file; do not silently
        // destroy a prior account configuration.
        Config::read(&path)?
    } else {
        Config::default()
    };''',
    "distinguish malformed TOML from failed file reads"
    ),
    (
'''    slot_store::atomic_write(&path, text.as_bytes()).map_err(|_| "Cannot save RA login")?;
    protect(&path);
    Ok(())''',
'''    slot_store::atomic_write(&path, text.as_bytes()).map_err(|error| {
        // The specific filesystem failure is safe to log; no password value.
        eprintln!("slot: RetroAchievements login save failed: {error}");
        "Cannot save RA login"
    })?;
    protect(&path);
    Ok(())''',
    "report actual failed filesystem write to device log"
    ),
])

# Keep strict error detection for a mistyped core setting when the required
# enabled key is absent, while preserving valid optional extension keys.
patch("crates/slot-achievements/src/storage.rs",[
    (
'''        // TOML diagnostics include source lines, which may contain credentials.
        toml::from_str(&text).map_err(|_| "Invalid achievement config")''',
'''        // TOML diagnostics include source lines, which may contain credentials.
        let doc: toml::Table = toml::from_str(&text).map_err(|_| "Invalid achievement config")?;
        let config: Self = toml::from_str(&text).map_err(|_| "Invalid achievement config")?;
        // An unknown field with no explicit enabled key is likely a typo
        // (e.g. "enabeld"). Keep the original fail-closed behavior.
        if !config.extra.is_empty() && !doc.contains_key("enabled") {
            return Err("Invalid achievement config");
        }
        Ok(config)''',
    "recognize config typo instead of silently treating account as disabled"
    ),
])

patch("crates/slot/src/app.rs",[
    (
'''    RaRestart,
    RaPasswordNeeded,
    RaSaveFailed,''',
'''    RaRestart,
    RaPasswordNeeded,
    RaSaveFailed,
    RaInvalidConfig,
    RaReadFailed,
    RaInvalidCredentials,''',
    "distinct failure notices"
    ),
    (
'''                    Err("Password needed for this account") => NetNotice::RaPasswordNeeded,
                    Err(_) => NetNotice::RaSaveFailed,''',
'''                    Err("Password needed for this account") => NetNotice::RaPasswordNeeded,
                    Err("Invalid achievement config") => NetNotice::RaInvalidConfig,
                    Err("Cannot read achievement config") => NetNotice::RaReadFailed,
                    Err("Invalid RetroAchievements credentials") => NetNotice::RaInvalidCredentials,
                    Err(_) => NetNotice::RaSaveFailed,''',
    "diagnose RA save failure"
    ),
    (
'''            UpdateState::Notice(NetNotice::RaSaveFailed) => (
                "Could not save login".into(),
                "Check the SD card and try again.".into(),
            ),''',
'''            UpdateState::Notice(NetNotice::RaSaveFailed) => (
                "Could not write login".into(),
                "Config folder may be read-only. Check Logs/slot.log.".into(),
            ),
            UpdateState::Notice(NetNotice::RaInvalidConfig) => (
                "Invalid RA configuration".into(),
                "Review Config/retroachievements.toml.".into(),
            ),
            UpdateState::Notice(NetNotice::RaReadFailed) => (
                "Could not read RA login".into(),
                "Check Config/retroachievements.toml.".into(),
            ),
            UpdateState::Notice(NetNotice::RaInvalidCredentials) => (
                "Invalid login entry".into(),
                "Check the username and password length.".into(),
            ),''',
    "explain exact category instead of blaming SD for every failure"
    ),
])

with Path("crates/slot-achievements/src/tests.rs").open("a") as test:
    test.write("""
#[test]
fn menu_login_preserves_other_settings_in_preexisting_toml() {
    let root = configured();
    let path = root.path().join("Config/retroachievements.toml");
    std::fs::write(&path, "enabled = true\\nusername = 'Player'\\ncustom_setting = 'keep'\\n".replace("\\\\n", "\\n")).unwrap();
    configure_login(root.path(), "Player", "Secret!9").unwrap();
    let config = Config::read(&path).unwrap();
    assert_eq!(config.username, "Player");
    assert_eq!(config.password, "Secret!9");
    assert_eq!(
        config.extra.get("custom_setting").and_then(toml::Value::as_str),
        Some("keep")
    );
    assert!(std::fs::read_to_string(&path).unwrap().contains("custom_setting ="));
}

#[test]
fn menu_login_refuses_malformed_file_without_overwriting_it() {
    let root = configured();
    let path = root.path().join("Config/retroachievements.toml");
    let before = "[malformed\\npassword = 'not a login'\\n".replace("\\\\n", "\\n");
    std::fs::write(&path, &before).unwrap();
    assert_eq!(
        configure_login(root.path(), "Player", "Secret!9"),
        Err("Invalid achievement config")
    );
    assert_eq!(std::fs::read_to_string(&path).unwrap(), before);
}

#[test]
fn menu_login_reports_real_filesystem_errors_without_destroying_other_data() {
    let root = configured();
    let path = root.path().join("Config/retroachievements.toml");
    std::fs::remove_file(&path).unwrap();
    std::fs::create_dir(&path).unwrap();
    assert_eq!(
        configure_login(root.path(), "Player", "Secret!9"),
        Err("Cannot read achievement config")
    );
    assert!(path.is_dir());
}
""")
print("Added RA config compatibility and diagnostic tests")
