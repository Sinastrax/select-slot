"""Miyoo custom patches: rendering; applied in exact build order."""
from .patcher import edit

# Miyoo-specific shader removal. Both menus hide the selector, shortcut
# cycling is inert and the frontend always selects the original unfiltered
# CPU path. Old shader names remain readable in the saved configuration,
# but are ignored for rendering; no user data or saves are deleted.
edit("crates/slot/src/app.rs", [
    ('''    pub fn in_game_hidden(&self) -> Vec<QuickRow> {
        let no_bezel = self.playing_platform() == Platform::Gba && !self.framed_panel();
        let mut hidden = Vec::new();''',
     '''    pub fn in_game_hidden(&self) -> Vec<QuickRow> {
        let no_bezel = self.playing_platform() == Platform::Gba && !self.framed_panel();
        // The shaders are intentionally disabled for this Miyoo build.
        let mut hidden = vec![
            QuickRow::Shader, QuickRow::GbaShader,
            QuickRow::GbShader, QuickRow::GbcShader,
        ];'''),
    ('''        let mut hidden = Vec::new();
        if !own {
            hidden.push(QuickRow::WallpaperTint);''',
     '''        // Remove the shader row from every system's quick settings.
        let mut hidden = vec![
            QuickRow::Shader, QuickRow::GbaShader,
            QuickRow::GbShader, QuickRow::GbcShader,
        ];
        if !own {
            hidden.push(QuickRow::WallpaperTint);'''),
    ('''    pub fn screen_shader(&self) -> Shader {
        match self.playing_platform() {
            Platform::Gba => self.state.shader_gba,
            Platform::Gb => self.state.shader_gb,
            Platform::Gbc => self.state.shader_gbc,
        }
    }''',
     '''    pub fn screen_shader(&self) -> Shader {
        // Force the unfiltered picture even for pre-existing saved choices.
        Shader::Off
    }'''),
    ('''    fn step_shader(&mut self, right: bool) {
        if !matches!(self.phase, Phase::Inserting { .. } | Phase::Playing { .. }) {
            return;
        }
        let (shader, choices) = match self.playing_platform() {
            Platform::Gba => (&mut self.state.shader_gba, &Shader::GBA[..]),
            Platform::Gb => (&mut self.state.shader_gb, &Shader::GB[..]),
            Platform::Gbc => (&mut self.state.shader_gbc, &Shader::GB[..]),
        };
        *shader = shader.step(choices, right);
        let said = match *shader {
            Shader::Off => Toast::ShaderOff,
            Shader::Lcd3x => Toast::ShaderLcd3x,
            Shader::Grid => Toast::ShaderGrid,
            Shader::Dot => Toast::ShaderDot,
            Shader::Simpletex => Toast::ShaderSimpletex,
        };
        self.persist();
        self.hud.toast(said, self.now());
    }''',
     '''    fn step_shader(&mut self, _right: bool) {
        // Ignore existing next/previous shader shortcuts as well.
    }'''),
])
edit("crates/slot/src/frontend.rs", [
    ('''        compositor.set_screen_effect(match self.session.app().screen_shader() {
            slot_store::Shader::Off => ScreenEffect::None,
            slot_store::Shader::Lcd3x => ScreenEffect::Lcd3x,
            slot_store::Shader::Grid => ScreenEffect::Grid,
            slot_store::Shader::Dot => ScreenEffect::Dot,
            slot_store::Shader::Simpletex => ScreenEffect::Simpletex,
        });''',
     '''        // No shader or software effect can be selected on Miyoo.
        // Keep the original unfiltered renderer for every platform.
        compositor.set_screen_effect(ScreenEffect::None);'''),
])
edit("crates/slot-store/src/slot_state.rs", [
    ('''            shader_gba: Shader::Grid,
            shader_gb: Shader::Simpletex,
            shader_gbc: Shader::Simpletex,''',
     '''            shader_gba: Shader::Off,
            shader_gb: Shader::Off,
            shader_gbc: Shader::Off,'''),
])


