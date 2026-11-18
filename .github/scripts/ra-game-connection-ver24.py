#!/usr/bin/env python3
"""Ver.24: expose genuine per-game RetroAchievements session readiness."""
from pathlib import Path

def edit(path, changes):
    p=Path(path)
    data=p.read_text()
    for old,new in changes:
        count=data.count(old)
        if count != 1:
            raise SystemExit(f"{path}: expected 1 occurrence, got {count}: {old[:90]!r}")
        data=data.replace(old,new,1)
    p.write_text(data)
    print(path, "updated")

edit("crates/slot-achievements/src/lib.rs",[
("""#[derive(Default)]
struct Status {
    network: AtomicU8,""",
"""/// A game is Online only after an accepted RA session, not merely Wi-Fi.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
pub enum GameConnection {
    Disabled,
    Checking,
    OfflineReady,
    Online,
    NoAchievements,
}

#[derive(Default)]
struct Status {
    network: AtomicU8,
    game_generation: AtomicU64,
    game_connection: AtomicU8,"""),
("""impl Status {
    fn set(&self, value: SyncStatus) {""",
"""impl Status {
    fn set_game(&self, generation: u64, state: GameConnection) {
        self.game_connection.store(state as u8, Ordering::Release);
        self.game_generation.store(generation, Ordering::Release);
    }

    fn game_for(&self, generation: u64) -> GameConnection {
        if generation == 0 || self.game_generation.load(Ordering::Acquire) != generation {
            return GameConnection::Checking;
        }
        match self.game_connection.load(Ordering::Acquire) {
            2 => GameConnection::OfflineReady,
            3 => GameConnection::Online,
            4 => GameConnection::NoAchievements,
            _ => GameConnection::Checking,
        }
    }

    fn set(&self, value: SyncStatus) {"""),
("""    pub fn sync_status(&self) -> SyncStatus {
        self.status.get()
    }""",
"""    pub fn sync_status(&self) -> SyncStatus {
        self.status.get()
    }

    pub fn game_connection(&self) -> GameConnection {
        if !self.enabled.load(Ordering::Acquire) {
            return GameConnection::Disabled;
        }
        self.status.game_for(self.current.load(Ordering::Acquire))
    }"""),
("""                Ok(Control::Load(load)) => {
                    generation = load.generation;
                    playing = None;""",
"""                Ok(Control::Load(load)) => {
                    generation = load.generation;
                    status.set_game(generation, GameConnection::Checking);
                    playing = None;"""),
("""                Ok(Control::Unload(id)) if id == generation => {
                    generation = 0;
                    playing = None;""",
"""                Ok(Control::Unload(id)) if id == generation => {
                    generation = 0;
                    status.set_game(0, GameConnection::Checking);
                    playing = None;"""),
("""        for prepared in prepared_rx.try_iter() {
            if prepared.generation != generation {
                continue;
            }
            if let Some(game) = playing.as_mut() {""",
"""        for prepared in prepared_rx.try_iter() {
            if prepared.generation != generation {
                continue;
            }
            let connection = if prepared.game.id == 0 {
                GameConnection::NoAchievements
            } else if !prepared.cached
                || status.game_for(generation) == GameConnection::Online
            {
                GameConnection::Online
            } else {
                GameConnection::OfflineReady
            };
            status.set_game(generation, connection);
            if let Some(game) = playing.as_mut() {"""),
])

edit("crates/slot/src/session.rs",[
("""    pub fn achievement_sync_status(&self) -> slot_achievements::SyncStatus {
        self.achievements.sync_status()
    }""",
"""    pub fn achievement_sync_status(&self) -> slot_achievements::SyncStatus {
        self.achievements.sync_status()
    }

    pub fn achievement_game_connection(&self) -> slot_achievements::GameConnection {
        self.achievements.game_connection()
    }"""),
])
with Path("crates/slot-achievements/src/tests.rs").open("a") as f:
    f.write("""
#[test]
fn per_game_connection_is_generation_scoped_and_never_guesses_online() {
    let status = Status::default();
    status.set_game(1, GameConnection::OfflineReady);
    assert_eq!(status.game_for(1), GameConnection::OfflineReady);
    assert_eq!(status.game_for(2), GameConnection::Checking);
    status.set_game(1, GameConnection::Online);
    assert_eq!(status.game_for(1), GameConnection::Online);
    status.set_game(2, GameConnection::NoAchievements);
    assert_eq!(status.game_for(1), GameConnection::Checking);
    assert_eq!(status.game_for(2), GameConnection::NoAchievements);
}
""")
print("RA session state regression added")
