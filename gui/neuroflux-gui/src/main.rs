use eframe::egui;
use serde::Deserialize;
use serde_json::Value;
use std::{env, fs};

fn main() -> eframe::Result {
    let manifest_path = env::args()
        .nth(1)
        .unwrap_or_else(|| "lab_runs/latest/manifest.json".to_string());
    let options = eframe::NativeOptions::default();

    eframe::run_native(
        "NeuroFlux Autonomous Lab",
        options,
        Box::new(move |_cc| Ok(Box::new(NeuroFluxApp::new(manifest_path)))),
    )
}

struct NeuroFluxApp {
    manifest_path: String,
    manifest: Option<Value>,
    scene: Option<Scene3d>,
    error: Option<String>,
}

impl NeuroFluxApp {
    fn new(manifest_path: String) -> Self {
        let mut app = Self {
            manifest_path,
            manifest: None,
            scene: None,
            error: None,
        };
        app.reload();
        app
    }

    fn reload(&mut self) {
        match fs::read_to_string(&self.manifest_path) {
            Ok(content) => match serde_json::from_str::<Value>(&content) {
                Ok(value) => {
                    self.scene = load_scene_from_manifest(&value);
                    self.manifest = Some(value);
                    self.error = None;
                }
                Err(err) => {
                    self.manifest = None;
                    self.scene = None;
                    self.error = Some(format!("Invalid manifest JSON: {err}"));
                }
            },
            Err(err) => {
                self.manifest = None;
                self.scene = None;
                self.error = Some(format!("Cannot read manifest: {err}"));
            }
        }
    }
}

impl eframe::App for NeuroFluxApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::TopBottomPanel::top("top_bar").show(ctx, |ui| {
            ui.horizontal(|ui| {
                ui.heading("NeuroFlux Autonomous Lab");
                if ui.button("Reload").clicked() {
                    self.reload();
                }
            });
            ui.label(format!("Manifest: {}", self.manifest_path));
        });

        egui::CentralPanel::default().show(ctx, |ui| {
            if let Some(error) = &self.error {
                ui.colored_label(egui::Color32::RED, error);
                ui.separator();
                ui.label("Run `neuroflux-lab run --iterations 3 --output lab_runs` first.");
                return;
            }

            let Some(manifest) = &self.manifest else {
                ui.label("No manifest loaded.");
                return;
            };

            render_run_overview(ui, manifest);
            ui.separator();
            render_best_candidate(ui, manifest);
            ui.separator();
            render_thermal(ui, manifest);
            ui.separator();
            render_artifacts(ui, manifest);
            ui.separator();
            render_scene_inspector(ui, self.scene.as_ref());
            ui.separator();
            render_iterations(ui, manifest);
        });
    }
}

#[derive(Clone, Debug, Deserialize)]
struct Scene3d {
    title: String,
    meshes: Vec<SceneMesh>,
}

#[derive(Clone, Debug, Deserialize)]
struct SceneMesh {
    kind: String,
    name: String,
    color: String,
    dimensions: Value,
}

fn render_run_overview(ui: &mut egui::Ui, manifest: &Value) {
    ui.heading("Run");
    ui.label(format!("Run ID: {}", text(manifest, &["run_id"])));
    ui.label(format!(
        "Runtime: {} ms",
        number(manifest, &["computation_time_ms"])
    ));
    ui.label(format!(
        "Manifest Path: {}",
        text(manifest, &["manifest_path"])
    ));
}

fn render_best_candidate(ui: &mut egui::Ui, manifest: &Value) {
    ui.heading("Best Candidate");
    let Some(candidate) = manifest.get("best_candidate") else {
        ui.label("No candidate.");
        return;
    };
    ui.label(format!("ID: {}", text(candidate, &["candidate_id"])));
    ui.label(format!("Score: {:.3}", number(candidate, &["score"])));
    ui.label(format!(
        "Meets Requirements: {}",
        text(candidate, &["meets_requirements"])
    ));

    if let Some(result) = candidate.get("analytical_result") {
        ui.label(format!("Torque: {:.3} N m", number(result, &["torque_nm"])));
        ui.label(format!("Power: {:.3} W", number(result, &["power_w"])));
        ui.label(format!(
            "Efficiency: {:.3}",
            number(result, &["efficiency"])
        ));
    }
}

fn render_thermal(ui: &mut egui::Ui, manifest: &Value) {
    ui.heading("Thermal");
    let Some(thermal) = manifest.get("thermal_analysis") else {
        ui.label("No thermal analysis in manifest.");
        return;
    };
    ui.label(format!("Status: {}", text(thermal, &["status"])));
    ui.label(format!(
        "Winding temperature: {:.1} C",
        number(thermal, &["max_winding_temp_c"])
    ));
    ui.label(format!(
        "Magnet temperature: {:.1} C",
        number(thermal, &["max_magnet_temp_c"])
    ));
    ui.label(format!(
        "Total losses: {:.3} W",
        number(thermal, &["total_losses_w"])
    ));
}

fn render_artifacts(ui: &mut egui::Ui, manifest: &Value) {
    ui.heading("Artifacts");
    let Some(artifacts) = manifest.get("artifacts") else {
        ui.label("No artifact index in manifest.");
        return;
    };
    ui.label(format!("Report: {}", text(artifacts, &["report_md"])));
    ui.label(format!("3D scene: {}", text(artifacts, &["scene3d_json"])));
    ui.label(format!("Viewer: {}", text(artifacts, &["viewer_html"])));
    ui.label(format!("Gmsh geometry: {}", text(artifacts, &["geometry_geo"])));
}

