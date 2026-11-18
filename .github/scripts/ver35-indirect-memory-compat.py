#!/usr/bin/env python3
"""Ver35: match rc_client's handling of out-of-range indirect RAM reads.

Evidence: real RGSP Smaragd log shows the runtime resetting all achievements
after an out-of-range read. Official rcheevos rc_client_peek() ignores a failed
pointer-chain read, returning zero; only an invalid *static* memref disables
its affected achievement. Our existing rc_runtime_validate_addresses() already
validates static addresses every frame before evaluation.

Do not treat a bad indirect pointer as a reason to reset the entire game set.
Preserve all emulated saves, cores, offline unlocks and non-RA menus.
"""
from pathlib import Path

def change(path, old, new, reason):
    f=Path(path)
    src=f.read_text()
    n=src.count(old)
    if n != 1:
        raise SystemExit(f"Ver35 {path}: {reason}: expected 1 anchor, found {n}")
    f.write_text(src.replace(old,new,1))
    print(f"Ver35: {reason}")

c="crates/slot-achievements/src/runtime.c"
rs="crates/slot-achievements/src/runtime.rs"
storage="crates/slot-achievements/src/storage.rs"
tests="crates/slot-achievements/src/tests.rs"

change(c,
'''    int invalid;
    uint32_t disabled;
} slot_frame;''',
'''    int invalid;
    uint32_t disabled;
    int evaluating;
    int indirect_read;
    uint32_t first_indirect_address;
} slot_frame;''',
"separate indirect pointer failures from unsupported static memory")

change(c,
'''        if (address > UINT32_MAX - i || !valid_address(address + i)) {
            current->invalid = 1;
            return 0;
        }''',
'''        if (address > UINT32_MAX - i || !valid_address(address + i)) {
            /* Only a wholly unmapped starting address is a possible pointer
               chain. A static multibyte read beginning in mapped RAM but
               crossing an unmapped edge is still treated as unsafe. */
            if (current->evaluating && !valid_address(address)) {
                /*
                 * rcheevos rc_client_peek: an unavailable address reached by
                 * a pointer chain is an observed zero, NOT a reason to reset
                 * the runtime and erase progress of unrelated achievements.
                 * Static memrefs have already been checked/disabled via
                 * rc_runtime_validate_addresses before this frame.
                 */
                if (!current->indirect_read)
                    current->first_indirect_address = address + i;
                current->indirect_read = 1;
                return 0;
            }
            current->invalid = 1;
            return 0;
        }''',
"match official rc_client behavior for invalid pointer-chain lookups")

change(c,
'''    slot_frame frame = { ram, regions, region_count, earned, capacity, 0, 0, 0 };
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
    /* Rich Presence is purely informational: its RAM lookups must not erase''',
'''    slot_frame frame = {0};
    uint32_t errors = 0;
    frame.ram = ram;
    frame.regions = regions;
    frame.region_count = region_count;
    frame.earned = earned;
    frame.capacity = capacity;
    current = &frame;
    /* Static memrefs are validated before every frame, as in rc_client. */
    rc_runtime_validate_addresses(runtime, event, valid_address);
    frame.evaluating = 1;
    rc_runtime_do_frame(runtime, event, peek, NULL, NULL);
    frame.evaluating = 0;

    if (frame.indirect_read)
        errors |= 8;
    /* Optional Rich Presence is evaluated separately and never cancels awards.
       Treat truly unsupported static addresses as invalid via validation. */
    if (frame.invalid) {
        errors |= 1;
        rc_runtime_reset(runtime);
        frame.count = 0;
    }
    /* Rich Presence is purely informational: its RAM lookups must not erase''',
"prevent unrelated achievements from losing hit counts on bad pointers")

change(c,
'''    if (diagnostics) *diagnostics = errors;
    return frame.count;''',
'''    if (diagnostics) {
        diagnostics[0] = errors;
        diagnostics[1] = frame.first_indirect_address;
    }
    return frame.count;''',
"expose first invalid indirect address for precise device diagnostics")

