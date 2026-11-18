#!/usr/bin/env python3
"""Ver34: evaluate every emulated frame on the core thread, including fast-forward.

Compared against RetroAchievements rc_client integration guide, RetroArch,
OpenEmu-Silicon and slot.advance. No RAM snapshot queues or dropped frames.
Only triggered IDs cross a channel; card writes and HTTPS remain off the
emulator thread. Preserve the old evaluator's narrow unit-test entry point.
"""
from pathlib import Path

def change(path, old, new, title):
    p=Path(path)
    src=p.read_text()
    n=src.count(old)
    if n!=1:
        raise SystemExit(f"Ver34 {path}: {title}: expected 1 anchor, found {n}")
    p.write_text(src.replace(old,new,1))
    print(f"Ver34 {path}: {title}")

lib="crates/slot-achievements/src/lib.rs"
runtime="crates/slot-achievements/src/runtime.rs"
core="crates/slot-achievements/src/core.rs"
tests="crates/slot-achievements/src/tests.rs"

# The runtime never owns emulator memory pointers, only its own C allocations.
# Every call is protected by one Mutex. Event C callbacks use _Thread_local
# state for the duration of a single frame. Moving between initial setup on
# the worker and evaluation on the emulator thread cannot overlap.
change(runtime,
'''pub(crate) struct Runtime {
    ptr: NonNull<c_void>,''',
'''pub(crate) struct Runtime {
    ptr: NonNull<c_void>,''',
"confirm native runtime declaration")
# Insert after the struct, so the code is reviewed in context.
change(runtime,
'''    warned_diagnostics: u32,
}

impl Runtime {''',
'''    warned_diagnostics: u32,
}

// SAFETY: this Runtime owns its C allocation, no pointers into core memory.
// The Arc<Mutex<Option<Playing>>> permits only one thread to access a runtime
// at a time. runtime.c's callback state is thread-local to each frame call.
unsafe impl Send for Runtime {}

impl Runtime {''',
"make lock-protected runtime transferable to the emulator thread")

change(lib,
'''struct Frame {
    generation: u64,''',
'''/// A rare triggered award, independent from bulk RAM snapshots.
struct Earned {
    generation: u64,
    hash: String,
    achievement: storage::Achievement,
    earned_at: u64,
}

struct Frame {
    generation: u64,''',
"define lossless lightweight unlock messages")

change(lib,
'''    controls: mpsc::Sender<Control>,
    frames: mpsc::SyncSender<Frame>,''',
'''    controls: mpsc::Sender<Control>,
    frames: mpsc::SyncSender<Frame>,
    earned: mpsc::Sender<Earned>,
    playing: Arc<Mutex<Option<Playing>>>,''',
"share a synchronized evaluator with the core thread")

change(lib,
'''        let (frames, frame_rx) = mpsc::sync_channel(QUEUE_SIZE);
        let (notice_tx, notices) = mpsc::channel();''',
'''        let (frames, frame_rx) = mpsc::sync_channel(QUEUE_SIZE);
        let (earned, earned_rx) = mpsc::channel();
        let playing = Arc::new(Mutex::new(None::<Playing>));
        let worker_playing = playing.clone();
        let (notice_tx, notices) = mpsc::channel();''',
"create lightweight award channel, no RAM frame queue in production")

change(lib,
'''                    control_rx,
                    frame_rx,
                    notice_tx,
                    worker_status,
                    transport,''',
'''                    control_rx,
                    frame_rx,
                    earned_rx,
                    worker_playing,
                    notice_tx,
                    worker_status,
                    transport,''',
"pass shared runtime and earned events into storage worker")

change(lib,
'''            controls,
            frames,
            notices,
            enabled,''',
'''            controls,
            frames,
            earned,
            playing,
            notices,
            enabled,''',
"wire core's service handles")

change(lib,
'''    frames: mpsc::Receiver<Frame>,
    notices: mpsc::Sender<Notice>,
    status: Arc<Status>,
    transport:''',
'''    frames: mpsc::Receiver<Frame>,
    earned: mpsc::Receiver<Earned>,
    shared_playing: Arc<Mutex<Option<Playing>>>,
    notices: mpsc::Sender<Notice>,
    status: Arc<Status>,
    transport:''',
"worker receives compact, durably recorded awards")

