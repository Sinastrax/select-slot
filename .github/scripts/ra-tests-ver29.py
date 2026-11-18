#!/usr/bin/env python3
"""Ver.29: opt-in library regression tests and quiet shelf indication."""
from pathlib import Path

def change(path, before, after, why):
    p=Path(path)
    source=p.read_text()
    n=source.count(before)
    if n!=1:
        raise SystemExit(f"{path}: {why}: expected one anchor, got {n}")
    p.write_text(source.replace(before,after,1))
    print(f"Ver29 {path}: {why}")

# Old tests expected auto indexing from the original Slot behavior. Preserve
# those expectations by opting the test fixture into the optional feature.
tests="crates/slot-achievements/src/tests.rs"
change(tests,
'''fn configured() -> tempfile::TempDir {
    let root = tempfile::tempdir().unwrap();
    std::fs::create_dir_all(root.path().join("Config")).unwrap();
    std::fs::create_dir_all(root.path().join("Games/GBA")).unwrap();
    std::fs::write(
        root.path().join("Config/retroachievements.toml"),
        "enabled = true\\nusername = 'Player'\\ntoken = 'fixture-token'\\n",
    )''',
'''fn configured() -> tempfile::TempDir {
    let root = tempfile::tempdir().unwrap();
    std::fs::create_dir_all(root.path().join("Config")).unwrap();
    std::fs::create_dir_all(root.path().join("Games/GBA")).unwrap();
    std::fs::write(
        root.path().join("Config/retroachievements.toml"),
        "enabled = true\\nusername = 'Player'\\ntoken = 'fixture-token'\\nindex_library = true\\n",
    )''',
"existing automatic-indexing fixtures explicitly opt in")

with Path(tests).open("a") as f:
    f.write(r"""

#[test]
fn library_index_is_disabled_by_default_but_manual_prepare_works() {
    let root = configured();
    let config = root.path().join("Config/retroachievements.toml");
    std::fs::write(&config,
        "enabled = true\nusername = 'Player'\ntoken = 'fixture-token'\n").unwrap();
    let rom = root.path().join("Games/GBA/Unindexed.gba");
    std::fs::write(&rom, b"manual only").unwrap();
    let store = Store::open(root.path(), "Player").unwrap();
    let cache = store.dir.join(format!("{:x}.json", md5::compute(b"manual only")));
    let (calls, _) = mpsc::channel();
    let service = Service::start_with(root.path().into(), Server { calls });
    wait_for(|| service.sync_status() == SyncStatus::Ready);
    assert!(!service.overview().index_library);
    assert!(!cache.exists(), "boot must not pre-index the whole library");
    service.request_library(LibraryAction::Prepare);
    wait_for(|| cache.exists());
    wait_for(|| service.sync_status() == SyncStatus::Ready);
}

#[test]
fn unreadable_rom_records_a_failure_without_permanent_orange_warning() {
    let root = configured();
    let empty = root.path().join("Games/GBA/Empty.gba");
    std::fs::write(&empty, b"").unwrap();
    let (calls, _) = mpsc::channel();
    let service = Service::start_with(root.path().into(), Server { calls });
    wait_for(|| service.overview().failed_roms == 1);
    wait_for(|| service.sync_status() == SyncStatus::Ready);
    assert!(!service.sync_pending());
    // The retry control can requeue the specific failed entry without
    // touching authentication or saved achievement history.
    service.request_library(LibraryAction::RetryFailed);
    wait_for(|| service.overview().failed_roms == 1);
    assert_eq!(service.sync_status(), SyncStatus::Ready);
}

#[test]
fn unsupported_rom_is_cached_as_success_and_never_counts_as_a_failed_rom() {
    struct Unknown(mpsc::Sender<String>);
    impl network::Transport for Unknown {
        fn call(&mut self, fields: &[(&str, String)]) -> Result<Value, network::Failure> {
            let request = fields.iter().find(|(k, _)| *k == "r").unwrap().1.as_str();
            let _ = self.0.send(request.to_string());
            Ok(match request {
                "login2" => json!({"Success":true,"User":"Player","Token":"fixture-token"}),
                "gameid" => json!({"Success":true,"GameID":0}),
                other => panic!("unsupported ROM must not request {other}"),
            })
        }
    }
    let root = configured();
    let config = root.path().join("Config/retroachievements.toml");
    std::fs::write(&config,
        "enabled = true\nusername = 'Player'\ntoken = 'fixture-token'\n").unwrap();
    let rom = root.path().join("Games/GBA/Regional.gba");
    std::fs::write(&rom, b"unknown regional ROM").unwrap();
    let store = Store::open(root.path(), "Player").unwrap();
    let (calls, requests) = mpsc::channel();
    let service = Service::start_with(root.path().into(), Unknown(calls));
    let mut core = service.wrap(Box::<TestCore>::default());
    core.load(&rom).unwrap();
    wait_for(|| service.game_connection() == GameConnection::NoAchievements);
    assert_eq!(service.overview().failed_roms, 0);
    assert!(library::fresh(&store.dir, &rom, network::now()));
    assert!(!service.sync_pending());
    drop(core);
    let previous = requests.try_iter().filter(|r| r == "gameid").count();
    assert_eq!(previous, 1);
    let mut core = service.wrap(Box::<TestCore>::default());
    core.load(&rom).unwrap();
    wait_for(|| service.game_connection() == GameConnection::NoAchievements);
    assert_eq!(requests.try_iter().filter(|r| r == "gameid").count(), 0,
        "fresh negative result must not be queried again");
}
""")
print("Added opt-in scanning, unreadable ROM, and regional ROM tests")

change("crates/slot/src/achievement_ui.rs",
'''attention: matches!(status, SyncStatus::Offline | SyncStatus::Attention),''',
'''attention: status == SyncStatus::Attention,''',
"orange indicator only for failures requiring attention, not transient disconnects")

with Path("crates/slot-ui/src/quick_menu.rs").open("a") as f:
    f.write(r"""

#[cfg(test)]
mod select_ra_menu_tests {
    use super::QuickRow;

    #[test]
    fn ra_submenu_is_reachable_and_b_returns_to_tools() {
        assert_eq!(QuickRow::RetroAchievements.child(), Some(QuickRow::RaAccount));
        assert_eq!(QuickRow::RaAccount.parent(), Some(QuickRow::RetroAchievements));
        assert_eq!(QuickRow::RaBackground.page(), &QuickRow::RA);
        assert_eq!(QuickRow::RetroAchievements.page(), &QuickRow::NETWORK);
        assert!(QuickRow::RaPrepare.opens());
        assert!(QuickRow::RaStatus.opens());
    }
}
""")
