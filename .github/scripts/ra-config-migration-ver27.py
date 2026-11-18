#!/usr/bin/env python3
"""Ver.27: one-time safe, automatic RetroAchievements TOML normalization at boot.

Preserve user account, credentials, token, known settings and compatible
extension fields. Never reset offline achievement caches or history. Do not
overwrite unreadable/malformed files, and avoid repeated writes after migration.
"""
from pathlib import Path

def replace(path, patches):
    p=Path(path)
    s=p.read_text()
    for before,after,name in patches:
        count=s.count(before)
        if count != 1:
            raise SystemExit(f"{path}: {name}: expected exactly one anchor; got {count}")
        s=s.replace(before,after,1)
    p.write_text(s)
    print("Updated",path)

replace("crates/slot-achievements/src/storage.rs",[
(
'''/// Stage credentials on SD for the next startup; never perform an in-place
/// account switch while the achievement workers still own the old account.''',
'''/// One-time firmware migration. Only a fully parseable TOML file is rewritten;
/// the login fields and any compatible additional settings are preserved.
pub(crate) fn migrate_config(root: &Path) -> Result<bool, &'static str> {
    let path = root.join("Config/retroachievements.toml");
    if !path.exists() {
        return Ok(false);
    }

    // Fail closed: malformed data must remain untouched for manual recovery.
    let mut config = Config::read(&path)?;
    const VERSION: i64 = 1;
    const MARK: &str = "select_slot_ra_schema";
    if config.extra.get(MARK) == Some(&toml::Value::Integer(VERSION)) {
        return Ok(false);
    }
    // Don't attempt to downgrade files from a future firmware.
    if config.extra.contains_key(MARK) {
        return Ok(false);
    }
    config.extra.insert(MARK.to_string(), toml::Value::Integer(VERSION));
    let normalized = toml::to_string(&config).map_err(|_| "Cannot encode achievement config")?;

    // Round-trip validation before touching the source file.
    let checked: Config = toml::from_str(&normalized)
        .map_err(|_| "Cannot encode achievement config")?;
    if checked.enabled != config.enabled
        || checked.username != config.username
        || checked.password != config.password
        || checked.token != config.token
        || checked.ui_login != config.ui_login
        || checked.extra != config.extra
    {
        return Err("Cannot preserve achievement config");
    }

    // atomic_write writes a sibling temporary file and renames only after a
    // successful fsync. Failure leaves the original config in place.
    slot_store::atomic_write(&path, normalized.as_bytes())
        .map_err(|_| "Cannot update achievement config")?;
    protect(&path);
    Ok(true)
}

/// Stage credentials on SD for the next startup; never perform an in-place
/// account switch while the achievement workers still own the old account.''',
"insert guarded one-time migration"
),
])

replace("crates/slot-achievements/src/lib.rs",[
(
'''    let config_path = root.join("Config/retroachievements.toml");
    if !config_path.exists() {
        return;
    }
    let config = match Config::read(&config_path) {''',
'''    let config_path = root.join("Config/retroachievements.toml");
    if !config_path.exists() {
        return;
    }
    // Every firmware update can normalize an older supported account config.
    // If migration is blocked (read-only card or malformed source), continue
    // reading the original rather than deleting the account or its unlocks.
    match storage::migrate_config(&root) {
        Ok(true) => eprintln!("slot: RetroAchievements config migrated"),
        Ok(false) => {}
        Err(why) => eprintln!("slot: RetroAchievements migration skipped: {why}"),
    }
    let config = match Config::read(&config_path) {''',
"run migration before loading achievement account"
),
])

with Path("crates/slot-achievements/src/tests.rs").open("a") as test:
    test.write("""
#[test]
fn firmware_upgrade_normalizes_ra_config_only_once_and_preserves_account() {
    let root = configured();
    let path = root.path().join("Config/retroachievements.toml");
    let original = "# My account\\nenabled = true\\nusername = 'Player'\\npassword = 'secret'\\ntoken = 'original-token'\\nui_login = true\\nextra_setting = 'keep'\\n".replace("\\\\n", "\\n");
    std::fs::write(&path, &original).unwrap();
    assert!(storage::migrate_config(root.path()).unwrap());
    let config = Config::read(&path).unwrap();
    assert!(config.enabled && config.ui_login);
    assert_eq!(config.username, "Player");
    assert_eq!(config.password, "secret");
    assert_eq!(config.token, "original-token");
    assert_eq!(config.extra.get("extra_setting").and_then(toml::Value::as_str), Some("keep"));
    assert_eq!(config.extra.get("select_slot_ra_schema"), Some(&toml::Value::Integer(1)));
    let migrated = std::fs::read(&path).unwrap();
    assert!(!storage::migrate_config(root.path()).unwrap());
    assert_eq!(std::fs::read(&path).unwrap(), migrated);
}

#[test]
fn firmware_upgrade_never_overwrites_malformed_config_or_saved_unlocks() {
    let root = configured();
    let path = root.path().join("Config/retroachievements.toml");
    let broken = "enabled = true\\nusername = 'Player'\\npassword = [\\n".replace("\\\\n", "\\n");
    std::fs::write(&path, &broken).unwrap();
    let saves = root.path().join("Saves/RetroAchievements/account/unlocks.json");
    std::fs::create_dir_all(saves.parent().unwrap()).unwrap();
    std::fs::write(&saves, b"saved data").unwrap();
    assert_eq!(storage::migrate_config(root.path()), Err("Invalid achievement config"));
    assert_eq!(std::fs::read_to_string(&path).unwrap(), broken);
    assert_eq!(std::fs::read(&saves).unwrap(), b"saved data");
}

#[test]
fn firmware_upgrade_does_not_invent_an_account_or_rewrite_future_schema() {
    let root = configured();
    let path = root.path().join("Config/retroachievements.toml");
    std::fs::remove_file(&path).unwrap();
    assert_eq!(storage::migrate_config(root.path()), Ok(false));
    assert!(!path.exists());
    std::fs::write(&path, "enabled = true\\nusername = 'Player'\\nselect_slot_ra_schema = 99\\n".replace("\\\\n", "\\n")).unwrap();
    let original = std::fs::read(&path).unwrap();
    assert_eq!(storage::migrate_config(root.path()), Ok(false));
    assert_eq!(std::fs::read(&path).unwrap(), original);
}
""")
print("Added automatic migration regression tests")
