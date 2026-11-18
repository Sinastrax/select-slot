#!/usr/bin/env python3
"""Ver.29: opt-in RA library preparation, negative ROM caching and quiet retries.

Only the active game's metadata is required for gameplay. Optional full-library
work is paused while playing/asleep; unreadable or unsupported ROMs must not
leave an indefinite global warning. Existing account caches and unlocks remain.
"""
from pathlib import Path

def change(path, before, after, reason):
    p = Path(path)
    s = p.read_text()
    count = s.count(before)
    if count != 1:
        raise SystemExit(f"{path}: {reason}: expected one anchor, found {count}")
    p.write_text(s.replace(before, after, 1))
    print(f"Ver29 {path}: {reason}")

storage = "crates/slot-achievements/src/storage.rs"
change(storage,
'''    pub ui_login: bool,
    // A pre-existing user config may contain additional options''',
'''    pub ui_login: bool,
    // Full-library preparation is optional; active-game achievements always work.
    pub index_library: bool,
    // A pre-existing user config may contain additional options''',
"optional index configuration")
change(storage,
'''pub(crate) fn migrate_config(root: &Path) -> Result<bool, &'static str> {''',
'''pub(crate) fn set_library_index(root: &Path, enabled: bool) -> Result<(), &'static str> {
    let path = root.join("Config/retroachievements.toml");
    let mut config = Config::read(&path)?;
    config.index_library = enabled;
    let text = toml::to_string(&config).map_err(|_| "Cannot encode achievement config")?;
    slot_store::atomic_write(&path, text.as_bytes())
        .map_err(|_| "Cannot save achievement config")?;
    protect(&path);
    Ok(())
}

pub(crate) fn migrate_config(root: &Path) -> Result<bool, &'static str> {''',
"persist index choice atomically")

library = "crates/slot-achievements/src/library.rs"
change(library,
'''pub(crate) fn checked(dir: &Path, path: &Path, now: u64) {''',
'''/// A negative RA lookup is valid for seven days, just like supported metadata.
pub(crate) fn fresh(dir: &Path, path: &Path, now: u64) -> bool {
    let index: Index = storage::read(&dir.join("library.json")).unwrap_or_default();
    index.get(path).is_some_and(|entry| {
        entry.modified_ns != 0
            && fingerprint(path).ok() == Some((entry.size, entry.modified_ns))
            && entry.checked_at != 0
            && entry.badge_version >= 2
            && now.saturating_sub(entry.checked_at) < 7 * 86400
            && dir.join(format!("{}.json", entry.hash)).exists()
    })
}

pub(crate) fn checked(dir: &Path, path: &Path, now: u64) {''',
"negative lookup TTL")

