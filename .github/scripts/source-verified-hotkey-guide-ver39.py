#!/usr/bin/env python3
"""Ver.39: source-audited, read-only H700 shortcut reference.

Input handling and all user controls remain unchanged. This patch edits only
the QuickRow information pages and their display-only binding text in App.
Anchors deliberately fail closed if upstream/source layout drifts.
"""
from pathlib import Path
import re

# Additional informational-only rows, never registered as editable bindings.
NEW = [
    "FixedRecovery",
    "FixFastUnlatch",
    "FixFastToggle",
    "FixStudio",
    "FixCorePicker",
    "FixRepair",
    "FixAboutRestart",
    "FixKidUnlock",
    "FixKidExit",
]
LABELS = {
    "FixedRecovery": "Recovery / Kid Mode",
    "FixFastUnlatch": "Stop Fast-Forward Lock",
    "FixFastToggle": "Fast-Forward Toggle",
    "FixStudio": "Open Cart Studio",
    "FixCorePicker": "Choose Emulator",
    "FixRepair": "Repair SD (if offered)",
    "FixAboutRestart": "Restart (About only)",
    "FixKidUnlock": "Unlock Kid Mode (boot)",
    "FixKidExit": "Kid Mode: Exit Game",
}
KEYS = {
    "FixFastUnlatch": "TAP FAST-FORWARD",
    "FixFastToggle": "NOT ASSIGNED",
    "FixStudio": "TAP SELECT",
    "FixCorePicker": "START",
    "FixRepair": "SELECT + START",
    "FixAboutRestart": "SELECT + START",
    "FixKidUnlock": "START+SELECT+L2+R2",
    "FixKidExit": "TAP MENU",
}
# Ver.38 source strings -> verified non-misleading reference text.
UPDATED = [
    ("FixGameMenu", "Game Menu", "Game Menu", "MENU", "TAP MENU"),
    ("FixStateSwitcher", "Screenshots / States", "Save States (if saved)", "PRESS MENU TWICE", "TAP MENU TWICE"),
    ("FixExit", "Return to Shelf", "Exit (if multiple games)", "HOLD MENU", "HOLD MENU"),
    ("FixLink", "Link Play", "Link Play (if supported)", "SELECT + MENU", "SELECT + MENU"),
    ("FixFastRelease", "Stop Fast-Forward", "Hold Fast-Forward", "FAST-FORWARD", "HOLD FAST-FORWARD"),
    ("FixGbStretch", "Stretch Game Boy / Color", "Stretch Game Boy/Color", "L1", "L1 (IF FREE)"),
    ("FixGbOriginal", "Restore Game Boy / Color", "Normal Game Boy/Color", "R1", "R1 (IF FREE)"),
    ("FixAddCollection", "Add to Collection", "Add to Collection", "HOLD Y", "HOLD FAVORITE KEY"),
    ("FixRemoveFromCollection", "Remove from Collection", "Remove from Collection", "HOLD Y", "HOLD FAVORITE KEY"),
    ("FixMoveInCollection", "Move Game", "Move Game", "X", "REMOVE RECENT KEY"),
    ("FixMoveCollection", "Move Collection", "Reorder Collection", "HOLD X", "HOLD REMOVE RECENT"),
]

def once(src, old, new, note):
    count = src.count(old)
    if count != 1:
        raise SystemExit(f"{note}: expected exactly one anchor, got {count}")
    return src.replace(old, new, 1)

def scoped(src, start, end, fn, note):
    a = src.find(start)
    if a < 0:
        raise SystemExit(f"{note}: start anchor missing")
    b = src.find(end, a)
    if b < 0:
        raise SystemExit(f"{note}: end anchor missing")
    return src[:a] + fn(src[a:b]) + src[b:]

def edit(path, fn):
    file = Path(path)
    src = file.read_text()
    changed = fn(src)
    if changed == src:
        raise SystemExit(f"{path}: no changes")
    file.write_text(changed)

