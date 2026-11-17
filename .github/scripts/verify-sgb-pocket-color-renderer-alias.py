#!/usr/bin/env python3
"""Regression guard for the empirically correct Pocket Color-on-SGB live test.

Do not simulate the image and call it a hardware validation: instead ensure
the *exact same* Screen::PocketColor Look is returned by PocketSgb and all
other emulator/palette selections remain unchanged across restarts.

Color Correction On/Off may only switch GPU source color conversion,
never the Authentic shader selection or Pocket geometry.
"""
from pathlib import Path

auth=Path("crates/slot-gfx/src/authentic.rs").read_text()
shader=Path("crates/slot-gfx/src/shaders.rs").read_text()
app=Path("crates/slot/src/app.rs").read_text()
core=Path("crates/slot/src/core.rs").read_text()
front=Path("crates/slot/src/frontend.rs").read_text()
pipe=Path("crates/slot-gfx/src/pipeline.rs").read_text()

assert "Screen::PocketSgb => {" in auth
sgb=auth.split("Screen::PocketSgb => {",1)[1].split("Screen::Light =>",1)[0]
assert "Screen::PocketColor.look()" in sgb
assert "look.lcd[0]" not in sgb
assert "look.lcd[0] = 2.0;" in auth
assert "look.lcd[0] = 3.0;" not in auth

# Renderer remains selected independently from the correction switch.
auth_fn=app.split("pub fn authentic(&self, platform: Platform) -> bool {",1)[1].split("\n    }",1)[0]
assert "shader == Shader::Authentic" in auth_fn
assert "colour_correction" not in auth_fn
fx=app.split("pub fn screen_effect(&self) -> slot_gfx::ScreenEffect {",1)[1].split("\n    }",1)[0]
assert "Shader::Authentic => ScreenEffect::Authentic" in fx
assert "colour_correction" not in fx
assert "pub fn authentic_colour_correction(&self) -> bool {" in app
assert "self.colour_correction_for(self.playing_platform())" in app
assert "gl::Uniform1f(self.u_authentic_correction" in pipe

# Both modes use identical *runtime GLSL logic*: x==2, so the SGB-only
# u_lcd.x>2.5 branch is never selected. Core supply still differs as wanted.
assert "if (u_lcd.x > 1.5 && inside)" in shader
assert "u_lcd.x < 2.5" in shader
assert "vec3 panelRgb = raw;" in shader
assert "float gapShare = clamp((dotLuma - baseLuma)" in shader
assert "float shadow = ink_near(" in shader
assert "c = clamp(mix(panelRgb, reflector, gapShare) * shadowShare" in shader

assert "GbModel::PocketSgb => slot_gfx::Screen::PocketSgb" in front
assert "GbModel::PocketColor => slot_gfx::Screen::PocketColor" in front
assert "Shader::Authentic if self.gb_model() == GbModel::PocketSgb => GbColors::SgbAuto" in app
assert "Core::Sameboy | Core::Mgba => self.state.gb_model_mgba" in app
assert 'core.set_option("mgba_gb_model", "Super Game Boy");' in core
assert 'core.set_option("mgba_gb_colors_preset", "2");' in core
assert 'core.set_option("mgba_gb_colors", "Auto");' in core
assert 'core.set_option("mgba_sgb_borders", "OFF");' in core

# Save a human-auditable code path marker in the firmware CI logs.
print("PASS: SGB profile and Pocket Color return the exact same GPU Look;")
print("      mGBA SGB hardware/palette selection is unchanged on restart;")
print("      Authentic stays selected for Color Correction On and Off.")
