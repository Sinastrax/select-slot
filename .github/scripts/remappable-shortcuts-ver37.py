#!/usr/bin/env python3
"""Expose formerly hard-coded H700 mute and Link Play chords as persisted Shortcuts.

Runs after the verified Ver.35 preparation. The existing shortcuts.txt parser
uses defaults for keys absent from older files, so old cards migrate safely.
"""
from pathlib import Path
import re


def edit(path, transform):
    file = Path(path)
    before = file.read_text()
    after = transform(before)
    if before == after:
        raise SystemExit(f"{path}: patch unexpectedly made no changes")
    file.write_text(after)


def one(s, old, new, note):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"{note}: expected one anchor, found {n}")
    return s.replace(old, new, 1)


def block(s, pattern, transform, note):
    matches = list(re.finditer(pattern, s, flags=re.S))
    if len(matches) != 1:
        raise SystemExit(f"{note}: expected one block, found {len(matches)}")
    m = matches[0]
    return s[:m.start()] + transform(m.group(0)) + s[m.end():]


def adjust_count(s, name, old, added):
    pattern = rf"(pub const {name}: \[[A-Za-z]+; )(\d+)(\])"
    return block(s, pattern,
                 lambda x: re.sub(r"; \d+\]", f"; {old + added}]", x)
                 if int(re.search(r"; (\d+)\]", x).group(1)) == old
                 else (_ for _ in ()).throw(RuntimeError(f"{name} count drift")),
                 name)


def bindings(s):
    # RG34XXSP adds six digital inputs before this patch.
    s = one(s, "    RRight,\n}\n\nimpl Device {",
            "    RRight,\n    Menu,\n    VolUp,\n    VolDown,\n}\n\nimpl Device {", "device variants")
    s = one(s, "pub const ALL: [Device; 20]", "pub const ALL: [Device; 23]", "device count")
    s = one(s, "        Device::RRight,\n    ];",
            "        Device::RRight,\n        Device::Menu,\n        Device::VolUp,\n        Device::VolDown,\n    ];", "devices ALL")
    s = one(s, '            Device::RRight => "right_right",',
            '            Device::RRight => "right_right",\n            Device::Menu => "menu_button",\n            Device::VolUp => "vol_up",\n            Device::VolDown => "vol_down",', "device key")
    s = one(s, '            Device::RRight => "R-RIGHT",',
            '            Device::RRight => "R-RIGHT",\n            Device::Menu => "MENU",\n            Device::VolUp => "VOL+",\n            Device::VolDown => "VOL-",', "device label")
    # The key 'menu' is reserved for the existing MENU modifier, not a solo device.
    # MENU can still be captured as the second key in SELECT+MENU.
    s = block(s, r"pub enum Shortcut \{.*?\n\}", lambda x: one(
        x, "    Guide,\n}", "    Guide,\n    Mute,\n    MuteAlt,\n    MuteBoth,\n    LinkMenu,\n}", "shortcut variants"), "Shortcut enum")
    s = one(s, "pub const ALL: [Shortcut; 19]", "pub const ALL: [Shortcut; 23]", "shortcut count")
    s = one(s, "        Shortcut::Guide,\n    ];",
            "        Shortcut::Guide,\n        Shortcut::Mute,\n        Shortcut::MuteAlt,\n        Shortcut::MuteBoth,\n        Shortcut::LinkMenu,\n    ];", "shortcuts ALL")
    s = one(s, '            Shortcut::Guide => "Guide",',
            '            Shortcut::Guide => "Guide",\n            Shortcut::Mute => "Mute",\n            Shortcut::MuteAlt => "Mute Alternate",\n            Shortcut::MuteBoth => "Mute Both Buttons",\n            Shortcut::LinkMenu => "Link Play",', "shortcut labels")
    s = one(s, '            Shortcut::Guide => "guide",',
            '            Shortcut::Guide => "guide",\n            Shortcut::Mute => "mute",\n            Shortcut::MuteAlt => "mute_alternate",\n            Shortcut::MuteBoth => "mute_both",\n            Shortcut::LinkMenu => "link_menu",', "shortcut keys")
    s = one(s, '            Shortcut::SunlightUp | Shortcut::SunlightDown | Shortcut::Reset | Shortcut::Guide => {',
            '            Shortcut::Mute => select(Device::VolUp),\n            Shortcut::MuteAlt => select(Device::VolDown),\n            Shortcut::MuteBoth => Binding::pair(Device::VolUp, Device::VolDown),\n            Shortcut::LinkMenu => select(Device::Menu),\n            Shortcut::SunlightUp | Shortcut::SunlightDown | Shortcut::Reset | Shortcut::Guide => {',
            "shortcut defaults")
    s = one(s, "keys: [Option<Binding>; 19]", "keys: [Option<Binding>; 23]", "shortcut store")
    return s


