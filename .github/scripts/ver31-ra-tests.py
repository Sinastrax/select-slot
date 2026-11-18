#!/usr/bin/env python3
"""Ver.31: regression coverage for verified ROM refresh, save safety and ping failure."""
from pathlib import Path

path=Path("crates/slot-achievements/src/library.rs")
path.write_text(path.read_text()+r"""

#[cfg(test)]
mod force_hash_refresh_tests {
    use super::*;

    #[test]
    fn manual_refresh_recovers_from_stale_fingerprint_cache() {
        let d = tempfile::tempdir().unwrap();
        let cache = d.path().join("Saves/RetroAchievements/test");
        std::fs::create_dir_all(&cache).unwrap();
        let rom = d.path().join("German-Emerald.gba");
        std::fs::write(&rom, b"game data").unwrap();
        let real = hash(&cache, &rom).unwrap();
        let index_path = cache.join("library.json");
        let mut index: Index = storage::read(&index_path).unwrap();
        let stale = "00000000000000000000000000000000";
        index.get_mut(&rom).unwrap().hash = stale.into();
        storage::write(&index_path, &index).unwrap();
        // Routine lookups may reuse the fingerprint; explicit refresh never does.
        assert_eq!(hash(&cache, &rom).unwrap(), stale);
        assert_eq!(rehash(&cache, &rom).unwrap(), real);
        assert_eq!(hash(&cache, &rom).unwrap(), real);
        assert_eq!(std::fs::read(&rom).unwrap(), b"game data");
    }
}
""")

path=Path("crates/slot-achievements/src/tests.rs")
path.write_text(path.read_text()+r"""

#[test]
fn accepted_game_session_is_online_even_if_presence_ping_fails() {
    struct NoPresence(Server);
    impl network::Transport for NoPresence {
        fn call(&mut self, fields: &[(&str, String)]) -> Result<Value, network::Failure> {
            if fields.iter().any(|(k, v)| *k == "r" && v == "ping") {
                return Err(network::Failure::Network);
            }
            self.0.call(fields)
        }
    }
    let root = configured();
    let rom = root.path().join("Games/GBA/German Emerald.gba");
    std::fs::write(&rom, b"realistic unique fixture").unwrap();
    let (calls, requests) = mpsc::channel();
    let service=Service::start_with(root.path().into(),NoPresence(Server { calls }));
    wait_for(|| service.enabled.load(Ordering::Acquire));
    let mut core=service.wrap(Box::<TestCore>::default());
    core.load(&rom).unwrap();
    wait_for(|| service.game_connection()==GameConnection::Online);
    assert!(service.game_connection_detail().unwrap_or_default().contains("Connected"));
    assert!(requests.try_iter().any(|entry| entry == "startsession"));
    // Actual game remains running, and cached definitions are still present.
    core.run_frame(ButtonMask(0));
    wait_for(|| service.achievement_view().is_some());
}

#[test]
fn manual_refresh_rechecks_romanized_rom_identity_without_touching_saves() {
    let root = configured();
    let rom = root.path().join("Games/GBA/German Emerald.gba");
    std::fs::write(&rom, b"german emerald game").unwrap();
    let save = root.path().join("Games/GBA/German Emerald.sav");
    std::fs::write(&save, b"precious in-game progress").unwrap();
    let (calls, requests) = mpsc::channel();
    let service=Service::start_with(root.path().into(),Server { calls });
    wait_for(|| service.enabled.load(Ordering::Acquire));
    let mut core=service.wrap(Box::<TestCore>::default());
    core.load(&rom).unwrap();
    wait_for(|| service.game_connection()==GameConnection::Online);
    let original_hash = format!("{:x}",md5::compute(std::fs::read(&rom).unwrap()));
    assert!(service.refresh_active());
    wait_for(|| {
        service.game_connection()==GameConnection::Online
            && service.game_connection_detail().as_deref()==Some("Online session accepted")
    });
    // The refresh never modifies the ROM, save RAM, or local offline awards.
    let store=Store::open(root.path(),"Player").unwrap();
    assert_eq!(library::hash(&store.dir,&rom).unwrap(),original_hash);
    assert_eq!(std::fs::read(save).unwrap(),b"precious in-game progress");
    // Wait for the second accepted session, not merely the previous Online flag.
    let mut started = requests.try_iter().filter(|req| req == "startsession").count();
    wait_for(|| {
        started += requests.try_iter().filter(|req| req == "startsession").count();
        started >= 2 && service.game_connection() == GameConnection::Online
    });
}
""")

# Fix a legitimate Ver.29 test race: per-game status is published before pending
# is recomputed by the independent HTTP worker.
tests=Path("crates/slot-achievements/src/tests.rs")
data=tests.read_text()
needle='''    assert!(library::fresh(&store.dir, &rom, network::now()));
    assert!(!service.sync_pending());'''
replacement='''    assert!(library::fresh(&store.dir, &rom, network::now()));
    wait_for(|| !service.sync_pending());'''
assert data.count(needle)==1, "Ver29 negative cache test anchor changed"
tests.write_text(data.replace(needle,replacement,1))
print("Ver.31 network/session and forced rehash regression tests added")
