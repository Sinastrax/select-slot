#!/usr/bin/env python3
"""Create a Miyoo-only patch after Dean's device patches, without touching H700.
Runs against the already patched upstream checkout. Exact replacements fail closed.
"""
from pathlib import Path
from difflib import unified_diff
import sys

src = Path(sys.argv[1])
dest = Path(sys.argv[2])
changes = {}

def edit(path, operations):
    file = src / path
    old = file.read_text()
    new = old
    for before, after in operations:
        count = new.count(before)
        if count != 1:
            raise RuntimeError(f"{path}: expected exactly one match, found {count}: {before[:100]!r}")
        new = new.replace(before, after, 1)
    diff = "".join(unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"a/{path}", tofile=f"b/{path}", n=4
    ))
    if not diff:
        raise RuntimeError(f"{path}: no changes")
    changes[path] = diff

edit("crates/slot-store/src/core.rs", [
    ("    Gpsp,\n}", "    Gpsp,\n    Gambatte,\n}"),
    ('            Core::Gpsp => "gpsp",', '            Core::Gpsp => "gpsp",\n            Core::Gambatte => "gambatte",'),
    ('            Core::Gpsp => "gpSP",', '            Core::Gpsp => "gpSP",\n            Core::Gambatte => "Gambatte",'),
    ('            "gpsp" => Some(Core::Gpsp),', '            "gpsp" => Some(Core::Gpsp),\n            "gambatte" => Some(Core::Gambatte),'),
    ('            Core::Gpsp => platform == Platform::Gba,',
     '            Core::Gpsp => platform == Platform::Gba,\n            Core::Gambatte => platform != Platform::Gba,'),
    ('            Platform::Gba | Platform::Gb | Platform::Gbc => Core::Mgba,',
     '            Platform::Gba => Core::Gpsp,\n            Platform::Gb | Platform::Gbc => Core::Gambatte,'),
])
# Keep the classic two-chip GBA picker unchanged. GB/GBC now default to Gambatte.
# mGBA remains available for explicit legacy selections; no SGB mode is added.

