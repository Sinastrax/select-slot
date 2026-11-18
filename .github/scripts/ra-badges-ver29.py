#!/usr/bin/env python3
"""Ver.29: lazy achievement badge work and immediate index-disable behavior."""
from pathlib import Path

def change(path, old, new, reason):
    p=Path(path)
    s=p.read_text()
    n=s.count(old)
    if n != 1:
        raise SystemExit(f"{path}: {reason}: expected one match, got {n}")
    p.write_text(s.replace(old,new,1))
    print(f"Ver29 {path}: {reason}")

change("crates/slot-achievements/src/badges.rs",
'''    pub fn new(dir: &Path) -> Self {
        let mut queue = Self {
            dir: dir.into(),
            names: BTreeSet::new(),
            known: BTreeSet::new(),
            pending: VecDeque::new(),
            retry: Instant::now(),
            waiting: false,
        };
        queue.scan();
        queue
    }''',
'''    pub fn new(dir: &Path) -> Self {
        let mut queue = Self::empty(dir);
        queue.scan();
        queue
    }

    /// No all-library badge scan unless indexing is enabled or user requests it.
    pub fn empty(dir: &Path) -> Self {
        Self {
            dir: dir.into(),
            names: BTreeSet::new(),
            known: BTreeSet::new(),
            pending: VecDeque::new(),
            retry: Instant::now(),
            waiting: false,
        }
    }''',
"opt-in badge discovery")
change("crates/slot-achievements/src/network.rs",
'''    let mut badges = crate::badges::Queue::new(&dir);''',
'''    let mut badges = if config.index_library {
        crate::badges::Queue::new(&dir)
    } else {
        crate::badges::Queue::empty(&dir)
    };''',
"only load active-game badge queue by default")
change("crates/slot-achievements/src/lib.rs",
'''            LibraryAction::SetIndex(enabled) => {
                self.status.index_library.store(enabled, Ordering::Release);
                if enabled {
                    self.status.scan_request.store(1, Ordering::Release);
                }
            }''',
'''            LibraryAction::SetIndex(enabled) => {
                self.status.index_library.store(enabled, Ordering::Release);
                self.status.scan_request.store(if enabled { 1 } else { 3 }, Ordering::Release);
            }''',
"cancel existing index queue when switching off")
change("crates/slot-achievements/src/lib.rs",
'''    scan_request: AtomicU8, // 0 none, 1 prepare, 2 retry failed''',
'''    scan_request: AtomicU8, // 0 none, 1 prepare, 2 retry failed, 3 stop''',
"document stop-index request")
change("crates/slot-achievements/src/network.rs",
'''        } else if request == 2 {
            library = failed_roms.drain(..).collect();
            library_total = library.len();
            status.failed_roms.store(0, std::sync::atomic::Ordering::Release);
            next_attempt = Instant::now();
        } else if status.index_library.load(std::sync::atomic::Ordering::Acquire)''',
'''        } else if request == 2 {
            library = failed_roms.drain(..).collect();
            library_total = library.len();
            status.failed_roms.store(0, std::sync::atomic::Ordering::Release);
            next_attempt = Instant::now();
        } else if request == 3 {
            library.clear();
            library_total = 0;
            status.progress.store(0, std::sync::atomic::Ordering::Release);
        } else if status.index_library.load(std::sync::atomic::Ordering::Acquire)''',
"stop queued index work when turned off")
change("crates/slot-achievements/src/badges.rs",
'''        if result.is_ok() {
            self.names.remove(&name);
            if self.pending.is_empty() {
                self.waiting = false;
            }
        } else {''',
'''        if result.is_ok() {
            self.names.remove(&name);
            self.waiting = false;
        } else {''',
"resume badge progress after successful retry")
