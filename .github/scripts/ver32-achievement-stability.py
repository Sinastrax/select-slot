#!/usr/bin/env python3
"""Ver.32: bound achievement rendering to six reusable texture slots.

Repeated X sorting or Y refresh must not allocate one new GPU texture per
achievement, per state change. Keep ROM data, saves, shaders, firmware OTA and
the existing RetroAchievements evaluator untouched.
"""
from pathlib import Path

def change(path, before, after, why):
    p = Path(path)
    s = p.read_text()
    n = s.count(before)
    if n != 1:
        raise SystemExit(f"{path}: {why}: expected 1 anchor, got {n}")
    p.write_text(s.replace(before, after, 1))
    print(f"Ver32: {why}")

app = "crates/slot/src/app.rs"
ui = "crates/slot-ui/src/quick_menu.rs"
ui_lib = "crates/slot-ui/src/lib.rs"
front = "crates/slot/src/frontend.rs"
service = "crates/slot-achievements/src/lib.rs"

# The UI renderer and frontend must agree on the same six-row viewport.
change(ui,
'''pub const QUICK_VISIBLE: usize = 6;''',
'''pub const QUICK_VISIBLE: usize = 6;

/// Visible achievement rows; selected and total refer to the complete list.
pub fn achievement_page_window(selected: usize, total: usize) -> (usize, usize) {
    if total == 0 {
        return (0, 0);
    }
    window(selected.min(total - 1), total, QUICK_VISIBLE)
}''', "share achievement viewport math")
change(ui_lib,
'''visible_rows, achievement_detail_face, AchievementPage, CheatPage,''',
'''visible_rows, achievement_page_window, achievement_detail_face, AchievementPage, CheatPage,''',
"export bounded achievement window")

change(ui,
'''    pub selected: usize,
    pub names: &'a [[(TexId,u32,u32); 2]],''',
'''    pub selected: usize,
    pub total: usize,
    pub names: &'a [[(TexId,u32,u32); 2]],''',
"add total count independent from cached row textures")
change(ui,
'''        let count = self.names.len().min(self.values.len());
        let (start, len) = window(self.selected, count, QUICK_VISIBLE);''',
'''        let count = self.total;
        let (start, len) = achievement_page_window(self.selected, count);''',
"compute scroll over all achievements, not cached six")
change(ui,
'''        for i in start..start + len {
            let y = top + QUICK_PITCH * (i-start) as f32 + TYPE_DROP;
            let lit = i == self.selected;
            if let Some(Some((tex,_,_))) = self.badges.get(i) {
                push(out,*tex, QUICK_LABEL_X - 32.0, y+1.0,24,24);
            }
            push_label(out,faces,self.names[i][lit as usize],
                QUICK_LABEL_X+8.0, y,lit);
            let (tex,w,h) = self.values[i][lit as usize];
            push(out,tex,right+MENU_PAD as f32-w as f32,y,w,h);
        }''',
'''        for i in start..start + len {
            let local = i - start;
            // The frontend uploads exactly the visible window; never index an
            // off-screen achievement through a finite six-slot texture cache.
            let (Some(names), Some(values)) = (self.names.get(local), self.values.get(local)) else {
                break;
            };
            let y = top + QUICK_PITCH * local as f32 + TYPE_DROP;
            let lit = i == self.selected;
            if let Some(Some((tex,_,_))) = self.badges.get(local) {
                push(out,*tex, QUICK_LABEL_X - 32.0, y+1.0,24,24);
            }
            push_label(out,faces,names[lit as usize],
                QUICK_LABEL_X+8.0, y,lit);
            let (tex,w,h) = values[lit as usize];
            push(out,tex,right+MENU_PAD as f32-w as f32,y,w,h);
        }''',
"draw visible rows with local slot indexing")

