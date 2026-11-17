#!/usr/bin/env python3
"""Keep working Pocket LCD optics and repair ONLY the RGB sources/transfers.

Identified from Ver. 15 merged source and RG SP hardware feedback:
  1. Pocket Color with saved palette Auto passes Some(GbColors::Auto).
     apply_core_options() routes that into Some(p) and forces GB_MODEL_DMG,
     suppressing the title's GBC automatic palette when loading the ROM.
  2. Pocket SGB aliases the GBC GPU screen as intended, but its previous
     discriminator (lcd.x=3) was the only way to select the SGB/SNES color
     transfer. Alias lcd.x=2 makes Correction On select GBC transfer.

Fix without changing ANY pixel gap/ink/shadow/glass/mixing math:
- GbcAuto is an internal (not menu-visible) directive to force GBC hardware
  plus GBC automatic palettes when Pocket Color + Authentic uses Auto.
- Keep explicit palettes and mono modes on their existing hardware models.
- Keep SGB model and palette from mGBA. Mark SGB's correction family using
  lcd.y=0 (was 1), which is never used for Pocket LCD geometry.
- Both Pocket profiles retain lcd.x=2, so identical dot geometry and optics.
"""
from pathlib import Path

palette_file=Path("crates/slot-store/src/gb_palette.rs")
p=palette_file.read_text()
a="""    Auto,
    /// Internal directive: launch the Super Game Boy hardware model in mGBA."""
b="""    Auto,
    /// Internal directive: use GBC hardware and its automatic title palettes
    /// while drawing the Pocket Color LCD. Not exposed as a palette choice.
    GbcAuto,
    /// Internal directive: launch the Super Game Boy hardware model in mGBA."""
assert p.count(a)==1
p=p.replace(a,b)
p=p.replace("GbColors::Auto | GbColors::SgbAuto => 0,","GbColors::Auto | GbColors::GbcAuto | GbColors::SgbAuto => 0,")
p=p.replace("GbColors::Auto | GbColors::SgbAuto => GbColors::Palette(GbPalette(0)),","GbColors::Auto | GbColors::GbcAuto | GbColors::SgbAuto => GbColors::Palette(GbPalette(0)),")
p=p.replace("GbColors::Auto | GbColors::SgbAuto => GbColors::Palette(GbPalette((GbPalette::COUNT - 1) as u8)),","GbColors::Auto | GbColors::GbcAuto | GbColors::SgbAuto => GbColors::Palette(GbPalette((GbPalette::COUNT - 1) as u8)),")
p=p.replace('GbColors::Auto => "Auto",\n            GbColors::SgbAuto', 'GbColors::Auto => "Auto",\n            GbColors::GbcAuto => "Game Boy Color",\n            GbColors::SgbAuto')
p=p.replace('GbColors::Auto | GbColors::SgbAuto => "Auto",', 'GbColors::Auto | GbColors::GbcAuto | GbColors::SgbAuto => "Auto",')
assert p.count("GbcAuto")==6, p.count("GbcAuto")
palette_file.write_text(p)

state_file=Path("crates/slot-store/src/slot_state.rs")
s=state_file.read_text()
a="GbColors::Auto | GbColors::SgbAuto => self.gb_palettes = false,"
b="GbColors::Auto | GbColors::GbcAuto | GbColors::SgbAuto => self.gb_palettes = false,"
assert s.count(a)==1
state_file.write_text(s.replace(a,b))

app_file=Path("crates/slot/src/app.rs")
app=app_file.read_text()
a="""            Shader::Authentic if self.gb_model() == GbModel::PocketSgb => GbColors::SgbAuto,
            Shader::Authentic if !matches!(self.gb_model(), GbModel::Gbc | GbModel::PocketColor) => {"""
b="""            Shader::Authentic if self.gb_model() == GbModel::PocketSgb => GbColors::SgbAuto,
            // Auto for RGB Pocket screens MUST actually request GBC hardware,
            // not an explicit monochrome palette that forces ordinary GB.
            // User-selected fixed palettes still retain their existing meaning.
            Shader::Authentic
                if matches!(self.gb_model(), GbModel::Gbc | GbModel::PocketColor)
                    && self.state.gb_colors() == GbColors::Auto => GbColors::GbcAuto,
            Shader::Authentic if !matches!(self.gb_model(), GbModel::Gbc | GbModel::PocketColor) => {"""
