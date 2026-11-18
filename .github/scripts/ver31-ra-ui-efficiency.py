#!/usr/bin/env python3
"""Avoid rebuilding hundreds of achievement textures as connection stages change.

The in-game viewer may contain ~200 achievements; network status updates should
only update its header texture, not allocate a second complete set of badges.
"""
from pathlib import Path
def change(path,old,new,why):
    p=Path(path);s=p.read_text()
    if s.count(old)!=1: raise SystemExit(f"{path} {why}: found {s.count(old)} anchors")
    p.write_text(s.replace(old,new,1))
    print("Optimized",path,why)
app="crates/slot/src/app.rs"
front="crates/slot/src/frontend.rs"

change(app,
'''    achievement_refresh: bool,
    achievement_row: usize,''',
'''    achievement_refresh: bool,
    achievement_header_dirty: bool,
    achievement_row: usize,''',"header dirty flag")
change(app,
'''            achievement_refresh: false,
            achievement_row: 0,''',
'''            achievement_refresh: false,
            achievement_header_dirty: false,
            achievement_row: 0,''',"init header dirty flag")
change(app,
'''        if self.achievement_connection != next {
            self.achievement_connection = next;
            self.achievement_header = None;
        }''',
'''        if self.achievement_connection != next {
            self.achievement_connection = next;
            self.achievement_header_dirty = true;
        }''',"status updates do not invalidate full list")
change(app,
'''                self.achievement_connection = "Refreshing ROM and achievements".into();
                self.achievement_header = None;''',
'''                self.achievement_connection = "Refreshing ROM and achievements".into();
                self.achievement_header_dirty = true;''',"Y refresh updates only header")
change(app,
'''    pub fn achievement_connection_label(&self) -> &str {''',
'''    pub fn achievement_header_dirty(&self) -> bool {
        self.achievement_header_dirty
    }

    pub fn achievement_header_texture(&self) -> Option<(TexId, u32, u32)> {
        self.achievement_header
    }

    pub fn update_achievement_header_size(&mut self, width: u32, height: u32) {
        if let Some((tex, _, _)) = self.achievement_header {
            self.achievement_header = Some((tex, width, height));
        }
        self.achievement_header_dirty = false;
    }

    pub fn achievement_connection_label(&self) -> &str {''',"in-place header texture update")
change(app,
'''        self.achievement_header = Some(header);
    }

    pub fn set_achievement_description''',
'''        self.achievement_header = Some(header);
        self.achievement_header_dirty = false;
    }

    pub fn set_achievement_description''',"new viewer header clears dirty flag")

change(front,
'''        app.set_achievement_faces(names,values,badges,header);
    }
    if !app.achievement_description_ready() {''',
'''        app.set_achievement_faces(names,values,badges,header);
    }
    // Connection changes while this menu is open can occur repeatedly during
    // a slow ROM lookup. Update just the existing texture instead of creating
    // hundreds of new badge/label textures for each status transition.
    if app.achievement_header_dirty() {
        if let Some((tex,_,_)) = app.achievement_header_texture() {
            let title = match app.achievement_view_ref() {
                Some(v) => {
                    let earned=v.entries.iter().filter(|a|a.unlocked).count();
                    let total:u32=v.entries.iter().map(|a|a.points).sum();
                    let received:u32=v.entries.iter().filter(|a|a.unlocked)
                        .map(|a|a.points).sum();
                    format!("{} — {}/{} ({}%) · {}/{} pts",
                        v.title,earned,v.entries.len(),
                        if v.entries.is_empty() {0} else {earned*100/v.entries.len()},
                        received,total)
                }
                None => "Achievements — connecting or no offline cache".into(),
            };
            let state=format!("{} | Y Refresh | X Sort",
                app.achievement_connection_label());
            let face=quick_description_face(&[&title,&state]);
            compositor.update_texture(tex,face.w,face.h,&face.rgba);
            app.update_achievement_header_size(face.w,face.h);
        }
    }
    if !app.achievement_description_ready() {''',"update header texture without full list rebuild")
print("Ver31: lightweight per-game connection status rendering")