change(app,
'''    achievement_sort: bool,
    achievement_detail: bool,''',
'''    achievement_sort: bool,
    achievement_faces_dirty: bool,
    achievement_visible_start: usize,
    achievement_detail: bool,''',
"track six-slot cache validity")
change(app,
'''    achievement_description: Option<(TexId, u32, u32)> ,''',
'''    achievement_description: Option<(TexId, u32, u32)> ,
    achievement_description_slot: Option<TexId>,''',
"retain description texture when selection changes")
change(app,
'''            achievement_sort: false,
            achievement_detail: false,''',
'''            achievement_sort: false,
            achievement_faces_dirty: true,
            achievement_visible_start: 0,
            achievement_detail: false,''',
"initialize six-slot cache")
change(app,
'''            achievement_description: None,
            shelves,''',
'''            achievement_description: None,
            achievement_description_slot: None,
            shelves,''',
"initialize reusable description texture")

change(app,
'''            self.achievement_view = view;
            self.achievement_names.clear();
            self.achievement_values.clear();
            self.achievement_badges.clear();
            self.achievement_header = None;
            self.achievement_description = None;''',
'''            self.achievement_view = view;
            // Preserve texture IDs: the compositor never releases abandoned
            // IDs during a session. Rebuild only the bounded visible slots.
            self.achievement_faces_dirty = true;
            self.achievement_header_dirty = true;
            self.achievement_description = None;''',
"retain GPU slots across refreshed achievement snapshots")
change(app,
'''    pub fn achievement_faces_ready(&self) -> bool {
        self.achievement_header.is_some() &&
            self.achievement_names.len() == self.achievement_order().len()
    }''',
'''    pub fn achievement_selected_row(&self) -> usize {
        self.achievement_row
    }

    pub fn achievement_reuse_faces(&self) -> (
        &[[(TexId, u32, u32); 2]],
        &[[(TexId, u32, u32); 2]],
        &[Option<(TexId, u32, u32)>],
    ) {
        (&self.achievement_names, &self.achievement_values, &self.achievement_badges)
    }

    pub fn achievement_faces_ready(&self) -> bool {
        let total = self.achievement_view.as_ref().map_or(0, |v| v.entries.len());
        let (start, len) = slot_ui::achievement_page_window(self.achievement_row, total);
        !self.achievement_faces_dirty
            && self.achievement_header.is_some()
            && self.achievement_visible_start == start
            && self.achievement_names.len() == len
            && self.achievement_values.len() == len
            && self.achievement_badges.len() == len
    }''',
"validate only visible achievement faces")
change(app,
'''        header: (TexId, u32, u32),
    ) {
        self.achievement_names = names;
        self.achievement_values = values;
        self.achievement_badges = badges;
        self.achievement_header = Some(header);
        self.achievement_header_dirty = false;
    }''',
'''        header: (TexId, u32, u32),
        visible_start: usize,
    ) {
        self.achievement_names = names;
        self.achievement_values = values;
        self.achievement_badges = badges;
        self.achievement_header = Some(header);
        self.achievement_visible_start = visible_start;
        self.achievement_faces_dirty = false;
        self.achievement_header_dirty = false;
    }''',
"record the actual visible window after face updates")
change(app,
'''    pub fn set_achievement_description(&mut self, face: Option<(TexId, u32, u32)>) {
        self.achievement_description = face;
    }''',
'''    pub fn achievement_description_texture(&self) -> Option<TexId> {
        self.achievement_description_slot
    }

    pub fn set_achievement_description(&mut self, face: Option<(TexId, u32, u32)>) {
        if let Some((tex, _, _)) = face {
            self.achievement_description_slot = Some(tex);
        }
        self.achievement_description = face;
    }''',
"reuse description texture after navigation")
change(app,
'''                self.achievement_names.clear();
                self.achievement_values.clear();
                self.achievement_badges.clear();
                self.achievement_header = None;
                self.achievement_description = None;
                self.in_game_menu = Some(QuickRow::AchievementList);''',
'''                self.achievement_faces_dirty = true;
                self.achievement_header_dirty = true;
                self.achievement_description = None;
                self.in_game_menu = Some(QuickRow::AchievementList);''',
"avoid dropping cached textures when opening viewer")
change(app,
'''                self.achievement_sort = !self.achievement_sort;
                self.achievement_row = 0;
                self.achievement_detail = false;
                self.achievement_names.clear();
                self.achievement_values.clear();
                self.achievement_badges.clear();
                self.achievement_description = None;''',
'''                self.achievement_sort = !self.achievement_sort;
                self.achievement_row = 0;
                self.achievement_detail = false;
                self.achievement_faces_dirty = true;
                self.achievement_description = None;''',
"X sorting never invalidates GPU texture handles")
change(app,
'''                    selected: self.achievement_row,
                    names: &self.achievement_names,''',
'''                    selected: self.achievement_row,
                    total: self.achievement_view.as_ref().map_or(0, |v| v.entries.len()),
                    names: &self.achievement_names,''',
"pass total list length to viewport renderer")

