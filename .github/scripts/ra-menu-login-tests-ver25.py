#!/usr/bin/env python3
"""Regression tests for restart-only RA login and masked password input."""
from pathlib import Path

p=Path("crates/slot-achievements/src/tests.rs")
with p.open("a") as f:
    f.write("""
#[test]
fn menu_login_is_staged_for_restart_and_keeps_the_password_out_of_the_ui() {
    let root = configured();
    let user = "DifferentUser";
    configure_login(root.path(), user, "TestPass!1").expect("stage login");
    assert_eq!(configured_username(root.path()).as_deref(), Some(user));
    let cfg = Config::read(&root.path().join("Config/retroachievements.toml")).unwrap();
    assert_eq!(cfg.username, user);
    assert_eq!(cfg.password, "TestPass!1");
    assert!(cfg.ui_login && cfg.enabled);
    assert_eq!(cfg.token, "");
    assert!(
        std::fs::read_to_string(root.path().join("Config/retroachievements.toml"))
            .unwrap()
            .contains("ui_login = true")
    );
    // The network worker uses these fields on the next boot, not during
    // editing. Only a successful persisted token allows scrubbing.
    storage::scrub_ui_password(root.path(), user, "wrong");
    assert_eq!(
        Config::read(&root.path().join("Config/retroachievements.toml"))
            .unwrap().password,
        "TestPass!1"
    );
    storage::scrub_ui_password(root.path(), user, "TestPass!1");
    assert_eq!(
        Config::read(&root.path().join("Config/retroachievements.toml"))
            .unwrap().password,
        ""
    );
}

#[test]
fn menu_login_requires_credentials_when_changing_accounts() {
    let root = configured();
    let e = configure_login(root.path(), "NewUser", "");
    assert_eq!(e, Err("Password needed for this account"));
    assert_eq!(configured_username(root.path()).as_deref(), Some("Player"));
    // A saved token makes an empty password legitimate for that account.
    let account = format!("{:x}", md5::compute("player"));
    let auth_dir = root.path().join("Saves/RetroAchievements").join(account);
    std::fs::create_dir_all(&auth_dir).unwrap();
    std::fs::write(auth_dir.join("auth.json"), "{}").unwrap();
    configure_login(root.path(), "Player", "").unwrap();
    assert_eq!(configured_username(root.path()).as_deref(), Some("Player"));
}

#[test]
fn manual_config_password_is_not_automatically_erased() {
    let root = configured();
    let config_path = root.path().join("Config/retroachievements.toml");
    std::fs::write(&config_path,
        "enabled = true\\nusername = 'Player'\\npassword = 'hand-written'\\n"
            .replace("\\\\n", "\\n")
    ).unwrap();
    storage::scrub_ui_password(root.path(), "Player", "hand-written");
    assert_eq!(Config::read(&config_path).unwrap().password, "hand-written");
}
""")
p=Path("crates/slot-ui/src/keyboard.rs")
with p.open("a") as f:
    f.write("""
#[cfg(test)]
mod secret_input_test {
    use super::*;

    #[test]
    fn password_keeps_actual_input_but_renders_only_stars() {
        let secret = Keyboard::new(Layout::General, "Password", None, "Secret42").masked();
        assert_eq!(secret.text(), "Secret42");
        let (masked_face, masked_cursors) = keyboard_text_face(&secret);
        let stars = Keyboard::new(Layout::General, "Password", None, "********");
        let (stars_face, stars_cursors) = keyboard_text_face(&stars);
        assert_eq!(masked_face.rgba, stars_face.rgba);
        assert_eq!(masked_cursors, stars_cursors);
        let (visible, _) = keyboard_text_face(
            &Keyboard::new(Layout::General, "Password", None, "Secret42")
        );
        assert_ne!(visible.rgba, masked_face.rgba);
    }
}
""")
print("Added config, restart staging and password masking tests")