assert app.count(a)==1
app_file.write_text(app.replace(a,b))

core_file=Path("crates/slot/src/core.rs")
core=core_file.read_text()
a="""        (Core::Gambatte, GbColors::Auto) => vec![("gambatte_gb_colorization", "GBC")],"""
b="""        (Core::Gambatte, GbColors::Auto | GbColors::GbcAuto) => vec![("gambatte_gb_colorization", "GBC")],"""
assert core.count(a)==1
core=core.replace(a,b)
a="""        (Core::Mgba, GbColors::SgbAuto) => vec![
            ("mgba_gb_model", "Super Game Boy"),
            ("mgba_gb_colors_preset", "2"),
        ],"""
b="""        (Core::Mgba, GbColors::GbcAuto) => vec![
            ("mgba_gb_model", "Game Boy Color"),
            ("mgba_gb_colors_preset", "1"),
        ],
        (Core::Mgba, GbColors::SgbAuto) => vec![
            ("mgba_gb_model", "Super Game Boy"),
            ("mgba_gb_colors_preset", "2"),
        ],"""
assert core.count(a)==1
core=core.replace(a,b)
a="""        match palette {
            Some(GbColors::SgbAuto) => {"""
b="""        match palette {
            Some(GbColors::GbcAuto) => {
                // Pocket Color is a GBC screen + GBC-compatible source colors.
                // Merely passing Some(Auto) would force 'Game Boy' below.
                core.set_option("mgba_gb_model", "Game Boy Color");
                core.set_option("mgba_gb_colors_preset", "1");
                core.set_option("mgba_gb_colors", "Auto");
            }
            Some(GbColors::SgbAuto) => {"""
assert core.count(a)==1
core=core.replace(a,b)
# Gambatte's GBC correction behavior doesn't change for GbcAuto.
a="""            GbColors::SgbAuto => true,
            GbColors::Palette(choice) => choice.core_name().starts_with("SGB "),
            GbColors::Auto => false,"""
b="""            GbColors::SgbAuto => true,
            GbColors::Palette(choice) => choice.core_name().starts_with("SGB "),
            GbColors::Auto | GbColors::GbcAuto => false,"""
assert core.count(a)==1
core=core.replace(a,b)
core_file.write_text(core)

auth_file=Path("crates/slot-gfx/src/authentic.rs")
auth=auth_file.read_text()
a="""            Screen::PocketSgb => {
                // Use EXACTLY the same GPU screen profile as Pocket Color.
                // The SGB palette comes from mGBA core options, not u_lcd.x.
                // Identical uniforms intentionally select identical GLSL
                // branches, for both Color Correction On and Off.
                Screen::PocketColor.look()
            },"""
b="""            Screen::PocketSgb => {
                // Identical geometry, panel, shadow, ghost and glass to
                // Pocket Color (lcd.x = 2). lcd.y is used ONLY to choose
                // the RGB transfer family when Color Correction is On.
                // SGB colors come from mGBA; never run them through GBC's LCD.
                let mut look = Screen::PocketColor.look();
                look.lcd[1] = 0.0;
                look
            },"""
assert auth.count(a)==1
auth=auth.replace(a,b)
assert "look.lcd[0] = 3.0" not in auth
auth_file.write_text(auth)

sh_file=Path("crates/slot-gfx/src/shaders.rs")
sh=sh_file.read_text()
a="if (u_authentic_correction > 0.5 && u_lcd.x < 2.5) {"
b="if (u_authentic_correction > 0.5 && u_lcd.y > 0.5) {"
assert sh.count(a)==1
sh=sh.replace(a,b)
# No other change to the shader source; all optical and Fit math untouched.
sh_file.write_text(sh)
print("PASS: RGB Pocket starts with real GBC Auto palette, SGB keeps mGBA SGB palette, LCD optics unchanged")
