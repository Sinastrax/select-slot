#!/usr/bin/env python3
"""Ver.30: cached in-game RetroAchievements viewer, no shelf access or extra network scanning."""
from pathlib import Path

def replace(path, old, new, reason):
    p=Path(path); s=p.read_text()
    n=s.count(old)
    if n!=1: raise SystemExit(f"{path}: {reason}: expected once, found {n}")
    p.write_text(s.replace(old,new,1))

service="crates/slot-achievements/src/lib.rs"
replace(service,
'''    presence: Mutex<Option<(u64, String)>>,''',
'''    presence: Mutex<Option<(u64, String)>>,
    /// Cloned cheaply by the paused in-game viewer; written by the evaluator only.
    viewer: Mutex<Option<Arc<AchievementView>>>,''',"viewer in worker status")
replace(service,
'''pub struct Service {
    controls:''',
'''#[derive(Clone, Debug)]
pub struct AchievementInfo {
    pub id: u32,
    pub title: String,
    pub description: String,
    pub points: u32,
    pub badge: Option<PathBuf>,
    pub unlocked: bool,
}

#[derive(Clone, Debug)]
pub struct AchievementView {
    pub title: String,
    pub entries: Vec<AchievementInfo>,
}

/// Active game only. The game cache is already loaded by RetroAchievements workers.
pub struct Service {
    controls:''',"public view structs")
replace(service,
'''    pub fn sync_progress(&self) -> Option<u8> {''',
'''    pub fn achievement_view(&self) -> Option<Arc<AchievementView>> {
        self.status.viewer.lock().ok().and_then(|v| v.clone())
    }

    pub fn sync_progress(&self) -> Option<u8> {''',"read snapshot API")
replace(service,
'''                    playing = None;
                    *status.presence.lock().unwrap() = None;''',
'''                    playing = None;
                    *status.presence.lock().unwrap() = None;
                    *status.viewer.lock().unwrap() = None;''',"clear viewer for new ROM")
replace(service,
'''                    playing = None;
                    *status.presence.lock().unwrap() = None;
                    let _ = loads.send(None);''',
'''                    playing = None;
                    *status.presence.lock().unwrap() = None;
                    *status.viewer.lock().unwrap() = None;
                    let _ = loads.send(None);''',"clear viewer on eject")
replace(service,
'''                evaluate(frame, &mut playing, &store, &notices, &mut unsaved);''',
'''                evaluate(frame, &mut playing, &store, &notices, &mut unsaved, &status);''',"first evaluator")
replace(service,
'''            evaluate(frame, &mut playing, &store, &notices, &mut unsaved);''',
'''            evaluate(frame, &mut playing, &store, &notices, &mut unsaved, &status);''',"second evaluator")
replace(service,
'''            if let Some(game) = playing.as_mut() {
                // Preserve hits for unchanged definitions.''',
'''            {
                let saved = store.lock().unwrap();
                let view = AchievementView {
                    title: prepared.game.title.clone(),
                    entries: prepared.game.achievements.iter()
                        .filter(|a| a.flags == 3)
                        .map(|a| AchievementInfo {
                            id: a.id,
                            title: a.title.clone(),
                            description: a.description.clone(),
                            points: a.points,
                            badge: badges::path(&saved.dir, &a.badge),
                            unlocked: prepared.unlocked.contains(&a.id)
                                || saved.unlocks.contains_key(&a.id)
                                || unsaved.contains_key(&a.id),
                        })
                        .collect(),
                };
                *status.viewer.lock().unwrap() = Some(Arc::new(view));
            }
            if let Some(game) = playing.as_mut() {
                // Preserve hits for unchanged definitions.''',"publish cached metadata")
replace(service,
'''    unsaved: &mut BTreeMap<u32, (Unlock, Notice)>,
) {''',
'''    unsaved: &mut BTreeMap<u32, (Unlock, Notice)>,
    status: &Arc<Status>,
) {''',"evaluator signature")
replace(service,
'''                        Ok(true) => {
                            let _ = notices.send(notice);
                        }''',
'''                        Ok(true) => {
                            if let Some(view) = status.viewer.lock().unwrap().as_mut() {
                                if let Some(a) = Arc::make_mut(view).entries.iter_mut()
                                    .find(|a| a.id == id) {
                                    a.unlocked = true;
                                }
                            }
                            let _ = notices.send(notice);
                        }''',"update viewer when awarded")

