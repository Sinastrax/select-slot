#!/usr/bin/env python3
"""Ver.38: clearer text in the *read-only* H700 fixed-shortcut guide.

No input engine, binding formats, shortcut behavior, gameplay, emulators, or
save files are modified. Active Fast-Forward bindings are rendered only as
text, so the user never sees an ambiguous "FF KEY" placeholder.
"""
from pathlib import Path

# (enum row, old label, new label, old key text, new key text)
CHANGES = [
    ("FixVolumeUp", "Volume Up", "Increase Volume", "VOL+", "VOLUME UP"),
    ("FixVolumeDown", "Volume Down", "Decrease Volume", "VOL-", "VOLUME DOWN"),
    ("FixMuteSelectUp", "Mute", "Mute", "SEL+VOL+", "SELECT + VOLUME UP"),
    ("FixMuteSelectDown", "Mute", "Mute", "SEL+VOL-", "SELECT + VOLUME DOWN"),
    ("FixMuteBoth", "Mute", "Mute", "VOL+ & VOL-", "PRESS BOTH VOLUME BUTTONS"),
    ("FixSleep", "Sleep / Wake", "Sleep / Wake", "POWER", "POWER"),
    ("FixPowerOff", "Shut Down", "Shut Down", "HOLD POWER", "HOLD POWER"),
    ("FixGameMenu", "Game Menu", "Game Menu", "MENU", "MENU"),
    ("FixStateSwitcher", "Save Switcher", "Screenshots / States", "2x MENU", "PRESS MENU TWICE"),
    ("FixExit", "Return to Shelf", "Return to Shelf", "HOLD MENU", "HOLD MENU"),
    ("FixLink", "Link Play", "Link Play", "SEL+MENU", "SELECT + MENU"),
    ("FixFastLatch", "FF Lock", "Lock Fast-Forward", "2x FF KEY", "FAST-FORWARD TWICE"),
    ("FixFastRelease", "FF Unlock", "Stop Fast-Forward", "FF KEY", "FAST-FORWARD"),
    ("FixGbStretch", "GB/C Stretch", "Stretch Game Boy / Color", "L1", "L1"),
    ("FixGbOriginal", "GB/C Restore", "Restore Game Boy / Color", "R1", "R1"),
    ("FixFresh", "Start Fresh", "Start Fresh", "HOLD A", "HOLD A"),
    ("FixMultiselect", "Multi-select", "Multi-select", "HOLD SEL", "HOLD SELECT"),
    ("FixAddCollection", "Add to Collection", "Add to Collection", "HOLD Y", "HOLD Y"),
    ("FixRemoveFromCollection", "Remove Game", "Remove from Collection", "HOLD Y", "HOLD Y"),
    ("FixMoveInCollection", "Move Game", "Move Game", "X", "X"),
    ("FixMoveCollection", "Move Collection", "Move Collection", "HOLD X", "HOLD X"),
    ("FixStatePrev", "Previous", "Previous State", "LEFT", "LEFT"),
    ("FixStateNext", "Next", "Next State", "RIGHT", "RIGHT"),
    ("FixStateLoad", "Load State", "Load State", "A", "A"),
    ("FixStateDelete", "Delete State", "Delete State", "Y", "Y"),
    ("FixStateUndo", "Undo", "Undo", "X", "X"),
    ("FixStateBack", "Back", "Back", "B", "B"),
]


def one(source, old, new, description):
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{description}: expected 1 unique anchor, found {count}")
    return source.replace(old, new, 1)


ui = Path("crates/slot-ui/src/quick_menu.rs")
source = ui.read_text()
for row, old_label, new_label, old_value, new_value in CHANGES:
    if old_label != new_label:
        source = one(source, f'QuickRow::{row} => "{old_label}",',
            f'QuickRow::{row} => "{new_label}",', f"{row} label")
    if old_value != new_value:
        source = one(source, f'QuickRow::{row} => Some("{old_value}"),',
            f'QuickRow::{row} => Some("{new_value}"),', f"{row} value")
