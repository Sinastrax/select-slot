"""Keep text inside the display and leave a gap between menu columns."""
from pathlib import Path
import sys

root = Path(sys.argv[1])

def replace(source, before, after):
    if source.count(before) != 1:
        raise ValueError(f'Unexpected layout source: {before[:100]}')
    return source.replace(before, after)

menu = root / 'crates/slot-ui/src/quick_menu.rs'
source = menu.read_text()
h700 = 'row.fixed_keys().is_some()' in source
start = source.index('            let mut label_end = QUICK_LABEL_X;' if h700 else
                     '            if let Some(&(tex, w, h)) = faces.labels.get(row.index())')
values = source.index('            let value = match row {', start)
end = source.index('            let Some((tex, w, h)) = value else {', values)
after = source.index('        }\n        if let Some(bar)', end)
carets = '' if h700 else '''
            let caret_pair = (lit && !row.opens() && !row.binds() && value.is_some())
                .then_some(faces.carets);
            let value_right = caret_pair.map_or(right, |[_, (_, rw, _)]| {
                right - rw as f32 - CARET_GAP
            });
            let extra_gap = caret_pair.map_or(0.0, |[(_, lw, _), _]| lw as f32 + CARET_GAP);
'''
fixed = '''            let scale_limit = if row.fixed_keys().is_some() { 0.8 } else { 1.0 };
            let value_right = right;
            let extra_gap = 0.0;
''' if h700 else '            let scale_limit = 1.0;\n'
tail = '' if h700 else '''
                if let Some([(left_tex, lw, lh), (right_tex, rw, rh)]) = caret_pair {
                    let left = value_right - value_ink * scale - CARET_GAP - lw as f32;
                    push(out, left_tex, left, y, lw, lh);
                    push(out, right_tex, right - rw as f32, y, rw, rh);
                }
'''
source = source[:start] + source[values:end] + fixed + carets + '''
            let label = faces.labels.get(row.index()).map(|pair| pair[lit as usize]);
            let label_left = if row.centred() {
                (self.canvas.centred(main_w as f32) + pad).max(QUICK_LABEL_X)
            } else {
                QUICK_LABEL_X
            };
            let label_ink = label.map_or(0.0, |(_, w, _)| (w as f32 - 2.0 * pad).max(0.0));
            let value_ink = value.map_or(0.0, |(_, w, _)| (w as f32 - 2.0 * pad).max(0.0));
            let gap = if label.is_some() && value.is_some() { 24.0 } else { 0.0 };
            let room = value_right - extra_gap - label_left - gap;
            let scale = menu_row_scale(label_ink, value_ink, room, scale_limit);

            if let Some((tex, w, h)) = label {
                draw_scaled_row_text(out, tex, w, h, label_left - pad * scale, y, scale);
                if lit {
                    let (pointer, pw, ph) = faces.pointer;
                    let x = label_left - POINTER_GAP - pw as f32;
                    push(out, pointer, x, y - POINTER_BLEED as f32, pw, ph);
                }
            }
            if let Some((tex, w, h)) = value {
                let x = value_right - (w as f32 - pad) * scale;
                draw_scaled_row_text(out, tex, w, h, x, y, scale);''' + tail + '''
            }
''' + source[after:]
draw_helper = '''
fn menu_row_scale(label: f32, value: f32, room: f32, limit: f32) -> f32 {
    // A fixed gap and, on Miyoo, both carets have already been reserved.
    // A minimum scale here could make the columns overlap again.
    (room.max(0.0) / (label + value).max(1.0)).min(limit)
}

#[allow(clippy::too_many_arguments)]
fn draw_scaled_row_text(
    out: &mut Vec<Draw>, tex: TexId, w: u32, h: u32, x: f32, y: f32, scale: f32,
) {
    let height = h as f32 * scale;
    out.push(Draw::Tex {
        x: x.round(),
        y: (y + (h as f32 - height) * 0.5).round(),
        w: w as f32 * scale,
        h: height,
        tex,
        alpha: 1.0,
    });
}

#[cfg(test)]
mod localized_layout_tests {
    use super::*;

    #[test]
    fn long_menu_columns_leave_room_for_values_and_arrows() {
        let pad = 2.0 * MENU_PAD as f32;
        let label = quick_label_face(QuickRow::Language, true).w as f32 - pad;
        let value = quick_value_face(QuickValue::German.text(), true).w as f32 - pad;
        let room = 640.0 - 53.0 - 32.0 - 24.0 - 84.0;
        assert_eq!(menu_row_scale(label, value, room, 1.0), 1.0);
        let long_label = label + 320.0;
        let long_value = value + 160.0;
        let scale = menu_row_scale(long_label, long_value, room, 1.0);
        assert!(scale < 1.0 && (long_label + long_value) * scale <= room + 0.01);
    }

    #[test]
    fn long_description_wraps_inside_the_narrowest_display() {
        let face = quick_description_face(&[
            "Zum Löschen der gefundenen Dateien erneut den entsprechenden Menüpunkt auswählen.",
        ]);
        assert!(face.w <= 564 && face.h > (DESCRIPTION_PX * 1.4).ceil() as u32);
    }
}
'''
source = replace(source, 'fn push(out: &mut Vec<Draw>', draw_helper + '\nfn push(out: &mut Vec<Draw>')

