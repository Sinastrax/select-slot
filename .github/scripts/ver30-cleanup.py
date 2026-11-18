#!/usr/bin/env python3
"""Ver.30: optional, bounded cleanup of old logs and temporary cache files.

The System/ update manifest is NOT modified. Never scan System/, System.new/,
Games/, Saves/, Config/, or any custom folder unless explicitly in a narrow
allowlist. This manual operation requires a separate confirmation.
"""
from pathlib import Path

def change(path, old, new, why):
    p=Path(path); s=p.read_text()
    if s.count(old)!=1: raise SystemExit(f"{path}: {why}: found {s.count(old)} matches")
    p.write_text(s.replace(old,new,1))

Path("crates/slot/src/cleanup.rs").write_text(r'''//! Conservative user-invoked cleanup. No firmware directories or private files.
use std::fs;
use std::path::{Path, PathBuf};
use std::time::{Duration, SystemTime};

const AGE: Duration = Duration::from_secs(7*24*60*60);
const MAX_ENTRIES: usize = 2048;
const MAX_DEPTH: usize = 3;

#[derive(Clone)]
pub struct Candidate {
    pub relative: PathBuf,
    pub size: u64,
    pub modified: SystemTime,
}
#[derive(Clone, Default)]
pub struct Report {
    pub files: Vec<Candidate>,
    pub bytes: u64,
}
pub fn protected_paths(root: &Path) -> Vec<PathBuf> {
    let mut paths: Vec<PathBuf> = [
        "Games", "Saves", "Config", "System", "System.new",
        "BIOS", "Bios", "Screenshots", "Saves/RetroAchievements",
    ].into_iter().map(PathBuf::from).collect();
    if let Ok(text) = fs::read_to_string(root.join("Config/cleanup-protected.txt")) {
        for line in text.lines() {
            let line=line.trim().trim_end_matches('/');
            if line.is_empty() || line.starts_with('#') {continue}
            let p=Path::new(line);
            if !p.components().all(|c| matches!(c, std::path::Component::Normal(_))) {
                continue;
            }
            paths.push(p.to_path_buf());
        }
    }
    paths
}
fn permitted(rel: &Path, protected: &[PathBuf]) -> bool {
    if protected.iter().any(|p| rel.starts_with(p)) {return false}
    let name=rel.file_name().and_then(|s|s.to_str()).unwrap_or("");
    if rel.parent()==Some(Path::new("Logs")) {
        return name.ends_with(".log.1") || name.ends_with(".log.old");
    }
    rel.starts_with("Cache") &&
        (name.ends_with(".tmp") || name.ends_with(".part"))
}
fn walk(
    root: &Path, rel: &Path, level: usize, now: SystemTime,
    protected: &[PathBuf], report: &mut Report, visited: &mut usize
) {
    if level>MAX_DEPTH || *visited>=MAX_ENTRIES ||
       protected.iter().any(|p| rel.starts_with(p)) { return; }
    let directory=root.join(rel);
    let Ok(directory_meta)=fs::symlink_metadata(&directory) else {return};
    if !directory_meta.is_dir() || directory_meta.file_type().is_symlink() {return}
    let Ok(read)=fs::read_dir(&directory) else {return};
    for item in read.flatten() {
        *visited+=1;
        if *visited>MAX_ENTRIES {break}
        let path=rel.join(item.file_name());
        if protected.iter().any(|p|path.starts_with(p)) {continue}
        let Ok(meta)=fs::symlink_metadata(item.path()) else {continue};
        if meta.file_type().is_symlink() {continue}
        if meta.is_dir() {
            walk(root,&path,level+1,now,protected,report,visited);
        } else if meta.is_file() && permitted(&path,protected) {
            if let Ok(modified)=meta.modified() {
                if now.duration_since(modified).is_ok_and(|age|age>=AGE) {
                    report.bytes=report.bytes.saturating_add(meta.len());
                    report.files.push(Candidate {
                        relative:path,size:meta.len(),modified,
                    });
                }
            }
        }
    }
}
pub fn scan(root: &Path) -> Report {
    let protect=protected_paths(root);
    let mut report=Report::default();
    let mut visited=0usize;
    let now=SystemTime::now();
    for rel in ["Logs","Cache"] {
        walk(root,Path::new(rel),0,now,&protect,&mut report,&mut visited);
    }
    report
}
pub fn clean(root: &Path, previous: &Report) -> Result<(usize,u64),String> {
    // Repeat the scan to honor new exclusions and avoid stale preview decisions.
    let current=scan(root);
    let mut removed=0usize;
    let mut bytes=0u64;
    for file in &previous.files {
        if !current.files.iter().any(|fresh|
            fresh.relative==file.relative && fresh.size==file.size &&
            fresh.modified==file.modified) {continue}
        let path=root.join(&file.relative);
        let meta=fs::symlink_metadata(&path).map_err(|e|e.to_string())?;
        if !meta.file_type().is_file() || meta.len()!=file.size ||
            meta.modified().ok()!=Some(file.modified) {continue}
        fs::remove_file(&path).map_err(|e|e.to_string())?;
        removed+=1;
        bytes+=file.size;
    }
    Ok((removed,bytes))
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn unknown_and_system_files_are_never_candidates() {
        let root=tempfile::tempdir().unwrap();
        for dir in ["System","Games","Saves","Config","Cache","Logs"] {
            fs::create_dir_all(root.path().join(dir)).unwrap();
        }
        for name in ["System/dead.tmp","Games/dead.part","Saves/dead.log.1",
                     "Config/dead.tmp","Cache/unknown.json","Logs/important.log"] {
            fs::write(root.path().join(name),"safe").unwrap();
        }
        assert_eq!(scan(root.path()).files.len(),0);
    }
    #[cfg(unix)]
    #[test]
    fn symlinked_cache_root_is_not_traversed() {
        use std::os::unix::fs::symlink;
        let root=tempfile::tempdir().unwrap();
        let outside=tempfile::tempdir().unwrap();
        fs::write(outside.path().join("old.tmp"),"private").unwrap();
        symlink(outside.path(),root.path().join("Cache")).unwrap();
        assert!(scan(root.path()).files.is_empty());
        assert!(outside.path().join("old.tmp").exists());
    }
    #[test]
    fn exclusions_prevent_cleanup() {
        let root=tempfile::tempdir().unwrap();
        fs::create_dir_all(root.path().join("Config")).unwrap();
        fs::write(root.path().join("Config/cleanup-protected.txt"),
                  "# user entries\nCache/custom\n../invalid\n").unwrap();
        let protected=protected_paths(root.path());
        assert!(protected.iter().any(|p|p==Path::new("Cache/custom")));
        assert!(!protected.iter().any(|p|p==Path::new("../invalid")));
        assert!(!permitted(Path::new("Cache/custom/old.tmp"),&protected));
        assert!(permitted(Path::new("Cache/old.tmp"),&protected));
    }
}
''')

