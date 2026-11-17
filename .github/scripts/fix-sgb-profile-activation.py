"""Activate mGBA Pocket SGB's authentic LCD and source palette.

Apply after fix-pocket-sgb-parity.py. On select. slot. 1.16.0 Ver. 11
the mGBA profile was constructed as PocketSgb + Simpletex: the optical
shader was not active, and mGBA SGB hardware was not selected because
core_gb_colors() only returns SgbAuto while Authentic is enabled.

Migrate precisely that old invalid default once; users can still explicitly
choose any shader afterwards. Keep Gambatte's separate profiles unchanged.
"""
from pathlib import Path

app_path=Path("crates/slot/src/app.rs")
app=app_path.read_text()
# mGBA SGB requires the effective core's Authentic mode. This guard is
# correct as written; the persisted Simpletex default is the real issue.
assert "Shader::Authentic if self.core == Core::Mgba && self.gb_model() == GbModel::PocketSgb => GbColors::SgbAuto," in app
# A live model change should apply the *effective* palette, not the saved
# generic palette. The mGBA hardware mode still requires a game restart.
old_menu="""let model = self.step_gb_model(action == Action::PaletteNext);
                self.palette_pending = Some(self.state.gb_colors());"""
new_menu="""let model = self.step_gb_model(action == Action::PaletteNext);
                self.palette_pending = Some(self.core_gb_colors());"""
assert app.count(old_menu)==1, "Expected model hotkey palette sync"
app=app.replace(old_menu,new_menu,1)
old_quick="""self.step_gb_model(right);
                self.palette_pending = Some(self.state.gb_colors());"""
new_quick="""self.step_gb_model(right);
                self.palette_pending = Some(self.core_gb_colors());"""
assert app.count(old_quick)==1, "Expected quick-menu model palette sync"
app=app.replace(old_quick,new_quick,1)
assert 'core.set_option("mgba_gb_model", "Super Game Boy");' in Path("crates/slot/src/core.rs").read_text()
app_path.write_text(app)

state_path=Path("crates/slot-store/src/slot_state.rs")
state=state_path.read_text()
def one(old,new,label):
    global state
    assert state.count(old)==1, f"{label}: {state.count(old)} matches"
    state=state.replace(old,new,1)

# Newly created mGBA Pocket SGB profiles must visibly use the Authentic
# shader. Gambatte remains independent and untouched.
one("shader_gb_mgba: Shader::Simpletex,",
    "shader_gb_mgba: Shader::Authentic,",
    "mGBA SGB visible default")
# A simple on-disk migration marker (not an exposed SlotState field) lets
# existing mGBA Pocket SGB configurations migrate once, without overriding
# a later deliberate switch to Standard LCD/Off/Grid.
one('text.push_str(&format!("shader_gb_mgba={}\\n", s.shader_gb_mgba.name()));',
    'text.push_str(&format!("shader_gb_mgba={}\\n", s.shader_gb_mgba.name()));\n    text.push_str("sgb_profile_migrated=1\\n");',
    "persist one-time migration marker")
one("    let mut gb_model_mgba = None;",
    "    let mut gb_model_mgba = None;\n    let mut sgb_profile_migrated = false;",
    "one-time migration parser local")
one('            "gb_model_mgba" => gb_model_mgba = GbModel::parse(value),',
    '            "gb_model_mgba" => gb_model_mgba = GbModel::parse(value),\n            "sgb_profile_migrated" => sgb_profile_migrated = flag(value).unwrap_or(false),',
    "one-time migration marker read")
one("    let fallback = SlotState::default();",
    """    let fallback = SlotState::default();
    // Previous firmware saved Pocket SGB + Simpletex for mGBA by default.
    // Only upgrade this broken combination once. Future explicit user
    // changes are respected because all new config writes carry a marker.
    let migrate_mgba_sgb = !sgb_profile_migrated
        && gb_model_mgba.unwrap_or(fallback.gb_model_mgba) == GbModel::PocketSgb
        && shader_gb_mgba == Some(Shader::Simpletex);""",
    "one-time migration condition")
one("shader_gb_mgba: shader_gb_mgba.or(shader_gb).unwrap_or(fallback.shader_gb_mgba),",
    """shader_gb_mgba: if migrate_mgba_sgb {
            Shader::Authentic
        } else {
            shader_gb_mgba.or(shader_gb).unwrap_or(fallback.shader_gb_mgba)
        },""",
    "apply legacy SGB default migration")
# Unit-test migration and preserve user override after first save.
test_anchor="""    #[test]
    fn old_settings_migrate_without_losing_the_existing_gb_shader() {"""
test="""    #[test]
    fn broken_mgba_pocket_sgb_default_migrates_only_once() {
        let dir = tempfile::tempdir().unwrap();
        std::fs::create_dir(dir.path().join("Config")).unwrap();
        let mut state = SlotState::default();
        state.cart = Some("SGB Game".to_owned());
        state.shader_gb = Shader::Grid;
        state.gb_model = GbModel::PocketColor;
        state.gb_model_mgba = GbModel::PocketSgb;
        state.shader_gb_mgba = Shader::Simpletex;
        write_slot_state(dir.path(), &state).unwrap();
        let path = state_path(dir.path());
        let old = std::fs::read_to_string(&path).unwrap();
        assert!(old.contains("sgb_profile_migrated=1"));
        std::fs::write(&path, old.replace("sgb_profile_migrated=1\\n", "")).unwrap();
        let mut migrated = read_slot_state(dir.path());
        assert_eq!(migrated.gb_model_mgba, GbModel::PocketSgb);
        assert_eq!(migrated.shader_gb_mgba, Shader::Authentic);
        assert_eq!(migrated.shader_gb, Shader::Grid);
        assert_eq!(migrated.gb_model, GbModel::PocketColor);
        write_slot_state(dir.path(), &migrated).unwrap();
        migrated.shader_gb_mgba = Shader::Simpletex;
        write_slot_state(dir.path(), &migrated).unwrap();
        let override_loaded = read_slot_state(dir.path());
        assert_eq!(override_loaded.shader_gb_mgba, Shader::Simpletex);
    }

"""
assert state.count(test_anchor)==1
state=state.replace(test_anchor,test+test_anchor,1)
state_path.write_text(state)
print("Fixed mGBA SGB missing Authentic by one-time state migration; Gambatte unchanged")