sess="crates/slot/src/session.rs"
replace(sess,
'''    pub fn achievement_sync_status(&self) -> slot_achievements::SyncStatus {''',
'''    pub fn achievement_view(&self) -> Option<std::sync::Arc<slot_achievements::AchievementView>> {
        self.achievements.achievement_view()
    }

    pub fn achievement_sync_status(&self) -> slot_achievements::SyncStatus {''',"session exposes view")
replace(sess,
'''        self.app.set_achievement_overview(self.achievements.overview());''',
'''        if self.app.in_game_menu() == Some(slot_ui::QuickRow::AchievementList) {
            self.app.set_achievement_view(self.achievements.achievement_view());
        }
        self.app.set_achievement_overview(self.achievements.overview());''',"snapshot on viewer while paused")

app="crates/slot/src/app.rs"
replace(app,
'''    ra_overview: Option<slot_achievements::Overview>,''',
'''    ra_overview: Option<slot_achievements::Overview>,
    achievement_view: Option<Arc<slot_achievements::AchievementView>>,
    achievement_row: usize,
    achievement_sort: bool,
    achievement_detail: bool,
    achievement_names: Vec<[(TexId, u32, u32); 2]>,
    achievement_values: Vec<[(TexId, u32, u32); 2]>,
    achievement_badges: Vec<Option<(TexId, u32, u32)>>,
    achievement_header: Option<(TexId, u32, u32)>,
    achievement_description: Option<(TexId, u32, u32)> ,''',"app viewer state")
replace(app,
'''            ra_overview: None,
            shelves,''',
'''            ra_overview: None,
            achievement_view: None,
            achievement_row: 0,
            achievement_sort: false,
            achievement_detail: false,
            achievement_names: Vec::new(),
            achievement_values: Vec::new(),
            achievement_badges: Vec::new(),
            achievement_header: None,
            achievement_description: None,
            shelves,''',"initialize view")
replace(app,
'''    pub fn take_achievement_action(&mut self) -> Option<slot_achievements::LibraryAction> {''',
'''    pub fn set_achievement_view(&mut self, view: Option<Arc<slot_achievements::AchievementView>>) {
        let same = match (&self.achievement_view, &view) {
            (None, None) => true,
            (Some(a), Some(b)) => Arc::ptr_eq(a, b),
            _ => false,
        };
        if !same {
            self.achievement_view = view;
            self.achievement_names.clear();
            self.achievement_values.clear();
            self.achievement_badges.clear();
            self.achievement_header = None;
            self.achievement_description = None;
        }
    }

    pub fn achievement_view_ref(&self) -> Option<&slot_achievements::AchievementView> {
        self.achievement_view.as_deref()
    }

    pub fn achievement_order(&self) -> Vec<usize> {
        let Some(v) = self.achievement_view.as_ref() else { return Vec::new() };
        let mut order: Vec<usize> = (0..v.entries.len()).collect();
        if self.achievement_sort {
            order.sort_by_key(|i| (v.entries[*i].unlocked, *i));
        }
        order
    }

    pub fn achievement_faces_ready(&self) -> bool {
        self.achievement_header.is_some() &&
            self.achievement_names.len() == self.achievement_order().len()
    }

    pub fn set_achievement_faces(
        &mut self,
        names: Vec<[(TexId, u32, u32); 2]>,
        values: Vec<[(TexId, u32, u32); 2]>,
        badges: Vec<Option<(TexId, u32, u32)>>,
        header: (TexId, u32, u32),
    ) {
        self.achievement_names = names;
        self.achievement_values = values;
        self.achievement_badges = badges;
        self.achievement_header = Some(header);
    }

    pub fn set_achievement_description(&mut self, face: Option<(TexId, u32, u32)>) {
        self.achievement_description = face;
    }

    fn achievement_list_input(&mut self, action: Action) {
        let count = self.achievement_order().len();
        match action {
            Action::GbaDown(Btn::Up) if count > 0 => {
                self.achievement_row = (self.achievement_row + count - 1) % count;
                self.achievement_description = None;
            }
            Action::GbaDown(Btn::Down) if count > 0 => {
                self.achievement_row = (self.achievement_row + 1) % count;
                self.achievement_description = None;
            }
            Action::GbaDown(Btn::A) => {
                self.achievement_detail = !self.achievement_detail;
            }
            Action::GbaDown(Btn::X) => {
                self.achievement_sort = !self.achievement_sort;
                self.achievement_row = 0;
                self.achievement_detail = false;
                self.achievement_names.clear();
                self.achievement_values.clear();
                self.achievement_badges.clear();
                self.achievement_description = None;
            }
            Action::GbaDown(Btn::B) => {
                if self.achievement_detail {
                    self.achievement_detail = false;
                } else {
                    self.in_game_menu = Some(QuickRow::Achievements);
                }
            }
            Action::QuickMenu => self.tap_in_game_menu(None),
            _ => {}
        }
    }

    pub fn achievement_selected_description(&self) -> Option<String> {
        let view = self.achievement_view.as_deref()?;
        let index = *self.achievement_order().get(self.achievement_row)?;
        let a = &view.entries[index];
        Some(format!("{}: {} ({} points) {}",
            a.title, a.description, a.points, if a.unlocked { "Unlocked" } else { "Locked" }))
    }

    pub fn achievement_description_ready(&self) -> bool {
        self.achievement_description.is_some()
    }

    pub fn take_achievement_action(&mut self) -> Option<slot_achievements::LibraryAction> {''',"app viewer handlers")
