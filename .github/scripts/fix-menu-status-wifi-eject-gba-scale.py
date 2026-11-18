#!/usr/bin/env python3
"""Ver.22: keep Wi-Fi through actual ejection, render menu status with menu
ink, and expose a meaningful GBA 2x scaling choice on 720x480 panels.

All changes are applied after the previous Ver.21 patch. The verified GBA/GB/
GBC shader and color code, OTA safety, and other device layouts are untouched.
"""
from pathlib import Path
import re

def edit(path, edits):
    p=Path(path)
    value=p.read_text()
    for old, new, description in edits:
        n=value.count(old)
        if n != 1:
            raise SystemExit(f"{path}: {description}: expected 1 match; got {n}")
        value=value.replace(old, new, 1)
    p.write_text(value)
    print("Updated",path)

edit("crates/slot/src/app.rs", [
    (
'''    battery_percent: slot_ui::Printed,
    bolt: Option<TexId>,''',
'''    battery_percent: slot_ui::Printed,
    /// Separately rasterised with the menu's HUD_INK: text in top corners
    /// must not reuse dark ink from the light-theme shelf footer.
    menu_battery_percent: slot_ui::Printed,
    bolt: Option<TexId>,''',
    "menu percent texture field"),
    (
'''    shelf_clock: slot_ui::Printed,
    achievement_sync: Option<slot_ui::SyncIndicator>,''',
'''    shelf_clock: slot_ui::Printed,
    menu_clock: slot_ui::Printed,
    achievement_sync: Option<slot_ui::SyncIndicator>,''',
    "menu clock texture field"),
    (
'''            battery_percent: slot_ui::Printed::default(),
            bolt: None,''',
'''            battery_percent: slot_ui::Printed::default(),
            menu_battery_percent: slot_ui::Printed::default(),
            bolt: None,''',
    "menu percent initialization"),
    (
'''            shelf_clock: slot_ui::Printed::default(),
            achievement_sync: None,''',
'''            shelf_clock: slot_ui::Printed::default(),
            menu_clock: slot_ui::Printed::default(),
            achievement_sync: None,''',
    "menu clock initialization"),
    (
'''    fn gauge(&self) -> slot_ui::Gauge {
        slot_ui::Gauge {
            battery: self.battery,
            percent: self.battery_percent,
            display: self.state.battery_display,
        }
    }

    pub fn set_shelf_clock_face(&mut self, face: TexId, w: u32) {
        self.shelf_clock = slot_ui::Printed::new(face, w);
    }''',
'''    fn gauge(&self) -> slot_ui::Gauge {
        slot_ui::Gauge {
            battery: self.battery,
            percent: self.battery_percent,
            display: self.state.battery_display,
        }
    }

    pub fn set_menu_battery_percent_face(&mut self, face: TexId, w: u32) {
        self.menu_battery_percent = slot_ui::Printed::new(face, w);
    }

    fn menu_gauge(&self) -> slot_ui::Gauge {
        let mut gauge = self.gauge();
        gauge.percent = self.menu_battery_percent;
        gauge
    }

    pub fn set_shelf_clock_face(&mut self, face: TexId, w: u32) {
        self.shelf_clock = slot_ui::Printed::new(face, w);
    }

    pub fn set_menu_clock_face(&mut self, face: TexId, w: u32) {
        self.menu_clock = slot_ui::Printed::new(face, w);
    }''',
    "separate menu faces while preserving shelf footer"),
    (
'''    fn wifi_wanted(&self) -> bool {
        if self.seated_cart().is_some() {''',
'''    fn wifi_wanted(&self) -> bool {
        // Ejecting still reports a seated cartridge, even after the game
        // begins closing. Treat that animation as a return to the shelf.
        // Do NOT test wifi_up() here: DHCP/association may go down briefly
        // while leaving the core, and issuing Release would kill both
        // wpa_supplicant and udhcpc. If Wi-Fi was not held while gaming,
        // start rejoining the saved network during ejection.
        if matches!(self.phase, Phase::Ejecting { .. }) {
            return !self.state.wifi_off
                && !self.link_active()
                && self.prejoin.is_none()
                && !self.shutting_down()
                && (self.wifi_held || self.has_saved());
        }
        if self.seated_cart().is_some() {''',
    "actual eject phase must retain/reacquire wireless"),
])
p = Path("crates/slot/src/app.rs")
src = p.read_text()
pattern = r'(slot_ui::draw_corners\(\s*self\.canvas\(\),\s*)self\.gauge\(\),(\s*)self\.hud_bolt,(\s*)self\.shelf_clock,'
src, n = re.subn(pattern, r'\1self.menu_gauge(),\2self.hud_bolt,\3self.menu_clock,', src)
if n != 2:
    raise SystemExit(f"Expected exactly two menu-corner paths, got {n}")
