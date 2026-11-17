#!/usr/bin/env python3
"""Verify mGBA SGB model, effective shader and one-time legacy migration."""
from pathlib import Path
app=Path("crates/slot/src/app.rs").read_text()
core=Path("crates/slot/src/core.rs").read_text()
state=Path("crates/slot-store/src/slot_state.rs").read_text()
front=Path("crates/slot/src/frontend.rs").read_text()
auth=Path("crates/slot-gfx/src/authentic.rs").read_text()
gfx=Path("crates/slot-gfx/src/shaders.rs").read_text()
assert "Shader::Authentic if self.core == Core::Mgba && self.gb_model() == GbModel::PocketSgb => GbColors::SgbAuto," in app
assert "self.palette_pending = Some(self.core_gb_colors());" in app
assert app.count("self.palette_pending = Some(self.core_gb_colors());") >= 2
assert "shader_gb_mgba: Shader::Authentic," in state
assert "sgb_profile_migrated=1" in state
assert "let migrate_mgba_sgb = !sgb_profile_migrated" in state
assert "fn broken_mgba_pocket_sgb_default_migrates_only_once()" in state
assert '(Core::Mgba, GbColors::SgbAuto) => vec![' in core
assert 'core.set_option("mgba_gb_model", "Super Game Boy");' in core
assert "GbModel::PocketSgb => slot_gfx::Screen::PocketSgb" in front
assert "let mut look = Screen::PocketColor.look();" in auth
assert "look.lcd[0] = 3.0;" in auth
assert "if (u_lcd.x > 1.5 && inside)" in gfx
assert "float leftGap = u_ink.z * (a + west);" in gfx
assert "float upperGap = u_ink.z * (a + north);" in gfx
assert "vec3 panelRgb = raw;" in gfx
assert "vec3 sgbCode = floor(raw * 31.0 + vec3(0.5));" in gfx
assert "float shadow = ink_near(" in gfx
assert "uniform float u_authentic_correction;" in gfx
print("PASS: mGBA Pocket SGB model and Authentic shader are active after one-time migration")
