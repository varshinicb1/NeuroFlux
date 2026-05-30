use eframe::egui;
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
    error: Option<String>,
}

impl NeuroFluxApp {
    fn new(manifest_path: String) -> Self {
        let mut app = Self {
            manifest_path,
            manifest: None,
            error: None,
        };
        app.reload();
        app
    }

    fn reload(&mut self) {
        match fs::read_to_string(&self.manifest_path) {
            Ok(content) => match serde_json::from_str::<Value>(&content) {
                Ok(value) => {
                    self.manifest = Some(value);
                    self.error = None;
                }
                Err(err) => {
                    self.manifest = None;
                    self.error = Some(format!("Invalid manifest JSON: {err}"));
                }
            },
            Err(err) => {
                self.manifest = None;
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
            render_iterations(ui, manifest);
        });
    }
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
