use eframe::egui;
use serde::Deserialize;
use serde_json::Value;
use std::{
    env, fs,
    path::{Path, PathBuf},
    process::Command,
};

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
                    self.scene = load_scene_from_manifest(&value, &self.manifest_path);
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
            render_external_tools(ui, manifest, &self.manifest_path);
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
    ui.label(format!(
        "Gmsh geometry: {}",
        text(artifacts, &["geometry_geo"])
    ));
}

fn render_external_tools(ui: &mut egui::Ui, manifest: &Value, manifest_path: &str) {
    ui.heading("External Solvers And Viewers");
    let tools = [
        ("Gmsh", find_executable("gmsh", &[])),
        (
            "ParaView",
            find_executable(
                "paraview",
                &[r"C:\Program Files\ParaView 6.1.0\bin\paraview.exe"],
            ),
        ),
        (
            "ElmerGUI",
            find_executable("ElmerGUI", &elmer_known_paths("ElmerGUI.exe")),
        ),
        (
            "ElmerSolver",
            find_executable("ElmerSolver", &elmer_known_paths("ElmerSolver.exe")),
        ),
        (
            "FreeCAD",
            find_executable(
                "freecad",
                &[r"C:\Users\varsh\AppData\Local\Programs\FreeCAD 1.1\bin\freecad.exe"],
            ),
        ),
        (
            "OpenSCAD",
            find_executable(
                "openscad",
                &[r"C:\Users\varsh\tools\OpenSCAD-2021.01\openscad-2021.01\openscad.exe"],
            ),
        ),
    ];

    for (name, path) in tools {
        match path {
            Some(path) => ui.label(format!("{name}: {}", path.display())),
            None => ui.colored_label(egui::Color32::YELLOW, format!("{name}: not found")),
        };
    }

    ui.horizontal_wrapped(|ui| {
        if let Some(geometry) = pdr_geometry_path(manifest, manifest_path) {
            if ui.button("Open Geometry In Gmsh").clicked() {
                launch_tool("gmsh", &[], Some(&geometry));
            }
        }
        if let Some(vtk) = thermal_vtk_path(manifest) {
            if ui.button("Open Thermal VTK In ParaView").clicked() {
                launch_tool(
                    "paraview",
                    &[r"C:\Program Files\ParaView 6.1.0\bin\paraview.exe"],
                    Some(&vtk),
                );
            }
        }
        if ui.button("Open ElmerGUI").clicked() {
            launch_tool("ElmerGUI", &elmer_known_paths("ElmerGUI.exe"), None);
        }
        if let Some(stl) = pdr_stl_path(manifest_path) {
            if ui.button("Open STL In FreeCAD").clicked() {
                launch_tool(
                    "freecad",
                    &[r"C:\Users\varsh\AppData\Local\Programs\FreeCAD 1.1\bin\freecad.exe"],
                    Some(&stl),
                );
            }
        }
    });
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

fn load_scene_from_manifest(manifest: &Value, manifest_path: &str) -> Option<Scene3d> {
    let path = manifest
        .get("artifacts")
        .and_then(|artifacts| artifacts.get("scene3d_json"))
        .and_then(Value::as_str)
        .map(PathBuf::from)
        .or_else(|| {
            Path::new(manifest_path)
                .parent()
                .map(|dir| dir.join("scene3d.json"))
        })?;
    let content = fs::read_to_string(path).ok()?;
    serde_json::from_str::<Scene3d>(&content).ok()
}

fn pdr_geometry_path(manifest: &Value, manifest_path: &str) -> Option<PathBuf> {
    if let Some(path) = manifest
        .get("solver_handoffs")
        .and_then(|handoffs| handoffs.get("elmer"))
        .and_then(|elmer| elmer.get("geometry_geo_path"))
        .and_then(Value::as_str)
    {
        return Some(PathBuf::from(path));
    }
    if let Some(path) = manifest
        .get("artifacts")
        .and_then(|artifacts| artifacts.get("geometry_geo"))
        .and_then(Value::as_str)
    {
        return Some(PathBuf::from(path));
    }
    let manifest_dir = Path::new(manifest_path).parent()?;
    Some(manifest_dir.join("geometry.geo"))
}

fn thermal_vtk_path(manifest: &Value) -> Option<PathBuf> {
    manifest
        .get("thermal_fea")
        .and_then(|thermal| thermal.get("revised").or_else(|| thermal.get("baseline")))
        .and_then(|result| result.get("vtk_path"))
        .and_then(Value::as_str)
        .map(PathBuf::from)
}

fn pdr_stl_path(manifest_path: &str) -> Option<PathBuf> {
    let path = Path::new(manifest_path).parent()?.join("assembly.stl");
    Some(path)
}

fn launch_tool(name: &str, known_paths: &[&str], artifact: Option<&Path>) {
    let Some(executable) = find_executable(name, known_paths) else {
        return;
    };
    let mut command = Command::new(executable);
    if let Some(path) = artifact {
        command.arg(path);
    }
    let _ = command.spawn();
}

fn find_executable(name: &str, known_paths: &[&str]) -> Option<PathBuf> {
    for path in known_paths {
        let path = PathBuf::from(path);
        if path.exists() {
            return Some(path);
        }
    }

    let pathext: Vec<String> = env::var("PATHEXT")
        .unwrap_or_else(|_| ".EXE;.BAT;.CMD".to_string())
        .split(';')
        .map(|ext| ext.to_ascii_lowercase())
        .collect();
    for dir in env::split_paths(&env::var_os("PATH")?) {
        let direct = dir.join(name);
        if direct.exists() {
            return Some(direct);
        }
        for ext in &pathext {
            let candidate = dir.join(format!("{name}{ext}"));
            if candidate.exists() {
                return Some(candidate);
            }
        }
    }
    None
}

fn elmer_known_paths(executable: &str) -> Vec<&'static str> {
    match executable {
        "ElmerGUI.exe" => {
            vec![r"C:\Users\varsh\tools\ElmerFEM-gui-nompi-Windows-AMD64\bin\ElmerGUI.exe"]
        }
        "ElmerSolver.exe" => {
            vec![r"C:\Users\varsh\tools\ElmerFEM-gui-nompi-Windows-AMD64\bin\ElmerSolver.exe"]
        }
        _ => vec![],
    }
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
        assert_eq!(
            parse_hex_color("#58616a"),
            egui::Color32::from_rgb(88, 97, 106)
        );
        assert_eq!(
            thermal_vtk_path(&serde_json::json!({
                "thermal_fea": {"revised": {"vtk_path": "thermal.vtk"}}
            })),
            Some(PathBuf::from("thermal.vtk"))
        );
    }
}
