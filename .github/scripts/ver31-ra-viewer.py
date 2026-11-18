#!/usr/bin/env python3
"""Ver.31: refresh active ROM on Y and display the actual online session stage.

Read-only per-game metadata and measured achievements; no save data operations.
"""
from pathlib import Path

def change(path,old,new,note):
    p=Path(path);s=p.read_text()
    count=s.count(old)
    if count!=1: raise SystemExit(f"Ver31 {path}: {note}: expected 1, found {count}")
    p.write_text(s.replace(old,new,1))
    print(f"Ver31 {path}: {note}")

session="crates/slot/src/session.rs"
app="crates/slot/src/app.rs"
ache="crates/slot-achievements/src/lib.rs"
runtime="crates/slot-achievements/src/runtime.rs"
frontend="crates/slot/src/frontend.rs"

change(session,
'''    pub fn achievement_game_connection(&self) -> slot_achievements::GameConnection {
        self.achievements.game_connection()
    }''',
'''    pub fn achievement_game_connection(&self) -> slot_achievements::GameConnection {
        self.achievements.game_connection()
    }

    pub fn achievement_game_detail(&self) -> Option<String> {
        self.achievements.game_connection_detail()
    }''',"session status access")
change(session,
'''        if self.app.in_game_menu() == Some(slot_ui::QuickRow::AchievementList) {
            self.app.set_achievement_view(self.achievements.achievement_view());
        }
        self.app.set_achievement_overview(self.achievements.overview());''',
'''        if self.app.in_game_menu() == Some(slot_ui::QuickRow::AchievementList) {
            self.app.set_achievement_view(self.achievements.achievement_view());
            self.app.set_achievement_connection(
                self.achievements.game_connection(),
                self.achievements.game_connection_detail(),
            );
        }
        if self.app.take_achievement_refresh() {
            if !self.achievements.refresh_active() {
                self.app.set_achievement_connection(
                    slot_achievements::GameConnection::Disabled,
                    Some("Login not configured or no active game".into()),
                );
            }
        }
        self.app.set_achievement_overview(self.achievements.overview());''',
"route Y refresh on existing session worker")
change(app,
'''    achievement_view: Option<Arc<slot_achievements::AchievementView>>,
    achievement_row: usize,''',
'''    achievement_view: Option<Arc<slot_achievements::AchievementView>>,
    achievement_connection: String,
    achievement_refresh: bool,
    achievement_row: usize,''',"UI status and action flag")
change(app,
'''            achievement_view: None,
            achievement_row: 0,''',
'''            achievement_view: None,
            achievement_connection: "Checking achievement session".into(),
            achievement_refresh: false,
            achievement_row: 0,''',"initialize refresh state")
change(app,
'''    pub fn achievement_view_ref(&self) -> Option<&slot_achievements::AchievementView> {''',
'''    pub fn set_achievement_connection(
        &mut self,
        state: slot_achievements::GameConnection,
        detail: Option<String>,
    ) {
        let name = match state {
            slot_achievements::GameConnection::Disabled => "Off",
            slot_achievements::GameConnection::Checking => "Connecting",
            slot_achievements::GameConnection::OfflineReady => "Cached; not yet connected",
            slot_achievements::GameConnection::Online => "Connected",
            slot_achievements::GameConnection::NoAchievements => "Not registered",
        };
        let next = match detail {
            Some(detail) if !detail.is_empty() => format!("{name}: {detail}"),
            _ => name.into(),
        };
        if self.achievement_connection != next {
            self.achievement_connection = next;
            self.achievement_header = None;
        }
    }

    pub fn achievement_connection_label(&self) -> &str {
        &self.achievement_connection
    }

    pub fn take_achievement_refresh(&mut self) -> bool {
        std::mem::take(&mut self.achievement_refresh)
    }

    pub fn achievement_view_ref(&self) -> Option<&slot_achievements::AchievementView> {''',
"Expose online status and Y refresh action")
change(app,
'''            Action::GbaDown(Btn::X) => {
                self.achievement_sort = !self.achievement_sort;''',
'''            Action::GbaDown(Btn::Y) if !self.achievement_detail => {
                self.achievement_refresh = true;
                self.achievement_connection = "Refreshing ROM and achievements".into();
                self.achievement_header = None;
            }
            Action::GbaDown(Btn::X) => {
                self.achievement_sort = !self.achievement_sort;''',"Y triggers nonblocking refresh inside viewer")

