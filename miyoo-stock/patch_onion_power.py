#!/usr/bin/env python3
"""Minimal OnionOS POWER ownership fix against official stock slot-miyoo v0.3.0.

No custom cores, features, screen effects, brightness changes, or theme files.
The changes are generated as a Git patch after the stock port patches are
applied, then normal task release re-applies everything from scratch.
"""
from pathlib import Path
from difflib import unified_diff
import sys

source = Path(sys.argv[1])
output = Path(sys.argv[2])
file = source / "crates/slot/src/app.rs"
original = file.read_text()

before = '''    pub fn apply(&mut self, action: Action) {
        self.track_held_dir(action);
        match action {
            Action::LidClose => return self.doze(),'''
after = '''    pub fn apply(&mut self, action: Action) {
        self.track_held_dir(action);
        // In OnionOS, keymon owns the physical POWER button. Its short
        // press SIGSTOPs apps, powers down LCD/PWM, then on wake restores
        // the LCD and SIGCONTs apps. Handling the same tap here ALSO
        // calls Slot's internal doze() and causes alternating wake/sleep:
        // keymon wakes the LCD while Slot is still drawing black; the
        // next press wakes Slot but keymon suspends it again.
        //
        // Only delegate when Onion's *running* keymon is actually present.
        // Stock firmware and Allium retain the unchanged Slot controls.
        // We do not modify Onion's bootScreen/theme/BMO assets or power
        // handler, and save-on-press is preserved.
        if matches!(
            action,
            Action::PowerPress | Action::PowerTap | Action::PowerHold
        ) && self.root.as_ref().is_some_and(|root| {
            root.join(".tmp_update/runtime.sh").is_file()
        }) && std::process::Command::new("pgrep")
            .args(["-x", "keymon"])
            .status()
            .is_ok_and(|status| status.success())
        {
            if matches!(action, Action::PowerPress) {
                self.flush_resume();
            }
            return;
        }
        match action {
            Action::LidClose => return self.doze(),'''

if original.count(before) != 1:
    raise RuntimeError(f"stock Slot power-action anchor count = {original.count(before)}")
changed = original.replace(before, after, 1)
diff = "".join(unified_diff(original.splitlines(keepends=True),
                            changed.splitlines(keepends=True),
                            fromfile="a/crates/slot/src/app.rs",
                            tofile="b/crates/slot/src/app.rs", n=4))
output.write_text("diff --git a/crates/slot/src/app.rs b/crates/slot/src/app.rs\n" + diff)
if sum(line.startswith("@@ ") for line in diff.splitlines()) != 1:
    raise RuntimeError("Expected exactly one code hunk")
print("Stock v0.3.0: fixed only OnionOS physical POWER ownership in app.rs")
