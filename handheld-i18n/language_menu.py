"""Add the same saved language selector to the two pinned Slot source trees."""
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
menu = root / "crates/slot-ui/src/quick_menu.rs"
app = root / "crates/slot/src/app.rs"

def replace(source, before, after, count=1):
    if source.count(before) != count:
        raise RuntimeError(f"Language menu anchor changed: {before!r}")
    return source.replace(before, after)

s = menu.read_text()
for label, kind, extra in [('ALL', 'QuickRow', 1), ('GENERAL', 'QuickRow', 1), ('ALL', 'QuickValue', 2)]:
    pattern = rf'(pub const {label}: \[{kind}; )(\d+)'
    s, n = re.subn(pattern, lambda m: m[1] + str(int(m[2]) + extra), s)
    assert n == 1
s = replace(s, '\n    Theme,', '\n    Theme,\n    Language,')
s = replace(s, '\n        QuickRow::Theme,', '\n        QuickRow::Theme,\n        QuickRow::Language,', 2)
s = replace(s, '| QuickRow::Theme\n', '| QuickRow::Theme\n            | QuickRow::Language\n')
s = replace(s, 'QuickRow::Theme => "Theme",', 'QuickRow::Theme => "Theme",\n            QuickRow::Language => "Language (restart)",')
s = replace(s, '\n    Dark,', '\n    Dark,\n    English,\n    German,')
s = replace(s, '\n        QuickValue::Dark,', '\n        QuickValue::Dark,\n        QuickValue::English,\n        QuickValue::German,')
s = replace(s, 'QuickValue::Dark => "Dark",', 'QuickValue::Dark => "Dark",\n            QuickValue::English => "English",\n            QuickValue::German => "Deutsch",')
menu.write_text(s)
s = app.read_text()
s = replace(s, 'pub struct App {', 'pub struct App {\n    german_next_boot: bool,')
s = replace(s, '            root: None,', '            root: None,\n            german_next_boot: false,')
s = replace(s, 'app.root = Some(root.to_path_buf());', '''app.root = Some(root.to_path_buf());
        app.german_next_boot = std::fs::read_to_string(root.join("Config/language.txt"))
            .is_ok_and(|value| value.trim() == "de");''')
s = replace(s, 'QuickRow::Theme => Some(if self.light()', '''QuickRow::Language => Some(if self.german_next_boot { QuickValue::German } else { QuickValue::English }),
            QuickRow::Theme => Some(if self.light()''')
s = replace(s, '| QuickRow::Theme\n', '| QuickRow::Theme\n            | QuickRow::Language\n')
s = replace(s, 'QuickRow::Theme => s.appearance', '''QuickRow::Language => {
                if let Some(root) = self.root.as_ref() {
                    let file = root.join("Config/language.txt");
                    let temp = file.with_extension("tmp");
                    let language = if self.german_next_boot { "en" } else { "de" };
                    if std::fs::write(&temp, language).and_then(|_| std::fs::rename(temp, file)).is_ok() {
                        self.german_next_boot = !self.german_next_boot;
                    }
                }
            }
            QuickRow::Theme => s.appearance''')
app.write_text(s)
