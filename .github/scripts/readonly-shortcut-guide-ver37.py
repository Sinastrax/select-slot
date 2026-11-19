#!/usr/bin/env python3
"""H700: document built-in input gestures on-device; DO NOT change input or bindings.

This is deliberately an interface-only addition. The original Actions,
input gesture state machine, settings formats and all configurable shortcuts
are untouched. The read-only rows have no Shortcut or GameButton binding.
"""
from pathlib import Path
import re

GROUPS = [
    ("FixedGlobal", "Global"),
    ("FixedGame", "In-Game"),
    ("FixedShelf", "Shelf"),
    ("FixedCollections", "Collections"),
    ("FixedStates", "Save States"),
]
# (Enum row name, left-hand action label, right-hand chord label)
ROWS = {
    "FixedGlobal": [
        ("FixVolumeUp", "Volume Up", "VOL+"),
        ("FixVolumeDown", "Volume Down", "VOL-"),
        ("FixMuteSelectUp", "Mute", "SEL+VOL+"),
        ("FixMuteSelectDown", "Mute", "SEL+VOL-"),
        ("FixMuteBoth", "Mute", "VOL+ & VOL-"),
        ("FixSleep", "Sleep / Wake", "POWER"),
        ("FixPowerOff", "Shut Down", "HOLD POWER"),
    ],
    "FixedGame": [
        ("FixGameMenu", "Game Menu", "MENU"),
        ("FixStateSwitcher", "Save Switcher", "2x MENU"),
        ("FixExit", "Return to Shelf", "HOLD MENU"),
        ("FixLink", "Link Play", "SEL+MENU"),
        ("FixFastLatch", "FF Lock", "2x FF KEY"),
        ("FixFastRelease", "FF Unlock", "FF KEY"),
        ("FixGbStretch", "GB/C Stretch", "L1"),
        ("FixGbOriginal", "GB/C Restore", "R1"),
    ],
    "FixedShelf": [
        ("FixFresh", "Start Fresh", "HOLD A"),
        ("FixMultiselect", "Multi-select", "HOLD SEL"),
        ("FixAddCollection", "Add to Collection", "HOLD Y"),
    ],
    "FixedCollections": [
        ("FixRemoveFromCollection", "Remove Game", "HOLD Y"),
        ("FixMoveInCollection", "Move Game", "X"),
        ("FixMoveCollection", "Move Collection", "HOLD X"),
    ],
    "FixedStates": [
        ("FixStatePrev", "Previous", "LEFT"),
        ("FixStateNext", "Next", "RIGHT"),
        ("FixStateLoad", "Load State", "A"),
        ("FixStateDelete", "Delete State", "Y"),
        ("FixStateUndo", "Undo", "X"),
        ("FixStateBack", "Back", "B"),
    ],
}
LEAVES = [entry for entries in ROWS.values() for entry in entries]
ALL_NEW = ["FixedShortcuts"] + [x for x, _ in GROUPS] + [x[0] for x in LEAVES]


def one(src, original, updated, name):
    n = src.count(original)
    if n != 1:
        raise SystemExit(f"{name}: expected one anchor, got {n}")
    return src.replace(original, updated, 1)


def one_pattern(src, pattern, replace, name):
    matches = list(re.finditer(pattern, src, re.S))
    if len(matches) != 1:
        raise SystemExit(f"{name}: expected one pattern, got {len(matches)}")
    match = matches[0]
    return src[:match.start()] + replace(match) + src[match.end():]


def edit(path, func):
    file = Path(path)
    before = file.read_text()
    after = func(before)
    if after == before:
        raise SystemExit(f"{path}: no change")
    file.write_text(after)


