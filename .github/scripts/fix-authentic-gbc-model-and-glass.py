#!/usr/bin/env python3
"""Add an independent Authentic model for GBC and soften the lower glass shade."""

from pathlib import Path


def replace_once(path: str, old: str, new: str, label: str) -> None:
    file = Path(path)
    source = file.read_text()
    count = source.count(old)
    if count != 1:
        raise AssertionError(f"{label}: expected one match in {path}, found {count}")
    file.write_text(source.replace(old, new, 1))


def replace_all(path: str, old: str, new: str, expected: int, label: str) -> None:
    file = Path(path)
    source = file.read_text()
    count = source.count(old)
    if count != expected:
        raise AssertionError(f"{label}: expected {expected} matches in {path}, found {count}")
    file.write_text(source.replace(old, new))


store = "crates/slot-store/src/slot_state.rs"
replace_once(store, "    pub gb_model_mgba: GbModel,\n    pub blending_gbc: Blending,", "    pub gb_model_mgba: GbModel,\n    /// Authentic LCD model used by native Game Boy Color games.\n    pub gbc_model: GbModel,\n    pub blending_gbc: Blending,", "GBC model state field")
replace_once(store, "            gb_model_mgba: GbModel::PocketSgb,\n            blending_gbc: Blending::Off,", "            gb_model_mgba: GbModel::PocketSgb,\n            gbc_model: GbModel::Gbc,\n            blending_gbc: Blending::Off,", "GBC model default")
replace_once(store, '    text.push_str(&format!("gb_model_mgba={}\\n", s.gb_model_mgba.key()));\n    text.push_str(&format!("blending_gbc={}\\n", s.blending_gbc.key()));', '    text.push_str(&format!("gb_model_mgba={}\\n", s.gb_model_mgba.key()));\n    text.push_str(&format!("gbc_model={}\\n", s.gbc_model.key()));\n    text.push_str(&format!("blending_gbc={}\\n", s.blending_gbc.key()));', "GBC model serialization")
replace_once(store, "    let mut gb_model_mgba = None;\n    let mut blending_gbc = None;", "    let mut gb_model_mgba = None;\n    let mut gbc_model = None;\n    let mut blending_gbc = None;", "GBC model parser local")
replace_once(store, '            "gb_model_mgba" => gb_model_mgba = GbModel::parse(value),\n            "blending_gbc" => blending_gbc = Some(Blending::parse(value).unwrap_or_default()),', '            "gb_model_mgba" => gb_model_mgba = GbModel::parse(value),\n            "gbc_model" => gbc_model = GbModel::parse(value),\n            "blending_gbc" => blending_gbc = Some(Blending::parse(value).unwrap_or_default()),', "GBC model parser")
replace_once(store, "        gb_model_mgba: gb_model_mgba.unwrap_or(fallback.gb_model_mgba),\n        blending_gbc: blending_gbc", "        gb_model_mgba: gb_model_mgba.unwrap_or(fallback.gb_model_mgba),\n        gbc_model: gbc_model.unwrap_or(fallback.gbc_model),\n        blending_gbc: blending_gbc", "GBC model parser fallback")

ui = "crates/slot-ui/src/quick_menu.rs"
replace_once(ui, "    GbModel,\n    Model,", "    GbModel,\n    GbcModel,\n    Model,", "GBC model row type")
replace_once(ui, "    pub const ALL: [QuickRow; 199 + cfg!(feature = \"nds\") as usize] = [", "    pub const ALL: [QuickRow; 200 + cfg!(feature = \"nds\") as usize] = [", "GBC model row count")
replace_once(ui, "        QuickRow::GbModel,\n        QuickRow::Model,", "        QuickRow::GbModel,\n        QuickRow::GbcModel,\n        QuickRow::Model,", "GBC model row index")
replace_once(ui, "    pub const SCREEN_GBC: [QuickRow; 8] = [\n        QuickRow::GbcShader,\n        QuickRow::GbcOverlay,", "    pub const SCREEN_GBC: [QuickRow; 9] = [\n        QuickRow::GbcShader,\n        QuickRow::GbcModel,\n        QuickRow::GbcOverlay,", "GBC settings model row")
replace_once(ui, "            QuickRow::GbcShader\n            | QuickRow::GbcOverlay", "            QuickRow::GbcShader\n            | QuickRow::GbcModel\n            | QuickRow::GbcOverlay", "GBC settings page mapping")
replace_once(ui, '            QuickRow::GbModel | QuickRow::Model => "Model",', '            QuickRow::GbModel | QuickRow::GbcModel | QuickRow::Model => "Model",', "GBC model label")
replace_once("crates/slot-ui/tests/quick_menu.rs", '        QuickRow::SCREEN_GBC.map(QuickRow::label),\n        [\n            "Shader",\n            "Overlay",', '        QuickRow::SCREEN_GBC.map(QuickRow::label),\n        [\n            "Shader",\n            "Model",\n            "Overlay",', "GBC menu expectation")

