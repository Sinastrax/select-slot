#!/usr/bin/env python3
"""Use BaseOS hardware identity for the default multiplayer nickname.

A 640x480 panel cannot distinguish RG35XX H from RG35XX SP. Keep user
nickname overrides and non-nickname device behavior completely unchanged.
"""
from pathlib import Path

path = Path("crates/slot/src/app.rs")
source = path.read_text()
before = '''    fn device_name(&self) -> &'static str {
        match self.panel {
            (720, 480) => "RG SP",
            (640, 480) => "RG35XXSP",
            _ => "slot",
        }
    }'''
after = '''    fn device_name(&self) -> &'static str {
        // The RG35XX H and RG35XX SP both have 640x480 panels.
        // Panel resolution alone is not a hardware identity.
        // BaseOS reports its exact target (for example "rg35xxh").
        // Cache the immutable boot identifiers, not the panel dimensions.
        static HARDWARE: std::sync::OnceLock<(Option<String>, Option<String>)> =
            std::sync::OnceLock::new();
        let (target, model) = HARDWARE.get_or_init(|| {
            (
                crate::baseos::var("BASEOS_TARGET"),
                crate::baseos::var("BASEOS_MODEL"),
            )
        });
        Self::device_name_for(self.panel, target.as_deref(), model.as_deref())
    }

    /// Returns the default link-play nickname; custom nicknames take precedence
    /// in nickname(). Only known BaseOS IDs receive specific product names.
    fn device_name_for(
        panel: (u32, u32),
        target: Option<&str>,
        model: Option<&str>,
    ) -> &'static str {
        fn known(value: &str) -> Option<&'static str> {
            // Accept target IDs (rg35xxh) and display labels (RG35XX H),
            // including a possible "Anbernic" prefix.
            let cleaned: String = value.chars()
                .filter(|ch| ch.is_ascii_alphanumeric())
                .map(|ch| ch.to_ascii_lowercase())
                .collect();
            let key = cleaned.strip_prefix("anbernic").unwrap_or(&cleaned);
            match key {
                "rg35xxh" => Some("RG35XX H"),
                "rg35xxsp" => Some("RG35XXSP"),
                "rg34xxsp" => Some("RG34XXSP"),
                "rg35xxplus" => Some("RG35XX Plus"),
                "rg35xxpro" => Some("RG35XX Pro"),
                "rg40xxh" => Some("RG40XX H"),
                "rg40xxv" => Some("RG40XX V"),
                "rgcubexx" => Some("RG Cube XX"),
                _ => None,
            }
        }

        if let Some(name) = target.and_then(known).or_else(|| model.and_then(known)) {
            return name;
        }
        // Unknown named hardware should not falsely advertise itself as a SP.
        if target.is_some_and(|id| !id.trim().is_empty())
            || model.is_some_and(|id| !id.trim().is_empty())
        {
            return "slot";
        }

        // Preserve the old fallback for host/simulator setups without BaseOS.
        match panel {
            (720, 480) => "RG SP",
            (640, 480) => "RG35XXSP",
            _ => "slot",
        }
    }'''
assert source.count(before)==1, f"Expected one upstream nickname function; found {source.count(before)}"
path.write_text(source.replace(before,after,1))

path.open("a").write(r'''

#[cfg(test)]
mod hardware_nickname_regression {
    use super::App;

    #[test]
    fn rg35xx_h_and_sp_same_resolution_get_different_names() {
        let panel = (640, 480);
        assert_eq!(App::device_name_for(panel, Some("rg35xxh"), None), "RG35XX H");
        assert_eq!(App::device_name_for(panel, Some("rg35xxsp"), None), "RG35XXSP");
        assert_eq!(
            App::device_name_for(panel, Some("rg35xxh"), Some("RG35XX SP")),
            "RG35XX H",
            "the BaseOS target is authoritative if a model label disagrees"
        );
    }

    #[test]
    fn model_fallback_supports_display_names_and_other_anbernic_models() {
        assert_eq!(
            App::device_name_for((640, 480), None, Some("Anbernic RG35XX H")),
            "RG35XX H"
        );
        assert_eq!(
            App::device_name_for((720, 480), Some("rg34xxsp"), None),
            "RG34XXSP"
        );
        assert_eq!(
            App::device_name_for((640, 480), Some("rg40xxh"), None),
            "RG40XX H"
        );
    }

    #[test]
    fn unknown_named_device_is_not_misrepresented_as_sp() {
        assert_eq!(App::device_name_for((640, 480), Some("unknown-h700"), None), "slot");
        assert_eq!(App::device_name_for((640, 480), None, None), "RG35XXSP");
        assert_eq!(App::device_name_for((720, 480), None, None), "RG SP");
        assert_eq!(App::device_name_for((800, 600), None, None), "slot");
    }
}
''')
print("BaseOS target/model now determine default nickname; custom names unchanged.")
