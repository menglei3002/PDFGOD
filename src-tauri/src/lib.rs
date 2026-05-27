use std::io::BufRead;
use std::process::{Command, Stdio};
use std::thread;
use tauri::{Emitter, Manager};

fn find_python() -> std::path::PathBuf {
    // Use system Python directly to avoid DLL init failures (STATUS_DLL_INIT_FAILED)
    // that occur when spawning venv python.exe from a Tauri process.
    // The venv wrapper relies on pyvenv.cfg to locate base Python DLLs, which
    // fails when the spawning process has a different environment.
    if cfg!(target_os = "windows") {
        for candidate in &["python", "py"] {
            let args = if *candidate == "py" {
                vec!["-3", "--version"]
            } else {
                vec!["--version"]
            };
            if Command::new(candidate)
                .args(&args)
                .stdout(Stdio::null())
                .stderr(Stdio::null())
                .status()
                .is_ok()
            {
                return std::path::PathBuf::from(candidate);
            }
        }
        std::path::PathBuf::from("python")
    } else {
        std::path::PathBuf::from("python3")
    }
}

#[tauri::command]
fn convert_pdf(
    app: tauri::AppHandle,
    input: String,
    format: String,
    output: Option<String>,
    dpi: Option<u32>,
) -> Result<String, String> {
    let python = find_python();

    // Search for engine/convert.py in multiple locations:
    // 1. Resource directory (production build: engine/ beside exe)
    // 2. Current directory (dev if launched from project root)
    // 3. ../engine/ from current dir (dev: cargo runs from src-tauri/)
    // 4. ../../../engine/ from exe (dev: exe is in src-tauri/target/debug/)
    let cwd = std::env::current_dir().unwrap_or_default();
    let exe_dir = std::env::current_exe()
        .ok()
        .and_then(|p| p.parent().map(|d| d.to_path_buf()))
        .unwrap_or_default();

    let candidates = vec![
        app.path().resource_dir().unwrap_or_default().join("engine").join("convert.py"),
        cwd.join("engine").join("convert.py"),
        cwd.join("..").join("engine").join("convert.py"),
        exe_dir.join("..").join("..").join("..").join("engine").join("convert.py"),
    ];

    let script = candidates
        .iter()
        .find(|p| p.exists())
        .cloned()
        .unwrap_or_else(|| candidates[0].clone());

    let mut cmd = Command::new(&python);
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

    let mut child = cmd.spawn().map_err(|e| format!("Failed to start Python ({}): {}", python.display(), e))?;

    // Take stdout and stderr before spawning threads
    let mut stdout = child.stdout.take().unwrap();
    let stderr = child.stderr.take().unwrap();

    // Read stderr in a separate thread to avoid pipe buffer deadlock
    let stderr_handle = thread::spawn(move || {
        let reader = std::io::BufReader::new(stderr);
        reader.lines().filter_map(|l| l.ok()).collect::<Vec<String>>()
    });

    // Read stdout byte-by-byte using split, handling non-UTF-8 input gracefully
    use std::io::Read;
    let mut buf = Vec::new();
    stdout.read_to_end(&mut buf).map_err(|e| format!("Failed to read stdout: {}", e))?;

    let mut last_output = String::new();
    let mut non_json_lines: Vec<String> = Vec::new();

    for line in buf.split(|&b| b == b'\n') {
        let line = String::from_utf8_lossy(line).trim().to_string();
        if line.is_empty() {
            continue;
        }
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
                    let _ = child.wait();
                    let _ = stderr_handle.join();
                    return Err(err_msg.to_string());
                }
                _ => {}
            }
        } else {
            if non_json_lines.len() < 20 {
                non_json_lines.push(line);
            }
        }
    }

    let status = child.wait().map_err(|e| format!("Failed to wait: {}", e))?;
    let stderr_lines = stderr_handle
        .join()
        .unwrap_or_default();

    eprintln!("[PDFGOD DEBUG] input='{}' format='{}' status={:?} last_output='{}' stderr_lines={:?} non_json={:?}",
        input, format, status.code(), last_output, stderr_lines, non_json_lines);

    if status.success() {
        if last_output.is_empty() {
            let detail = if !non_json_lines.is_empty() {
                format!(" | stdout: {}", non_json_lines.join(" | "))
            } else if !stderr_lines.is_empty() {
                format!(" | stderr: {}", stderr_lines.join(" | "))
            } else {
                String::new()
            };
            return Err(format!("Conversion completed but no output path returned{}", detail));
        }
        Ok(last_output)
    } else {
        let mut parts: Vec<String> = Vec::new();
        if !stderr_lines.is_empty() {
            parts.push(stderr_lines.join("\n"));
        }
        if !non_json_lines.is_empty() {
            parts.push(format!("stdout: {}", non_json_lines.join(" | ")));
        }
        let err_msg = if parts.is_empty() {
            format!("Python process exited with code: {:?}", status.code())
        } else {
            parts.join("\n")
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