replace(app,
'''            if row == QuickRow::CheatList {
                let on: Vec<bool> = self.cheats.iter().map(|c| c.on).collect();''',
'''            if row == QuickRow::AchievementList {
                slot_ui::AchievementPage {
                    selected: self.achievement_row,
                    names: &self.achievement_names,
                    values: &self.achievement_values,
                    badges: &self.achievement_badges,
                    header: self.achievement_header,
                    detail: if self.achievement_detail { self.achievement_description } else { None },
                    faces: self.quick_menu_faces.as_ref(),
                    footer_top,
                    canvas: self.canvas(),
                }.draw(out);
            } else if row == QuickRow::CheatList {
                let on: Vec<bool> = self.cheats.iter().map(|c| c.on).collect();''',"draw custom viewer")

ui="crates/slot-ui/src/quick_menu.rs"
replace(ui,
'''/// The Cheats page over the game: a row per cheat with its On or Off, laid out, lit and scrolled''',
'''/// Read-only achievement list rendered within the existing paused game menu.
pub struct AchievementPage<'a> {
    pub selected: usize,
    pub names: &'a [[(TexId,u32,u32); 2]],
    pub values: &'a [[(TexId,u32,u32); 2]],
    pub badges: &'a [Option<(TexId,u32,u32)>],
    pub header: Option<(TexId,u32,u32)>,
    pub detail: Option<(TexId,u32,u32)>,
    pub faces: Option<&'a QuickMenuFaces>,
    pub footer_top: f32,
    pub canvas: Canvas,
}

impl AchievementPage<'_> {
    pub fn draw(&self, out: &mut Vec<Draw>) {
        out.push(Draw::Rect {
            x: 0.0, y: 0.0, w: self.canvas.w, h: self.footer_top,
            colour: [0.0,0.0,0.0,GROUND_SCRIM],
        });
        let count = self.names.len().min(self.values.len());
        let (start, len) = window(self.selected, count, QUICK_VISIBLE);
        let top = ((LEGEND_Y - QUICK_PITCH * len as f32)/2.0).max(76.0);
        if let Some((tex,w,h)) = self.header {
            push(out, tex, self.canvas.centred(w as f32), top - h as f32 - 17.0, w,h);
        }
        let Some(faces) = self.faces else { return };
        let right = self.canvas.w - QUICK_EDGE;
        for i in start..start + len {
            let y = top + QUICK_PITCH * (i-start) as f32 + TYPE_DROP;
            let lit = i == self.selected;
            if let Some(Some((tex,_,_))) = self.badges.get(i) {
                push(out,*tex, QUICK_LABEL_X - 32.0, y+1.0,24,24);
            }
            push_label(out,faces,self.names[i][lit as usize],
                QUICK_LABEL_X+8.0, y,lit);
            let (tex,w,h) = self.values[i][lit as usize];
            push(out,tex,right+MENU_PAD as f32-w as f32,y,w,h);
        }
        if let Some(bar) = scroll_bar(top,len,count,self.selected) {
            push_scroll(out,self.canvas,bar);
        }
        if let Some((tex,w,h)) = self.detail {
            out.push(Draw::Rect {x: 0.0,y: self.canvas.h*0.19,
                w: self.canvas.w,h: self.canvas.h*0.55,
                colour: [0.0,0.0,0.0,0.95]});
            push(out,tex,self.canvas.centred(w as f32),
                self.canvas.h*0.43-h as f32/2.0,w,h);
        }
    }
}

/// The Cheats page over the game: a row per cheat with its On or Off, laid out, lit and scrolled''',"achievement renderer")
ui_lib="crates/slot-ui/src/lib.rs"
replace(ui_lib,
'''visible_rows, CheatPage, MenuGround, QuickMenu, QuickMenuFaces, QuickRow, QuickScroll,''',
'''visible_rows, AchievementPage, CheatPage, MenuGround, QuickMenu, QuickMenuFaces, QuickRow, QuickScroll,''',"export viewer")