lib = "crates/slot-achievements/src/lib.rs"
change(lib,
'''    pending: AtomicBool,
    // Bumped after each game cache write''',
'''    pending: AtomicBool,
    // Full-library work is independent of game session readiness.
    scan_request: AtomicU8, // 0 none, 1 prepare, 2 retry failed
    index_library: AtomicBool,
    awake: AtomicBool,
    playing_game: AtomicBool,
    failed_roms: AtomicU64,
    // Bumped after each game cache write''',
"independent library scan controls")
change(lib,
'''#[derive(Default)]
struct Status {''',
'''#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum LibraryAction {
    Prepare,
    RetryFailed,
    SetIndex(bool),
}

#[derive(Clone, Copy, Debug)]
pub struct Overview {
    pub state: SyncStatus,
    pub progress: Option<u8>,
    pub pending: bool,
    pub failed_roms: u64,
    pub index_library: bool,
}

#[derive(Default)]
struct Status {''',
"public overview and command")
change(lib,
'''        let status = Arc::new(Status::default());
        let worker_status = status.clone();''',
'''        let status = Arc::new(Status::default());
        status.awake.store(true, Ordering::Release);
        let worker_status = status.clone();''',
"start worker awake")
change(lib,
'''    pub fn sync_status(&self) -> SyncStatus {
        self.status.get()
    }''',
'''    pub fn sync_status(&self) -> SyncStatus {
        self.status.get()
    }

    pub fn overview(&self) -> Overview {
        Overview {
            state: self.sync_status(),
            progress: self.sync_progress(),
            pending: self.sync_pending(),
            failed_roms: self.status.failed_roms.load(Ordering::Acquire),
            index_library: self.status.index_library.load(Ordering::Acquire),
        }
    }

    pub fn request_library(&self, action: LibraryAction) {
        match action {
            LibraryAction::Prepare => self.status.scan_request.store(1, Ordering::Release),
            LibraryAction::RetryFailed => self.status.scan_request.store(2, Ordering::Release),
            LibraryAction::SetIndex(enabled) => {
                self.status.index_library.store(enabled, Ordering::Release);
                if enabled {
                    self.status.scan_request.store(1, Ordering::Release);
                }
            }
        }
    }

    pub fn set_activity(&self, awake: bool, playing: bool) {
        let was = self.status.awake.swap(awake, Ordering::AcqRel);
        self.status.playing_game.store(playing, Ordering::Release);
        if awake && !was {
            self.status.reconnect.store(true, Ordering::Release);
        }
    }''',
"live menu actions and status")
change(lib,
'''pub fn configured_username(root: &std::path::Path) -> Option<String> {''',
'''pub fn set_library_index(root: &std::path::Path, enabled: bool) -> Result<(), &'static str> {
    storage::set_library_index(root, enabled)
}

pub fn configured_username(root: &std::path::Path) -> Option<String> {''',
"expose persistent opt-in")
change(lib,
'''    // Every firmware update can normalize an older supported account config.''',
'''    // Every firmware update can normalize an older supported account config.''',
"config startup anchor check")