def ui(src):
    src = one_pattern(src, r"pub enum QuickRow \{.*?\n\}",
        lambda m: m[0][:-2] + "\n" +
        "".join(f"    {r},\n" for r in ALL_NEW) + "}", "enum QuickRow")

    def all_rows(m):
        old_count = int(m[1])
        old = m[0]
        insert = "".join(f"        QuickRow::{r},\n" for r in ALL_NEW)
        return old[:old.rfind("    ];")] + insert + old[old.rfind("    ];"):].replace(
            f"[QuickRow; {old_count} +", f"[QuickRow; {old_count + len(ALL_NEW)} +", 1
        ) if False else old.replace(
            f"[QuickRow; {old_count} +", f"[QuickRow; {old_count + len(ALL_NEW)} +", 1
        ).replace("    ];", insert + "    ];", 1)
    src = one_pattern(src,
        r"pub const ALL: \[QuickRow; (\d+) \+ cfg!\(feature = \"nds\"\) as usize\] = \[.*?\n    \];",
        all_rows, "all row index table")

    src = one(src, "pub const CONTROL_PAGES: [QuickRow; 4]",
              "pub const CONTROL_PAGES: [QuickRow; 5]", "Controls page count")
    src = one(src, "        QuickRow::ControlsInGame,\n    ];",
              "        QuickRow::ControlsInGame,\n        QuickRow::FixedShortcuts,\n    ];",
              "Controls entry")

    arrays = "    pub const FIXED_CATEGORIES: [QuickRow; 5] = [\n"
    arrays += "".join(f"        QuickRow::{group},\n" for group, _ in GROUPS)
    arrays += "    ];\n\n"
    for group, _ in GROUPS:
        rows = ROWS[group]
        arrays += f"    pub const {group.upper()}: [QuickRow; {len(rows)}] = [\n"
        arrays += "".join(f"        QuickRow::{r},\n" for r, _, _ in rows)
        arrays += "    ];\n\n"
    src = one(src, "    pub const SCREEN: [QuickRow; 4] = [",
              arrays + "    pub const SCREEN: [QuickRow; 4] = [", "fixed category pages")

    src = one(src,
              "            | QuickRow::ControlsInGame => &QuickRow::CONTROL_PAGES,",
              "            | QuickRow::ControlsInGame\n"
              "            | QuickRow::FixedShortcuts => &QuickRow::CONTROL_PAGES,\n"
              + "            " + " | ".join(f"QuickRow::{r}" for r, _ in GROUPS)
              + " => &QuickRow::FIXED_CATEGORIES,\n"
              + "".join(
                  "            " + " | ".join(f"QuickRow::{row}" for row, _, _ in ROWS[group])
                  + f" => &QuickRow::{group.upper()},\n"
                  for group, _ in GROUPS),
              "fixed menu page routing")

    src = one(src, "            QuickRow::ScSave => Some(QuickRow::Shortcuts),",
              "            QuickRow::ScSave => Some(QuickRow::Shortcuts),\n"
              "            QuickRow::FixedGlobal => Some(QuickRow::FixedShortcuts),\n"
              + "".join(
                  f"            QuickRow::{ROWS[g][0][0]} => Some(QuickRow::{g}),\n"
                  for g, _ in GROUPS)
              + "            QuickRow::FixedShortcuts => Some(QuickRow::Controls),",
              "fixed menu parent routing")
    src = one(src, "            &QuickRow::CONTROL_PAGES,",
              "            &QuickRow::CONTROL_PAGES,\n            &QuickRow::FIXED_CATEGORIES,",
              "categories align like other centered navigation pages")
    src = one(src, "            QuickRow::Shortcuts => Some(QuickRow::SHORTCUTS[0]),",
              "            QuickRow::Shortcuts => Some(QuickRow::SHORTCUTS[0]),\n"
              "            QuickRow::FixedShortcuts => Some(QuickRow::FIXED_CATEGORIES[0]),\n"
              + "".join(
                  f"            QuickRow::{g} => Some(QuickRow::{g.upper()}[0]),\n"
                  for g, _ in GROUPS),
              "read-only page navigation")
    src = one(src, '            QuickRow::Shortcuts => "Shortcuts",',
              '            QuickRow::Shortcuts => "Shortcuts",\n'
              '            QuickRow::FixedShortcuts => "Fixed Shortcuts",\n'
              + "".join(f'            QuickRow::{g} => "{label}",\n' for g, label in GROUPS)
              + "".join(f'            QuickRow::{r} => "{label}",\n' for r, label, _ in LEAVES),
              "visible action labels")

    src = one(src, "                | QuickRow::Shortcuts\n",
              "                | QuickRow::Shortcuts\n"
              "                | QuickRow::FixedShortcuts\n"
              + "".join(f"                | QuickRow::{g}\n" for g, _ in GROUPS),
              "read-only navigation rows are openable")

    src = one(src, "    pub fn binds(self) -> bool {",
              "    /// Physical gestures shown as a reference, never accepted by the editor.\n"
              "    pub fn fixed_keys(self) -> Option<&'static str> {\n"
              "        match self {\n"
              + "".join(f'            QuickRow::{r} => Some("{keys}"),\n' for r, _, keys in LEAVES)
              + "            _ => None,\n"
              "        }\n"
              "    }\n\n"
              "    pub fn binds(self) -> bool {",
              "fixed buttons are presentation-only")
    src = one(src, "                _ if row.binds() => self",
              "                // Read-only values reuse the existing text-face cache but\n"
              "                // deliberately have no Shortcut or binding API.\n"
              "                _ if row.fixed_keys().is_some() => self\n"
              "                    .bound\n"
              "                    .and_then(|b| b.get(row.index()).copied().flatten())\n"
              "                    .map(|c| c[lit as usize]),\n"
              "                _ if row.binds() => self",
              "fixed shortcut right-hand values")
    # All pages already scroll via the verified common viewport renderer.

    src += """
#[cfg(test)]
mod fixed_shortcut_reference_tests {
    use super::{QuickRow, Canvas, quick_window};
    #[test]
    fn every_fixed_shortcut_is_read_only_and_has_its_own_menu_route() {
        for row in QuickRow::ALL {
            if let Some(keys) = row.fixed_keys() {
                assert!(!keys.is_empty());
                assert!(!row.binds(), "{row:?} can accidentally be rebound");
                assert!(row.shortcut().is_none());
                assert!(row.game_button().is_none());
                assert!(row.parent().is_some());
                assert!(row.page().contains(&row));
            }
        }
        assert_eq!(QuickRow::FixedShortcuts.parent(), Some(QuickRow::Controls));
        assert_eq!(QuickRow::FixedGlobal.parent(), Some(QuickRow::FixedShortcuts));
        assert_eq!(QuickRow::FixMuteSelectUp.parent(), Some(QuickRow::FixedGlobal));
        assert_eq!(QuickRow::FixLink.parent(), Some(QuickRow::FixedGame));
    }

    #[test]
    fn long_read_only_pages_scroll_within_the_same_viewport_as_shortcuts() {
        for row in [QuickRow::FixPowerOff, QuickRow::FixGbOriginal] {
            let count = row.page().len();
            let (first, displayed) = quick_window(Canvas::FRAMED, row, &[]);
            assert!(count > displayed, "page should be scrolling: {row:?}");
            assert!(first > 0, "end-of-page row must be reachable: {row:?}");
        }
    }
}
"""
    return src


