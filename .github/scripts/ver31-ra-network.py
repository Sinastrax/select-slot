#!/usr/bin/env python3
"""Ver.31: verified per-game RA reconnect and safe active-ROM refresh.

The refresh never touches ROM saves, game state, offline awards, or Wi-Fi.
The existing System/ manifest updater is not modified.
"""
from pathlib import Path

def change(path, old, new, note):
    p=Path(path);s=p.read_text()
    n=s.count(old)
    if n!=1:
        raise SystemExit(f"Ver31 {path}: {note}: expected 1 anchor, found {n}")
    p.write_text(s.replace(old,new,1))
    print(f"Ver31 {path}: {note}")

net="crates/slot-achievements/src/network.rs"
lib="crates/slot-achievements/src/lib.rs"
core="crates/slot-achievements/src/core.rs"
library="crates/slot-achievements/src/library.rs"

change(net,
'''pub(crate) struct Load {
    pub generation: u64,
    pub path: PathBuf,
}''',
'''#[derive(Clone)]
pub(crate) struct Load {
    pub generation: u64,
    pub path: PathBuf,
    /// Explicit in-game refresh must rehash bytes, not trust a stale filename cache.
    pub refresh: bool,
}''',"refresh flag on per-game loads")
change(core,
'''            path: rom.to_path_buf(),
        }));''',
'''            path: rom.to_path_buf(),
            refresh: false,
        }));''',"ordinary game loads stay unchanged")
change(library,
'''pub(crate) fn content_hash(path: &Path) -> Result<String, String> {''',
'''/// Force a fresh ROM identity check, even when size and mtime are unchanged.
pub(crate) fn rehash(dir: &Path, path: &Path) -> Result<String, String> {
    let (size, modified_ns) = fingerprint(path)?;
    let hash = content_hash(path)?;
    let index_path = dir.join("library.json");
    let mut index: Index = storage::read(&index_path).unwrap_or_default();
    index.insert(path.to_path_buf(), Entry {
        size, modified_ns, hash: hash.clone(), checked_at: 0, badge_version: 0,
    });
    // Retain the freshly verified identity even if an SD write cannot be performed.
    let _ = storage::write(&index_path, &index);
    Ok(hash)
}

pub(crate) fn content_hash(path: &Path) -> Result<String, String> {''',"force true hash on refresh")
change(lib,
'''    presence: Mutex<Option<(u64, String)>>,
    /// Cloned cheaply by the paused in-game viewer; written by the evaluator only.''',
'''    presence: Mutex<Option<(u64, String)>>,
    game_detail: Mutex<Option<(u64, String)>>,
    /// Cloned cheaply by the paused in-game viewer; written by the evaluator only.''',
"per-game connection diagnostics")
change(lib,
'''    fn set_game(&self, generation: u64, state: GameConnection) {''',
'''    fn set_game_detail(&self, generation: u64, message: &str) {
        if let Ok(mut detail) = self.game_detail.lock() {
            *detail = Some((generation, message.to_owned()));
        }
    }

    fn game_detail_for(&self, generation: u64) -> Option<String> {
        self.game_detail.lock().ok()
            .and_then(|detail| detail.as_ref()
                .filter(|(id, _)| *id == generation)
                .map(|(_, message)| message.clone()))
    }

    fn set_game(&self, generation: u64, state: GameConnection) {''',
"stage status by ROM generation")
change(lib,
'''    Unload(u64),
    Flush(Arc<AtomicBool>),''',
'''    Unload(u64),
    Refresh(u64),
    Flush(Arc<AtomicBool>),''',
"per-game refresh command")
change(lib,
'''    pub fn game_connection(&self) -> GameConnection {
        if !self.enabled.load(Ordering::Acquire) {
            return GameConnection::Disabled;
        }
        self.status.game_for(self.current.load(Ordering::Acquire))
    }''',
'''    pub fn game_connection(&self) -> GameConnection {
        if !self.enabled.load(Ordering::Acquire) {
            return GameConnection::Disabled;
        }
        self.status.game_for(self.current.load(Ordering::Acquire))
    }

    pub fn game_connection_detail(&self) -> Option<String> {
        self.status.game_detail_for(self.current.load(Ordering::Acquire))
    }

    /// Recheck only the active ROM. Processing is asynchronous on the RA workers.
    /// Does not restart emulation, mutate save RAM, or discard local achievements.
    pub fn refresh_active(&self) -> bool {
        let generation = self.current.load(Ordering::Acquire);
        generation != 0
            && self.enabled.load(Ordering::Acquire)
            && self.controls.send(Control::Refresh(generation)).is_ok()
    }''',"public status and manual refresh")
change(lib,
'''    let mut generation = 0;
    let mut playing: Option<Playing> = None;''',
'''    let mut generation = 0;
    let mut active_rom: Option<network::Load> = None;
    let mut playing: Option<Playing> = None;''',"remember current game identity")
change(lib,
'''                Ok(Control::Load(load)) => {
                    generation = load.generation;
                    status.set_game(generation, GameConnection::Checking);
                    playing = None;''',
'''                Ok(Control::Load(load)) => {
                    generation = load.generation;
                    active_rom = Some(load.clone());
                    status.set_game(generation, GameConnection::Checking);
                    status.set_game_detail(generation, "Loading achievement metadata");
                    playing = None;''',"track ROM and initial connection stage")
change(lib,
'''                Ok(Control::Unload(id)) if id == generation => {
                    generation = 0;
                    status.set_game(0, GameConnection::Checking);''',
'''                Ok(Control::Unload(id)) if id == generation => {
                    generation = 0;
                    active_rom = None;
                    status.set_game_detail(0, "");
                    status.set_game(0, GameConnection::Checking);''',"clear identity when game exits")