lib="crates/slot/src/lib.rs"
change(lib,'''pub mod cheats;''','''pub mod cheats;
mod cleanup;''',"cleanup module registration")

app="crates/slot/src/app.rs"
change(app,
'''    achievement_description: Option<(TexId, u32, u32)> ,''',
'''    achievement_description: Option<(TexId, u32, u32)> ,
    cleanup_preview: Option<crate::cleanup::Report>,
    cleanup_confirm: bool,''',"cleanup state")
change(app,
'''            achievement_description: None,
            shelves,''',
'''            achievement_description: None,
            cleanup_preview: None,
            cleanup_confirm: false,
            shelves,''',"initialize cleanup")
change(app,
'''    RaNotConfigured,''',
'''    RaNotConfigured,
    CleanupScanned,
    CleanupConfirm,
    CleanupDone,
    CleanupEmpty,
    CleanupError,''',"cleanup notices")
change(app,
'''    fn open_quick_row(&mut self, row: QuickRow) {''',
'''    fn scan_cleanup(&mut self) {
        let Some(root) = self.root.as_ref() else {
            return self.set_update(Some(UpdateState::Notice(NetNotice::CleanupError)));
        };
        self.cleanup_preview = Some(crate::cleanup::scan(root));
        self.cleanup_confirm = false;
        let notice = if self.cleanup_preview.as_ref().is_some_and(|r|r.files.is_empty()) {
            NetNotice::CleanupEmpty
        } else {
            NetNotice::CleanupScanned
        };
        self.set_update(Some(UpdateState::Notice(notice)));
    }

    fn delete_cleanup(&mut self) {
        let Some(report) = self.cleanup_preview.as_ref() else {
            return self.scan_cleanup();
        };
        if report.files.is_empty() {
            return self.set_update(Some(UpdateState::Notice(NetNotice::CleanupEmpty)));
        }
        if !self.cleanup_confirm {
            self.cleanup_confirm = true;
            return self.set_update(Some(UpdateState::Notice(NetNotice::CleanupConfirm)));
        }
        let result = self.root.as_ref()
            .map(|r| crate::cleanup::clean(r, report))
            .unwrap_or_else(|| Err("Missing SD card".into()));
        self.cleanup_confirm = false;
        self.cleanup_preview = None;
        match result {
            Ok(_) => self.set_update(Some(UpdateState::Notice(NetNotice::CleanupDone))),
            Err(_) => self.set_update(Some(UpdateState::Notice(NetNotice::CleanupError))),
        }
    }

    fn open_quick_row(&mut self, row: QuickRow) {''',"cleanup actions")
change(app,
'''            UpdateState::Notice(NetNotice::RaNotConfigured) => (''',
'''            UpdateState::Notice(NetNotice::CleanupScanned) => {
                let report = self.cleanup_preview.as_ref();
                let files = report.map_or(0,|r|r.files.len());
                let bytes = report.map_or(0,|r|r.bytes);
                ("Cleanup scan complete".into(),
                 format!("{files} old files; {:.2} MiB. Select Clean Detected Files.",
                          bytes as f64 / 1_048_576.0))
            }
            UpdateState::Notice(NetNotice::CleanupConfirm) => (
                "Confirm cleanup".into(),
                "Select Clean Detected Files again to delete scanned items.".into(),
            ),
            UpdateState::Notice(NetNotice::CleanupDone) => (
                "Cleanup complete".into(), "Verified obsolete files were removed.".into(),
            ),
            UpdateState::Notice(NetNotice::CleanupEmpty) => (
                "Nothing to clean".into(), "No eligible old temporary or rotated log files.".into(),
            ),
            UpdateState::Notice(NetNotice::CleanupError) => (
                "Cleanup failed".into(), "No unsafe files were intentionally removed.".into(),
            ),
            UpdateState::Notice(NetNotice::RaNotConfigured) => (''',"cleanup screen copy")
print("Ver.30 conservative manual cleanup added. System manifest unchanged.")
