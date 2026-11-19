#!/usr/bin/env python3
"""Ver.40: a short, legible guide to *hidden* H700 hotkeys only.

All physical input, editable hotkeys and configuration data stay unchanged.
Scope: hide obvious reference rows and keep two columns apart at 640x480.
"""
from pathlib import Path

def once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: wanted 1 source anchor, found {count}")
    return text.replace(old, new, 1)

def edit(path, change):
    file = Path(path)
    old = file.read_text()
    new = change(old)
    if new == old:
        raise SystemExit(f"No-op: {path}")
    file.write_text(new)

# Only genuinely undiscoverable gestures need an entry.
# Never drop QuickRow variants or rewrite existing historical patches.
# Hiding keeps all historical tests / indices stable, and avoids adding
# a second set of independent action bindings.
HIDDEN = [
    "FixVolumeUp",      # normal VOL+ button is self-explanatory
    "FixVolumeDown",    # normal VOL- button is self-explanatory
    "FixMuteSelectDown",# consolidated with SELECT + either volume button
    "FixSleep",         # ordinary POWER tap
    "FixPowerOff",      # ordinary hold POWER
    "FixGameMenu",      # ordinary MENU tap
    "FixFastRelease",   # normal hold-to-fast-forward is in editable Shortcuts
    "FixFastUnlatch",   # follow-up tap follows naturally from latch
    "FixFastToggle",    # already shown in editable Shortcuts menu
    "FixGbOriginal",    # consolidated with L1 / R1 resize line
    "FixMoveCollection",# detailed collection editing is not a hidden hotkey
    "FixedStates",      # no ordinary save-state navigation instructions
    "FixStatePrev",
    "FixStateNext",
    "FixStateLoad",
    "FixStateDelete",
    "FixStateUndo",
    "FixStateBack",
    "FixAboutRestart",  # regular Restart entry exists in main menu
    "FixKidExit",       # ordinary MENU use, no need to list it twice
]
# New text is brief, clear and deliberately uses real hardware button names.
# Only rows visible after the HIDDEN filter are updated here.
LABELS = {
    "FixMuteSelectUp": "Mute",
    "FixMuteBoth": "Mute (both)",
    "FixStateSwitcher": "Save states",
    "FixExit": "Exit (multi-cart)",
    "FixLink": "Link Play*",
    "FixFastLatch": "FF double-tap lock",
    "FixGbStretch": "Game Boy resize",
    "FixFresh": "Start fresh",
    "FixMultiselect": "Multi-select",
    "FixAddCollection": "Add to collection",
    "FixStudio": "Cart Studio",
    "FixCorePicker": "Choose emulator",
    "FixRemoveFromCollection": "Remove game",
    "FixMoveInCollection": "Reorder game",
    "FixRepair": "SD repair (if offered)",
    "FixKidUnlock": "Kid unlock (boot)",
}
KEYS = {
    "FixMuteSelectUp": "SELECT + VOLUME UP/DOWN",
    "FixMuteBoth": "VOLUME UP + DOWN",
    "FixStateSwitcher": "MENU TWICE",
    "FixExit": "HOLD MENU",
    "FixLink": "SELECT + MENU",
    "FixGbStretch": "L1 / R1 (IF FREE)",
    "FixFresh": "HOLD A",
    "FixMultiselect": "HOLD SELECT",
    "FixStudio": "TAP SELECT",
    "FixCorePicker": "START",
    "FixRepair": "SELECT + START",
    "FixKidUnlock": "START + SELECT + L2 + R2",
}