# Replace the Ver.30-31 whole-list synchronizer, including the Ver.31
# header-only update, with bounded reusable texture slots.
p = Path(front)
s = p.read_text()
start = s.index("fn sync_achievement_view(app: &mut App, compositor: &mut Compositor) {")
end = s.index("fn sync_cheat_names(app: &mut App, compositor: &mut Compositor, state: &mut CheatNames) {", start)
new = '''fn achievement_upload(
    compositor: &mut Compositor, previous: Option<TexId>,
    w: u32, h: u32, rgba: &[u8],
) -> TexId {
    if let Some(tex) = previous {
        compositor.update_texture(tex, w, h, rgba);
        tex
    } else {
        compositor.create_texture(w, h, rgba)
    }
}

fn sync_achievement_view(app: &mut App, compositor: &mut Compositor) {
    if app.in_game_menu() != Some(QuickRow::AchievementList) {
        return;
    }
    let total = app.achievement_view_ref().map_or(0, |v| v.entries.len());
    let (start, len) = slot_ui::achievement_page_window(app.achievement_selected_row(), total);
    let rebuild = !app.achievement_faces_ready();
    let mut rows = None;
    if rebuild {
        let order = app.achievement_order();
        let (old_names, old_values, old_badges) = app.achievement_reuse_faces();
        let mut names = Vec::with_capacity(len);
        let mut values = Vec::with_capacity(len);
        let mut badges = Vec::with_capacity(len);
        if let Some(view) = app.achievement_view_ref() {
            for (slot, index) in order.into_iter().skip(start).take(len).enumerate() {
                let a = &view.entries[index];
                let name = [false, true].map(|lit| {
                    let f = cheat_name_face(&a.title, lit);
                    let previous = old_names.get(slot).map(|pair| pair[lit as usize].0);
                    (achievement_upload(compositor, previous, f.w, f.h, &f.rgba), f.w, f.h)
                });
                let value = [false, true].map(|lit| {
                    let label = if !a.unlocked {
                        if let Some((value, target)) = a.measured {
                            format!("{value}/{target}")
                        } else {
                            format!("○ {}", a.points)
                        }
                    } else {
                        format!("✓ {}", a.points)
                    };
                    let f = quick_value_face(&label, lit);
                    let previous = old_values.get(slot).map(|pair| pair[lit as usize].0);
                    (achievement_upload(compositor, previous, f.w, f.h, &f.rgba), f.w, f.h)
                });
                let badge = a.badge.as_ref()
                    .and_then(|path| slot_achievements::load_badge(path))
                    .map(|pic| {
                        let previous = old_badges.get(slot).and_then(|b| b.map(|(tex, _, _)| tex));
                        let tex = achievement_upload(
                            compositor, previous, pic.width, pic.height, &pic.rgba
                        );
                        (tex, pic.width, pic.height)
                    });
                names.push(name);
                values.push(value);
                badges.push(badge);
            }
        }
        rows = Some((names, values, badges));
    }
    if rebuild || app.achievement_header_dirty() {
        let title = match app.achievement_view_ref() {
            Some(v) => {
                let earned = v.entries.iter().filter(|a| a.unlocked).count();
                let total: u32 = v.entries.iter().map(|a| a.points).sum();
                let received: u32 = v.entries.iter().filter(|a| a.unlocked)
                    .map(|a| a.points).sum();
                format!("{} — {}/{} ({}%) · {}/{} pts",
                    v.title, earned, v.entries.len(),
                    if v.entries.is_empty() { 0 } else { earned * 100 / v.entries.len() },
                    received, total)
            }
            None => "Achievements — connecting or no offline cache".into(),
        };
        let state = format!("{} | Y Refresh | X Sort", app.achievement_connection_label());
        let f = quick_description_face(&[&title, &state]);
        let previous = app.achievement_header_texture().map(|(tex, _, _)| tex);
        let tex = achievement_upload(compositor, previous, f.w, f.h, &f.rgba);
        if let Some((names, values, badges)) = rows {
            app.set_achievement_faces(names, values, badges, (tex, f.w, f.h), start);
        } else {
            app.update_achievement_header_size(f.w, f.h);
        }
    }
    if !app.achievement_description_ready() {
        let description = app.achievement_selected_description().unwrap_or_default();
        let f = slot_ui::achievement_detail_face(&description);
        if f.w > 0 && f.h > 0 {
            let previous = app.achievement_description_texture();
            let tex = achievement_upload(compositor, previous, f.w, f.h, &f.rgba);
            app.set_achievement_description(Some((tex, f.w, f.h)));
        }
    }
}

'''
p.write_text(s[:start] + new + s[end:])
print("Ver32: replace whole-list uploads with six reusable GPU slots")