def ui(src):
    # The guide includes read-only explanations of some *editable* keys.
    # Call it a guide rather than implying every listed shortcut is fixed.
    src = once(src, 'QuickRow::FixedShortcuts => "Fixed Shortcuts",',
               'QuickRow::FixedShortcuts => "Hotkey Guide",',
               "accurate read-only menu title")
    src = once(src, "    FixStateBack,\n}", "    FixStateBack,\n"
               + "".join(f"    {row},\n" for row in NEW) + "}", "QuickRow enum")

    def add_to_all(chunk):
        m = re.search(r"(pub const ALL: \[QuickRow; )(\d+)( \+ cfg!\(feature = \"nds\"\) as usize\])", chunk)
        if not m:
            raise SystemExit("QuickRow ALL count not found")
        chunk = chunk[:m.start(2)] + str(int(m[2]) + len(NEW)) + chunk[m.end(2):]
        return once(chunk, "        QuickRow::FixStateBack,\n    ];",
                    "        QuickRow::FixStateBack,\n"
                    + "".join(f"        QuickRow::{row},\n" for row in NEW)
                    + "    ];", "QuickRow ALL content")
    src = scoped(src, "    pub const ALL: [QuickRow;", "    pub const MAIN:", add_to_all, "ALL rows")

    src = once(src, "pub const FIXED_CATEGORIES: [QuickRow; 5]",
               "pub const FIXED_CATEGORIES: [QuickRow; 6]", "category length")
    src = once(src, "        QuickRow::FixedStates,\n    ];",
               "        QuickRow::FixedStates,\n        QuickRow::FixedRecovery,\n    ];",
               "add recovery category")
    src = once(src, "pub const FIXEDGAME: [QuickRow; 8]",
               "pub const FIXEDGAME: [QuickRow; 10]", "in-game guide length")
    src = once(src, "        QuickRow::FixGbOriginal,\n    ];",
               "        QuickRow::FixGbOriginal,\n"
               "        QuickRow::FixFastUnlatch,\n"
               "        QuickRow::FixFastToggle,\n    ];", "new fast-forward guide rows")
    src = once(src, "pub const FIXEDSHELF: [QuickRow; 3]",
               "pub const FIXEDSHELF: [QuickRow; 5]", "shelf guide length")
    src = once(src, "        QuickRow::FixAddCollection,\n    ];",
               "        QuickRow::FixAddCollection,\n"
               "        QuickRow::FixStudio,\n"
               "        QuickRow::FixCorePicker,\n    ];", "shelf guide rows")
    src = once(src, "    pub const SCREEN: [QuickRow; 4] = [",
               """    pub const FIXEDRECOVERY: [QuickRow; 4] = [
        QuickRow::FixRepair,
        QuickRow::FixAboutRestart,
        QuickRow::FixKidUnlock,
        QuickRow::FixKidExit,
    ];

    pub const SCREEN: [QuickRow; 4] = [""", "recovery page")

    src = once(src, "QuickRow::FixedStates => &QuickRow::FIXED_CATEGORIES,",
               "QuickRow::FixedStates | QuickRow::FixedRecovery => &QuickRow::FIXED_CATEGORIES,",
               "recovery page routing")
    src = once(src, "QuickRow::FixGbOriginal => &QuickRow::FIXEDGAME,",
               "QuickRow::FixGbOriginal | QuickRow::FixFastUnlatch | QuickRow::FixFastToggle => &QuickRow::FIXEDGAME,",
               "fast forward routing")
    src = once(src, "QuickRow::FixAddCollection => &QuickRow::FIXEDSHELF,",
               "QuickRow::FixAddCollection | QuickRow::FixStudio | QuickRow::FixCorePicker => &QuickRow::FIXEDSHELF,",
               "shelf routing")
    src = once(src, "QuickRow::FixStateBack => &QuickRow::FIXEDSTATES,",
               "QuickRow::FixStateBack => &QuickRow::FIXEDSTATES,\n"
               "            QuickRow::FixRepair | QuickRow::FixAboutRestart | QuickRow::FixKidUnlock | QuickRow::FixKidExit => &QuickRow::FIXEDRECOVERY,",
               "recovery leaf routing")
    src = once(src, "            QuickRow::FixStatePrev => Some(QuickRow::FixedStates),",
               "            QuickRow::FixStatePrev => Some(QuickRow::FixedStates),\n"
               "            QuickRow::FixRepair => Some(QuickRow::FixedRecovery),",
               "recovery back navigation")
    src = once(src, "            QuickRow::FixedStates => Some(QuickRow::FIXEDSTATES[0]),",
               "            QuickRow::FixedStates => Some(QuickRow::FIXEDSTATES[0]),\n"
               "            QuickRow::FixedRecovery => Some(QuickRow::FIXEDRECOVERY[0]),",
               "recovery open navigation")
    src = once(src, "                | QuickRow::FixedStates\n",
               "                | QuickRow::FixedStates\n"
               "                | QuickRow::FixedRecovery\n", "recovery is openable")
    src = once(src, '            QuickRow::FixStateBack => "Back",',
               '            QuickRow::FixStateBack => "Back",\n'
               + "".join(f'            QuickRow::{row} => "{LABELS[row]}",\n' for row in NEW),
               "new row names")
    src = once(src, '            QuickRow::FixStateBack => Some("B"),',
               '            QuickRow::FixStateBack => Some("B"),\n'
               + "".join(f'            QuickRow::{row} => Some("{KEYS[row]}"),\n' for row in KEYS),
               "new key legends")
    for row, old_label, new_label, old_key, new_key in UPDATED:
        if old_label != new_label:
            src = once(src, f'QuickRow::{row} => "{old_label}",',
                       f'QuickRow::{row} => "{new_label}",', f"{row} action")
        if old_key != new_key:
            src = once(src, f'QuickRow::{row} => Some("{old_key}"),',
                       f'QuickRow::{row} => Some("{new_key}"),', f"{row} legend")

    src += r"""

#[cfg(test)]
mod source_verified_hotkey_guide_tests {
    use super::QuickRow;

    #[test]
    fn every_informational_shortcut_is_never_user_editable() {
        for row in QuickRow::ALL {
            if row.fixed_keys().is_some() {
                assert!(!row.binds(), "{row:?} accidentally editable");
                assert!(row.game_button().is_none());
                assert!(row.shortcut().is_none());
                assert!(row.carousel_action().is_none());
                assert!(!row.fixed_keys().unwrap().is_empty());
                assert!(row.page().contains(&row));
                assert!(row.parent().is_some());
            }
        }
    }

    #[test]
    fn recoveries_and_contextual_controls_are_reachable() {
        assert!(QuickRow::FIXED_CATEGORIES.contains(&QuickRow::FixedRecovery));
        assert_eq!(QuickRow::FixedRecovery.parent(), Some(QuickRow::FixedShortcuts));
        assert_eq!(QuickRow::FixRepair.parent(), Some(QuickRow::FixedRecovery));
        assert_eq!(QuickRow::FixStudio.parent(), Some(QuickRow::FixedShelf));
        assert_eq!(QuickRow::FixFastToggle.parent(), Some(QuickRow::FixedGame));
        assert!(QuickRow::FixedRecovery.opens());
        assert!(QuickRow::FIXEDGAME.len() > 6);
    }

    #[test]
    fn physical_shortcuts_do_not_claim_the_wrong_feature() {
        assert_eq!(QuickRow::FixStateSwitcher.label(), "Save States (if saved)");
        assert_eq!(QuickRow::FixAboutRestart.fixed_keys(), Some("SELECT + START"));
        assert_eq!(QuickRow::FixRepair.fixed_keys(), Some("SELECT + START"));
        assert!(QuickRow::FixGbStretch.fixed_keys().unwrap().contains("IF FREE"));
    }
}
"""
    return src