def bind(s):
    s = one(s, "const PAIRS: [(Device, Btn); 20]", "const PAIRS: [(Device, Btn); 23]", "input pairs")
    s = one(s, "    (Device::RRight, Btn::RRight),",
            "    (Device::RRight, Btn::RRight),\n    (Device::Menu, Btn::Menu),\n    (Device::VolUp, Btn::VolUp),\n    (Device::VolDown, Btn::VolDown),", "input device mapping")
    s = one(s, "        Shortcut::Guide => Action::Guide,",
            "        Shortcut::Guide => Action::Guide,\n        Shortcut::Mute | Shortcut::MuteAlt | Shortcut::MuteBoth => Action::MuteToggle,\n        Shortcut::LinkMenu => Action::GameMenu,", "input shortcut mapping")
    return s


def ui(s):
    s = block(s, r"pub enum QuickRow \{.*?\n\}", lambda x: x[:-2] + "\n" +
        "    ScMute,\n    ScMuteAlt,\n    ScMuteBoth,\n    ScLinkMenu,\n}", "QuickRow variants")
    s = block(s, r"pub const ALL: \[QuickRow; \d+ \+ cfg!\(feature = \"nds\"\) as usize\] = \[.*?\n    \];",
        lambda x: re.sub(r"(pub const ALL: \[QuickRow; )(\d+)",
        lambda m: m[1]+str(int(m[2])+4), x[:x.rfind("    ];")] +
        "        QuickRow::ScMute,\n        QuickRow::ScMuteAlt,\n        QuickRow::ScMuteBoth,\n        QuickRow::ScLinkMenu,\n" + x[x.rfind("    ];"):]), "QuickRow::ALL")
    s = block(s, r"pub const SHORTCUTS: \[QuickRow; \d+\] = \[.*?\n    \];",
        lambda x: x.replace("SHORTCUTS: [QuickRow; 19]", "SHORTCUTS: [QuickRow; 23]")
        .replace("    ];", "        QuickRow::ScMute,\n        QuickRow::ScMuteAlt,\n        QuickRow::ScMuteBoth,\n        QuickRow::ScLinkMenu,\n    ];"), "SHORTCUTS rows")
    s = one(s, "            | QuickRow::ScGuide => self.shortcut().map_or(\"\", Shortcut::label),",
            "            | QuickRow::ScGuide\n            | QuickRow::ScMute\n            | QuickRow::ScMuteAlt\n            | QuickRow::ScMuteBoth\n            | QuickRow::ScLinkMenu => self.shortcut().map_or(\"\", Shortcut::label),",
            "shortcut labels match")
    s = one(s, "            QuickRow::ScGuide => Shortcut::Guide,",
            "            QuickRow::ScGuide => Shortcut::Guide,\n            QuickRow::ScMute => Shortcut::Mute,\n            QuickRow::ScMuteAlt => Shortcut::MuteAlt,\n            QuickRow::ScMuteBoth => Shortcut::MuteBoth,\n            QuickRow::ScLinkMenu => Shortcut::LinkMenu,", "UI mapping")
    return s


