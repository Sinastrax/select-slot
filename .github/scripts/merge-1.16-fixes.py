#!/usr/bin/env python3
"""Resolve renderer API overlap between the v1.15 select. slot. patches and Slot v1.16.

Slot 1.16 moved FrameBlend/LCD response into ghost.rs. Keep that upstream
implementation while preserving our Authentic correction and fast-forward paths.
Fail loudly when expected merged source changes.
"""
from pathlib import Path

gfx = Path("crates/slot-gfx/src")
pipeline = gfx / "pipeline.rs"
p = pipeline.read_text()

old_enum = """/// How each new frame meets the ones before it, at the game's own size before any scaling.
/// Authentic draws its LCD response except during fast-forward.
#[derive(Copy, Clone, PartialEq, Eq, Debug, Default)]
pub enum FrameBlend {
    #[default]
    Off,
    /// Each frame half and half with the one before it.
    Mix,
    /// Authentic's LCD response for the screen in play: each pixel slow to change, slower
    /// while it turns lighter.
    Ghosting,
}

"""
assert p.count(old_enum) == 1, "Expected obsolete FrameBlend enum not found"
p = p.replace(old_enum, "", 1)

old = "    screen: Screen,\n    ghost: Ghost,"
new = "    screen: Screen,\n    lcd: Lcd,\n    ghost: Ghost,"
assert p.count(old) == 1, "GamePass LCD field context changed"
p = p.replace(old, new, 1)

old = "            screen: Screen::Gba,\n            ghost,"
new = "            screen: Screen::Gba,\n            lcd: Lcd::Gba,\n            ghost,"
assert p.count(old) == 1, "GamePass LCD default context changed"
p = p.replace(old, new, 1)

old = "    fn blend(&self) -> FrameBlend {"
new = """    fn response(&self) -> [f32; 2] {
        self.lcd.response()
    }

    fn blend(&self) -> FrameBlend {"""
assert p.count(old) == 1, "GamePass blend selector moved"
p = p.replace(old, new, 1)
pipeline.write_text(p)

fbo = gfx / "fbo.rs"
s = fbo.read_text()

# Keep only one set_frame_blend and cut_frame_blend method, with the
# newest upstream set_lcd method and our additional Authentic controls.
first = """    pub fn set_frame_blend(&mut self, blend: crate::FrameBlend) {
        self.game.set_blend(blend, &self.quad);
    }

    pub fn set_authentic_fast_forward"""
assert s.count(first) == 1, "Old frame-blend method moved"
s = s.replace(first, "    pub fn set_authentic_fast_forward", 1)

old_cut = """    /// The game's picture jumped (another game, a state load, a reset): blend nothing of
    /// what came before into the next frame.
    pub fn cut_frame_blend(&mut self) {
        self.game.cut();
    }

    pub fn set_authentic_colour_correction"""
assert s.count(old_cut) == 1, "Old frame-blend cut method moved"
s = s.replace(old_cut, "    pub fn set_authentic_colour_correction", 1)
assert s.count("pub fn set_frame_blend(") == 1
assert s.count("pub fn cut_frame_blend(") == 1
fbo.write_text(s)

menu = Path("crates/slot-ui/src/quick_menu.rs")
q = menu.read_text()
old_count = "pub const SYSTEM: [QuickRow; 8] = ["
assert q.count(old_count) == 1, "Upstream system settings layout changed"
q = q.replace(old_count, "pub const SYSTEM: [QuickRow; 9] = [", 1)
menu.write_text(q)

power = Path("crates/slot-power/src/power.rs")
p = power.read_text()
old = "    pub fn battery(&self) -> Option<Battery> {"
new = """    // Slot 1.16 bottom-panel control, retained alongside our menu-only idle blanking.
    pub fn set_bottom_backlight(&mut self, on: bool) {
        self.platform.set_bottom_backlight(on);
    }

    pub fn battery(&self) -> Option<Battery> {"""
assert p.count(old) == 1 and "pub fn set_bottom_backlight(" not in p
power.write_text(p.replace(old, new, 1))