# Each rapid Y tap was previously allowed to enqueue another ROM rehash,
# network session request and view re-publication. Coalesce short bursts.
change(service,
'''    game_detail: Mutex<Option<(u64, String)>>,
    last_measured: Mutex<Option<Instant>>,''',
'''    game_detail: Mutex<Option<(u64, String)>>,
    last_measured: Mutex<Option<Instant>>,
    last_manual_refresh: Mutex<Option<Instant>>,''',
"store refresh burst guard")
change(service,
'''        generation != 0
            && self.enabled.load(Ordering::Acquire)
            && self.controls.send(Control::Refresh(generation)).is_ok()''',
'''        if generation == 0 || !self.enabled.load(Ordering::Acquire) {
            return false;
        }
        let Ok(mut last) = self.status.last_manual_refresh.lock() else {
            return false;
        };
        // Ignore repeated Y presses while a slow network request is pending.
        // Returning true makes a coalesced request a harmless no-op in the UI.
        if last.as_ref().is_some_and(|at| at.elapsed() < Duration::from_secs(20)) {
            return true;
        }
        *last = Some(Instant::now());
        drop(last);
        if self.controls.send(Control::Refresh(generation)).is_err() {
            *self.status.last_manual_refresh.lock().unwrap() = None;
            return false;
        }
        true''',
"coalesce repeated Y into one refresh attempt")
change(service,
'''                    active_rom = Some(load.clone());
                    status.set_game(generation, GameConnection::Checking);''',
'''                    active_rom = Some(load.clone());
                    *status.last_manual_refresh.lock().unwrap() = None;
                    status.set_game(generation, GameConnection::Checking);''',
"reset Y guard on new ROM")

# A lightweight, deterministic layout regression test requires no GPU.
p = Path(ui)
p.write_text(p.read_text() + r'''

#[cfg(test)]
mod achievement_viewport_burst_tests {
    use super::*;
    #[test]
    fn very_large_achievement_lists_stay_in_six_visible_rows() {
        for total in [0, 1, 5, 6, 7, 50, 200, 500] {
            for selected in [0, 1, 5, 6, 50, 199, 499] {
                let (start, len) = achievement_page_window(selected, total);
                assert!(len <= QUICK_VISIBLE);
                assert!(start + len <= total);
                if selected < total {
                    assert!(start <= selected && selected < start + len);
                }
            }
        }
    }
}
''')
print("Ver32: 500-item viewport regression added")