def app(src):
    # Main-menu exhaustiveness: this app holds three large match statements
    # for row value, activation and left/right adjustment. Fixed leaves are
    # handled as inert, not bound or mutable, rows in all three.
    rows = [r for r, _, _ in LEAVES]
    pattern = "            | QuickRow::ScGuide\n"
    count = src.count(pattern)
    if count != 3:
        raise SystemExit(f"app exhaustive row groups: expected 3, got {count}")
    src = src.replace(pattern, pattern + "".join(f"            | QuickRow::{r}\n" for r in rows))

    # For the value match and the change-setting match, FixedShortcuts and the
    # category rows behave like informational entries. The open-row match
    # instead enters a child page when A is pressed.
    qv_start = src.index("    pub fn quick_value(&self, row: QuickRow)")
    qv_end = src.index("    pub fn set_quick_menu_faces(", qv_start)
    qv = src[qv_start:qv_end]
    qv = one(qv, "            | QuickRow::ScGuide\n",
        "            | QuickRow::ScGuide\n"
        "            | QuickRow::FixedShortcuts\n"
        + "".join(f"            | QuickRow::{g}\n" for g, _ in GROUPS),
        "no value for guide pages")
    src = src[:qv_start] + qv + src[qv_end:]

    open_start = src.index("    fn open_quick_row(&mut self, row: QuickRow)")
    open_end = src.index("    fn change_setting(&mut self, row: QuickRow", open_start)
    part = src[open_start:open_end]
    part = one(part, "            | QuickRow::Shortcuts\n",
        "            | QuickRow::Shortcuts\n"
        "            | QuickRow::FixedShortcuts\n"
        + "".join(f"            | QuickRow::{g}\n" for g, _ in GROUPS),
        "A opens built-in guide/category")
    src = src[:open_start] + part + src[open_end:]

    change_start = src.index("    fn change_setting(&mut self, row: QuickRow")
    change_end = src.index("    pub fn apply_at(&mut self", change_start)
    part = src[change_start:change_end]
    part = one(part, "            | QuickRow::ScGuide\n",
        "            | QuickRow::ScGuide\n"
        "            | QuickRow::FixedShortcuts\n"
        + "".join(f"            | QuickRow::{g}\n" for g, _ in GROUPS),
        "no left/right setting mutation for guide pages")
    src = src[:change_start] + part + src[change_end:]

    # Values are generated by the same cached text renderer as assigned
    # keys, but never pass through the capture/reset/editor pipeline.
    src = one(src,
        """            .filter(|r| r.binds())
            .map(|r| self.bound_text(*r))""",
        """            .filter(|r| r.binds() || r.fixed_keys().is_some())
            .map(|r| match r.fixed_keys() {
                Some(keys) => keys.to_string(),
                None => self.bound_text(*r),
            })""",
        "render physical button labels for readonly shortcut rows")
    src = one(src,
        """                if !r.binds() {
                    return None;
                }
                let text = match self.capture_row() == Some(*r) {""",
        """                if let Some(keys) = r.fixed_keys() {
                    return self.binding_faces.get(keys).copied();
                }
                if !r.binds() {
                    return None;
                }
                let text = match self.capture_row() == Some(*r) {""",
        "lookup fixed gesture faces without a binding")
    return src


edit("crates/slot-ui/src/quick_menu.rs", ui)
edit("crates/slot/src/app.rs", app)
print("Added only fixed-shortcut reference pages: no gestures, remapping or settings changed.")
