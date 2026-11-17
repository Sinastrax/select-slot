#!/usr/bin/env python3
"""Apply Custom slot's first Miyoo feature layer after Dean's ARMv7 patches.

The upstream submodule is never committed modified. This is a reproducible,
assertion-checked source transformation run by the port's patch task on
an isolated pinned checkout. Fail closed if its upstream interfaces change.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

def edit(rel, old, new):
    p = root / rel
    source = p.read_text()
    n = source.count(old)
    if n != 1:
        raise RuntimeError(f"{rel}: expected one matching source block, got {n}: {old[:90]!r}")
    p.write_text(source.replace(old, new, 1))

def balanced_replace(rel, start, body):
    p = root / rel
    source = p.read_text()
    at = source.find(start)
    if at < 0 or source.find(start, at + 1) >= 0:
        raise RuntimeError(f"{rel}: missing or repeated {start}")
    opening = source.index("{", at)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    p.write_text(source[:at] + body + source[end:])

# All affected application code gets the same explicit semantic Core variant:
# Gambatte handles GB/GBC, gpSP handles GBA. No hidden alias to an mGBA core.
for base in ("crates/slot", "crates/slot-store", "crates/slot-ui"):
    for path in (root / base).rglob("*.rs"):
        source = path.read_text()
        if "Core::Mgba" in source:
            path.write_text(source.replace("Core::Mgba", "Core::Gambatte"))

core_file = "crates/slot-store/src/core.rs"
edit(core_file, "    Mgba,\n    Gpsp,\n", "    Gambatte,\n    Gpsp,\n")
edit(core_file, '"mgba",', '"gambatte",')
edit(core_file, '"mGBA",', '"Gambatte",')
edit(core_file, '            "mgba" => Some(Core::Gambatte),', '            "mgba" | "gambatte" => Some(Core::Gambatte),')
edit(core_file, "            Core::Gambatte => true,", "            Core::Gambatte => platform != Platform::Gba,")
edit(core_file, "            Platform::Gba | Platform::Gb | Platform::Gbc => Core::Gambatte,",
     "            Platform::Gba => Core::Gpsp,\n            Platform::Gb | Platform::Gbc => Core::Gambatte,")

# The two original menu sockets are now Gambatte / gpSP. The core chooser is
# intentionally disabled: a platform has exactly one permitted core.
balanced_replace("crates/slot/src/app.rs", "    fn open_core_picker(&mut self)", """    fn open_core_picker(&mut self) {
        // This edition has a single supported core for each console.
        // No picker: users cannot select a core that cannot run this ROM.
    }""")

core = "crates/slot/src/core.rs"
source = (root / core).read_text()
start = source.find("pub fn colour_option(")
end = source.find("\npub fn apply_link_options(", start)
if start == -1 or end == -1:
    raise RuntimeError("slot core: colour_option section no longer matches")
newcolour = """pub fn colour_option(
    which: Core,
    platform: Platform,
    on: bool,
) -> Option<(&'static str, &'static str)> {
    match which {
        Core::Gambatte => Some((
            "gambatte_gbc_color_correction",
            if !on { "disabled" }
            else if platform == Platform::Gb { "always" }
            else { "GBC only" },
        )),
        Core::Gpsp => Some((
            "gpsp_color_correction",
            if on { "enabled" } else { "disabled" },
        )),
    }
}

pub fn gambatte_palette_options(colours: GbColors) -> Vec<(&'static str, &'static str)> {
    match colours {
        GbColors::Auto => vec![("gambatte_gb_colorization", "GBC")],
        GbColors::Palette(p) => vec![
            ("gambatte_gb_colorization", "internal"),
            ("gambatte_gb_internal_palette", p.gambatte_name()),
        ],
    }
}
"""
source = source[:start] + newcolour + source[end:]
# Replace only the mGBA-specific block, which was renamed by the first pass.
start = source.find("    if which == Core::Gambatte {", source.find("pub fn apply_core_options("))
end = source.find("    if which == Core::Gpsp {", start)
if start < 0 or end < 0:
    raise RuntimeError("slot core: mGBA options block no longer matches")
source = source[:start] + """    if which == Core::Gambatte {
        core.set_option("gambatte_gb_hwmode", "Auto");
        core.set_option("gambatte_mix_frames", "disabled");
        for (key, value) in gambatte_palette_options(palette.unwrap_or(GbColors::Auto)) {
            core.set_option(key, value);
        }
        if let Some((key, value)) = colour_option(which, platform, colour) {
            core.set_option(key, value);
        }
    }