edit("crates/slot/src/core.rs", [
    ('        Core::Gpsp => Some((\n            "gpsp_color_correction",',
     '        Core::Gambatte => Some((\n            "gambatte_gbc_color_correction",\n            if on { "GBC only" } else { "disabled" },\n        )),\n        Core::Gpsp => Some((\n            "gpsp_color_correction",'),
    ('    if which == Core::Gpsp {\n        core.set_option("gpsp_serial", serial);',
     '''    if which == Core::Gambatte {
        // Do not request SGB palettes or emulate SGB hardware. GB titles may
        // use the chosen built-in palette; GBC titles supply their own colors.
        match palette {
            Some(slot_store::GbColors::Palette(p)) => {
                let name = match p.label() {
                    "DMG Green" => "GB - DMG",
                    "GB Pocket" => "GB - Pocket",
                    "GB Light" => "GB - Light",
                    "Grayscale" => "GBC - Grayscale",
                    "GBC Brown" => "GBC - Brown",
                    "GBC Red" => "GBC - Red",
                    "GBC Dark Brown" => "GBC - Dark Brown",
                    "GBC Blue" => "GBC - Blue",
                    "GBC Dark Blue" => "GBC - Dark Blue",
                    "GBC Green" => "GBC - Green",
                    "GBC Dark Green" => "GBC - Dark Green",
                    other if other.starts_with("GBC ") => "GBC - Grayscale",
                    _ => "GB - DMG",
                };
                core.set_option("gambatte_gb_colorization", "internal");
                core.set_option("gambatte_gb_internal_palette", name);
            }
            _ => core.set_option("gambatte_gb_colorization", "GBC"),
        }
        if let Some((key, value)) = colour_option(which, platform, colour) {
            core.set_option(key, value);
        }
        core.set_option("gambatte_gbc_color_correction_mode", "fast");
    }
    if which == Core::Gpsp {
        core.set_option("gpsp_serial", serial);'''),
])
# Update palette changes live for Gambatte rather than writing mGBA options to it.
edit("crates/slot/src/session.rs", [
    ('                emu.set_option("mgba_gb_colors", p.core_name());',
     '''                match self.app.core() {
                    slot_store::Core::Gambatte => {
                        // Gambatte options are core-specific. Reopen on a
                        // palette change to ensure the new core settings apply.
                        if let slot_store::GbColors::Palette(palette) = p {
                            let name = match palette.label() {
                                "DMG Green" => "GB - DMG",
                                "GB Pocket" => "GB - Pocket",
                                "GB Light" => "GB - Light",
                                "Grayscale" => "GBC - Grayscale",
                                "GBC Brown" => "GBC - Brown",
                                "GBC Red" => "GBC - Red",
                                "GBC Dark Brown" => "GBC - Dark Brown",
                                "GBC Blue" => "GBC - Blue",
                                "GBC Dark Blue" => "GBC - Dark Blue",
                                "GBC Green" => "GBC - Green",
                                "GBC Dark Green" => "GBC - Dark Green",
                                _ => "GB - DMG",
                            };
                            emu.set_option("gambatte_gb_colorization", "internal");
                            emu.set_option("gambatte_gb_internal_palette", name);
                        } else {
                            emu.set_option("gambatte_gb_colorization", "GBC");
                        }
                    }
                    _ => emu.set_option("mgba_gb_colors", p.core_name()),
                }'''),
])
# Per-game scaling stored in Config/video_mode.txt.
edit("crates/slot/src/video_mode.rs", [
    ("    Actual,\n    Stretch,\n}", "    Actual,\n    Stretch,\n    Integer,\n    Aspect,\n    Fill,\n    FullStretch,\n}"),
    ('            VideoMode::Stretch => "stretch",',
     '            VideoMode::Stretch => "stretch",\n            VideoMode::Integer => "integer",\n            VideoMode::Aspect => "aspect",\n            VideoMode::Fill => "fill",\n            VideoMode::FullStretch => "full-stretch",'),
    ('            "stretch" => Some(VideoMode::Stretch),',
     '            "stretch" => Some(VideoMode::Stretch),\n            "integer" => Some(VideoMode::Integer),\n            "aspect" => Some(VideoMode::Aspect),\n            "fill" => Some(VideoMode::Fill),\n            "full-stretch" => Some(VideoMode::FullStretch),'),
    ('''    }
}

pub fn video_mode_for''',
     '''    }

    pub fn next(self) -> VideoMode {
        match self {
            VideoMode::Actual | VideoMode::FullStretch => VideoMode::Integer,
            VideoMode::Integer => VideoMode::Aspect,
            VideoMode::Aspect | VideoMode::Stretch => VideoMode::Fill,
            VideoMode::Fill => VideoMode::FullStretch,
        }
    }

    pub fn previous(self) -> VideoMode {
        match self {
            VideoMode::Actual | VideoMode::Integer => VideoMode::FullStretch,
            VideoMode::Aspect => VideoMode::Integer,
            VideoMode::Fill | VideoMode::Stretch => VideoMode::Aspect,
            VideoMode::FullStretch => VideoMode::Fill,
        }
    }
}

pub fn video_mode_for'''),
    ('''    if (w, h) == (SRC_W, SRC_H) {
        return fit_width(PICTURE);
    }
    match mode {
        // The frame, not just the game inside it: the console body is drawn
        // around this and its opening has to land on the picture, so both
        // scale together. See `backdrop::frame_in`.
        VideoMode::Actual => fit_width(PICTURE),
        // Stretch overflows the panel on purpose -- what hangs over the side
        // is paper, and clipping it is how the picture fills the height -- so
        // it is not fitted.
        VideoMode::Stretch => {
            let k = out_h() as f32 / h as f32;
            [SRC_W as f32 * k, SRC_H as f32 * k]
        }
    }''',
     '''    // Source texture is 240x160 even for 160x144 GB; scale both together.
    let native_w = w as f32;
    let native_h = h as f32;
    let panel_w = out_w() as f32;
    let panel_h = out_h() as f32;
    match mode {
        VideoMode::Actual => fit_width(PICTURE),
        VideoMode::Integer => {
            let k = (panel_w / native_w).min(panel_h / native_h).floor().max(1.0);
            [SRC_W as f32 * k, SRC_H as f32 * k]
        }
        VideoMode::Aspect | VideoMode::Stretch => {
            if (w, h) == (SRC_W, SRC_H) && mode == VideoMode::Stretch {
                return fit_width(PICTURE);
            }
            let k = (panel_w / native_w).min(panel_h / native_h);
            [SRC_W as f32 * k, SRC_H as f32 * k]
        }
        VideoMode::Fill => {
            let k = (panel_w / native_w).max(panel_h / native_h);
            [SRC_W as f32 * k, SRC_H as f32 * k]
        }
        VideoMode::FullStretch => [
            SRC_W as f32 * panel_w / native_w,
            SRC_H as f32 * panel_h / native_h,
        ],
    }'''),
])
edit("crates/slot/src/app.rs", [
    ("self.set_picture(VideoMode::Stretch)", "self.set_picture(self.video_mode.next())"),
    ("self.set_picture(VideoMode::Actual)", "self.set_picture(self.video_mode.previous())"),
])

# A software renderer cannot use the H700 GLSL effects; Authentic is deferred
# pending a measured LUT/lookup-table implementation. Do not fake it.

parts = []
for path, diff in changes.items():
    parts.append(f"diff --git a/{path} b/{path}\n{diff}")
dest.write_text("".join(parts))
print(f"Generated {dest}: {len(changes)} Miyoo-only source files")
