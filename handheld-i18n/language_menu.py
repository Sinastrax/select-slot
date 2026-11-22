"""Add the same saved language selector to the two pinned Slot source trees."""
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
menu = root / "crates/slot-ui/src/quick_menu.rs"
app = root / "crates/slot/src/app.rs"

# The More.slot patch carries this setting itself. Keep this source-prep helper
# safe to rerun across both patched and upstream-only trees.
if menu.exists() and "QuickRow::Language" in menu.read_text():
    print("Language setting is already present in this source tree")
    raise SystemExit(0)

if (menu.exists() and 'const GENERIC: [QuickRow;' in menu.read_text()):
    def replace(source, before, after, count=1):
        if source.count(before) != count:
            raise RuntimeError(f"Language menu anchor changed: {before!r}")
        return source.replace(before, after)

    s = menu.read_text()
    s = replace(s, "    Theme,\n", "    Theme,\n    Language,\n", 1)
    s, n = re.subn(
        r"const GENERIC: \[QuickRow; (\d+)\]",
        lambda m: f"const GENERIC: [QuickRow; {int(m.group(1)) + 1}]",
        s,
        count=1,
    )
    if n != 1:
        raise RuntimeError("Language menu could not find the generic row count")
    s = replace(s, "    QuickRow::Theme,\n    QuickRow::Wallpaper,", "    QuickRow::Theme,\n    QuickRow::Language,\n    QuickRow::Wallpaper,")
    s = replace(s, "pub const GENERAL: [QuickRow; 15]", "pub const GENERAL: [QuickRow; 16]")
    s = replace(s, "        QuickRow::Theme,\n        QuickRow::BootLogo,", "        QuickRow::Theme,\n        QuickRow::Language,\n        QuickRow::BootLogo,")
    s = replace(s, "            | QuickRow::Theme\n", "            | QuickRow::Theme\n            | QuickRow::Language\n")
    s = replace(s, 'QuickRow::Theme => "Theme",', 'QuickRow::Theme => "Theme",\n            QuickRow::Language => "Language",')
    s = replace(s, "    Authentic,\n", "    Authentic,\n    English,\n    German,\n", 1)
    s = replace(s, "pub const ALL: [QuickValue; 52]", "pub const ALL: [QuickValue; 54]")
    s = replace(s, "        QuickValue::Authentic,\n", "        QuickValue::Authentic,\n        QuickValue::English,\n        QuickValue::German,\n", 1)
    s = replace(s, 'QuickValue::Authentic => "Authentic",', 'QuickValue::Authentic => "Authentic",\n            QuickValue::English => "English",\n            QuickValue::German => "Deutsch",')
    menu.write_text(s)

    s = app.read_text()
    s = replace(s, "    root: Option<PathBuf>,", "    root: Option<PathBuf>,\n    language_german: bool,")
    s = replace(s, "            root: None,", "            root: None,\n            language_german: false,")
    s = replace(s, "        app.root = Some(root.to_path_buf());", "        app.root = Some(root.to_path_buf());\n        app.language_german = std::fs::read_to_string(root.join(\"Config/language.txt\"))\n            .is_ok_and(|v| v.trim() == \"de\");")
    s = replace(s, "            QuickRow::WallpaperTint => Some(match self.state.wallpaper_tint {", "            QuickRow::Language => Some(if self.language_german { QuickValue::German } else { QuickValue::English }),\n            QuickRow::WallpaperTint => Some(match self.state.wallpaper_tint {")
    s = replace(s, "            | QuickRow::Hardcore\n            | QuickRow::Theme\n            | QuickRow::Clock", "            | QuickRow::Hardcore\n            | QuickRow::Theme\n            | QuickRow::Language\n            | QuickRow::Clock")
    s = replace(s, "            | QuickRow::Controls\n            | QuickRow::Bezel => return,", "            | QuickRow::Controls\n            | QuickRow::Language\n            | QuickRow::Bezel => return,")
    s = replace(s, "        if row == QuickRow::Theme {", "        if row == QuickRow::Language {\n            if let Some(root) = self.root.as_ref() {\n                let path = root.join(\"Config/language.txt\");\n                let next = if self.language_german { \"en\\n\" } else { \"de\\n\" };\n                if slot_store::atomic_write(&path, next.as_bytes()).is_ok() {\n                    self.language_german = !self.language_german;\n                }\n            }\n            return;\n        }\n        if row == QuickRow::Theme {")
    app.write_text(s)
    print("Added the saved English/German selector to UnsloT's General settings")
    raise SystemExit(0)

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
s = replace(s, 'QuickRow::Theme => "Theme",', 'QuickRow::Theme => "Theme",\n            QuickRow::Language => "Language",')
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