# Descriptions can occupy two lines per entry, with a side margin at 640 px.
start = source.index('        .map(|line| {', source.index('pub fn quick_description_face'))
end = source.index('        .collect();', start)
source = source[:start] + '''        .flat_map(|line| {
            let layout = text::fit(font, line, 560.0, 2, DESCRIPTION_PX, 14.0);
            layout.lines.into_iter().map(move |line| {
                let w = text::line_width(font, &line, layout.px, layout.tracking).ceil() as u32 + 4;
                let single = text::Layout {
                    lines: vec![line],
                    px: layout.px,
                    tracking: layout.tracking,
                };
                let mut rgba = vec![0u8; (w * line_h * 4) as usize];
                text::draw_centred(&mut rgba, w, line_h, &single, DIM_INK);
                (rgba, w)
            })
        })
''' + source[end:]
menu.write_text(source)

if h700:
    receipt = root / 'crates/slot-ui/src/receipt.rs'
    source = receipt.read_text()
    start = source.index('    let smooth = raster(')
    end = source.index('\n}\n', start)
    source = source[:start] + '''    // Rasterize at the paper texture's native resolution. Overlaying a second,
    // half-sized font shifted thin strokes and distorted umlauts.
    let mut typed = raster(lines, top, PW, CUT, FIT_W, MIN_PX);
    typed.resize(PW * PH, 0.0);
    typed''' + source[end:]
    source = replace(source, """    let mut lines = vec![Line {
        text: "SCAN OR GO TO".into(),
        px: 18.0,
        gap: 24,
    }];""", """    let instruction = "SCAN OR GO TO";
    let wrapped = instruction.lines().count() > 1;
    let mut lines: Vec<_> = instruction.lines().map(|text| Line {
        text: text.into(),
        px: if wrapped { 14.0 } else { 18.0 },
        gap: if wrapped { 18 } else { 24 },
    }).collect();""")
    after_instruction = source.index("    if let Some(host)", source.index("    let wrapped"))
    stop = source.index('    lines.push(Line {\n        text: format!("PIN', after_instruction)
    source = source[:after_instruction] + source[after_instruction:stop].replace(
        "gap: 28,", "gap: if wrapped { 22 } else { 28 },"
    ) + source[stop:]
    receipt.write_text(source)

    studio = root / 'crates/slot/src/studio_view.rs'
    source = replace(studio.read_text(), 'const LIST_INSET: f32 = 8.0;', 'const LIST_INSET: f32 = 20.0;')
    studio.write_text(source)

    frontend = root / 'crates/slot/src/frontend.rs'
    source = replace(frontend.read_text(), '        let detail = menu_detail_face(&detail);',
                     '        let detail = quick_description_face(&[&detail]);')
    frontend.write_text(source)

    app = root / 'crates/slot/src/app.rs'
    source = replace(app.read_text(), '    format!("{prefix}{}", fixed_fast_forward_text(Some(binding), false))', '''    let key = fixed_fast_forward_text(Some(binding), false);
    match prefix {
        "HOLD " => format!("HOLD {key}"),
        "TAP " => format!("TAP {key}"),
        "PRESS " => format!("PRESS {key}"),
        _ => format!("{prefix}{key}"),
    }''')
    app.write_text(source)