p.write_text(src)
print("Both main quick-menu and in-game menu corners use menu-specific text textures")

edit("crates/slot/src/frontend.rs", [
    (
'''    shelf: Option<TexId>,
    picked: Option<slot_ui::ClockPicker>,
    shown: String,
    battery: String,
    battery_tex: Option<TexId>,''',
'''    shelf: Option<TexId>,
    menu_shelf: Option<TexId>,
    picked: Option<slot_ui::ClockPicker>,
    shown: String,
    menu_shown: String,
    battery: String,
    battery_tex: Option<TexId>,
    menu_battery: String,
    menu_battery_tex: Option<TexId>,''',
    "separate menu raster texture cache"),
    (
'''    if shown != clocks.shown {
        let face = word_ink(&shown, clocks.ink);
        clocks.shown = shown;
        let w = face.w;
        let id = upload(compositor, &mut clocks.shelf, face);
        app.set_shelf_clock_face(id, w);
    }
    let platform_shown''',
'''    if shown != clocks.shown {
        let face = word_ink(&shown, clocks.ink);
        clocks.shown = shown.clone();
        let w = face.w;
        let id = upload(compositor, &mut clocks.shelf, face);
        app.set_shelf_clock_face(id, w);
    }
    // Menu corners sit on dark backgrounds in both theme modes. They use
    // HUD_INK (like the battery outline) instead of the light-theme footer's
    // dark ink, and must not be invalidated by shelf-theme changes.
    if shown != clocks.menu_shown {
        let face = word_ink(&shown, slot_ui::HUD_INK);
        clocks.menu_shown = shown;
        let w = face.w;
        let id = upload(compositor, &mut clocks.menu_shelf, face);
        app.set_menu_clock_face(id, w);
    }
    let platform_shown''',
    "menu clock face always rendered in HUD ink"),
    (
'''    if battery_shown != clocks.battery {
        clocks.battery = battery_shown.clone();
        if !battery_shown.is_empty() {
            let face = word_ink(&battery_shown, clocks.ink);
            let w = face.w;
            let id = upload(compositor, &mut clocks.battery_tex, face);
            app.set_battery_percent_face(id, w);
        }
    }
}''',
'''    if battery_shown != clocks.battery {
        clocks.battery = battery_shown.clone();
        if !battery_shown.is_empty() {
            let face = word_ink(&battery_shown, clocks.ink);
            let w = face.w;
            let id = upload(compositor, &mut clocks.battery_tex, face);
            app.set_battery_percent_face(id, w);
        }
    }
    if battery_shown != clocks.menu_battery {
        clocks.menu_battery = battery_shown.clone();
        if !battery_shown.is_empty() {
            let face = word_ink(&battery_shown, slot_ui::HUD_INK);
            let w = face.w;
            let id = upload(compositor, &mut clocks.menu_battery_tex, face);
            app.set_menu_battery_percent_face(id, w);
        }
    }
}''',
    "menu battery-percent face always rendered in HUD ink"),
])

# A native 240x160 GBA has 3x = the entire 720x480 panel. Originally Fit,
# Integer (3x), and Full Screen were visually identical there and the app
# hid the Scale row. Offer a true 2x integer option only for that panel, while
# retaining Fit/full-screen at 3x and leaving all other systems and panel
# layouts unchanged.
edit("crates/slot-gfx/src/placement.rs", [
    (
'''    if let Some([x, y, w, h]) = table_placement(size, picture, sizing) {''',
'''    if window == (720, 480) && picture == GBA && sizing == Sizing::Integer {
        let (sx, sy) = (OUT_W as f32 / 720.0, OUT_H as f32 / 480.0);
        return GameLayout {
            panel: false,
            rect: [120.0 * sx, 80.0 * sy, 480.0 * sx, 320.0 * sy],
        };
    }
    if let Some([x, y, w, h]) = table_placement(size, picture, sizing) {''',
    "meaningful 2x GBA integer scaling on 720x480"),
])

with Path("crates/slot-gfx/tests/placement.rs").open("a") as out:
    out.write("""
#[test]
fn gba_720x480_now_has_a_genuine_smaller_2x_integer_choice() {
    let smaller = game_layout((720, 480), (240, 160), Sizing::Integer);
    let fitted = game_layout((720, 480), (240, 160), Sizing::Band);
    assert!(!smaller.panel);
    assert_eq!(px((720, 480), smaller), (120, 80, 480, 320));
    assert_ne!(smaller, fitted, "GBA Scale must offer two distinct pictures");
    // All other device and GB/GBC native scaling remain unchanged.
    assert_eq!(px((640, 480), game_layout((640, 480), (240, 160), Sizing::Integer)), (80, 53, 480, 320));
    assert_eq!(px((720, 480), game_layout((720, 480), (160, 144), Sizing::Integer)), (120, 24, 480, 432));
}
""")