def gesture(s):
    s = one(s, "Action::BrightnessUp | Action::BrightnessDown | Action::BlueLightUp | Action::BlueLightDown",
            "Action::BrightnessUp | Action::BrightnessDown | Action::BlueLightUp | Action::BlueLightDown | Action::MuteToggle",
            "mute is available in all contexts")
    s = one(s, """            let action = match b {
                Btn::VolUp | Btn::VolDown => Some(Action::MuteToggle),
                _ => self.shortcut(Some(Mod::Select), b),
            };""",
            "            let action = self.shortcut(Some(Mod::Select), b);", "remove Select+Vol hard-code")
    s = one(s, """        if self.chording(now) {
            let action = self.shortcut(Some(Mod::Select), b);""",
            """        if b != Btn::Menu && self.chording(now) {
            // MENU is handled by menu_down so it clears an earlier menu tap.
            let action = self.shortcut(Some(Mod::Select), b);""",
            "MENU chord must retain menu-tap state cleanup")
    s = one(s, "if let Some((first, action)) = self.pair(b) {",
            "if let Some((first, action)) = self.pair(b, now) {", "pair has timestamp")
    s = one(s, """            return self.fire(b, action, now);
        }
        let system = matches!(""",
            """            if matches!((first, b), (Btn::VolUp, Btn::VolDown) | (Btn::VolDown, Btn::VolUp)) {
                // Keep the original one-step volume response and timed two-key
                // gesture, but route the actual action through the user's binding.
                let mut out = self.volume_press(b, now);
                self.mute_fired = action == Action::MuteToggle;
                out.extend(self.fire(b, action, now));
                return out;
            }
            return self.fire(b, action, now);
        }
        let system = matches!(""", "volume pair handling")
    s = one(s, """        if let Some(at) = self.held.iter().position(|(h, _)| *h == b) {
            return match self.held.remove(at).1 {
                Release::Nothing => Vec::new(),
                Release::Send(action) => vec![action],
            };
        }""",
            """        if let Some(at) = self.held.iter().position(|(h, _)| *h == b) {
            let release = self.held.remove(at).1;
            if matches!(b, Btn::VolUp | Btn::VolDown) {
                self.volume_release(b);
            }
            return match release {
                Release::Nothing => Vec::new(),
                Release::Send(action) => vec![action],
            };
        }""", "volume combo release")
    s = one(s, "    fn pair(&self, b: Btn) -> Option<(Btn, Action)> {",
            "    fn pair(&self, b: Btn, now: Millis) -> Option<(Btn, Action)> {", "pair function")
    s = one(s, """            .find_map(|h| {
                self.shortcut(Some(Mod::Button(*h)), b)
                    .or_else(|| self.shortcut(Some(Mod::Button(b)), *h))
                    .map(|action| (*h, action))
            })""",
            """            .find_map(|h| {
                // The two volume controls are not a chord if pressed far apart.
                if matches!((*h, b), (Btn::VolUp, Btn::VolDown) | (Btn::VolDown, Btn::VolUp)) {
                    let other_at = if b == Btn::VolUp { self.vol_down_at } else { self.vol_up_at };
                    if !other_at.is_some_and(|t| now.saturating_sub(t) <= MUTE_CHORD_MS) {
                        return None;
                    }
                }
                self.shortcut(Some(Mod::Button(*h)), b)
                    .or_else(|| self.shortcut(Some(Mod::Button(b)), *h))
                    .map(|action| (*h, action))
            })""", "timed mute combo")
    s = one(s, """        if self.chording(now) {
            self.mark_chorded();
            self.menu_down_at = None;
            self.menu_last_tap = None;
            return vec![Action::GameMenu];
        }""",
            """        if self.chording(now) {
            if let Some(action) = self.shortcut(Some(Mod::Select), Btn::Menu) {
                self.mark_chorded();
                self.menu_down_at = None;
                self.menu_last_tap = None;
                return self.hold(Btn::Menu, action);
            }
        }""", "link menu is configurable")
    s = one(s, """        let (mine, other, action) = match b {
            Btn::VolUp => (&mut self.vol_up_at, self.vol_down_at, Action::VolumeUp),
            _ => (&mut self.vol_down_at, self.vol_up_at, Action::VolumeDown),
        };""",
            """        let (mine, action) = match b {
            Btn::VolUp => (&mut self.vol_up_at, Action::VolumeUp),
            _ => (&mut self.vol_down_at, Action::VolumeDown),
        };""", "volume press")
    s = one(s, """        let mut out = vec![action];
        let paired = other.is_some_and(|t| now.abs_diff(t) <= MUTE_CHORD_MS);
        if paired && !self.mute_fired {
            self.mute_fired = true;
            out.push(Action::MuteToggle);
        }
        out""",
            "        vec![action]", "remove hard-coded volume mute")
    return s


def table(s):
    s = one(s,
        """                        contexts: match (anywhere(action), binding.modifier) {
                            (false, _) => Contexts::GAME,
                            (true, None) => Contexts::GAME.with(Contexts::SHELF),
                            (true, Some(_)) => Contexts::ALL,
                        },""",
        """                        contexts: match (action, anywhere(action), binding.modifier) {
                            // Link Play also closes an already-open link menu.
                            (Action::GameMenu, _, _) => Contexts::ALL,
                            (_, false, _) => Contexts::GAME,
                            (_, true, None) => Contexts::GAME.with(Contexts::SHELF),
                            (_, true, Some(_)) => Contexts::ALL,
                        },""",
        "Link Play remains usable while its modal menu is open")
    return one(s, "                (Some(_), false) => false,",
        "                (Some(Action::MuteToggle | Action::GameMenu), false) => true,\n"
        "                (Some(_), false) => false,",
        "retain previously hard-coded system gestures in Kid Mode")

