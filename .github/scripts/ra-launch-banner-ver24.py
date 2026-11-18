#!/usr/bin/env python3
"""Ver.24: silent, live RA status banner at game launch, keeping earned popups."""
from pathlib import Path

p=Path("crates/slot/src/achievement_ui.rs")
s=p.read_text()
changes=[
("""use slot_achievements::{Notice, NoticeKind, SyncStatus};""",
 """use slot_achievements::{GameConnection, Notice, NoticeKind, SyncStatus};"""),
("""const BADGE_PX: u32 = 32;""",
 """const BADGE_PX: u32 = 32;
const LAUNCH_DURATION: Duration = Duration::from_millis(3400);"""),
("""    progress: Option<[TexId; 2]>,
}""",
 """    progress: Option<[TexId; 2]>,
    launch_seen: u64,
    launch_started: Option<Instant>,
    launch_text: Option<String>,
    launch_loaded: Option<String>,
    launch_texture: Option<TexId>,
    launch_badge: Option<TexId>,
}"""),
("""enum Request {
    Earned(Notice, u32),
    Progress(u8),
}""",
 """enum Request {
    Earned(Notice, u32),
    Progress(u8),
    Launch(String),
}"""),
("""enum Built {
    Progress(u8, [CartFace; 2]),
    Sync([CartFace; 2]),
    Banner(CartFace, CartFace, Vec<i16>),
}""",
 """enum Built {
    Progress(u8, [CartFace; 2]),
    Sync([CartFace; 2]),
    Banner(CartFace, CartFace, Vec<i16>),
    Launch(String, CartFace, CartFace),
}"""),
("""                        Request::Progress(percent) => {
                            if outbox
                                .send(Built::Progress(""",
 """                        Request::Launch(label) => {
                            let notice = Notice {
                                badge: None,
                                generation: 0,
                                title: label.clone(),
                                detail: String::new(),
                                kind: NoticeKind::Status,
                            };
                            if outbox
                                .send(Built::Launch(
                                    label,
                                    face(&notice),
                                    slot_ui::achievement_icon_face(BADGE_PX),
                                ))
                                .is_err()
                            {
                                return;
                            }
                            continue;
                        }
                        Request::Progress(percent) => {
                            if outbox
                                .send(Built::Progress("""),
("""            progress: None,
        }""",
 """            progress: None,
            launch_seen: 0,
            launch_started: None,
            launch_text: None,
            launch_loaded: None,
            launch_texture: None,
            launch_badge: None,
        }"""),
("""        let percent = session.achievement_sync_progress();
        if percent != self.requested_progress {""",
 """        let launches = session.launches();
        if launches != self.launch_seen {
            self.launch_seen = launches;
            if launches > 0 {
                self.launch_started = Some(Instant::now());
                self.launch_text = None;
                self.launch_loaded = None;
            }
        }
        if matches!(session.app().phase(), Phase::Shelf | Phase::Ejecting { .. }) {
            self.launch_started = None;
        }
        if let Some(started) = self.launch_started {
            if started.elapsed() < LAUNCH_DURATION {
                let label = launch_label(
                    session.achievement_game_connection(),
                    session.app().wifi_up(),
                );
                if self.launch_text.as_deref() != Some(label) {
                    self.launch_text = Some(label.into());
                    let _ = self.requests.send(Request::Launch(label.into()));
                }
            } else {
                self.launch_started = None;
            }
        }
        let percent = session.achievement_sync_progress();
        if percent != self.requested_progress {"""),
("""                Built::Banner(face, badge, sound) => {
                    self.waiting = false;""",
 """                Built::Launch(label, face, badge) => {
                    if self.launch_text.as_deref() != Some(label.as_str()) {
                        continue;
                    }
                    match self.launch_texture {
                        Some(id) => compositor.update_texture(id, face.w, face.h, &face.rgba),
                        None => {
                            self.launch_texture =
                                Some(compositor.create_texture(face.w, face.h, &face.rgba))
                        }
                    }
                    match self.launch_badge {
                        Some(id) => compositor.update_texture(id, badge.w, badge.h, &badge.rgba),
                        None => {
                            self.launch_badge =
                                Some(compositor.create_texture(badge.w, badge.h, &badge.rgba))
                        }
                    }
                    self.launch_loaded = Some(label);
                }
                Built::Banner(face, badge, sound) => {
                    self.waiting = false;"""),
("""        if let (Some(tex), Some(badge), Some(shown)) = (self.texture, self.badge, self.shown) {
            draw_banner(
                session.app().canvas(),
                tex,
                badge,
                shown.elapsed().as_secs_f32(),
                draws,
            );
        }
    }
}

fn progress_face""",
 """        if let (Some(tex), Some(badge), Some(shown)) = (self.texture, self.badge, self.shown) {
            draw_banner(
                session.app().canvas(),
                tex,
                badge,
                shown.elapsed().as_secs_f32(),
                draws,
            );
        } else if let (Some(started), Some(tex), Some(badge)) =
            (self.launch_started, self.launch_texture, self.launch_badge)
        {
            if self.launch_text == self.launch_loaded {
                draw_banner(
                    session.app().canvas(),
                    tex,
                    badge,
                    launch_animation(started.elapsed().as_secs_f32()),
                    draws,
                );
            }
        }
    }
}

/// RA connectivity is confirmed by the RA service; WLAN alone is not sufficient.
fn launch_label(connection: GameConnection, wlan_online: bool) -> &'static str {
    match connection {
        GameConnection::Disabled => "RetroAchievements: Off",
        GameConnection::Checking if wlan_online => "RetroAchievements: Connecting...",
        GameConnection::Checking => "RetroAchievements: No offline cache yet",
        GameConnection::OfflineReady if wlan_online => "RetroAchievements: Cached; connecting",
        GameConnection::OfflineReady => "RetroAchievements: Offline ready",
        GameConnection::Online if wlan_online => "RetroAchievements: Connected",
        GameConnection::Online => "RetroAchievements: Offline ready",
        GameConnection::NoAchievements => "RetroAchievements: No achievements",
    }
}

fn launch_animation(seconds: f32) -> f32 {
    if seconds < 3.15 {
        seconds.min(1.2)
    } else {
        1.55 + (seconds - 3.15).min(0.25)
    }
}

fn progress_face"""),
("""    #[test]
    fn notification_enters_settles_and_is_gone_before_two_seconds() {""",
 """    #[test]
    fn launch_status_distinguishes_real_ra_online_from_wifi_only() {
        assert_eq!(
            launch_label(GameConnection::Checking, true),
            "RetroAchievements: Connecting..."
        );
        assert_eq!(
            launch_label(GameConnection::OfflineReady, false),
            "RetroAchievements: Offline ready"
        );
        assert_eq!(
            launch_label(GameConnection::Online, true),
            "RetroAchievements: Connected"
        );
        assert_eq!(
            launch_label(GameConnection::Disabled, true),
            "RetroAchievements: Off"
        );
        assert!(launch_animation(0.2) < 1.0);
        assert!(launch_animation(3.3) > 1.55);
    }

    #[test]
    fn notification_enters_settles_and_is_gone_before_two_seconds() {"""),
]
for old,new in changes:
    n=s.count(old)
    if n!=1:
        raise SystemExit(f"UI patch anchor occurrence {n}: {old[:115]!r}")
    s=s.replace(old,new,1)
p.write_text(s)
print("Added launch-specific, silent RetroAchievements status banner without touching earned notifications")