app = "crates/slot/src/app.rs"
replace_once(app, "        if !(self.authentic(platform) && platform == Platform::Gb) {\n            hidden.push(QuickRow::Model);\n        }", "        if !(self.authentic(platform) && matches!(platform, Platform::Gb | Platform::Gbc)) {\n            hidden.push(QuickRow::Model);\n        }", "in-game GBC model visibility")
replace_once(app, "            QuickRow::GbModel | QuickRow::Model => Some(match self.gb_model() {\n                GbModel::Dmg => QuickValue::GameBoy,\n                GbModel::Pocket => QuickValue::Pocket,\n                GbModel::PocketColor => QuickValue::PocketColor,\n                GbModel::PocketSgb => QuickValue::PocketSgb,\n                GbModel::Light => QuickValue::Light,\n                GbModel::Gbc => QuickValue::GameBoyColor,\n            }),", "            QuickRow::GbcModel => Some(match self.state.gbc_model {\n                GbModel::Dmg => QuickValue::GameBoy,\n                GbModel::Pocket => QuickValue::Pocket,\n                GbModel::PocketColor => QuickValue::PocketColor,\n                GbModel::PocketSgb => QuickValue::PocketSgb,\n                GbModel::Light => QuickValue::Light,\n                GbModel::Gbc => QuickValue::GameBoyColor,\n            }),\n            QuickRow::GbModel => Some(match self.gb_model() {\n                GbModel::Dmg => QuickValue::GameBoy,\n                GbModel::Pocket => QuickValue::Pocket,\n                GbModel::PocketColor => QuickValue::PocketColor,\n                GbModel::PocketSgb => QuickValue::PocketSgb,\n                GbModel::Light => QuickValue::Light,\n                GbModel::Gbc => QuickValue::GameBoyColor,\n            }),\n            QuickRow::Model => Some(match (if self.playing_platform() == Platform::Gbc { self.state.gbc_model } else { self.gb_model() }) {\n                GbModel::Dmg => QuickValue::GameBoy,\n                GbModel::Pocket => QuickValue::Pocket,\n                GbModel::PocketColor => QuickValue::PocketColor,\n                GbModel::PocketSgb => QuickValue::PocketSgb,\n                GbModel::Light => QuickValue::Light,\n                GbModel::Gbc => QuickValue::GameBoyColor,\n            }),", "GBC model value")
replace_once(app, "    fn step_gb_model(&mut self, right: bool) -> GbModel {\n        let to = self.gb_model().step(right);", "    fn step_gb_model(&mut self, right: bool) -> GbModel {\n        if self.playing_platform() == Platform::Gbc {\n            self.state.gbc_model = self.state.gbc_model.step(right);\n            return self.state.gbc_model;\n        }\n        let to = self.gb_model().step(right);", "GBC model action routing")
replace_once(app, "        if let QuickRow::GbModel | QuickRow::Model = row {\n            self.step_gb_model(right);\n            self.palette_pending = Some(self.state.gb_colors());\n            self.persist();\n            return;\n        }", "        if row == QuickRow::GbcModel {\n            self.state.gbc_model = self.state.gbc_model.step(right);\n            self.persist();\n            return;\n        }\n        if let QuickRow::GbModel | QuickRow::Model = row {\n            self.step_gb_model(right);\n            self.palette_pending = Some(self.state.gb_colors());\n            self.persist();\n            return;\n        }", "GBC model action row")
replace_once(app, "        if !self.authentic(Platform::Gb) {\n            hidden.push(QuickRow::GbModel);\n        }", "        if !self.authentic(Platform::Gb) {\n            hidden.push(QuickRow::GbModel);\n        }\n        if !self.authentic(Platform::Gbc) {\n            hidden.push(QuickRow::GbcModel);\n        }", "GBC model settings visibility")
replace_all(app, "            | QuickRow::GbModel\n            | QuickRow::Model", "            | QuickRow::GbModel\n            | QuickRow::GbcModel\n            | QuickRow::Model", 2, "GBC model input and action routing")
replace_once(app, "    /// The GB Authentic model is selected per running emulator core, not globally.\n    /// Existing saved gb_model continues to belong to Gambatte.\n    pub fn gb_model(&self) -> GbModel {", "    /// Authentic model selected for native Game Boy Color games.\n    pub fn gbc_model(&self) -> GbModel {\n        self.state.gbc_model\n    }\n\n    /// The GB Authentic model is selected per running emulator core, not globally.\n    /// Existing saved gb_model continues to belong to Gambatte.\n    pub fn gb_model(&self) -> GbModel {", "GBC model accessor")

replace_once("crates/slot/src/frontend.rs", "        Console::Gbc => slot_gfx::Screen::Gbc,", "        Console::Gbc => match app.gbc_model() {\n            slot_store::GbModel::Dmg => slot_gfx::Screen::Dmg,\n            slot_store::GbModel::Pocket => slot_gfx::Screen::Pocket,\n            slot_store::GbModel::PocketColor => slot_gfx::Screen::PocketColor,\n            slot_store::GbModel::PocketSgb => slot_gfx::Screen::PocketSgb,\n            slot_store::GbModel::Light => slot_gfx::Screen::Light,\n            slot_store::GbModel::Gbc => slot_gfx::Screen::Gbc,\n        },", "GBC model rendering")
replace_once("crates/slot-gfx/src/shaders.rs", "        float shade = max(v_uv.y - 0.55 - 0.05 * v_uv.x, 0.0) * (0.44 - 0.11 * v_uv.x);", "        float shadeEdge = v_uv.y - 0.55 - 0.05 * v_uv.x;\n        float shade = smoothstep(-0.08, 0.32, shadeEdge) * (0.12 - 0.03 * v_uv.x);", "Authentic lower glass gradient")

print("Added independent Authentic GBC model choices and softened the lower glass shade")
