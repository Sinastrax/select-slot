#!/usr/bin/env python3
"""H700 keyboard: Shift once = next character; twice = Caps Lock; third = off.

Applies to the shared on-screen keyboard (including RetroAchievements login).
Preserves Host shifted digits and symbol mode, password masking, all mappings,
and the separate Miyoo build, whose pinned Slot 1.8.1 has no keyboard module.
"""
from pathlib import Path

PATH = Path("crates/slot-ui/src/keyboard.rs")

def replace_once(s, before, after, label):
    count = s.count(before)
    if count != 1:
        raise SystemExit(f"keyboard Shift patch: {label}: expected 1 match, got {count}")
    return s.replace(before, after, 1)

source = PATH.read_text()
s = source
s = replace_once(s,
    "    shift: bool,\n    symbols: bool,",
    "    shift: bool, // One character only.\n    caps_lock: bool, // Persistent until Shift is pressed again.\n    symbols: bool,",
    "keyboard state")
s = replace_once(s,
    "            shift: false,\n            symbols: false,",
    "            shift: false,\n            caps_lock: false,\n            symbols: false,",
    "keyboard initialization")
s = replace_once(s,
    "    pub fn shift(&self) -> bool {\n        self.shift\n    }",
    """    pub fn shift(&self) -> bool {
        self.shift || self.caps_lock
    }

    pub fn caps_locked(&self) -> bool {
        self.caps_lock
    }

    // The on-screen Shift cap and SELECT share the same deterministic cycle.
    fn cycle_shift(&mut self) {
        if self.caps_lock {
            self.caps_lock = false;
        } else if self.shift {
            self.shift = false;
            self.caps_lock = true;
        } else {
            self.shift = true;
        }
    }""",
    "shift state helpers")
s = replace_once(s,
    """    fn insert(&mut self, c: char) -> Typed {
        self.text.insert(self.cursor, c);
        self.cursor += 1;
        Typed::Changed
    }""",
    """    fn insert(&mut self, c: char) -> Typed {
        self.text.insert(self.cursor, c);
        self.cursor += 1;
        // Shift is one-shot, not sticky. Caps Lock is independent.
        self.shift = false;
        Typed::Changed
    }""",
    "consume one-shot on insertion")
s = replace_once(s,
    """        } else if self.shift {
            nth(UPPER, i)
        } else {
            nth(LOWER, i)
        }""",
    """        } else if self.shift || self.caps_lock {
            nth(UPPER, i)
        } else {
            nth(LOWER, i)
        }""",
    "uppercase letter mode")
# Preserve original symbol and Host digit Shift behavior only for a one-shot
# Shift. Caps Lock is letter-only, so the numeric row stays 1234567890.
s = replace_once(s,
    """                Cap::Special(Shift) => {
                    self.shift = !self.shift;
                    Typed::Changed
                }""",
    """                Cap::Special(Shift) => {
                    self.cycle_shift();
                    Typed::Changed
                }""",
    "on-screen Shift key")
s = replace_once(s,
    """            Btn::Select if general => {
                self.shift = !self.shift;
                Typed::Changed
            }""",
    """            Btn::Select if general => {
                self.cycle_shift();
                Typed::Changed
            }""",
    "SELECT Shift shortcut")
s = replace_once(s,
    '            Shortcut::Shift => "Shift",',
    '            Shortcut::Shift => "Shift x2 = Caps",',
    "on-screen keyboard help")
s = replace_once(s,
    """    let (fill, ink) = match chosen {
        true => (CHOSEN, CHOSEN_INK),
        false => (TILE, MENU_INK),
    };
    let mut rgba = tile(w, h, fill);
    match cap_icon(cap).and_then(|i| icon_coverage(i, ICON_PX)) {""",
    """    let locked = cap == Cap::Special(Shift) && kb.caps_locked();
    let (fill, ink) = match chosen || (cap == Cap::Special(Shift) && kb.shift()) {
        true => (CHOSEN, CHOSEN_INK),
        false => (TILE, MENU_INK),
    };
    let mut rgba = tile(w, h, fill);
    // Persistent Caps Lock is visibly labeled, unlike temporary Shift.
    let icon = if locked { None } else { cap_icon(cap) };
    match icon.and_then(|i| icon_coverage(i, ICON_PX)) {""",
    "Caps Lock key highlight")
s = replace_once(s,
    """            let label = kb.label(cap);
            let px = match label.chars().count() {""",
    """            let label = if locked { "CAPS".to_string() } else { kb.label(cap) };
            let px = match label.chars().count() {""",
    "Caps Lock key label")
if "mod select_keyboard_shift_tests" in s:
    raise SystemExit("keyboard Shift test module already exists")