""" + source[end:]
# Gambatte does not use a frameskip option.
source = source.replace(
    '    core.set_option(&format!("{}_frameskip", which.as_str()), "auto");',
    '    if which == Core::Gpsp {\n        core.set_option("gpsp_frameskip", "auto");\n    }'
)
# Prevent the port from configuring mGBA's link protocol on Gambatte.
source = source.replace(
    '    core.set_option("mgba_link", "on");',
    '    // Gambatte does not provide the old mGBA cable transport.\n    return;'
)
(root / core).write_text(source)

# Reuse the verified pvaibhav Gambatte palette-name mapping, without SGB hardware.
palette = "crates/slot-store/src/gb_palette.rs"
edit(palette, "    pub fn core_name(self) -> &'static str {\n        NAMES[self.index()]\n    }\n\n    pub fn label(self) -> &'static str {", """    pub fn core_name(self) -> &'static str {
        NAMES[self.index()]
    }

    pub fn gambatte_name(self) -> &'static str {
        const GBC: [&str; 12] = [
            "GBC - Brown", "GBC - Red", "GBC - Dark Brown", "GBC - Pastel Mix",
            "GBC - Orange", "GBC - Yellow", "GBC - Blue", "GBC - Dark Blue",
            "GBC - Grayscale", "GBC - Green", "GBC - Dark Green", "GBC - Inverted",
        ];
        const SGB: [&str; 32] = [
            "SGB - 1A", "SGB - 1B", "SGB - 1C", "SGB - 1D",
            "SGB - 1E", "SGB - 1F", "SGB - 1G", "SGB - 1H",
            "SGB - 2A", "SGB - 2B", "SGB - 2C", "SGB - 2D",
            "SGB - 2E", "SGB - 2F", "SGB - 2G", "SGB - 2H",
            "SGB - 3A", "SGB - 3B", "SGB - 3C", "SGB - 3D",
            "SGB - 3E", "SGB - 3F", "SGB - 3G", "SGB - 3H",
            "SGB - 4A", "SGB - 4B", "SGB - 4C", "SGB - 4D",
            "SGB - 4E", "SGB - 4F", "SGB - 4G", "SGB - 4H",
        ];
        match self.index() {
            0 => "GBC - Grayscale",
            1 => "GB - DMG",
            2 => "GB - Pocket",
            3 => "GB - Light",
            i @ 4..=15 => GBC[i - 4],
            i => SGB[i - 16],
        }
    }

    pub fn label(self) -> &'static str {""")

# Runtime palette changes must use Gambatte options, not mGBA-only keys.
session = "crates/slot/src/session.rs"
edit(session,
     '                emu.set_option("mgba_gb_colors", p.core_name());',
     """                for (key, value) in crate::core::gambatte_palette_options(p) {
                    emu.set_option(key, value);
                }""")
edit(session,
     '                    emu.set_option("mgba_gb_colors", self.app.gb_colors().core_name());',
     """                    for (key, value) in crate::core::gambatte_palette_options(self.app.gb_colors()) {
                        emu.set_option(key, value);
                    }""")

# Separate, persistent picture modes. All scale computations are relative to
# the actual 640x480 (or 752x560 Flip) framebuffer size.
video = "crates/slot/src/video_mode.rs"
edit(video, "    Actual,\n    Stretch,\n", "    Actual,\n    Integer,\n    Fit,\n    Fill,\n    Stretch,\n")
edit(video,
     '            VideoMode::Actual => "actual",\n            VideoMode::Stretch => "stretch",',
     '            VideoMode::Actual => "actual",\n            VideoMode::Integer => "integer",\n            VideoMode::Fit => "fit",\n            VideoMode::Fill => "fill",\n            VideoMode::Stretch => "stretch",')
