#!/usr/bin/env python3
"""Expose native Miyoo picture scaling modes in Slot's in-game Screen menu.

Runs after port_features.py; fail on unexpected upstream schema.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1])

def replace(path,old,new):
    target=root/path
    src=target.read_text()
    n=src.count(old)
    if n!=1: raise RuntimeError(f"{path}: expected one anchor, got {n}: {old[:80]}")
    target.write_text(src.replace(old,new,1))

menu="crates/slot-ui/src/quick_menu.rs"
replace(menu,
        "    AutoLoad,\n}\n\nimpl QuickRow {",
        "    AutoLoad,\n    PictureScale,\n}\n\nimpl QuickRow {")
replace(menu,
        "pub const ALL: [QuickRow; 80] = [",
        "pub const ALL: [QuickRow; 81] = [")
replace(menu,
        "        QuickRow::AutoLoad,\n    ];\n\n    pub const MAIN:",
        "        QuickRow::AutoLoad,\n        QuickRow::PictureScale,\n    ];\n\n    pub const MAIN:")
replace(menu,
        "pub const PLAY_SCREEN: [QuickRow; 6] = [",
        "pub const PLAY_SCREEN: [QuickRow; 7] = [")
replace(menu,
        "    pub const PLAY_SCREEN: [QuickRow; 7] = [\n        QuickRow::Shader,",
        "    pub const PLAY_SCREEN: [QuickRow; 7] = [\n        QuickRow::PictureScale,\n        QuickRow::Shader,")
replace(menu,
        "            QuickRow::Shader | QuickRow::ColourCorrection | QuickRow::Palette | QuickRow::Bezel => {",
        "            QuickRow::PictureScale | QuickRow::Shader | QuickRow::ColourCorrection | QuickRow::Palette | QuickRow::Bezel => {")
replace(menu,
        '            QuickRow::PlayScreen => "Screen",',
        '            QuickRow::PlayScreen => "Screen",\n            QuickRow::PictureScale => "Scaling",')
replace(menu,
        "    Level9,\n}\n\nimpl QuickValue {",
        "    Level9,\n    ScaleActual,\n    ScaleInteger,\n    ScaleFit,\n    ScaleFill,\n    ScaleStretch,\n}\n\nimpl QuickValue {")
replace(menu,
        "pub const ALL: [QuickValue; 33] = [",
        "pub const ALL: [QuickValue; 38] = [")
replace(menu,
        "        QuickValue::Level9,\n    ];\n\n    pub const LEVELS:",
        "        QuickValue::Level9,\n        QuickValue::ScaleActual,\n        QuickValue::ScaleInteger,\n        QuickValue::ScaleFit,\n        QuickValue::ScaleFill,\n        QuickValue::ScaleStretch,\n    ];\n\n    pub const LEVELS:")
replace(menu,
        '            QuickValue::Level9 => "9",',
        '''            QuickValue::Level9 => "9",
            QuickValue::ScaleActual => "Original",
            QuickValue::ScaleInteger => "Integer",
            QuickValue::ScaleFit => "Aspect Fit",
            QuickValue::ScaleFill => "Fill / Crop",
            QuickValue::ScaleStretch => "Full Stretch",''')

app="crates/slot/src/app.rs"
replace(app,
        "            QuickRow::AutoLoad => Some(QuickValue::flag(self.state.auto_load)),",
        """            QuickRow::PictureScale => Some(match self.video_mode {
                VideoMode::Actual => QuickValue::ScaleActual,
                VideoMode::Integer => QuickValue::ScaleInteger,
                VideoMode::Fit => QuickValue::ScaleFit,
                VideoMode::Fill => QuickValue::ScaleFill,
                VideoMode::Stretch => QuickValue::ScaleStretch,
            }),
            QuickRow::AutoLoad => Some(QuickValue::flag(self.state.auto_load)),""")
replace(app,
        "    fn change_setting(&mut self, row: QuickRow, right: bool) {\n        let row = self.playing_row(row);",
        """    fn change_setting(&mut self, row: QuickRow, right: bool) {
        let row = self.playing_row(row);
        if row == QuickRow::PictureScale {
            let mode = if right { self.video_mode.next() } else { self.video_mode.prev() };
            self.set_picture(mode);
            return;
        }""")
# Keep final match exhaustive even though early return handles this case.
replace(app,
        "            | QuickRow::ControlsInGame\n            | QuickRow::LidOff => return,",
        "            | QuickRow::ControlsInGame\n            | QuickRow::PictureScale\n            | QuickRow::LidOff => return,")
# A new menu row should be visible on GBA as well: no dependence on shoulder inputs.

print("Custom slot Miyoo: in-game scaling menu rows enabled")
