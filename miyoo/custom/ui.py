"""Miyoo menu/status customizations; no user-facing Restart action."""
from .patcher import edit, version_label

# Miyoo UI: bounded scrolling, high-contrast menu HUD, and About version.
# Neither the settings page nor the About screen offers Restart.
# All quick-menu pages use the existing viewport/scroll logic.
edit("crates/slot-ui/src/quick_menu.rs", [
    ('''fn scrolls(page: &[QuickRow]) -> bool {
    [
        &QuickRow::CONTROLS[..],
        &QuickRow::SHORTCUTS,
        &QuickRow::GENERAL,
        &QuickRow::PLAY_SCREEN,
    ]
    .contains(&page)
}''',
     '''fn scrolls(page: &[QuickRow]) -> bool {
    // Gameplay, settings and future menu pages share a bounded viewport.
    !page.is_empty()
}'''),
])

edit("crates/slot/src/app.rs", [
    ('''    battery_percent: slot_ui::Printed,
    bolt: Option<TexId>,''',
     '''    battery_percent: slot_ui::Printed,
    menu_battery_percent: slot_ui::Printed,
    bolt: Option<TexId>,'''),
    ('''    shelf_clock: slot_ui::Printed,
    hud: Hud,''',
     '''    shelf_clock: slot_ui::Printed,
    menu_clock: slot_ui::Printed,
    hud: Hud,'''),
    ('''            battery_percent: slot_ui::Printed::default(),
            bolt: None,''',
     '''            battery_percent: slot_ui::Printed::default(),
            menu_battery_percent: slot_ui::Printed::default(),
            bolt: None,'''),
    ('''            shelf_clock: slot_ui::Printed::default(),
            hud: Hud::new(),''',
     '''            shelf_clock: slot_ui::Printed::default(),
            menu_clock: slot_ui::Printed::default(),
            hud: Hud::new(),'''),
    ('''    pub fn set_battery_percent_face(&mut self, face: TexId, w: u32) {
        self.battery_percent = slot_ui::Printed::new(face, w);
    }''',
     '''    pub fn set_battery_percent_face(&mut self, face: TexId, w: u32) {
        self.battery_percent = slot_ui::Printed::new(face, w);
    }

    pub fn set_menu_battery_percent_face(&mut self, face: TexId, w: u32) {
        self.menu_battery_percent = slot_ui::Printed::new(face, w);
    }'''),
    ('''    pub fn set_shelf_clock_face(&mut self, face: TexId, w: u32) {
        self.shelf_clock = slot_ui::Printed::new(face, w);
    }''',
     '''    pub fn set_shelf_clock_face(&mut self, face: TexId, w: u32) {
        self.shelf_clock = slot_ui::Printed::new(face, w);
    }

    pub fn set_menu_clock_face(&mut self, face: TexId, w: u32) {
        self.menu_clock = slot_ui::Printed::new(face, w);
    }'''),
    ('''                    self.battery_percent,
                    self.hud_bolt,
                    self.shelf_clock,
                    out,
                );
            }
        }
        self.draw_menu_footer(out);''',
     '''                    self.menu_battery_percent,
                    self.hud_bolt,
                    self.menu_clock,
                    out,
                );
            }
        }
        self.draw_menu_footer(out);'''),
])

# Menu status uses a bright raster independent from the shelf theme.
# The original clock/battery and framebuffer paths are unchanged.
edit("crates/slot/src/frontend.rs", [
    ('''    shelf: Option<TexId>,
    picked: Option<String>,
    shown: String,
    battery: String,
    battery_tex: Option<TexId>,''',
     '''    shelf: Option<TexId>,
    menu_clock_tex: Option<TexId>,
    picked: Option<String>,
    shown: String,
    battery: String,
    battery_tex: Option<TexId>,
    menu_battery_tex: Option<TexId>,'''),
    ('''        app.set_shelf_clock_face(id, w);
    }
    let platform_shown''',
     '''        app.set_shelf_clock_face(id, w);
        let face = word_ink(&shown, slot_ui::HUD_INK);
        let menu_w = face.w;
        let menu_id = upload(compositor, &mut clocks.menu_clock_tex, face);
        app.set_menu_clock_face(menu_id, menu_w);
    }
    let platform_shown'''),
    ('''            app.set_battery_percent_face(id, w);
        }
    }
}

fn sync_game_bezel''',
     '''            app.set_battery_percent_face(id, w);
            let face = word_ink(&battery_shown, slot_ui::HUD_INK);
            let menu_w = face.w;
            let menu_id = upload(compositor, &mut clocks.menu_battery_tex, face);
            app.set_menu_battery_percent_face(menu_id, menu_w);
        }
    }
}

fn sync_game_bezel'''),
    ('''        version: build.version,''',
     f'''        version: "{version_label}",'''),
])

# Match the H700 status treatment in shelf quick settings as well as the
# already updated in-game menu. The original shelf remains theme colored.
edit("crates/slot/src/app.rs", [
    ('''            Phase::QuickMenu { row } => QuickMenu {
                row: *row,''',
     '''            Phase::QuickMenu { row } => {
                QuickMenu {
                row: *row,'''),
    ('''            }
            .draw(out),
            Phase::Shelf => {''',
     '''                }
                .draw(out);
                slot_ui::draw_corners(
                    self.canvas(),
                    self.battery,
                    self.menu_battery_percent,
                    self.hud_bolt,
                    self.menu_clock,
                    out,
                );
            }
            Phase::Shelf => {'''),
])

edit("crates/slot/src/frontend.rs", [
    ('''        clocks.shown = shown;''',
     '''        clocks.shown = shown.clone();'''),
])


# Upstream Slot 1.8.1's About sticker lets X restart the hardware.
# This Miyoo build deliberately has no user-facing Restart control.
# Keep B/Menu back navigation and remove the misleading X legend.
edit("crates/slot/src/app.rs", [
    ('''            Phase::About if action == Action::GbaDown(Btn::X) => self.begin_restart(),
''',
     ''''''),
    ('''        let [back, _, _, _, restart, ..] = match self.light() {
            true => faces.legend_light,
            false => faces.legend,
        };''',
     '''        let back = match self.light() {
            true => faces.legend_light[0],
            false => faces.legend[0],
        };'''),
    ('''        self.draw_side_legend(restart, true, LINK_LEGEND_Y, out);
''',
     ''''''),
])