edit(video,
     '            "actual" => Some(VideoMode::Actual),\n            "stretch" => Some(VideoMode::Stretch),',
     '            "actual" => Some(VideoMode::Actual),\n            "integer" => Some(VideoMode::Integer),\n            "fit" => Some(VideoMode::Fit),\n            "fill" => Some(VideoMode::Fill),\n            "stretch" => Some(VideoMode::Stretch),')
edit(video, "impl VideoMode {\n", """impl VideoMode {
    pub const ALL: [VideoMode; 5] = [
        VideoMode::Integer, VideoMode::Fit, VideoMode::Fill,
        VideoMode::Stretch, VideoMode::Actual,
    ];
    pub fn next(self) -> Self {
        let i = Self::ALL.iter().position(|v| *v == self).unwrap_or(0);
        Self::ALL[(i + 1) % Self::ALL.len()]
    }
    pub fn prev(self) -> Self {
        let i = Self::ALL.iter().position(|v| *v == self).unwrap_or(0);
        Self::ALL[(i + Self::ALL.len() - 1) % Self::ALL.len()]
    }
""")
edit(video,
     "if mode == VideoMode::Actual || (w, h) == (SRC_W, SRC_H)",
     "if matches!(mode, VideoMode::Actual | VideoMode::Integer) || (w, h) == (SRC_W, SRC_H)")

# The effective scaled picture is proportional to each platform's visible
# picture; the surrounding 240x160 backing texture may be clipped by design.
video2 = "crates/slot/src/video_mode.rs"
base_func = """pub fn base_size(platform: Platform, mode: VideoMode) -> [f32; 2] {
    let (w, h) = platform.picture();
    let (w, h) = (w as f32, h as f32);
    let (panel_w, panel_h) = (slot_gfx::out_w() as f32, slot_gfx::out_h() as f32);
    let k_fit = (panel_w / w).min(panel_h / h);
    let k_fill = (panel_w / w).max(panel_h / h);
    let size = match mode {
        VideoMode::Actual => return fit_width(slot_gfx::PICTURE),
        VideoMode::Integer => k_fit.floor().max(1.0),
        VideoMode::Fit => k_fit,
        VideoMode::Fill => k_fill,
        VideoMode::Stretch => {
            return [
                slot_gfx::SRC_W as f32 * panel_w / w,
                slot_gfx::SRC_H as f32 * panel_h / h,
            ];
        }
    };
    [slot_gfx::SRC_W as f32 * size, slot_gfx::SRC_H as f32 * size]
}
"""
# Dean's port has base_size in video_mode.rs; replace its function only, retain
# all other helpers and tests. Avoid asserting out_w/out_h for an unported API.
base_func = base_func.replace("slot_gfx::PICTURE", "PICTURE").replace("slot_gfx::out_w()", "out_w()").replace("slot_gfx::out_h()", "out_h()").replace("slot_gfx::SRC_W", "SRC_W").replace("slot_gfx::SRC_H", "SRC_H")
balanced_replace(video2, "pub fn base_size(platform: Platform, mode: VideoMode)", base_func)

app = "crates/slot/src/app.rs"
edit(app, "self.set_picture(VideoMode::Stretch)", "self.set_picture(self.video_mode.next())")
edit(app, "self.set_picture(VideoMode::Actual)", "self.set_picture(self.video_mode.prev())")
edit(app,
     "if self.video_mode == VideoMode::Stretch {",
     "if matches!(self.video_mode, VideoMode::Stretch | VideoMode::Fit | VideoMode::Fill) {")

print("Custom Miyoo source layer applied: Gambatte / gpSP, 5 scale modes, no mGBA.")
