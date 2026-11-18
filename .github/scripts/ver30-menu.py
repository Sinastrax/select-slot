#!/usr/bin/env python3
"""Ver.30 menus: top-level Restart, in-game Achievements, Tools storage cleanup."""
from pathlib import Path
import re

def change(path, old, new, label):
    p=Path(path)
    s=p.read_text()
    n=s.count(old)
    if n!=1: raise SystemExit(f"{path}: {label}: expected 1, found {n}")
    p.write_text(s.replace(old,new,1))

ui="crates/slot-ui/src/quick_menu.rs"
change(ui,"    RaBackground,\n}","    RaBackground,\n    Restart,\n    Achievements,\n    AchievementList,\n    Cleanup,\n    CleanupScan,\n    CleanupDelete,\n}","enum")
p=Path(ui);s=p.read_text()
old="        QuickRow::RaBackground,\n    ];"
new="        QuickRow::RaBackground,\n        QuickRow::Restart,\n        QuickRow::Achievements,\n        QuickRow::AchievementList,\n        QuickRow::Cleanup,\n        QuickRow::CleanupScan,\n        QuickRow::CleanupDelete,\n    ];"
assert s.count(old)>=1, "ALL rows not found"
p.write_text(s.replace(old,new,1))
p=Path(ui);s=p.read_text()
m=re.search(r'(pub const ALL: \[QuickRow; )(\d+)( \+ cfg!\(feature = "nds"\) as usize\])',s)
assert m, "QuickRow count missing"
s=s[:m.start(2)]+str(int(m.group(2))+6)+s[m.end(2):]
p.write_text(s)
change(ui,'''    pub const MAIN: [QuickRow; 6] = [
        QuickRow::General,
        QuickRow::Game,
        QuickRow::Controls,
        QuickRow::Screen,
        QuickRow::Network,
        QuickRow::System,
    ];''','''    pub const MAIN: [QuickRow; 7] = [
        QuickRow::General,
        QuickRow::Game,
        QuickRow::Controls,
        QuickRow::Screen,
        QuickRow::Network,
        QuickRow::System,
        QuickRow::Restart,
    ];''',"Restart below System")
p=Path(ui);s=p.read_text()
s,n=re.subn(r'(pub const NETWORK: \[QuickRow; )(\d+)( \+ cfg!\(feature = "nds"\) as usize\])',lambda m:m[1]+str(int(m[2])+1)+m[3],s)
assert n==1,"Tools menu count"
p.write_text(s)
change(ui,'''        QuickRow::RetroAchievements,
    ];''','''        QuickRow::RetroAchievements,
        QuickRow::Cleanup,
    ];''',"Tools cleanup")
change(ui,'''    pub const CHEAT_LIST: [QuickRow; 1] = [QuickRow::CheatList];''','''    pub const CHEAT_LIST: [QuickRow; 1] = [QuickRow::CheatList];
    pub const ACHIEVEMENT_LIST: [QuickRow; 1] = [QuickRow::AchievementList];
    pub const CLEANUP: [QuickRow; 2] = [QuickRow::CleanupScan, QuickRow::CleanupDelete];''',"subpages")
change(ui,'''    pub const PLAY: [QuickRow; 10] = [''','''    pub const PLAY: [QuickRow; 11] = [''',"in-game count")
change(ui,'''        QuickRow::Cheats,
        QuickRow::Guide,
        QuickRow::Settings,''','''        QuickRow::Cheats,
        QuickRow::Achievements,
        QuickRow::Guide,
        QuickRow::Settings,''',"in-game entry")
change(ui,'''            QuickRow::RetroAchievements => &QuickRow::NETWORK,''','''            QuickRow::RetroAchievements | QuickRow::Cleanup => &QuickRow::NETWORK,
            QuickRow::CleanupScan | QuickRow::CleanupDelete => &QuickRow::CLEANUP,''',"cleanup navigation")