app = Path("crates/slot/src/app.rs")
a = app.read_text()
old = "        let turbo_off = slot_store::legacy_turbo_off(root);\n"
assert a.count(old) == 1, "Removed upstream legacy turbo migration changed"
a = a.replace(old, "", 1)
old = """        if turbo_off {
            app.turbo_off_moves_to_controls(root);
        }
"""
assert a.count(old) == 1, "Removed upstream turbo migration block changed"
a = a.replace(old, "", 1)
app.write_text(a)

# The core picker/link changes overlap in open_game_menu. Restore the complete
# upstream .2 dispatcher so armGBA's cable path and the existing mGBA/gpSP
# restrictions stay together instead of retaining a malformed mixed hunk.
a = app.read_text()
start = a.index("    fn open_game_menu(&mut self) {")
end = a.index("\n    fn open_cable_menu(&mut self)", start)
function = '''    fn open_game_menu(&mut self) {
        if self.game_menu.is_some() {
            return;
        }
        if self.link_active() {
            return self.refuse();
        }
        if !self.has_wifi_hardware() {
            self.hud.toast(Toast::NoWifi, self.now());
            return;
        }
        let wireless = || {
            self.seated()
                .is_some_and(|stem| self.link_mode(stem).0 == LinkKind::Wireless)
        };
        match self.core {
            Core::Gambatte => {
                self.hud.toast(Toast::NeedsMgba, self.now());
                return;
            }
            Core::Armgba => {
                let refused = match self.platform {
                    Platform::Gba if self.wireless_only() => Some(Toast::NeedsGpsp),
                    Platform::Gba => None,
                    Platform::Gb | Platform::Gbc => Some(Toast::NeedsMgba),
                    Platform::Gbav => Some(Toast::NoLink),
                    #[cfg(feature = "nds")]
                    Platform::Nds => Some(Toast::NoLink),
                };
                match refused {
                    Some(toast) => self.hud.toast(toast, self.now()),
                    None => self.open_cable_menu(),
                }
                return;
            }
            Core::Mgba => {
                match wireless() {
                    true => self.hud.toast(Toast::NeedsGpsp, self.now()),
                    false => self.open_cable_menu(),
                }
                return;
            }
            Core::Gpsp => {}
            #[cfg(feature = "nds")]
            Core::Dsperate => {}
        }
        if self.platform != Platform::Gba {
            self.hud.toast(Toast::NoLink, self.now());
            return;
        }
        let carried = self
            .seated()
            .and_then(|stem| self.auto_link(stem))
            .is_some_and(|(cart, _)| link_carried(&cart.code, &cart.title));
        if !carried {
            self.hud.toast(Toast::NoLink, self.now());
            return;
        }
        if self.core != Core::Gpsp {
            self.hud.toast(Toast::NeedsGpsp, self.now());
            return;
        }
        let hardware = self
            .seated()
            .map_or(LinkKind::Cable, |stem| self.link_mode(stem).0);
        self.link_hardware = hardware;
        self.radio_down();
        self.radio.ask(RadioJob::Warm);
        self.learn_game();
        self.game_menu = Some(GameMenu::Pick(self.last_role));
    }
'''
a = a[:start] + function + a[end:]
app.write_text(a)

# The armGBA upstream update and select. slot.'s prior SameBoy migration
# touched the same core-selection file. Preserve the old config migration
# while adding armGBA as a real selectable core.
store_core = Path("crates/slot-store/src/core.rs")
c = store_core.read_text()
assert c.count("    Gambatte,\n    Sameboy,") == 1, "Core enum overlap changed"
c = c.replace("    Gambatte,\n    Sameboy,", "    Gambatte,\n    Armgba,", 1)
for old, new, label in [
    ('            Core::Gambatte => "gambatte",\n            Core::Sameboy => "sameboy",',
     '            Core::Gambatte => "gambatte",\n            Core::Armgba => "armgba",', "core name"),
    ('            Core::Gambatte => "Gambatte",\n            Core::Sameboy => "SameBoy",',
     '            Core::Gambatte => "Gambatte",\n            Core::Armgba => "armGBA",', "core label"),
    ('            "gambatte" => Some(Core::Gambatte),\n            // Migrate cartridge choices made while SameBoy was the alternate core.',
     '            "gambatte" => Some(Core::Gambatte),\n            "armgba" => Some(Core::Armgba),\n            // Migrate cartridge choices made while SameBoy was the alternate core.', "core parse"),
]:
    assert c.count(old) == 1, f"armGBA {label} overlap changed"
    c = c.replace(old, new, 1)
