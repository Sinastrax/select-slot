#!/usr/bin/env python3
"""Bound every Slot quick-menu list to its visible viewport.

This fixes overflow in main settings, gameplay, per-system screen pages, RomM,
the paused in-game menu, and any future page with more rows than available.
Does not change type sizes, spacing, emulator/settings behavior, or System OTA.
"""
from pathlib import Path

path=Path("crates/slot-ui/src/quick_menu.rs")
source=path.read_text()
old="""fn scrolls(page: &[QuickRow]) -> bool {
    [
        &QuickRow::CONTROLS[..],
        &QuickRow::SHORTCUTS,
        &QuickRow::GENERAL,
        &QuickRow::PLAY_SCREEN,
        &QuickRow::SYSTEM,
    ]
    .contains(&page)
}

"""
assert source.count(old)==1, "Expected legacy page-specific scroll allowlist"
source=source.replace(old,"",1)
old="""    if !scrolls(selected.page()) || count <= fits {
        return (0, count);
    }
    window(selected.position(hidden), count, fits)
"""
new="""    // All quick-menu pages share the same viewport. A hardcoded scroll
    // allowlist let new rows (and several existing 7+ row pages) overlap
    // the footer, especially on 480px-tall handheld displays.
    // Retain the three-row in-game Screen panel through visible().
    window(selected.position(hidden), count, fits)
"""
assert source.count(old)==1, "Expected legacy quick_window branch"
source=source.replace(old,new,1)
path.write_text(source)

test=Path("crates/slot-ui/src/quick_menu.rs")
test.write_text(test.read_text()+r"""

#[cfg(test)]
mod menu_viewport_tests {
    use super::*;

    #[test]
    fn every_quick_menu_page_scrolls_when_longer_than_its_viewport() {
        for canvas in [
            Canvas::FRAMED,
            Canvas { w: 640.0, h: 480.0 },
            Canvas { w: 800.0, h: 600.0 },
        ] {
            for row in QuickRow::ALL {
                let page=row.page();
                let shown=row.shown(&[]);
                let (start,len)=quick_window(canvas,row,&[]);
                let fit=visible(canvas,page);
                assert!(len<=fit,"{:?} shows {len} rows with a limit of {fit}",row);
                assert!(start+len<=shown.len(),"page window out of bounds: {:?}",row);
                if !shown.is_empty() {
                    let selected=row.position(&[]);
                    assert!(start<=selected && selected<start+len,
                        "{:?} must stay visible while scrolling",row);
                }
            }
        }
    }

    #[test]
    fn seven_row_main_and_long_in_game_menu_keep_last_entry_clear_of_footer() {
        let canvas=Canvas::FRAMED;
        let main=QuickRow::Restart;
        let (start,len)=quick_window(canvas,main,&[]);
        assert_eq!(QuickRow::MAIN.len(),7);
        assert_eq!(len,QUICK_VISIBLE);
        assert_eq!(start,1);
        for row in [QuickRow::Restart, QuickRow::ExitGame, QuickRow::GbStretch,
                    QuickRow::GbcStretch, QuickRow::RommDisconnect] {
            let (start,len)=quick_window(canvas,row,&[]);
            assert_eq!(len,QUICK_VISIBLE,"{:?} should scroll",row);
            let shown=row.shown(&[]);
            let top=quick_row_top_at(canvas,shown[start],row,&[]);
            let last_y=top+QUICK_PITCH*(len-1) as f32+TYPE_DROP;
            assert!(last_y + MENU_H as f32 <= legend_y(canvas) - 18.0,
                "{:?} overlaps lower chrome (bottom {})",row,last_y+MENU_H as f32);
        }
    }

    #[test]
    fn shorter_pages_remain_unscrolled_and_in_game_screen_keeps_three_rows() {
        let canvas=Canvas::FRAMED;
        assert_eq!(quick_window(canvas,QuickRow::WifiPower,&[]),(0,2));
        assert_eq!(quick_window(canvas,QuickRow::PlayScreen,&[]),(0,3));
        assert_eq!(quick_window(canvas,QuickRow::PlayContrast,&[]).1,3);
    }
}
""")
print("All Slot quick-menu pages now scroll at viewport capacity; layout tests added.")
