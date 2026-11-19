"""Build the German frontend from the same prepared sources as the English one.

Only exact source literals in these UI modules are eligible. ROM metadata,
credentials, filenames, wire protocol fields and user input are never filtered
at runtime. Static Rust slices and format strings remain compile-time checked.
"""
from pathlib import Path
from collections import Counter
import json
import re
import sys

root = Path(sys.argv[1]) / 'crates'
catalog = {}
for entry in Path(__file__).with_name('de.tsv').read_text().splitlines():
    en, de = entry.split('\t')
    if en in catalog or Counter(re.findall(r'\{[^}]*\}', en)) != Counter(re.findall(r'\{[^}]*\}', de)):
        raise ValueError(entry)
    catalog[en] = de

modules = {
    'slot-ui': 'quick_menu keyboard toast guide shot_viewer clock receipt polaroids power_menu plate edit_text shelf slot_chrome hud sticker',
    'slot': 'app frontend network_faces networks invite_card achievement_ui studio_view link_start link_screen wifi/attempt romm/install romm/jobs update',
    'slot-store': 'bindings slot_state',
    'slot-achievements': 'network lib',
}
literal = re.compile(r'"([^"\\\n]*(?:\\.[^"\\\n]*)*)"')
seen = set()
for crate, names in modules.items():
    for name in names.split():
        path = root / crate / 'src' / (name + '.rs')
        if not path.exists():
            continue
        source = path.read_text()
        def render(m):
            en = m[1]
            if en not in catalog:
                return m[0]
            prefix = source[max(0, m.start()-60):m.start()]
            if re.search(r'(?:\.join|Path::new|include_bytes!|include_str!)\(\s*$', prefix):
                return m[0]
            if name == 'bindings' and en in ('Select', 'Start'):
                return m[0]  # Printed button names.
            seen.add(en)
            return json.dumps(catalog[en], ensure_ascii=False)
        updated = literal.sub(render, source)
        if source != updated:
            path.write_text(updated)
if not {'Language (restart)', 'Settings', 'Resume', 'Brightness', 'General', 'Off'} <= seen:
    raise ValueError('Incomplete pinned menu tree')
print(f'German frontend: {len(seen)} distinct translated source strings')