old = """        .unwrap_or_else(|| match platform {
            Platform::Gb | Platform::Gbc if gb_core == Core::Gambatte => Core::Gambatte,"""
new = """        .unwrap_or_else(|| match platform {
            Platform::Gba => Core::Armgba,
            Platform::Gbav => Core::Mgba,
            Platform::Gb | Platform::Gbc if gb_core == Core::Gambatte => Core::Gambatte,"""
assert c.count(old) == 1, "GBA default core fallback changed"
store_core.write_text(c.replace(old, new, 1))

# SameBoy was not bundled by select. slot. Keep its old config key as a
# migration to mGBA, but remove the dead enum variant so armGBA's index and
# the optional DS core remain aligned with Core::ALL and the cartridge art.
c = store_core.read_text()
for old, new, label in [
    ("    Armgba,\n    Sameboy,", "    Armgba,", "legacy variant"),
    ('            Core::Sameboy => "sameboy",\n', "", "legacy name"),
    ('            Core::Sameboy => "SameBoy",\n', "", "legacy label"),
    ('            Core::Gambatte | Core::Sameboy => matches!(platform, Platform::Gb | Platform::Gbc),',
     '            Core::Gambatte => matches!(platform, Platform::Gb | Platform::Gbc),', "legacy platform"),
    ('            Platform::Gb | Platform::Gbc if matches!(gb_core, Core::Mgba | Core::Sameboy) => Core::Mgba,',
     '            Platform::Gb | Platform::Gbc if gb_core == Core::Mgba => Core::Mgba,', "legacy fallback"),
]:
    if c.count(old) == 1:
        c = c.replace(old, new, 1)
    elif label not in ("legacy variant", "legacy name", "legacy label"):
        raise AssertionError(f"SameBoy {label} overlap changed")
store_core.write_text(c)

state = Path("crates/slot-store/src/slot_state.rs")
s = state.read_text()
assert s.count("Core::Mgba | Core::Gpsp | Core::Gambatte | Core::Sameboy") == 1
state.write_text(s.replace("Core::Mgba | Core::Gpsp | Core::Gambatte | Core::Sameboy",
                            "Core::Mgba | Core::Gpsp | Core::Gambatte | Core::Armgba", 1))

app = Path("crates/slot/src/app.rs")
a = app.read_text()
a = a.replace("Core::Sameboy | Core::Mgba", "Core::Mgba")
a = a.replace("Core::Mgba | Core::Sameboy", "Core::Mgba")
a = a.replace("Core::Gambatte | Core::Sameboy", "Core::Gambatte")
a = a.replace("self.core == Core::Sameboy || self.core == Core::Mgba", "self.core == Core::Mgba")
assert "Core::Sameboy" not in a, "Legacy SameBoy app branches remain"
app.write_text(a)

core_options = Path("crates/slot/src/core.rs")
o = core_options.read_text()
for old, label in [
    ('''        Core::Sameboy => Some((
            "sameboy_color_correction_mode",
            if on { "emulate hardware" } else { "off" },
        )),
''', "colour option"),
    ('        Core::Sameboy => ("sameboy_interframe_blending", "off"),\n', "blend option"),
    ('''    // SameBoy has no interframe-blending core option.
    if which == Core::Sameboy { return; }
''', "blend shim"),
    ('        (Core::Sameboy, _) => Vec::new(),\n', "palette option"),
]:
    assert o.count(old) == 1, f"SameBoy {label} overlap changed"
    o = o.replace(old, "", 1)