change(lib,
'''    let mut playing: Option<Playing> = None;''',
'''    // The runtime is accessible to the emulator thread for every emulated frame.
    // Never hold this lock during HTTPS or filesystem writes.''',
"drop the worker-only runtime variable")

change(lib,
'''        loop {
            // Frames queued before an eject/load must be evaluated before retiring that game.''',
'''        // Only game achievements, never copied frame buffers, arrive from the
        // emulator. Record each before showing the unlock notification.
        for award in earned.try_iter() {
            let notice = Notice {
                badge: badges::path(&store.lock().unwrap().dir, &award.achievement.badge),
                generation: award.generation,
                title: format!("{} (+{})", award.achievement.title, award.achievement.points),
                detail: award.achievement.description.clone(),
                kind: NoticeKind::Earned,
            };
            let unlock = Unlock {
                id: award.achievement.id,
                hash: award.hash,
                earned_at: award.earned_at,
                synced: false,
            };
            match store.lock().unwrap().record(unlock.clone()) {
                Ok(true) => { let _ = notices.send(notice); }
                Ok(false) => {}
                Err(error) => {
                    let _ = notices.send(Notice::status(award.generation, &error));
                    unsaved.insert(unlock.id, (unlock, notice));
                }
            }
            if let Ok(mut viewer) = status.viewer.lock() {
                if let Some(view) = viewer.as_mut() {
                    if view.entries.iter().any(|a| a.id == award.achievement.id && !a.unlocked) {
                        let entries = &mut Arc::make_mut(view).entries;
                        for a in entries.iter_mut() {
                            if a.id == award.achievement.id {
                                a.unlocked = true;
                                a.measured = None;
                            }
                        }
                    }
                }
            }
        }
        // Network and disk work above is outside the runtime lock.
        let mut playing = shared_playing.lock().unwrap();
        loop {
            // Old synthetic frames are used only by unit tests. Hardware
            // evaluates rcheevos immediately after each actual run_frame.''',
"process unlocks off-thread and lock runtime only for metadata updates")

# When the entire state is replaced in the worker, assigning into the shared
# guard must dereference it.
change(lib,
'''                    status.set_game_detail(generation, "Loading achievement metadata");
                    playing = None;''',
'''                    status.set_game_detail(generation, "Loading achievement metadata");
                    *playing = None;''',
"discard stale game evaluator on load")

change(lib,
'''                    status.set_game(0, GameConnection::Checking);
                    playing = None;''',
'''                    status.set_game(0, GameConnection::Checking);
                    *playing = None;''',
"discard stale game evaluator on unload")

change(lib,
'''            if playing.as_ref().is_some_and(|g| g.hash != prepared.hash) {
                playing = None;
            }''',
'''            if playing.as_ref().is_some_and(|g| g.hash != prepared.hash) {
                *playing = None;
            }''',
"discard old rules when ROM hash changes")

change(lib,
'''            playing = Some(Playing {
                generation,''',
'''            *playing = Some(Playing {
                generation,''',
"publish initialized native runtime to emulator thread")

# The blocking frames.recv_timeout belongs to the synthetic-test path.
# Release the runtime lock while it waits, and acquire it only if needed.
change(lib,
'''        match frames.recv_timeout(Duration::from_millis(5)) {
            Ok(frame) => {
                evaluate(frame, &mut playing, &store, &notices, &mut unsaved, &status);
            }''',
'''        drop(playing);
        match frames.recv_timeout(Duration::from_millis(5)) {
            Ok(frame) => {
                let mut playing = shared_playing.lock().unwrap();
                evaluate(frame, &mut playing, &store, &notices, &mut unsaved, &status);
            }''',
"release core runtime before any blocking worker wait")

change(lib,
'''            *status.presence.lock().unwrap() = playing
                .as_ref()
                .map(|game| (game.generation, game.runtime.presence()));''',
'''            *status.presence.lock().unwrap() = shared_playing.lock().unwrap()
                .as_ref()
                .map(|game| (game.generation, game.runtime.presence()));''',
"read presence from shared evaluator without holding it elsewhere")