def regression(s):
    s = one(s, """        (plain(L2), RewindStart),
    ]""",
            """        (plain(L2), RewindStart),
        (select(VolUp), MuteToggle),
        (select(VolDown), MuteToggle),
        (Chord { modifier: Some(Mod::Button(VolUp)), button: VolDown }, MuteToggle),
        (select(Menu), GameMenu),
    ]""", "gesture test fixture")
    s += """
#[test]
fn mute_is_not_a_hidden_firmware_shortcut_when_unbound() {
    let mut g = gestures();
    g.set_shortcuts(today().into_iter().filter(|(_, a)| *a != MuteToggle).collect());
    g.feed(Down(Select), 0);
    let actions = g.feed(Down(VolUp), 50);
    assert!(!actions.contains(&MuteToggle), "{actions:?}");
    let mut g = gestures();
    g.set_shortcuts(today().into_iter().filter(|(_, a)| *a != MuteToggle).collect());
    g.feed(Down(VolUp), 0);
    let actions = g.feed(Down(VolDown), 50);
    assert!(!actions.contains(&MuteToggle), "{actions:?}");
}

#[test]
fn link_play_chord_is_reassignable_and_can_be_disabled() {
    let mut g = gestures();
    g.set_shortcuts(today().into_iter().filter(|(_, a)| *a != GameMenu).collect());
    g.feed(Down(Select), 0);
    let actions = g.feed(Down(Menu), 50);
    assert!(!actions.contains(&GameMenu), "{actions:?}");
    let mut g = gestures();
    let mut bindings: Vec<_> = today().into_iter().filter(|(_, a)| *a != GameMenu).collect();
    bindings.push((Chord { modifier: Some(Mod::Select), button: Start }, GameMenu));
    g.set_shortcuts(bindings);
    g.feed(Down(Select), 0);
    assert_eq!(g.feed(Down(Start), 50), vec![GameMenu]);
}
"""
    return s


def persistence(s):
    s += """
#[test]
fn remappable_system_shortcuts_persist_without_overwriting_old_settings() {
    let d = card();
    let default = ShortcutKeys::default();
    assert_eq!(default.get(Shortcut::Mute), with(Modifier::Select, Device::VolUp));
    assert_eq!(default.get(Shortcut::MuteAlt), with(Modifier::Select, Device::VolDown));
    assert_eq!(default.get(Shortcut::MuteBoth),
        with(Modifier::Button(Device::VolUp), Device::VolDown));
    assert_eq!(default.get(Shortcut::LinkMenu), with(Modifier::Select, Device::Menu));

    let mut custom = default;
    custom.set(Shortcut::Mute, None);
    custom.set(Shortcut::MuteAlt, with(Modifier::Select, Device::R3));
    custom.set(Shortcut::MuteBoth, None);
    custom.set(Shortcut::LinkMenu, with(Modifier::Select, Device::A));
    write_shortcuts(d.path(), &custom).unwrap();
    assert_eq!(read_shortcuts(d.path()), custom);

    // Older Config/shortcuts.txt files have no new keys: new defaults are
    // injected while the user's pre-existing overrides remain unchanged.
    std::fs::write(d.path().join("Config/shortcuts.txt"), "save_state=menu+x\\n").unwrap();
    let migrated = read_shortcuts(d.path());
    assert_eq!(migrated.get(Shortcut::SaveState), with(Modifier::Menu, Device::X));
    assert_eq!(migrated.get(Shortcut::Mute), default.get(Shortcut::Mute));
    assert_eq!(migrated.get(Shortcut::LinkMenu), default.get(Shortcut::LinkMenu));
}
"""
    return s


edit("crates/slot-store/src/bindings.rs", bindings)
edit("crates/slot/src/input/bind.rs", bind)
edit("crates/slot-ui/src/quick_menu.rs", ui)
edit("crates/slot-input/src/gesture.rs", gesture)
def app_exhaustive(s):
    # The three central QuickRow matches treat shortcut rows as value-less
    # settings (read, change, open). Keep the new entries in that category.
    old = "            | QuickRow::ScGuide\n"
    if s.count(old) != 3:
        raise SystemExit(f"app exhaustive shortcut arms: expected 3, got {s.count(old)}")
    return s.replace(old, old + (
        "            | QuickRow::ScMute\n"
        "            | QuickRow::ScMuteAlt\n"
        "            | QuickRow::ScMuteBoth\n"
        "            | QuickRow::ScLinkMenu\n"
    ))


edit("crates/slot/src/app.rs", app_exhaustive)
edit("crates/slot/src/input/table.rs", table)
edit("crates/slot-input/tests/gesture.rs", regression)
edit("crates/slot-store/tests/bindings.rs", persistence)
print("Remappable H700 mute (three inputs) and Link Play shortcuts installed.")