net = "crates/slot-achievements/src/network.rs"
change(net,
'''struct Active {
    generation: u64,
    hash: String,
    ready: bool,''',
'''struct Active {
    generation: u64,
    hash: String,
    path: PathBuf,
    ready: bool,''',
"track active ROM path for negative-result expiration")
change(net,
'''    let mut library = crate::library::pending(&root, &dir, now());
    let mut library_total = library.len();
    let mut library_failed = false;
    let mut rescanned = Instant::now();''',
'''    status.index_library.store(config.index_library, std::sync::atomic::Ordering::Release);
    let mut library = if config.index_library {
        crate::library::pending(&root, &dir, now())
    } else {
        std::collections::VecDeque::new()
    };
    let mut library_total = library.len();
    let mut failed_roms: Vec<PathBuf> = Vec::new();
    let mut rescanned = Instant::now();''',
"opt-in automatic library scanning")
change(net,
'''                        hash,
                        ready: false,
                        online: false,''',
'''                        hash,
                        path: load.path.clone(),
                        ready: false,
                        online: false,''',
"remember active ROM path")
change(net,
'''                                game.ready = true;
                            }
                        }
                    }
                    Some(game)''',
'''                                game.ready = true;
                                // A negative lookup is a successful, cacheable answer.
                                if game.ready
                                    && crate::library::fresh(&dir, &load.path, now())
                                {
                                    if let Ok((cached, _)) =
                                        storage::read::<(Game, BTreeSet<u32>)>(&cache)
                                    {
                                        if cached.id == 0 {
                                            game.online = true;
                                        }
                                    }
                                }
                            }
                        }
                    }
                    Some(game)''',
"do not repeatedly query fresh unsupported regional ROMs")
change(net,
'''        // Metadata preparation and badge downloads each occupy half of a cache refresh.
        status.pending.store(
            !library.is_empty()
                || library_failed
                || badges.pending()''',
'''        // Metadata preparation and badge downloads each occupy half of a cache refresh.
        status.pending.store(
            !library.is_empty()
                || (badges.pending() && !badges.waiting)''',
"no permanent pending state from failed background indexing")
change(net,
'''        if rescanned.elapsed() >= Duration::from_secs(300) {
            library = crate::library::pending(&root, &dir, now());
            library_total = library.len();
            library_failed = false;
            badges.scan();
            rescanned = Instant::now();
        }''',
'''        // The background worker keeps its cache and awards in memory across doze.
        // Avoid new HTTP work until the lid is open again.
        if !status.awake.load(std::sync::atomic::Ordering::Acquire) {
            continue;
        }
        let request = status.scan_request.swap(0, std::sync::atomic::Ordering::AcqRel);
        if request == 1 {
            library = crate::library::pending(&root, &dir, now());
            library_total = library.len();
            failed_roms.clear();
            status.failed_roms.store(0, std::sync::atomic::Ordering::Release);
            badges.scan();
            rescanned = Instant::now();
            next_attempt = Instant::now();
        } else if request == 2 {
            library = failed_roms.drain(..).collect();
            library_total = library.len();
            status.failed_roms.store(0, std::sync::atomic::Ordering::Release);
            next_attempt = Instant::now();
        } else if status.index_library.load(std::sync::atomic::Ordering::Acquire)
            && rescanned.elapsed() >= Duration::from_secs(300)
            && library.is_empty()
        {
            library = crate::library::pending(&root, &dir, now());
            library_total = library.len();
            failed_roms.clear();
            status.failed_roms.store(0, std::sync::atomic::Ordering::Release);
            badges.scan();
            rescanned = Instant::now();
        }''',
"manual preparation, retry and pause while asleep")
change(net,
'''                    if id == 0 {
                        let _ = notices.send(Notice::status(
                            game.generation,
                            "No achievements for this ROM",
                        ));
                        game.online = true;
                        game.ready = false;
                    } else {''',
'''                    if id == 0 {
                        // Cache a normal negative lookup; regional versions can be
                        // unsupported without producing a failure or endless pending icon.
                        let empty = Game {
                            presence: String::new(),
                            id: 0,
                            console: 5,
                            title: "No achievements for this ROM".into(),
                            achievements: vec![],
                        };
                        storage::write(
                            &dir.join(format!("{}.json", game.hash)),
                            &(empty, BTreeSet::<u32>::new()),
                        ).map_err(|_| Failure::Invalid)?;
                        crate::library::checked(&dir, &game.path, now());
                        status.cached.fetch_add(1, std::sync::atomic::Ordering::AcqRel);
                        let _ = notices.send(Notice::status(
                            game.generation,
                            "No achievements for this ROM",
                        ));
                        game.online = true;
                        game.ready = true;
                    } else {''',
"unsupported game is checked and ready")
change(net,
'''                        game.ready = true;
                        game.online = true;
                        game.last_ping = Instant::now();''',
'''                        game.ready = true;
                        game.online = true;
                        crate::library::checked(&dir, &game.path, now());
                        game.last_ping = Instant::now();''',
"timestamp active-game metadata")
change(net,
'''            if let Some(path) = library.front() {
                if let Ok(hash) = crate::library::hash(&dir, path) {''',
'''            if !status.playing_game.load(std::sync::atomic::Ordering::Acquire) {
              if let Some(path) = library.front() {
                if let Ok(hash) = crate::library::hash(&dir, path) {''',
"avoid library hashing while playing")
change(net,
'''                        Err(error) => {
                            library_failed = true;
                            deferred_error = Some(error);
                        }
                    }
                } else {
                    library_failed = true;
                }
                // Removed/unreadable ROMs are reconsidered on the next library scan.
                library.pop_front();''',
'''                        Err(error) => {
                            eprintln!("slot: RA library ROM metadata lookup failed: {error:?}");
                            if !failed_roms.contains(path) {
                                failed_roms.push(path.clone());
                            }
                        }
                    }
                } else {
                    eprintln!("slot: RA library ROM unreadable or unsupported size");
                    if !failed_roms.contains(path) {
                        failed_roms.push(path.clone());
                    }
                }
                status.failed_roms.store(failed_roms.len() as u64, std::sync::atomic::Ordering::Release);
                // One bad ROM must not keep the entire shelf in warning state.
                library.pop_front();''',
"track failed ROMs individually and keep processing")
change(net,
'''                if library.is_empty() && !library_failed && !badges.pending() {''',
'''                if library.is_empty() && !badges.pending() {''',
"success notification for completed work")
change(net,
'''            badges.step(&mut http);
            deferred_error.map_or(Ok(()), Err)''',
'''              }
              // Badge art is decorative; its failures must not block unlocks or gameplay.
              badges.step(&mut http);
            }
            deferred_error.map_or(Ok(()), Err)''',
"pause library/badges during gameplay")
change(net,
'''        status.pending.store(
            !library.is_empty()
                || library_failed
                || badges.pending()''',
'''        status.pending.store(
            !library.is_empty()
                || (badges.pending() && !badges.waiting)''',
"ignore background failures in post-pass pending")
change(net,
'''                status.set(if library_failed || badges.waiting {
                    SyncStatus::Attention
                } else if !library.is_empty()
                    || badges.pending()''',
'''                status.set(if !library.is_empty()
                    || (badges.pending() && !badges.waiting)''',
"only serious network/account faults require attention")
change(net,
'''                    || store.lock().unwrap().unlocks.values().any(|u| !u.synced)
                {
                    SyncStatus::Syncing
                } else {
                    SyncStatus::Ready
                });''',
'''                    || store.lock().unwrap().unlocks.values().any(|u| !u.synced)
                    || active.as_ref().is_some_and(|g| !g.ready)
                {
                    SyncStatus::Syncing
                } else {
                    SyncStatus::Ready
                });''',
"track active game readiness when otherwise idle")

