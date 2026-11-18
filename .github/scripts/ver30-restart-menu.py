#!/usr/bin/env python3
"""Add Restart as a standalone selection immediately after System in the main menu."""
from pathlib import Path
import re

def replace(path, old, new):
    p=Path(path)
    source=p.read_text()
    if source.count(old)!=1:
        raise SystemExit(f"{path}: expected unique {old[:80]!r}, found {source.count(old)}")
    p.write_text(source.replace(old,new,1))

ui="crates/slot-ui/src/quick_menu.rs"
app="crates/slot/src/app.rs"
replace(ui,
    "    BatteryDisplay,\n    System,\n    RetroAchievements,",
    "    BatteryDisplay,\n    System,\n    Restart,\n    RetroAchievements,")
replace(ui,
    "        QuickRow::BatteryDisplay,\n        QuickRow::System,\n        QuickRow::RetroAchievements,",
    "        QuickRow::BatteryDisplay,\n        QuickRow::System,\n        QuickRow::Restart,\n        QuickRow::RetroAchievements,")
p=Path(ui)
source=p.read_text()
match=re.search(r'(pub const ALL: \[QuickRow; )(\d+)( \+ cfg!\(feature = "nds"\) as usize\])',source)
if not match:
    raise SystemExit("Cannot locate QuickRow ALL count")
source=source[:match.start(2)]+str(int(match.group(2))+1)+source[match.end(2):]
p.write_text(source)
replace(ui,
    "    pub const MAIN: [QuickRow; 6] = [\n        QuickRow::General,\n        QuickRow::Game,\n        QuickRow::Controls,\n        QuickRow::Screen,\n        QuickRow::Network,\n        QuickRow::System,\n    ];",
    "    pub const MAIN: [QuickRow; 7] = [\n        QuickRow::General,\n        QuickRow::Game,\n        QuickRow::Controls,\n        QuickRow::Screen,\n        QuickRow::Network,\n        QuickRow::System,\n        QuickRow::Restart,\n    ];")
replace(ui, '            QuickRow::System => "System",',
    '            QuickRow::System => "System",\n            QuickRow::Restart => "Restart",')
replace(ui, "            QuickRow::DateTime\n                | QuickRow::FetchArt",
    "            QuickRow::Restart\n                | QuickRow::DateTime\n                | QuickRow::FetchArt")
replace(app, "            QuickRow::About => self.phase = Phase::About,",
    "            QuickRow::Restart => self.begin_restart(),\n            QuickRow::About => self.phase = Phase::About,")
p=Path(app)
source=p.read_text()
old="            | QuickRow::About\\n            | QuickRow::Screen"
new="            | QuickRow::About\\n            | QuickRow::Restart\\n            | QuickRow::Screen"
if source.count(old)!=2:
    raise SystemExit(f"Expected two non-action matches for Restart, got {source.count(old)}")
p.write_text(source.replace(old,new))
print("Ver.30 Restart row added below System; restart implementation and About unchanged.")
