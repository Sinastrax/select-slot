#!/usr/bin/env python3
"""Filter RetroAchievements server warning pseudo-achievements as official rc_client does.

See rcheevos rc_client.c: RC_CLIENT_ACHIEVEMENT_WARNING_ID=101000001.
The injected 'Warning: Unknown Emulator' / 'Unsupported Game' entries are not
real game achievements. Softcore tracking is allowed for unregistered clients.
"""
from pathlib import Path

p=Path("crates/slot-achievements/src/storage.rs")
s=p.read_text()
old='''    #[serde(rename = "Achievements")]
    pub achievements: Vec<Achievement>,
}'''
new='''    #[serde(rename = "Achievements", deserialize_with = "real_achievements")]
    pub achievements: Vec<Achievement>,
}

/// rcheevos rc_client filters server-injected compatibility warnings from
/// real achievement sets. Their IDs start at 101000001, and they may be
/// reported as zero-point unlocked entries. Preserve the underlying ROM and
/// account data: only parsed game metadata is filtered.
const RA_CLIENT_WARNING_FIRST_ID: u32 = 101_000_001;

fn real_achievements<'de, D>(deserializer: D) -> Result<Vec<Achievement>, D::Error>
where
    D: serde::Deserializer<'de>,
{
    let mut entries = Vec::<Achievement>::deserialize(deserializer)?;
    let count = entries.iter()
        .filter(|a| a.id >= RA_CLIENT_WARNING_FIRST_ID).count();
    if count != 0 {
        eprintln!("slot: RetroAchievements: server supplied {count} client compatibility warning(s); excluded from the real achievement set");
        entries.retain(|a| a.id < RA_CLIENT_WARNING_FIRST_ID);
    }
    Ok(entries)
}'''
if s.count(old)!=1:
    raise SystemExit(f"Ver34 RA warning filter: expected one Game field, found {s.count(old)}")
p.write_text(s.replace(old,new,1))
print("Ver34: non-game server warnings excluded during metadata parsing")

with Path("crates/slot-achievements/src/tests.rs").open("a") as f:
    f.write(r'''

#[test]
fn injected_unknown_emulator_warning_is_not_counted_as_a_game_achievement() {
    let genuine = achievement("0xH000000=1");
    let mut warning = genuine.clone();
    warning.id = 101_000_001;
    warning.title = "Warning: Unknown Emulator".into();
    warning.points = 0;
    let data = Game {
        presence: String::new(),
        id: 668,
        console: 5,
        title: "Pokemon Emerald".into(),
        achievements: vec![genuine.clone(), warning],
    };
    let serialized = serde_json::to_string(&data).unwrap();
    let parsed: Game = serde_json::from_str(&serialized).unwrap();
    assert_eq!(parsed.achievements.len(), 1);
    assert_eq!(parsed.achievements[0].id, genuine.id);
}
''')
print("Ver34: client warning regression installed")