fn render_scene_inspector(ui: &mut egui::Ui, scene: Option<&Scene3d>) {
    ui.heading("CAD Inspection");
    let Some(scene) = scene else {
        ui.label("No scene3d artifact loaded.");
        return;
    };
    ui.label(format!("Scene: {}", scene.title));
    ui.label(format!("Meshes: {}", scene.meshes.len()));

    let desired_size = egui::vec2(ui.available_width(), 360.0);
    let (rect, _) = ui.allocate_exact_size(desired_size, egui::Sense::hover());
    let painter = ui.painter_at(rect);
    painter.rect_filled(rect, 4.0, egui::Color32::from_rgb(16, 20, 24));

    let max_radius = scene
        .meshes
        .iter()
        .filter_map(mesh_outer_radius)
        .fold(0.001_f64, f64::max);
    let scale = 0.44 * rect.width().min(rect.height()) as f64 / max_radius;
    let center = rect.center();

    for mesh in &scene.meshes {
        let color = parse_hex_color(&mesh.color);
        match mesh.kind.as_str() {
            "rotor_disk" | "stator" => {
                if let Some(radius) = mesh_outer_radius(mesh) {
                    painter.circle_stroke(
                        center,
                        (radius * scale) as f32,
                        egui::Stroke::new(2.0, color),
                    );
                }
            }
            "magnet" => {
                let radius = mesh
                    .dimensions
                    .get("radius")
                    .and_then(Value::as_f64)
                    .unwrap_or(0.0);
                let angle = mesh
                    .dimensions
                    .get("angle_rad")
                    .and_then(Value::as_f64)
                    .unwrap_or(0.0);
                let width = mesh
                    .dimensions
                    .get("radial_width")
                    .and_then(Value::as_f64)
                    .unwrap_or(0.01);
                let pos = egui::pos2(
                    center.x + (angle.cos() * radius * scale) as f32,
                    center.y + (angle.sin() * radius * scale) as f32,
                );
                painter.circle_filled(pos, ((width * scale) as f32).max(3.0), color);
            }
            _ => {}
        }
    }

    for mesh in scene.meshes.iter().take(8) {
        ui.label(format!("{}: {}", mesh.kind, mesh.name));
    }
}

fn render_iterations(ui: &mut egui::Ui, manifest: &Value) {
    ui.heading("Iterations");
    let Some(iterations) = manifest.get("iterations").and_then(Value::as_array) else {
        ui.label("No iterations.");
        return;
    };

    egui::ScrollArea::vertical().show(ui, |ui| {
        for iteration in iterations {
            ui.group(|ui| {
                ui.label(format!("Iteration {}", text(iteration, &["index"])));
                ui.label(format!(
                    "Verdict: {}",
                    text(iteration, &["critique", "verdict"])
                ));
                ui.label(format!(
                    "Novelty: {:.3}",
                    number(iteration, &["novelty", "novelty_score"])
                ));
                ui.label(format!("Artifact: {}", text(iteration, &["artifact_path"])));
            });
        }
    });
}

fn load_scene_from_manifest(manifest: &Value) -> Option<Scene3d> {
    let path = manifest
        .get("artifacts")
        .and_then(|artifacts| artifacts.get("scene3d_json"))
        .and_then(Value::as_str)?;
    let content = fs::read_to_string(path).ok()?;
    serde_json::from_str::<Scene3d>(&content).ok()
}

fn mesh_outer_radius(mesh: &SceneMesh) -> Option<f64> {
    mesh.dimensions.get("outer_radius").and_then(Value::as_f64)
}

fn parse_hex_color(value: &str) -> egui::Color32 {
    let clean = value.trim_start_matches('#');
    if clean.len() != 6 {
        return egui::Color32::LIGHT_GRAY;
    }
    let red = u8::from_str_radix(&clean[0..2], 16).unwrap_or(200);
    let green = u8::from_str_radix(&clean[2..4], 16).unwrap_or(200);
    let blue = u8::from_str_radix(&clean[4..6], 16).unwrap_or(200);
    egui::Color32::from_rgb(red, green, blue)
}

fn text(value: &Value, path: &[&str]) -> String {
    let mut cursor = value;
    for key in path {
        match cursor.get(*key) {
            Some(next) => cursor = next,
            None => return "n/a".to_string(),
        }
    }
    match cursor {
        Value::String(text) => text.clone(),
        Value::Number(number) => number.to_string(),
        Value::Bool(flag) => flag.to_string(),
        _ => "n/a".to_string(),
    }
}

fn number(value: &Value, path: &[&str]) -> f64 {
    let mut cursor = value;
    for key in path {
        match cursor.get(*key) {
            Some(next) => cursor = next,
            None => return 0.0,
        }
    }
    cursor.as_f64().unwrap_or(0.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_scene3d_for_gui_inspection() {
        let scene: Scene3d = serde_json::from_str(
            r##"{
              "title": "AFPM inspection",
              "meshes": [
                {
                  "kind": "rotor_disk",
                  "name": "rotor_back_iron",
                  "color": "#58616a",
                  "dimensions": {"outer_radius": 0.12}
                },
                {
                  "kind": "magnet",
                  "name": "pm_01",
                  "color": "#1f77b4",
                  "dimensions": {"radius": 0.09, "angle_rad": 0.0, "radial_width": 0.02}
                }
              ]
            }"##,
        )
        .expect("scene should parse");

        assert_eq!(scene.meshes.len(), 2);
        assert_eq!(mesh_outer_radius(&scene.meshes[0]), Some(0.12));
        assert_eq!(parse_hex_color("#58616a"), egui::Color32::from_rgb(88, 97, 106));
    }
}