change(frontend,
'''        let f=quick_description_face(&[&title]);
        let header=(compositor.create_texture(f.w,f.h,&f.rgba),f.w,f.h);''',
'''        let state = format!("{} | Y Refresh | X Sort", app.achievement_connection_label());
        let f=quick_description_face(&[&title, &state]);
        let header=(compositor.create_texture(f.w,f.h,&f.rgba),f.w,f.h);''',
"Show connection state and refresh control at top of viewer")

# The selected achievement's measured values are provided by the actual
# rcheevos runtime. They do not represent automatically credited old milestones.
change(runtime,
'''    fn rc_runtime_deactivate_achievement(runtime: *mut c_void, id: u32);''',
'''    fn rc_runtime_deactivate_achievement(runtime: *mut c_void, id: u32);
    fn rc_runtime_get_achievement_measured(
        runtime: *mut c_void, id: u32,
        measured_value: *mut u32, measured_target: *mut u32,
    ) -> c_int;''',"rcheevos measured progress API")
change(runtime,
'''    pub fn deactivate(&mut self, id: u32) {''',
'''    pub fn measured(&self, id: u32) -> Option<(u32, u32)> {
        let mut value = 0u32;
        let mut target = 0u32;
        let ok = unsafe {
            rc_runtime_get_achievement_measured(self.ptr.as_ptr(), id, &mut value, &mut target)
        };
        (ok != 0 && target > 0).then_some((value.min(target), target))
    }

    pub fn deactivate(&mut self, id: u32) {''',
"read real measured achievement progress")
change(ache,
'''    pub unlocked: bool,
}''',
'''    pub unlocked: bool,
    /// Measured progress from rcheevos, if this achievement defines it.
    pub measured: Option<(u32, u32)>,
}''',"public viewer measured field")
change(ache,
'''                                || unsaved.contains_key(&a.id),
                        })''',
'''                                || unsaved.contains_key(&a.id),
                            measured: None,
                        })''',"initial viewer measured state")
change(ache,
'''    game_detail: Mutex<Option<(u64, String)>>,
    /// Cloned cheaply by the paused in-game viewer; written by the evaluator only.''',
'''    game_detail: Mutex<Option<(u64, String)>>,
    last_measured: Mutex<Option<Instant>>,
    /// Cloned cheaply by the paused in-game viewer; written by the evaluator only.''',
"throttle progress sampling, not the emulator")
change(ache,
'''                    *status.viewer.lock().unwrap() = None;
                    // Cached games can start evaluating''',
'''                    *status.viewer.lock().unwrap() = None;
                    *status.last_measured.lock().unwrap() = None;
                    // Cached games can start evaluating''',
"reset progress sampling for a newly launched ROM")
# This appears twice (load+unload); only reset needed on load, leaving unload unchanged.
# Insert the sample after evaluating a frame. It runs only every 5 seconds and
# publishes a new Arc only when progress actually changed; UI receives it only
# while the paused viewer is open, preventing per-frame texture churn.
change(ache,
'''                game.runtime.deactivate(id);
            }
        }
    }
    let _ = frame.recycle.try_send(frame.ram);''',
'''                game.runtime.deactivate(id);
            }
            let due = status.last_measured.lock().unwrap()
                .as_ref().is_none_or(|at| at.elapsed() >= Duration::from_secs(5));
            if due {
                *status.last_measured.lock().unwrap() = Some(Instant::now());
                let sample: Vec<_> = game.achievements.keys()
                    .map(|id| (*id, game.runtime.measured(*id))).collect();
                if let Ok(mut lock) = status.viewer.lock() {
                    if let Some(view) = lock.as_mut() {
                        let changed = sample.iter().any(|(id, value)| {
                            view.entries.iter().any(|entry|
                                entry.id == *id && entry.measured != *value)
                        });
                        if changed {
                            let entries = &mut Arc::make_mut(view).entries;
                            for (id, measured) in sample {
                                if let Some(entry) = entries.iter_mut().find(|e| e.id == id) {
                                    entry.measured = measured;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    let _ = frame.recycle.try_send(frame.ram);''',
"track real measured achievements without synthetic unlocks")
change(frontend,
'''                    let label = format!("{} {}",if a.unlocked {"✓"} else {"○"},a.points);''',
'''                    let label = if !a.unlocked {
                        if let Some((value,target)) = a.measured {
                            format!("{value}/{target}")
                        } else {
                            format!("○ {}",a.points)
                        }
                    } else {
                        format!("✓ {}",a.points)
                    };''',
"display measured progress, where available")

print("Ver.31 refresh input, diagnostic header, and measured progress integrated")