def update_ui(text):
    # Source-verified guide rows are plain enum entries, so they're easy to
    # distinguish from editable Shortcuts / emulator mappings.
    for row, label in LABELS.items():
        start = f"            QuickRow::{row} => "
        lines = [line for line in text.splitlines() if line.startswith(start) and 'Some(' not in line]
        if len(lines) != 1:
            raise SystemExit(f"Cannot identify QuickRow label {row}: {lines}")
        text = once(text, lines[0], f'            QuickRow::{row} => "{label}",', row + " label")

    for row, value in KEYS.items():
        start = f'            QuickRow::{row} => Some("'
        lines = [line for line in text.splitlines() if line.startswith(start)]
        if len(lines) != 1:
            raise SystemExit(f"Cannot identify QuickRow fixed key {row}: {lines}")
        text = once(text, lines[0], f'            QuickRow::{row} => Some("{value}"),', row + " key")

    # Only guide labels receive layout changes, in the normal QuickMenu
    # renderer; regular settings and editable binding rows use the old code.
    old = """                label_end = x + label.1 as f32 - pad;
                push_label(out, faces, label, x, y, lit);"""
    new = """                if row.fixed_keys().is_some() {
                    // Source reference rows have two text columns. The stock
                    // quick-menu font can let long names overlap a value.
                    // Reserve ~35% of width for the left label, scale both
                    // textures, and retain the original selected-row pointer.
                    let (tex, w, h) = label;
                    let max_label = (self.canvas.w * 0.35).min(240.0);
                    let ink = (w as f32 - 2.0 * pad).max(1.0);
                    let scale = (max_label / ink).min(0.8);
                    let sh = h as f32 * scale;
                    out.push(Draw::Tex {
                        x: x.round(),
                        y: (y + (h as f32 - sh) / 2.0).round(),
                        w: w as f32 * scale,
                        h: sh,
                        tex,
                        alpha: 1.0,
                    });
                    label_end = x + (w as f32 - pad) * scale;
                    if lit {
                        let (pointer, pw, ph) = faces.pointer;
                        let px = x + pad - POINTER_GAP - pw as f32;
                        push(out, pointer, px, y - POINTER_BLEED as f32, pw, ph);
                    }
                } else {
                    label_end = x + label.1 as f32 - pad;
                    push_label(out, faces, label, x, y, lit);
                }"""
    text = once(text, old, new, "menu label scaling")

    old = """            let s = (room / (w as f32 - 2.0 * pad)).clamp(VALUE_MIN_SCALE, 1.0);"""
    new = """            // Only on the read-only reference: never enforce the normal
            // 60% minimum when it would cause the two columns to collide.
            let s = if row.fixed_keys().is_some() {
                (room.max(0.0) / (w as f32 - pad).max(1.0))
                    .clamp(0.0, 0.8)
            } else {
                (room / (w as f32 - 2.0 * pad)).clamp(VALUE_MIN_SCALE, 1.0)
            };"""
    text = once(text, old, new, "menu value scaling")

    # The preceding two UI-only versions contain assertions of the exact
    # verbose labels they introduced. Update those assertions to match the
    # new compact wording rather than disabling regression coverage.
    for old, new in [
        ('Some("SELECT + VOLUME UP")', 'Some("SELECT + VOLUME UP/DOWN")'),
        ('Some("PRESS BOTH VOLUME BUTTONS")', 'Some("VOLUME UP + DOWN")'),
        ('Some("PRESS MENU TWICE")', 'Some("MENU TWICE")'),
        ('QuickRow::FixStateSwitcher.label(), "Save States (if saved)"',
         'QuickRow::FixStateSwitcher.label(), "Save states"'),
    ]:
        text = once(text, old, new, "legacy reference assertion")

    text += r"""

#[cfg(test)]
mod compact_guide_layout_tests {
    use super::*;

    #[test]
    fn all_read_only_guide_rows_fit_a_two_column_640px_layout() {
        // Same geometry used in QuickMenu::draw; tests longer-than-expected
        // synthetic key/label textures, not only today's English strings.
        for canvas_width in [640.0_f32, 720.0, 800.0] {
            let pad = MENU_PAD as f32;
            let right = canvas_width - QUICK_EDGE;
            let x = QUICK_LABEL_X - pad;
            for (label_ink, value_ink) in [(180.0, 340.0), (450.0, 380.0),
                                            (900.0, 650.0), (230.0, 590.0)] {
                let label_texture = label_ink + 2.0 * pad;
                let scale = ((canvas_width * 0.35).min(240.0) / label_ink).min(0.8);
                let label_end = x + (label_texture - pad) * scale;
                let room = (right - label_end - QUICK_VALUE_GAP).max(0.0);
                let value_scale = (room / (value_ink + pad)).min(0.8);
                let value_left = right - (value_ink + pad) * value_scale;
                assert!(label_end + QUICK_VALUE_GAP <= value_left + 1.0,
                    "reference columns touch on {canvas_width}px");
            }
        }
    }

    #[test]
    fn the_editable_shortcuts_page_keeps_its_original_layout() {
        assert!(QuickRow::ScFastForward.shortcut().is_some());
        assert!(QuickRow::ScFastForward.fixed_keys().is_none());
        assert!(QuickRow::FixMuteSelectUp.shortcut().is_none());
        assert!(QuickRow::FixMuteSelectUp.fixed_keys().is_some());
    }
}
"""
    return text

def update_app(src):
    # One central filter drives browsing, drawing and navigation, without
    # changing the source of any hotkeys or binding formats.
    start = "    fn hidden_rows_any_panel(&self) -> Vec<QuickRow> {"
    at = src.find(start)
    if at < 0:
        raise SystemExit("Cannot find common hidden-row filter")
    tail = src[at:]
    old = "        let mut hidden = Vec::new();"
    addition = """        let mut hidden = Vec::new();
        // Keep the Hotkey Guide short: list only undiscoverable gestures.
        // Regular POWER / MENU / volume, editable FF Toggle, and ordinary
        // save-state browsing don't need a duplicate reference entry.
        hidden.extend([
"""
    addition += "".join(f"            QuickRow::{row},\n" for row in HIDDEN)
    addition += "        ]);"
    tail = once(tail, old, addition, "common hidden guide rows")
    return src[:at] + tail

edit("crates/slot-ui/src/quick_menu.rs", update_ui)
edit("crates/slot/src/app.rs", update_app)
print("Compact Hotkey Guide: obvious shortcuts hidden, reference columns scaled.")