# armGBA's own LCD effects resize/filter the image and conflict with Slot's
# selected shader; upstream disables that option on every armGBA launch.
blend = "        Core::Gambatte => (\"gambatte_mix_frames\", \"disabled\"),\n"
armgba_blend = blend + "        Core::Armgba => (\"armgba_lcd_effects\", \"disabled\"),\n"
assert o.count(blend) == 1 and 'Core::Armgba => ("armgba_lcd_effects", "disabled")' not in o
o = o.replace(blend, armgba_blend, 1)
core_options.write_text(o)

session = Path("crates/slot/src/session.rs")
ss = session.read_text()
assert ss.count("Core::Mgba => crate::cheats::load(&root, platform, &stem, &rom),") == 1
ss = ss.replace("Core::Mgba => crate::cheats::load(&root, platform, &stem, &rom),",
                "Core::Mgba | Core::Armgba => crate::cheats::load(&root, platform, &stem, &rom),", 1)
assert ss.count("Core::Gpsp | Core::Gambatte | Core::Sameboy => Vec::new(),") == 1
ss = ss.replace("Core::Gpsp | Core::Gambatte | Core::Sameboy => Vec::new(),",
                "Core::Gpsp | Core::Gambatte => Vec::new(),", 1)
assert ss.count("if running && matches!(core, Core::Mgba | Core::Sameboy)") == 1
ss = ss.replace("if running && matches!(core, Core::Mgba | Core::Sameboy)",
                "if running && core == Core::Mgba", 1)
session.write_text(ss)

# Git's ours-side resolution can splice both generations into an invalid
# function body. Rebuild the small option dispatcher from the pinned .2 API,
# retaining select. slot.'s verified frame skip and SGB behavior. The next
# customization stage adds the SGB-safe Gambatte color-correction exception.
core_options = Path("crates/slot/src/core.rs")
o = core_options.read_text()
start = o.index("pub fn apply_core_options(")
end = o.index("\n#[cfg(test)]", start)
function = '''pub fn apply_core_options(
    core: &mut LibretroCore,
    which: Core,
    platform: Platform,
    serial: &str,
    firmware: bool,
    colour: bool,
    palette: Option<GbColors>,
) {
    if matches!(which, Core::Mgba | Core::Gpsp) {
        core.set_option(&format!("{}_frameskip", which.as_str()), "auto");
    }
    match which {
        Core::Mgba => {
            core.set_option("mgba_sgb_borders", "OFF");
            match palette {
                Some(GbColors::SgbAuto) => {
                    core.set_option("mgba_gb_model", "Super Game Boy");
                    core.set_option("mgba_gb_colors_preset", "2");
                    core.set_option("mgba_gb_colors", "Auto");
                }
                Some(p) => {
                    core.set_option("mgba_gb_model", "Game Boy");
                    core.set_option("mgba_gb_colors_preset", "0");
                    core.set_option("mgba_gb_colors", p.core_name());
                }
                None => {
                    core.set_option("mgba_gb_model", "Autodetect");
                    core.set_option("mgba_gb_colors_preset", "1");
                    core.set_option("mgba_gb_colors", "GBC Dark Green →A");
                }
            }
            if let Some((key, value)) = colour_option(which, platform, colour) {
                core.set_option(key, value);
            }
        }
        Core::Gambatte => {
            core.set_option("gambatte_gb_hwmode", "Auto");
            for (key, value) in palette_options(which, palette.unwrap_or(GbColors::Auto)) {
                core.set_option(key, value);
            }
            if let Some((key, value)) = colour_option(which, platform, colour) {
                core.set_option(key, value);
            }
        }
        Core::Gpsp => {
            core.set_option("gpsp_serial", serial);
            core.set_option("gpsp_rtc_time_source", "system");
            if firmware {
                core.set_option("gpsp_boot_mode", "bios");
            }
            if let Some((key, value)) = colour_option(which, platform, colour) {
                core.set_option(key, value);
            }
        }
        Core::Armgba => {
            for (key, value) in armgba_options(platform, firmware, colour) {
                core.set_option(key, value);
            }
        }
        #[cfg(feature = "nds")]
        Core::Dsperate => {}
    }
}
'''
o = o[:start] + function + o[end:]
core_options.write_text(o)

print("Integrated GPU blending, nickname, USB/dual-panel APIs and removed turbo setting")