change(rs,
'''        let mut diagnostics = 0u32;
        let count = unsafe {''',
'''        let mut diagnostics = [0u32; 2];
        let count = unsafe {''',
"provide a diagnostics buffer for the failing pointer address")

change(rs,
'''                &mut diagnostics,
            )
        };
        let new_errors = diagnostics & !self.warned_diagnostics;''',
'''                diagnostics.as_mut_ptr(),
            )
        };
        let new_errors = diagnostics[0] & !self.warned_diagnostics;''',
"pass diagnostics buffer safely through C FFI")

change(rs,
'''        self.warned_diagnostics |= diagnostics;
        &self.earned[..count]''',
'''        if new_errors & 8 != 0 {
            eprintln!(
                "slot: RetroAchievements: indirect pointer read outside available RAM at 0x{:06X}; returned zero without resetting other achievements (official rc_client behavior)",
                diagnostics[1]
            );
        }
        self.warned_diagnostics |= diagnostics[0];
        &self.earned[..count]''',
"distinguish pointer-chain failures from missing RAM and avoid duplicate log floods")

change(storage,
'''        eprintln!("slot: RetroAchievements: server supplied {count} client compatibility warning(s); excluded from the real achievement set");''',
'''        // The server can include compatibility warnings in every cached game
        // load. They are filtered without flooding logs for each library scan.
        let _ = count;''',
"silence repeated known non-game warning entries")

change(rs,
'''    pub fn activate(&mut self, id: u32, definition: &str) -> bool {''',
'''    #[cfg(test)]
    pub(crate) fn diagnostic_bits(&self) -> u32 {
        self.warned_diagnostics
    }

    pub fn activate(&mut self, id: u32, definition: &str) -> bool {''',
"expose exact pointer-failure path to unit tests")

with Path(tests).open("a") as f:
    f.write(r'''

#[test]
fn an_invalid_indirect_pointer_does_not_reset_unrelated_achievements() {
    // rc_client_peek returns 0 on pointer chains outside the active console
    // memory range. The old wrapper called rc_runtime_reset for the entire
    // game on every such frame, preventing independent conditions unlocking.
    let mut runtime = runtime::Runtime::new().unwrap();
    assert!(runtime.activate(7100, "I:0xX000020_0xH000000=9"));
    assert!(runtime.activate(7101, "0xH000010=1"));
    let mut ram = vec![0; RAM_SIZE];
    let valid = AchievementMemory::new([0..0x8000, 0x8000..0x48000]);
    // Pointer is far past available GBA work RAM; unlike direct invalid
    // memrefs, this is a dynamic lookup that may be temporarily unavailable.
    ram[0x20..0x24].copy_from_slice(&(0x70000u32).to_le_bytes());
    assert!(runtime.frame(&ram, &valid).is_empty());
    assert_ne!(runtime.diagnostic_bits() & 8, 0,
        "test must actually exercise an out-of-range indirect read");
    ram[0x10] = 1;
    assert_eq!(runtime.frame(&ram, &valid), &[7101]);
    assert!(runtime.frame(&ram, &valid).is_empty());
}
''')
print("Ver35: independent award survives an invalid pointer-chain read")

with Path(tests).open("a") as f:
    f.write(r'''

#[test]
fn a_direct_multi_byte_read_crossing_unmapped_memory_is_still_rejected() {
    let mut runtime = runtime::Runtime::new().unwrap();
    assert!(runtime.activate(7200, "0xX047FFF=1"));
    let mut ram = vec![0; RAM_SIZE];
    let valid = AchievementMemory::new([0..0x8000, 0x8000..0x48000]);
    ram[0x47fff] = 1;
    assert!(runtime.frame(&ram, &valid).is_empty());
    assert_ne!(runtime.diagnostic_bits() & 1, 0,
        "a static 32-bit read crossing the end of mapped RAM must fail closed");
}
''')
print("Ver35: strict rejection of static reads crossing unmapped RAM")