source += r"""

#[cfg(test)]
mod fixed_reference_plain_language_tests {
    use super::QuickRow;

    #[test]
    fn the_fixed_guide_avoids_unexplained_key_abbreviations() {
        for row in QuickRow::ALL {
            let label = row.label();
            let Some(value) = row.fixed_keys() else { continue };
            for unclear in ["SEL+", "HOLD SEL", "VOL+", "VOL-", "2x", "FF KEY", "GB/C"] {
                assert!(!value.contains(unclear), "{row:?} has unclear value {value}");
                assert!(!label.contains(unclear), "{row:?} has unclear label {label}");
            }
        }
        assert_eq!(QuickRow::FixMuteSelectUp.fixed_keys(), Some("SELECT + VOLUME UP"));
        assert_eq!(QuickRow::FixMuteBoth.fixed_keys(), Some("PRESS BOTH VOLUME BUTTONS"));
        assert_eq!(QuickRow::FixStateSwitcher.fixed_keys(), Some("PRESS MENU TWICE"));
    }
}
"""
ui.write_text(source)

app = Path("crates/slot/src/app.rs")
source = app.read_text()
source = one(source,
    "    pub fn binding_texts(&self) -> Vec<String> {",
    """    /// Fixed-reference values are presentation-only, not configurable actions.
    /// Fast Forward is unique: its shortcut *is* configurable, so reflect the
    /// user's existing assignment without touching the actual binding.
    fn fixed_reference_text(&self, row: QuickRow) -> Option<String> {
        match row {
            QuickRow::FixFastLatch => Some(fixed_fast_forward_text(
                self.shortcuts.get(slot_store::Shortcut::FastForward), true)),
            QuickRow::FixFastRelease => Some(fixed_fast_forward_text(
                self.shortcuts.get(slot_store::Shortcut::FastForward), false)),
            _ => row.fixed_keys().map(str::to_owned),
        }
    }

    pub fn binding_texts(&self) -> Vec<String> {""",
    "add display-only reference formatting")
source = one(source,
    """            .map(|r| match r.fixed_keys() {
                Some(keys) => keys.to_string(),
                None => self.bound_text(*r),
            })""",
    """            .map(|r| match self.fixed_reference_text(*r) {
                Some(keys) => keys,
                None => self.bound_text(*r),
            })""",
    "generate rendered faces for the assigned Fast-Forward button")
source = one(source,
    """                if let Some(keys) = r.fixed_keys() {
                    return self.binding_faces.get(keys).copied();
                }""",
    """                if let Some(keys) = self.fixed_reference_text(*r) {
                    return self.binding_faces.get(&keys).copied();
                }""",
    "use matching current reference value texture")

source += r"""

/// Only used by the informational fixed-shortcut guide; does not affect input.
fn fixed_fast_forward_text(binding: Option<Binding>, twice: bool) -> String {
    let Some(binding) = binding else {
        return "NOT ASSIGNED".to_owned();
    };
    let key = Binding::text(Some(binding));
    let key = if let Some(b) = key.strip_prefix("SEL+") {
        format!("SELECT + {b}")
    } else if let Some(b) = key.strip_prefix("MENU+") {
        format!("MENU + {b}")
    } else {
        key.replace('+', " + ")
    };
    if twice { format!("{key} TWICE") } else { key }
}

#[cfg(test)]
mod fixed_fast_forward_reference_tests {
    use super::*;
    #[test]
    fn current_mapping_is_explained_without_changing_its_binding() {
        let base = Some(Binding { modifier: None, button: Device::R2 });
        assert_eq!(fixed_fast_forward_text(base, true), "R2 TWICE");
        assert_eq!(fixed_fast_forward_text(base, false), "R2");
        assert_eq!(fixed_fast_forward_text(None, true), "NOT ASSIGNED");
        let custom = Some(Binding { modifier: Some(Modifier::Select), button: Device::L1 });
        assert_eq!(fixed_fast_forward_text(custom, true), "SELECT + L1 TWICE");
        assert_eq!(fixed_fast_forward_text(custom, false), "SELECT + L1");
    }
}
"""
app.write_text(source)
print("Clear fixed-shortcut guide labels and current FF key are now rendered as read-only text.")