# Guard unsupported games from future session pings.
change(net,
'''    online: bool,
    last_ping: Instant,''',
'''    online: bool,
    unmatched: bool,
    last_ping: Instant,''',
"distinguish negative-lookups from active achievement sessions")
change(net,
'''                        online: false,
                        last_ping: Instant::now(),''',
'''                        online: false,
                        unmatched: false,
                        last_ping: Instant::now(),''',
"initialize negative lookup state")
change(net,
'''                                        if cached.id == 0 {
                                            game.online = true;
                                        }''',
'''                                        if cached.id == 0 {
                                            game.online = true;
                                            game.unmatched = true;
                                        }''',
"skip RA session ping for cached unsupported ROMs")
change(net,
'''                        game.online = true;
                        game.ready = true;
                    } else {''',
'''                        game.online = true;
                        game.ready = true;
                        game.unmatched = true;
                    } else {''',
"do not ping unsupported ROMs")
change(net,
'''                !game.online || (game.ready && game.last_ping.elapsed() >= Duration::from_secs(120))''',
'''                !game.online || (game.ready && !game.unmatched && game.last_ping.elapsed() >= Duration::from_secs(120))''',
"skip scheduled ping for negative ROM match")
change(net,
'''                } else if game.ready && game.last_ping.elapsed() >= Duration::from_secs(120) {''',
'''                } else if game.ready && !game.unmatched && game.last_ping.elapsed() >= Duration::from_secs(120) {''',
"skip network request for unmatched cached game")

# No-achievement games should display a definitive launch status.

change(net,
'''                            &(empty, BTreeSet::<u32>::new()),
                        ).map_err(|_| Failure::Invalid)?;''',
'''                            &(empty.clone(), BTreeSet::<u32>::new()),
                        ).map_err(|_| Failure::Invalid)?;
                        let _ = prepared.send(Prepared {
                            generation: game.generation,
                            hash: game.hash.clone(),
                            game: empty,
                            unlocked: BTreeSet::new(),
                            cached: false,
                        });''',
"report unsupported ROMs through standard game-ready status");