with Path("crates/slot/tests/wifi_ui.rs").open("a") as out:
    out.write("""
#[test]
fn unplugging_while_wlan_is_reconnecting_never_stops_its_service() {
    let _g = serial();
    let fake = Fake::demo();
    let no_lease = fake.no_lease.clone();
    let (_d, mut a, log) = booted(true, fake);
    settle(&mut a);
    join_home(&mut a);
    a.apply(Action::Insert);
    frames(&mut a, 2);
    assert!(a.wifi().held);
    assert_eq!(count(&log, "stop"), 0);
    // DHCP may temporarily drop around core teardown. The ejection
    // must not translate that into an intentional Wi-Fi shutdown.
    no_lease.store(true, std::sync::atomic::Ordering::SeqCst);
    a.apply(Action::Eject);
    frames(&mut a, 2);
    assert!(matches!(a.phase(), Phase::Ejecting { .. }));
    assert_eq!(count(&log, "stop"), 0, "eject killed the Wi-Fi daemons");
    assert!(a.wifi().held, "the radio was released during cartridge removal");
    no_lease.store(false, std::sync::atomic::Ordering::SeqCst);
    settle(&mut a);
    assert!(a.wifi().held, "Wi-Fi did not survive return to shelf");
}

#[test]
fn wifi_off_during_ejection_remains_an_explicit_shutdown() {
    let _g = serial();
    let (_d, mut a, log) = on_shelf();
    settle(&mut a);
    join_home(&mut a);
    a.apply(Action::Insert);
    frames(&mut a, 2);
    a.apply(Action::Eject);
    a.set_wifi_off(true);
    frames(&mut a, 2);
    assert!(!a.wifi().held);
    assert!(count(&log, "stop") >= 1);
    assert_eq!(count(&log, "start"), 1);
}
""")

# Verify actual Draw::Tex identifiers used by menu corners, not merely the
# ink-selection helper. The status bar's icon remains separate from its text.
Path("crates/slot/tests/menu_status.rs").write_text("""mod common;

use common::{app_booting_at, tmp_root_with_carts, CLOCK_IS_SET};
use slot_input::Action;
use slot_store::{write_slot_state, Appearance, SlotState};
use slot_gfx::{Draw, TexId};

#[test]
fn light_theme_menu_draws_separate_bright_clock_and_battery_text() {
    let root = tmp_root_with_carts(&["Emerald", "Fusion"]);
    write_slot_state(root.path(), &SlotState {
        appearance: Appearance::Light,
        clock_set: true,
        ..SlotState::default()
    }).unwrap();
    let (mut app, _) = app_booting_at(root.path(), CLOCK_IS_SET);
    app.tick_ms(app.now()+1_000);
    app.set_shelf_clock_face(TexId::from_raw(8801), 30);
    app.set_battery_percent_face(TexId::from_raw(8802), 30);
    app.set_menu_clock_face(TexId::from_raw(8803), 30);
    app.set_menu_battery_percent_face(TexId::from_raw(8804), 30);
    app.apply(Action::QuickMenu);
    let mut out = Vec::new();
    app.draw(&mut out);
    let has = |id| out.iter().any(|d| matches!(d, Draw::Tex { tex, .. } if *tex == TexId::from_raw(id)));
    assert!(has(8803), "Menu clock was not drawn");
    assert!(has(8804), "Menu battery percentage was not drawn");
    assert!(!has(8801), "Menu reused the shelf clock ink");
    assert!(!has(8802), "Menu reused the shelf battery ink");
}
""")
with Path("crates/slot/src/app.rs").open("a") as out:
    out.write("""
#[cfg(test)]
mod eject_wifi_policy_regression {
    use super::{App, Phase};

    #[test]
    fn ejecting_a_cart_is_no_longer_treated_as_active_gameplay_for_wifi() {
        let mut app = App::new(Vec::new());
        app.phase = Phase::Ejecting {
            cart: "Emerald".into(),
            t: 0.0,
        };
        app.wifi_held = true;
        assert!(app.wifi_wanted(), "ejection must preserve held WLAN even with no DHCP address");
        app.state.wifi_off = true;
        assert!(!app.wifi_wanted(), "explicit Wi-Fi Off must still win");
    }
}
""")

print("Added H700 top-corner drawing, Wi-Fi ejection, and GBA scale regressions")
