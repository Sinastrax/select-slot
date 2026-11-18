#!/usr/bin/env python3
"""Ver.30: add a standalone Restart row immediately after System in the top-level menu.
Reuse Slot's existing safe restart path; do not alter About, Wi-Fi, or emulators.
"""
from pathlib import Path

def change(path, old, new):
    file = Path(path)
    body = file.read_text()
    hits = body.count(old)
    if hits != 1:
        raise SystemExit(f"{file}: expected one match, got {hits}: {old[:95]!r}")
    file.write_text(body.replace(old, new, 1))

ui = "crates/slot-ui/src/quick_menu.rs"
app = "crates/slot/src/app.rs"
change(ui,
    "    BatteryDisplay,\n    System,\n}",
    "    BatteryDisplay,\n    System,\n    Restart,\n}")
change(ui,
    "pub const ALL: [QuickRow; 143 + cfg!(feature = \"nds\") as usize] = [",
    "pub const ALL: [QuickRow; 144 + cfg!(feature = \"nds\") as usize] = [")
change(ui,
    "        QuickRow::BatteryDisplay,\n        QuickRow::System,\n    ];",
    "        QuickRow::BatteryDisplay,\n        QuickRow::System,\n        QuickRow::Restart,\n    ];")
change(ui,
    "    pub const MAIN: [QuickRow; 6] = [\n        QuickRow::General,\n        QuickRow::Game,\n        QuickRow::Controls,\n        QuickRow::Screen,\n        QuickRow::Network,\n        QuickRow::System,\n    ];",
    "    pub const MAIN: [QuickRow; 7] = [\n        QuickRow::General,\n        QuickRow::Game,\n        QuickRow::Controls,\n        QuickRow::Screen,\n        QuickRow::Network,\n        QuickRow::System,\n        QuickRow::Restart,\n    ];")
change(ui,
    '            QuickRow::System => "System",',
    '            QuickRow::System => "System",\n            QuickRow::Restart => "Restart",')
change(ui,
    "            QuickRow::DateTime\n                | QuickRow::FetchArt",
    "            QuickRow::Restart\n                | QuickRow::DateTime\n                | QuickRow::FetchArt")
change(app,
    "            QuickRow::About => self.phase = Phase::About,",
    "            QuickRow::Restart => self.begin_restart(),\n            QuickRow::About => self.phase = Phase::About,")
change(app,
    "            | QuickRow::About\n            | QuickRow::Screen",
    "            | QuickRow::About\n            | QuickRow::Restart\n            | QuickRow::Screen")
print("Restart appears as MAIN selectable entry immediately after System; About remains unchanged")