# Handle shutdown flush only after queued awards have been persisted. Because
# the UI calls this after the emulator stops producing frames, the earned channel
# must be drained for the last frame before marking flush completion.
change(lib,
'''                Ok(Control::Flush(done)) => {
                    retry_unsaved(&mut unsaved, &store, &notices);
                    done.store(true, Ordering::Release);
                }''',
'''                Ok(Control::Flush(done)) => {
                    for award in earned.try_iter() {
                        let notice = Notice {
                            badge: badges::path(&store.lock().unwrap().dir, &award.achievement.badge),
                            generation: award.generation,
                            title: format!("{} (+{})", award.achievement.title, award.achievement.points),
                            detail: award.achievement.description.clone(),
                            kind: NoticeKind::Earned,
                        };
                        let unlock = Unlock {
                            id: award.achievement.id, hash: award.hash,
                            earned_at: award.earned_at, synced: false,
                        };
                        match store.lock().unwrap().record(unlock.clone()) {
                            Ok(true) => { let _ = notices.send(notice); }
                            Ok(false) => {}
                            Err(_) => { unsaved.insert(unlock.id, (unlock, notice)); }
                        }
                    }
                    retry_unsaved(&mut unsaved, &store, &notices);
                    done.store(true, Ordering::Release);
                }''',
"flush earned IDs before shutdown acknowledgement")

# Apply a small replacement for the existing Tracked core, rather than
# duplicating the upstream generic RetroCore implementation. The editor leaves
# other hardware, save, rewind, video and audio paths intact.
p=Path(core)
s=p.read_text()
start=s.index("pub(crate) struct Tracked {")
impl_at=s.index("impl RetroCore for Tracked {", start)
new_prefix='''pub(crate) struct Tracked {
    core: Box<dyn RetroCore>,
    controls: mpsc::Sender<Control>,
    earned: mpsc::Sender<crate::Earned>,
    playing: Arc<std::sync::Mutex<Option<crate::Playing>>>,
    status: Arc<crate::Status>,
    enabled: Arc<AtomicBool>,
    current: Arc<AtomicU64>,
    generation: u64,
    ram: Vec<u8>,
    reported_tracking: bool,
}

impl Tracked {
    pub fn new(core: Box<dyn RetroCore>, service: &Service) -> Self {
        Self {
            core,
            controls: service.controls.clone(),
            earned: service.earned.clone(),
            playing: service.playing.clone(),
            status: service.status.clone(),
            enabled: service.enabled.clone(),
            current: service.current.clone(),
            generation: 0,
            ram: vec![0; RAM_SIZE],
            reported_tracking: false,
        }
    }

    /// Directly process *every* emulated frame after the core has run it.
    /// This includes fast-forward frames that are not rendered to the LCD.
    /// No I/O, HTTPS, badge decode or wait on a backlog happens here.
    fn snapshot(&mut self) {
        if !self.enabled.load(Ordering::Acquire) { return; }
        let valid = self.core.achievement_memory(&mut self.ram);
        let Ok(mut playing) = self.playing.lock() else { return };
        let Some(game) = playing.as_mut().filter(|g| g.generation == self.generation)
            else { return };
        if valid.regions().is_empty() {
            if !self.reported_tracking {
                eprintln!("slot: RetroAchievements: no emulated RAM regions available to evaluate");
                self.reported_tracking = true;
            }
            return;
        }
        if !self.reported_tracking {
            eprintln!("slot: RetroAchievements: evaluating every emulated frame, including fast-forward");
            self.reported_tracking = true;
        }
        let triggered = game.runtime.frame(&self.ram, &valid).to_vec();
        for id in triggered {
            if let Some(achievement) = game.achievements.remove(&id) {
                game.runtime.deactivate(id);
                let award = crate::Earned {
                    generation: self.generation,
                    hash: game.hash.clone(),
                    achievement,
                    earned_at: network::now(),
                };
                if self.earned.send(award).is_err() {
                    eprintln!("slot: RetroAchievements: award worker unavailable");
                }
            }
        }
        let due = self.status.last_measured.lock().unwrap()
            .as_ref().is_none_or(|at| at.elapsed() >= std::time::Duration::from_secs(5));
        if due {
            *self.status.last_measured.lock().unwrap() = Some(std::time::Instant::now());
            let sample: Vec<_> = game.achievements.keys()
                .map(|id| (*id, game.runtime.measured(*id))).collect();
            if let Ok(mut lock) = self.status.viewer.lock() {
                if let Some(view) = lock.as_mut() {
                    if sample.iter().any(|(id, value)| {
                        view.entries.iter().any(|entry| entry.id == *id && entry.measured != *value)
                    }) {
                        let entries = &mut Arc::make_mut(view).entries;
                        for (id, measured) in sample {
                            if let Some(entry) = entries.iter_mut().find(|e| e.id == id) {
                                entry.measured = measured;
                            }
                        }
                    }
                }
            }
        }
    }

    fn reset_achievements(&mut self) {
        if let Ok(mut playing) = self.playing.lock() {
            if let Some(game) = playing.as_mut().filter(|g| g.generation == self.generation) {
                game.runtime.reset();
            }
        }
    }
}

'''
p.write_text(s[:start] + new_prefix + s[impl_at:])
print("Ver34: core now owns a reusable RAM buffer and evaluates synchronously")