def app(src):
    # The three existing QuickRow exhaustive matches already contain the
    # original Fixed Shortcuts leaves and categories from Ver.37.
    leaf = "            | QuickRow::FixStateBack\n"
    if src.count(leaf) != 3:
        raise SystemExit(f"App read-only leaf matches: expected three, found {src.count(leaf)}")
    src = src.replace(leaf, leaf + "".join(f"            | QuickRow::{row}\n" for row in NEW[1:]))
    group = "            | QuickRow::FixedStates\n"
    if src.count(group) != 3:
        raise SystemExit(f"App guide group matches: expected three, found {src.count(group)}")
    src = src.replace(group, group + "            | QuickRow::FixedRecovery\n")

    def guide_value(s):
        old = """            QuickRow::FixFastRelease => Some(fixed_fast_forward_text(
                self.shortcuts.get(slot_store::Shortcut::FastForward), false)),
            _ => row.fixed_keys().map(str::to_owned),"""
        new = """            QuickRow::FixFastRelease => Some(fixed_key_with_prefix(
                self.shortcuts.get(slot_store::Shortcut::FastForward), "HOLD ")),
            QuickRow::FixFastUnlatch => Some(fixed_key_with_prefix(
                self.shortcuts.get(slot_store::Shortcut::FastForward), "TAP ")),
            QuickRow::FixFastToggle => Some(fixed_key_with_prefix(
                self.shortcuts.get(slot_store::Shortcut::FastForwardToggle), "PRESS ")),
            QuickRow::FixAddCollection | QuickRow::FixRemoveFromCollection => Some(
                fixed_holdable_shelf_key(self.carousel.get(slot_store::CarouselAction::Favorite))),
            QuickRow::FixMoveCollection => Some(fixed_holdable_shelf_key(
                self.carousel.get(slot_store::CarouselAction::ForgetRecent))),
            QuickRow::FixMoveInCollection => Some(fixed_fast_forward_text(
                self.carousel.get(slot_store::CarouselAction::ForgetRecent), false)),
            _ => row.fixed_keys().map(str::to_owned),"""
        return once(s, old, new, "resolve current user bindings")
    src = scoped(src, "    fn fixed_reference_text(", "    pub fn binding_texts(", guide_value,
                 "only modify read-only value formatter")

    src += r"""

/// Display helpers for the read-only reference menu. Never used by input.
fn fixed_key_with_prefix(binding: Option<Binding>, prefix: &str) -> String {
    let Some(binding) = binding else {
        return "NOT ASSIGNED".to_owned();
    };
    format!("{prefix}{}", fixed_fast_forward_text(Some(binding), false))
}

/// Hold gestures only arise for *plain* shelf bindings. Chords still work
/// for ordinary shelf actions, but do not trigger FavoriteHold or
/// ForgetRecentHold in the upstream gesture state machine.
fn fixed_holdable_shelf_key(binding: Option<Binding>) -> String {
    match binding {
        None => "NOT ASSIGNED".to_owned(),
        Some(Binding { modifier: Some(_), .. }) => "SINGLE KEY ONLY".to_owned(),
        Some(binding) => fixed_key_with_prefix(Some(binding), "HOLD "),
    }
}

#[cfg(test)]
mod source_verified_hotkey_guide_display_tests {
    use super::*;

    #[test]
    fn display_uses_effective_fast_forward_and_shelf_buttons() {
        let plain = Some(Binding { modifier: None, button: Device::R2 });
        assert_eq!(fixed_key_with_prefix(plain, "HOLD "), "HOLD R2");
        assert_eq!(fixed_key_with_prefix(plain, "TAP "), "TAP R2");
        assert_eq!(fixed_key_with_prefix(None, "TAP "), "NOT ASSIGNED");

        let custom = Some(Binding { modifier: None, button: Device::L1 });
        assert_eq!(fixed_holdable_shelf_key(custom), "HOLD L1");
        assert_eq!(fixed_holdable_shelf_key(None), "NOT ASSIGNED");
        let chord = Some(Binding {
            modifier: Some(Modifier::Select),
            button: Device::A,
        });
        assert_eq!(fixed_holdable_shelf_key(chord), "SINGLE KEY ONLY");
        assert_eq!(fixed_key_with_prefix(chord, "PRESS "), "PRESS SELECT + A");
    }
}
"""
    return src

edit("crates/slot-ui/src/quick_menu.rs", ui)
edit("crates/slot/src/app.rs", app)
print("Ver39 source-verified read-only shortcut reference applied.")