change(lib,
'''                Ok(_) => {}
                Err(mpsc::TryRecvError::Disconnected) => return,''',
'''                Ok(Control::Refresh(id)) if id == generation => {
                    if let Some(rom) = active_rom.as_ref() {
                        status.set_game_detail(id, "Rechecking ROM hash and achievement session");
                        status.set_game(id, GameConnection::OfflineReady);
                        let mut recheck = rom.clone();
                        recheck.refresh = true;
                        let _ = loads.send(Some(recheck));
                        // The runtime and its accumulated hit counts stay intact.
                    }
                }
                Ok(_) => {}
                Err(mpsc::TryRecvError::Disconnected) => return,''',"queue refresh on existing HTTP worker")
change(lib,
'''            if let Some(game) = playing.as_mut() {
                // Preserve hits for unchanged definitions.''',
'''            // A changed ROM identity must not reuse achievement addresses from
            // the previous hash, even though the emulation generation is unchanged.
            if playing.as_ref().is_some_and(|g| g.hash != prepared.hash) {
                playing = None;
            }
            if let Some(game) = playing.as_mut() {
                // Preserve hits for unchanged definitions.''',"avoid old ROM rules if identity changes")
change(net,
'''                    let hash = crate::library::hash(&dir, &load.path).ok()?;''',
'''                    let hash = match if load.refresh {
                        crate::library::rehash(&dir, &load.path)
                    } else {
                        crate::library::hash(&dir, &load.path)
                    } {
                        Ok(hash) => hash,
                        Err(_) => {
                            status.set_game_detail(load.generation, "Cannot read ROM for identification");
                            return None;
                        }
                    };
                    status.set_game_detail(load.generation, "ROM identified; requesting game session");''',
"rehash active ROM rather than filename cache")
change(net,
'''                    if id == 0 {
                        // Cache a normal negative lookup; regional versions can be''',
'''                    if id == 0 {
                        status.set_game_detail(game.generation, "ROM not registered on RetroAchievements");
                        // Cache a normal negative lookup; regional versions can be''',
"clear unsupported ROM state")
change(net,
'''                    let resolved = call(&mut http, auth, "gameid", &[("m", game.hash.clone())])?;''',
'''                    status.set_game_detail(game.generation, "Looking up exact ROM hash");
                    let resolved = call(&mut http, auth, "gameid", &[("m", game.hash.clone())])?;''',
"report game ID lookup")
change(net,
'''                        let patch = call(&mut http, auth, "patch", &[("g", id.to_string())])?;''',
'''                        status.set_game_detail(game.generation, "Loading achievement definitions");
                        let patch = call(&mut http, auth, "patch", &[("g", id.to_string())])?;''',
"report achievement definitions")
change(net,
'''                        let session = call(
                            &mut http,
                            auth,
                            "startsession",''',
'''                        status.set_game_detail(game.generation, "Establishing online game session");
                        let session = call(
                            &mut http,
                            auth,
                            "startsession",''',
"report startsession")
change(net,
'''                        badges.enqueue(&data);
                        ping(&mut http, auth, &status, game, &data)?;
                        let _ = prepared.send(Prepared {
                            generation: game.generation,
                            hash: game.hash.clone(),
                            game: data,
                            unlocked: ids,
                            cached: false,
                        });
                        game.ready = true;
                        game.online = true;
                        crate::library::checked(&dir, &game.path, now());
                        game.last_ping = Instant::now();''',
'''                        badges.enqueue(&data);
                        let _ = prepared.send(Prepared {
                            generation: game.generation,
                            hash: game.hash.clone(),
                            game: data.clone(),
                            unlocked: ids,
                            cached: false,
                        });
                        // A successful startsession is the definitive online signal.
                        // A separate Rich Presence ping must never prevent unlocking.
                        game.ready = true;
                        game.online = true;
                        game.unmatched = false;
                        status.set_game(game.generation, crate::GameConnection::Online);
                        status.set_game_detail(game.generation, "Online session accepted");
                        crate::library::checked(&dir, &game.path, now());
                        game.last_ping = Instant::now();
                        if let Err(error) = ping(&mut http, auth, &status, game, &data) {
                            eprintln!("slot: RA presence ping deferred after accepted session: {error:?}");
                            game.last_ping = Instant::now() - Duration::from_secs(90);
                            status.set_game_detail(game.generation, "Connected; presence ping retry pending");
                        }''',
"don't let presence ping invalidate successful startsession")
change(net,
'''                    ping(&mut http, auth, &status, game, &cached.0)?;
                    game.last_ping = Instant::now();''',
'''                    match ping(&mut http, auth, &status, game, &cached.0) {
                        Ok(()) => {
                            game.last_ping = Instant::now();
                            status.set_game_detail(game.generation, "Online session accepted");
                        }
                        Err(error) => {
                            eprintln!("slot: RA presence heartbeat retry: {error:?}");
                            game.last_ping = Instant::now() - Duration::from_secs(90);
                            status.set_game_detail(game.generation, "Connected; presence ping retry pending");
                        }
                    }''',"periodic heartbeat failure must not erase session")
change(net,
'''            Err(error) => {
                status.set(if error == Failure::Network {''',
'''            Err(error) => {
                if let Some(game) = active.as_ref() {
                    if !game.online {
                        let diagnosis = match error {
                            Failure::Network => "Network timeout; retry pending",
                            Failure::Authentication => "Login rejected; check account",
                            Failure::Rejected => "RetroAchievements rejected game request",
                            Failure::Invalid => "Invalid game data or SD storage",
                        };
                        status.set_game_detail(game.generation, diagnosis);
                    }
                }
                status.set(if error == Failure::Network {''',
"surface per-game reason, never log credentials")
print("Ver.31 active-game refresh and independent session/presence state installed")