change(core,
'''use crate::{network, Control, Frame, Service, QUEUE_SIZE, RAM_SIZE};''',
'''use crate::{network, Control, Service, RAM_SIZE};''',
"remove references to the old snapshot transport")
change(core,
'''        self.reported_backpressure = false;
        self.current.store(self.generation, Ordering::Release);''',
'''        self.current.store(self.generation, Ordering::Release);''',
"remove old queue-backpressure state from the load path")

change(core,
'''        self.current.store(self.generation, Ordering::Release);''',
'''        self.reported_tracking = false;
        self.current.store(self.generation, Ordering::Release);''',
"fresh log state for each ROM")

change(core,
'''            refresh: false,
        }));''',
'''            refresh: false,
        }));''',
"keep established ROM initialization")

change(core,
'''    fn reset(&mut self) {
        self.core.reset();
        self.timeline += 1;
    }''',
'''    fn reset(&mut self) {
        self.core.reset();
        self.reset_achievements();
    }''',
"reset only on a real core reset")

change(core,
'''    fn run_frame_linked(&mut self, p1: ButtonMask, p2: ButtonMask) {
        self.core.run_frame_linked(p1, p2);
        self.timeline += 1;
    }''',
'''    fn run_frame_linked(&mut self, p1: ButtonMask, p2: ButtonMask) {
        self.core.run_frame_linked(p1, p2);
        // As in slot.advance, linked sessions are not evaluated.
    }''',
"do not evaluate linked or network-cable frames")

change(core,
'''        self.core.unserialize(data)?;
        self.timeline += 1;
        Ok(())''',
'''        self.core.unserialize(data)?;
        self.reset_achievements();
        Ok(())''',
"reset rcheevos state on state load")

change(core,
'''        self.timeline += 1;
        self.core.start_link(client_id);''',
'''        self.reset_achievements();
        self.core.start_link(client_id);''',
"do not carry a previous hit state into link play")

change(core,
'''        self.core.stop_link();
        self.timeline += 1;''',
'''        self.core.stop_link();
        self.reset_achievements();''',
"do not carry a previous hit state out of link play")

# Keep the old worker-only Frame fixture and evaluate function for regression
# tests of discontinuities, but the production Core no longer sends snapshots.
with Path(tests).open("a") as f:
    f.write(r'''

#[test]
fn fast_forward_evaluates_each_emulated_frame_including_unrendered_frames() {
    let mut runtime = runtime::Runtime::new().unwrap();
    assert!(runtime.activate(7008, "0xH000000=5"));
    let mut ram = vec![0; RAM_SIZE];
    let valid = AchievementMemory::new([0..0x8000, 0x8000..0x48000]);
    let mut observed = Vec::new();
    // No notion of LCD presentation here: each run_frame must be evaluated.
    for frame in 0..360 {
        ram[0] = frame as u8;
        observed.extend_from_slice(runtime.frame(&ram, &valid));
    }
    assert_eq!(observed, vec![7008]);
}
''')
print("Ver34: fast-forward per-frame runtime regression installed")