s += r'''

#[cfg(test)]
mod select_keyboard_shift_tests {
    use super::*;

    fn keyboard(layout: Layout) -> Keyboard {
        Keyboard::new(layout, "Test", None, "")
    }

    fn key(kb: &mut Keyboard, row: usize, col: usize) -> Typed {
        kb.row = row;
        kb.col = col;
        kb.press(Btn::A)
    }

    #[test]
    fn one_shot_shift_uses_white_arrow_until_character_entry() {
        for layout in [Layout::General, Layout::Host] {
            let mut kb = keyboard(layout);
            let face = |kb: &Keyboard, chosen| cap_face(kb, Cap::Special(Shift), chosen, KEY_W).rgba;
            let idle = face(&kb, false);
            let white_arrow = face(&kb, true);
            assert!(idle != white_arrow);
            kb.press(Btn::Select);
            assert!(face(&kb, false) == white_arrow);
            key(&mut kb, 1, 0);
            assert!(face(&kb, false) == idle);
        }
    }

    #[test]
    fn select_one_shot_uppercase_then_lowercase() {
        let mut kb = keyboard(Layout::General);
        assert_eq!(kb.press(Btn::Select), Typed::Changed);
        assert!(kb.shift());
        assert!(!kb.caps_locked());
        assert_eq!(key(&mut kb, 1, 0), Typed::Changed);
        assert_eq!(kb.text(), "Q");
        assert!(!kb.shift());
        key(&mut kb, 1, 0);
        assert_eq!(kb.text(), "Qq");
    }

    #[test]
    fn two_shift_presses_lock_caps_and_third_turns_it_off() {
        let mut kb = keyboard(Layout::General);
        // Use physical A on the keyboard Shift cap, then SELECT to turn it off.
        assert_eq!(key(&mut kb, 3, 0), Typed::Changed);
        assert_eq!(key(&mut kb, 3, 0), Typed::Changed);
        assert!(kb.caps_locked());
        assert!(kb.shift());
        key(&mut kb, 1, 0);
        key(&mut kb, 1, 0);
        assert_eq!(kb.text(), "QQ");
        assert!(kb.caps_locked());
        kb.press(Btn::Select);
        assert!(!kb.caps_locked());
        assert!(!kb.shift());
        key(&mut kb, 1, 0);
        assert_eq!(kb.text(), "QQq");
    }

    #[test]
    fn keyboard_shift_and_select_share_one_state_machine() {
        let mut kb = keyboard(Layout::General);
        key(&mut kb, 3, 0);
        kb.press(Btn::Select);
        assert!(kb.caps_locked());
        key(&mut kb, 3, 0);
        assert!(!kb.shift());
        kb.press(Btn::Select);
        key(&mut kb, 1, 0);
        assert_eq!(kb.text(), "Q");
        assert!(!kb.shift());
    }

    #[test]
    fn delete_navigation_and_help_do_not_consume_one_shot() {
        let mut kb = keyboard(Layout::General);
        kb.press(Btn::Select);
        kb.press(Btn::B);
        kb.press(Btn::Left);
        kb.press(Btn::Menu);
        kb.press(Btn::B);
        assert!(kb.shift());
        key(&mut kb, 1, 0);
        assert_eq!(kb.text(), "Q");
        assert!(!kb.shift());
    }

    #[test]
    fn typing_space_consumes_temporary_shift() {
        let mut kb = keyboard(Layout::General);
        kb.press(Btn::Select);
        kb.press(Btn::X);
        assert_eq!(kb.text(), " ");
        assert!(!kb.shift());
        key(&mut kb, 1, 0);
        assert_eq!(kb.text(), " q");
    }

    #[test]
    fn caps_lock_keeps_numbers_unshifted_but_shift_once_maps_symbols() {
        let mut kb = keyboard(Layout::General);
        kb.press(Btn::Select);
        kb.press(Btn::Select);
        assert_eq!(key(&mut kb, 0, 0), Typed::Changed);
        assert_eq!(kb.text(), "1");
        assert!(kb.caps_locked());
        kb.press(Btn::Select);
        kb.press(Btn::Select);
        key(&mut kb, 0, 0);
        assert_eq!(kb.text(), "1!");
        assert!(!kb.shift());
    }

    #[test]
    fn host_layout_preserves_shifted_digits_and_caps_lock_letters() {
        let mut kb = keyboard(Layout::Host);
        kb.press(Btn::Select);
        key(&mut kb, 0, 0);
        assert_eq!(kb.text(), ".");
        assert!(!kb.shift());
        kb.press(Btn::Select);
        kb.press(Btn::Select);
        key(&mut kb, 0, 0);
        key(&mut kb, 1, 0);
        assert_eq!(kb.text(), ".1Q");
        assert!(kb.caps_locked());
    }

    #[test]
    fn numeric_layout_ignores_select_and_has_no_shift_cap() {
        let mut kb = keyboard(Layout::Numeric);
        assert_eq!(kb.press(Btn::Select), Typed::Nothing);
        assert!(!kb.shift());
        assert!(!kb.caps_locked());
    }
}
'''
if s == source:
    raise SystemExit("No changes to keyboard")
PATH.write_text(s)
print("H700 keyboard: Shift Off -> Once -> Caps Lock -> Off, plus keyboard regression tests")
