#!/usr/bin/env python3
"""Isolate Rich Presence from achievement evaluation and diagnose missed unlocks.

A Rich Presence memory error is allowed to clear the activity text, but must
never invalidate an otherwise valid award or reset achievement hit counters.
Log only the first runtime problem per game to avoid slowing H700 gameplay.
"""
from pathlib import Path

def change(path, old, new, why):
    p=Path(path)
    data=p.read_text()
    count=data.count(old)
    if count != 1:
        raise SystemExit(f"Ver33 {path}: {why}: expected one anchor, found {count}")
    p.write_text(data.replace(old, new, 1))
    print(f"Ver33 {path}: {why}")

c="crates/slot-achievements/src/runtime.c"
rs="crates/slot-achievements/src/runtime.rs"
core="crates/slot-achievements/src/core.rs"
tests="crates/slot-achievements/src/tests.rs"

change(c,
'''    size_t capacity, count;
    int invalid;
} slot_frame;''',
'''    size_t capacity, count;
    int invalid;
    uint32_t disabled;
} slot_frame;''',
"track disabled RAM-dependent conditions")

change(c,
'''static void event(const rc_runtime_event_t *ev) {
    if (ev->type == RC_RUNTIME_EVENT_ACHIEVEMENT_TRIGGERED && current->count < current->capacity)
        current->earned[current->count++] = ev->id;
}''',
'''static void event(const rc_runtime_event_t *ev) {
    if (ev->type == RC_RUNTIME_EVENT_ACHIEVEMENT_TRIGGERED && current->count < current->capacity)
        current->earned[current->count++] = ev->id;
    else if (ev->type == RC_RUNTIME_EVENT_ACHIEVEMENT_DISABLED)
        ++current->disabled;
}''',
"record unsupported achievement memory rules without affecting other achievements")

change(c,
'''                     uint32_t *earned, size_t capacity, char *presence, size_t presence_size) {
    slot_frame frame = { ram, regions, region_count, earned, capacity, 0, 0 };
    current = &frame;
    rc_runtime_validate_addresses(runtime, event, valid_address);
    rc_runtime_do_frame(runtime, event, peek, NULL, NULL);
    rc_runtime_get_richpresence(runtime, presence, presence_size, peek, NULL, NULL);
    presence[presence_size - 1] = 0;
    current = NULL;
    /* An invalid indirect read cannot count as an observed zero or satisfy a trigger. */
    if (frame.invalid) { presence[0] = 0; rc_runtime_reset(runtime); return 0; }
    return frame.count;
}''',
'''                     uint32_t *earned, size_t capacity, char *presence, size_t presence_size,
                     uint32_t *diagnostics) {
    slot_frame frame = { ram, regions, region_count, earned, capacity, 0, 0, 0 };
    uint32_t errors = 0;
    current = &frame;
    rc_runtime_validate_addresses(runtime, event, valid_address);
    rc_runtime_do_frame(runtime, event, peek, NULL, NULL);

    /* An invalid indirect achievement read must not be treated as zero. */
    if (frame.invalid) {
        errors |= 1;
        rc_runtime_reset(runtime);
        frame.count = 0;
    }
    /* Rich Presence is purely informational: its RAM lookups must not erase
       valid achievement triggers or reset their counters. */
    frame.invalid = 0;
    rc_runtime_get_richpresence(runtime, presence, presence_size, peek, NULL, NULL);
    presence[presence_size - 1] = 0;
    if (frame.invalid) {
        errors |= 2;
        presence[0] = 0;
    }
    if (frame.disabled) errors |= 4;
    current = NULL;
    if (diagnostics) *diagnostics = errors;
    return frame.count;
}''',
"do not let optional Rich Presence failures discard gameplay awards")

change(rs,
'''        presence_size: usize,
    ) -> usize;''',
'''        presence_size: usize,
        diagnostics: *mut u32,
    ) -> usize;''',
"expose runtime diagnostics without changing the award API")

change(rs,
'''    script: String,
}''',
'''    script: String,
    warned_diagnostics: u32,
}''',
"record one-shot diagnostics per running game")

change(rs,
'''            script: String::new(),
        })''',
'''            script: String::new(),
            warned_diagnostics: 0,
        })''',
"initialize diagnostics")