front="crates/slot/src/frontend.rs"
replace(front,
'''    cheat_names: CheatNames,
    wallpaper:''',
'''    cheat_names: CheatNames,
    wallpaper:''',"frontend uses existing renderer and state")
# Use a synchronous build only when the user opens this paused viewer. Cached images are bounded.
replace(front,
'''        sync_cheat_names(self.session.app_mut(), compositor, &mut self.cheat_names);''',
'''        sync_cheat_names(self.session.app_mut(), compositor, &mut self.cheat_names);
        sync_achievement_view(self.session.app_mut(), compositor);''',"build visible achievement faces")
replace(front,
'''fn sync_cheat_names(app: &mut App, compositor: &mut Compositor, state: &mut CheatNames) {''',
'''fn sync_achievement_view(app: &mut App, compositor: &mut Compositor) {
    if app.in_game_menu() != Some(QuickRow::AchievementList) {
        return;
    }
    if !app.achievement_faces_ready() {
        let view = app.achievement_view_ref();
        let order = app.achievement_order();
        let mut names=Vec::new();
        let mut values=Vec::new();
        let mut badges=Vec::new();
        let mut earned=0usize;
        let mut total=0u32;
        let mut received=0u32;
        if let Some(view) = view {
            for a in &view.entries {
                total += a.points;
                if a.unlocked {earned+=1;received+=a.points;}
            }
            for i in order {
                let a = &view.entries[i];
                let name = [false,true].map(|lit| {
                    let f=cheat_name_face(&a.title,lit);
                    let t=compositor.create_texture(f.w,f.h,&f.rgba);
                    (t,f.w,f.h)
                });
                let value=[false,true].map(|lit| {
                    let label = format!("{} {}",if a.unlocked {"✓"} else {"○"},a.points);
                    let f=quick_value_face(&label,lit);
                    let t=compositor.create_texture(f.w,f.h,&f.rgba);
                    (t,f.w,f.h)
                });
                let badge=a.badge.as_ref().and_then(|path| slot_achievements::load_badge(path))
                    .map(|pic| (compositor.create_texture(pic.width,pic.height,&pic.rgba),
                                pic.width,pic.height));
                names.push(name);values.push(value);badges.push(badge);
            }
        }
        let title=match app.achievement_view_ref() {
            Some(v) => format!("{} — {}/{} · {}/{} points",
                v.title,earned,v.entries.len(),received,total),
            None => "Achievements — connecting or no offline cache".into(),
        };
        let f=quick_description_face(&[&title]);
        let header=(compositor.create_texture(f.w,f.h,&f.rgba),f.w,f.h);
        app.set_achievement_faces(names,values,badges,header);
    }
    if !app.achievement_description_ready() {
        let description=app.achievement_selected_description().unwrap_or_default();
        let f=quick_description_face(&[&description]);
        if f.w>0 && f.h>0 {
            app.set_achievement_description(Some(
                (compositor.create_texture(f.w,f.h,&f.rgba),f.w,f.h)));
        }
    }
}

fn sync_cheat_names(app: &mut App, compositor: &mut Compositor, state: &mut CheatNames) {''',"frontend view synchronization")
print("Ver.30 in-game achievement browser installed")
