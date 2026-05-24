use std::io::BufRead;
use std::process::{Command, Stdio};
use tauri::{Emitter, Manager};

#[tauri::command]
fn convert_pdf(
    app: tauri::AppHandle,
    input: String,
    format: String,
    output: Option<String>,
    dpi: Option<u32>,
) -> Result<String, String> {
    let python = if cfg!(target_os = "windows") {
        "python"
    } else {
        "python3"
    };

    let engine_path = app
        .path()
        .resource_dir()
        .unwrap_or_default()
        .join("engine")
        .join("convert.py");

    // Fallback: look relative to the executable
    let script = if engine_path.exists() {
        engine_path
    } else {
        std::env::current_dir()
            .unwrap_or_default()
            .join("engine")
            .join("convert.py")
    };

    let mut cmd = Command::new(python);
    cmd.arg(&script)
        .arg("--input")
        .arg(&input)
        .arg("--format")
        .arg(&format)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    if let Some(out) = &output {
        cmd.arg("--output").arg(out);
    }
    if let Some(d) = dpi {
        cmd.arg("--dpi").arg(d.to_string());
    }

    let mut child = cmd.spawn().map_err(|e| format!("Failed to start Python: {}", e))?;

    let stdout = child.stdout.take().unwrap();
    let reader = std::io::BufReader::new(stdout);

    let mut last_output = String::new();

    for line in reader.lines() {
        if let Ok(line) = line {
            if let Ok(data) = serde_json::from_str::<serde_json::Value>(&line) {
                let event_type = data["type"].as_str().unwrap_or("");

                match event_type {
                    "progress" => {
                        let _ = app.emit("conversion-progress", &data);
                    }
                    "done" => {
                        last_output = data["output"].as_str().unwrap_or("").to_string();
                        let _ = app.emit("conversion-progress", &data);
                    }
                    "error" => {
                        let err_msg = data["error"].as_str().unwrap_or("Unknown error");
                        let _ = app.emit("conversion-progress", &data);
                        return Err(err_msg.to_string());
                    }
                    _ => {}
                }
            }
        }
    }

    let status = child.wait().map_err(|e| format!("Failed to wait: {}", e))?;

    if status.success() {
        if last_output.is_empty() {
            return Err("Conversion completed but no output path returned".to_string());
        }
        Ok(last_output)
    } else {
        // Read stderr for error details
        let stderr = child.stderr.take().unwrap();
        let err_reader = std::io::BufReader::new(stderr);
        let err_lines: Vec<String> = err_reader
            .lines()
            .filter_map(|l| l.ok())
            .collect();
        let err_msg = if err_lines.is_empty() {
            format!("Python process exited with code: {:?}", status.code())
        } else {
            err_lines.join("\n")
        };
        Err(err_msg)
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![convert_pdf])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