change(rs,
'''        let count = unsafe {
            slot_ra_frame(''',
'''        let mut diagnostics = 0u32;
        let count = unsafe {
            slot_ra_frame(''',
"capture frame health only inside the RA worker")

change(rs,
'''                self.presence.len(),
            )
        };
        &self.earned[..count]''',
'''                self.presence.len(),
                &mut diagnostics,
            )
        };
        let new_errors = diagnostics & !self.warned_diagnostics;
        if new_errors & 1 != 0 {
            eprintln!("slot: RetroAchievements: out-of-range achievement RAM read; award suppressed for safety");
        }
        if new_errors & 2 != 0 {
            eprintln!("slot: RetroAchievements: Rich Presence RAM read failed; achievement tracking preserved");
        }
        if new_errors & 4 != 0 {
            eprintln!("slot: RetroAchievements: some achievement definitions require memory the emulator does not expose");
        }
        self.warned_diagnostics |= diagnostics;
        &self.earned[..count]''',
"log abnormal tracking without spamming the emulator")

change(core,
'''    allocated: usize,
}''',
'''    allocated: usize,
    reported_backpressure: bool,
}''',
"record queue exhaustion only once per loaded game")

change(core,
'''            allocated: 0,
        }''',
'''            allocated: 0,
            reported_backpressure: false,
        }''',
"init backpressure guard")

change(core,
'''            Err(_) => return,
        };
        let valid = self.core.achievement_memory(&mut ram);''',
'''            Err(_) => {
                if !self.reported_backpressure {
                    eprintln!("slot: RetroAchievements: evaluation queue exhausted; some frames are not tracked");
                    self.reported_backpressure = true;
                }
                return;
            }
        };
        let valid = self.core.achievement_memory(&mut ram);''',
"identify saturation caused by large achievement sets")

change(core,
'''        if let Err(error) = self.frames.try_send(frame) {
            let (mpsc::TrySendError::Full(frame) | mpsc::TrySendError::Disconnected(frame)) = error;
            let _ = self.recycle.try_send(frame.ram);
        }''',
'''        if let Err(error) = self.frames.try_send(frame) {
            let (mpsc::TrySendError::Full(frame) | mpsc::TrySendError::Disconnected(frame)) = error;
            if !self.reported_backpressure {
                eprintln!("slot: RetroAchievements: evaluation queue full; missed frames reset consecutive-hit conditions");
                self.reported_backpressure = true;
            }
            let _ = self.recycle.try_send(frame.ram);
        }''',
"log frame gaps that can prevent certain multi-hit unlocks")

change(core,
'''        self.generation = NEXT_GAME.fetch_add(1, Ordering::Relaxed);
        self.current.store(self.generation, Ordering::Release);''',
'''        self.generation = NEXT_GAME.fetch_add(1, Ordering::Relaxed);
        self.reported_backpressure = false;
        self.current.store(self.generation, Ordering::Release);''',
"reset per-ROM diagnostics")

# This regression establishes that a valid triggered achievement still works
# when optional activity reporting requests unavailable RAM.
with Path(tests).open("a") as f:
    f.write(r'''

#[test]
fn a_rich_presence_ram_error_cannot_discard_an_independent_valid_achievement() {
    let mut runtime = runtime::Runtime::new().unwrap();
    assert!(runtime.activate(7001, "0xH000000=1"));
    // This address lies beyond the console's 0x58000 RAM snapshot.
    assert!(runtime.activate_presence("Display:\n@Number(0xH058000)"));
    let mut ram = vec![0; RAM_SIZE];
    let valid = AchievementMemory::new([0..0x8000, 0x8000..0x48000]);
    assert!(runtime.frame(&ram, &valid).is_empty());
    ram[0] = 1;
    assert_eq!(runtime.frame(&ram, &valid), &[7001]);
}

#[test]
fn a_missing_achievement_ram_address_never_falsely_awards() {
    let mut runtime = runtime::Runtime::new().unwrap();
    assert!(runtime.activate(7002, "0xH048000=0"));
    let ram = vec![0; RAM_SIZE];
    let valid = AchievementMemory::new([0..0x8000, 0x8000..0x48000]);
    for _ in 0..3 {
        assert!(runtime.frame(&ram, &valid).is_empty());
    }
}
''')
print("Ver33: memory error isolation and diagnostic regression tests installed")