change(ui,'''            QuickRow::CheatList => &QuickRow::CHEAT_LIST,''','''            QuickRow::CheatList => &QuickRow::CHEAT_LIST,
            QuickRow::AchievementList => &QuickRow::ACHIEVEMENT_LIST,''',"achievement page")
change(ui,'''            | QuickRow::Cheats
            | QuickRow::Guide
            | QuickRow::Settings''','''            | QuickRow::Cheats
            | QuickRow::Achievements
            | QuickRow::Guide
            | QuickRow::Settings''',"play mapping")
change(ui,'''            QuickRow::CheatList => Some(QuickRow::Cheats),''','''            QuickRow::CheatList => Some(QuickRow::Cheats),
            QuickRow::AchievementList => Some(QuickRow::Achievements),
            QuickRow::CleanupScan => Some(QuickRow::Cleanup),''',"back navigation")
change(ui,'''            QuickRow::Romm => Some(QuickRow::ROMM[0]),''','''            QuickRow::Romm => Some(QuickRow::ROMM[0]),
            QuickRow::Cleanup => Some(QuickRow::CLEANUP[0]),''',"submenu")
change(ui,'''            QuickRow::About => "About",''','''            QuickRow::About => "About",
            QuickRow::Restart => "Restart",
            QuickRow::Achievements | QuickRow::AchievementList => "Achievements",
            QuickRow::Cleanup => "Storage Cleanup",
            QuickRow::CleanupScan => "Scan Storage",
            QuickRow::CleanupDelete => "Clean Detected Files",''',"labels")
change(ui,'''                | QuickRow::About
                | QuickRow::Screen''','''                | QuickRow::About
                | QuickRow::Restart
                | QuickRow::Cleanup
                | QuickRow::CleanupScan
                | QuickRow::CleanupDelete
                | QuickRow::Achievements
                | QuickRow::AchievementList
                | QuickRow::Screen''',"opens")
app="crates/slot/src/app.rs"
change(app,'''            QuickRow::About => self.phase = Phase::About,''','''            QuickRow::About => self.phase = Phase::About,
            QuickRow::Restart => self.begin_restart(),
            QuickRow::CleanupScan => self.scan_cleanup(),
            QuickRow::CleanupDelete => self.delete_cleanup(),''',"actions")
change(app,'''            | QuickRow::RetroAchievements
            | QuickRow::Wifi
            | QuickRow::Controls''','''            | QuickRow::RetroAchievements
            | QuickRow::Cleanup
            | QuickRow::Wifi
            | QuickRow::Controls''',"submenu")
change(app,'''            | QuickRow::RaBackground
            | QuickRow::RetroAchievements
            | QuickRow::Nickname''','''            | QuickRow::RaBackground
            | QuickRow::RetroAchievements
            | QuickRow::Restart
            | QuickRow::Cleanup
            | QuickRow::CleanupScan
            | QuickRow::CleanupDelete
            | QuickRow::Achievements
            | QuickRow::AchievementList
            | QuickRow::Nickname''',"settings exhaustive")
change(app,'''            QuickRow::Cheats => {
                self.cheat_row = 0;''','''            QuickRow::Achievements => {
                self.achievement_row = 0;
                self.achievement_detail = false;
                self.in_game_menu = Some(QuickRow::AchievementList);
            }
            QuickRow::Cheats => {
                self.cheat_row = 0;''',"open achievements")
change(app,'''        if row == QuickRow::CheatList {
            return self.cheat_list_input(action);
        }''','''        if row == QuickRow::CheatList {
            return self.cheat_list_input(action);
        }
        if row == QuickRow::AchievementList {
            return self.achievement_list_input(action);
        }''',"achievements input")
change(app,'''            | QuickRow::CheatList
            | QuickRow::Guide''','''            | QuickRow::CheatList
            | QuickRow::Achievements
            | QuickRow::AchievementList
            | QuickRow::Guide''',"exhaustive in-game")
print("Ver.30 menu rows installed")
