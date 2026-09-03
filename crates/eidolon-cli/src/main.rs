use clap::Parser;
use crossterm::{
    cursor,
    event::{self, Event, KeyCode},
    execute,
    terminal::{self, ClearType, EnterAlternateScreen, LeaveAlternateScreen},
};
use serde_json::{json, Value};
use std::fs;
use std::io::{self, Read, Write};
use std::net::TcpStream;
use std::path::PathBuf;
use std::process::Command;
use std::time::Duration;

#[derive(Parser)]
#[command(name = "eidolon", version, about = "Eidolon Agent Runtime")]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(clap::Subcommand)]
enum Commands {
    Serve {
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    Chat {
        message: String,
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    Repl {
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    Tui {
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    Devices {
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    Paired {
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    Pair {
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    Unpair {
        peer_id: String,
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    Projects {
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    Workspaces {
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    WorkspaceExecute {
        workspace_id: Option<String>,
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    ProjectCreate {
        title: String,
        #[arg(long, default_value = "")]
        description: String,
        #[arg(long, default_value = "")]
        domain: String,
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    ProjectDelete {
        project_id: String,
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    Goals {
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    GoalCreate {
        title: String,
        #[arg(long, default_value = "")]
        description: String,
        #[arg(long, default_value = "system")]
        category: String,
        #[arg(long, default_value_t = 1)]
        priority: i64,
        #[arg(long = "step")]
        steps: Vec<String>,
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    GoalTransition {
        goal_id: String,
        status: String,
        #[arg(long, default_value = "")]
        error: String,
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    GoalDelete {
        goal_id: String,
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    Settings {
        area: Option<String>,
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    SettingsSet {
        area: String,
        key: String,
        value: String,
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    SettingsReset {
        area: String,
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    Setup {
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    OpenaiLogin {
        #[arg(long, default_value_t = true)]
        device_auth: bool,
    },
    OpenaiStatus,
    OpenaiUse {
        #[arg(long, default_value = "gpt-5.5")]
        model: String,
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    Api {
        method: String,
        path: String,
        body: Option<String>,
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
    Diagnose {
        #[arg(short, long, default_value = "8002")]
        port: u16,
    },
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum TuiTab {
    Chat,
    Status,
    Devices,
    Projects,
    Goals,
    Settings,
    Help,
}

impl TuiTab {
    fn all() -> [TuiTab; 7] {
        [TuiTab::Chat, TuiTab::Status, TuiTab::Devices, TuiTab::Projects, TuiTab::Goals, TuiTab::Settings, TuiTab::Help]
    }
    fn title(self) -> &'static str {
        match self {
            TuiTab::Chat => "Chat",
            TuiTab::Status => "Status",
            TuiTab::Devices => "Geräte",
            TuiTab::Projects => "Projekte",
            TuiTab::Goals => "Ziele",
            TuiTab::Settings => "Settings",
            TuiTab::Help => "Hilfe",
        }
    }
}

fn project_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).parent().and_then(|p| p.parent()).map(|p| p.to_path_buf()).expect("project root")
}

fn python_runtime_dir() -> PathBuf {
    project_root().join("python")
}

fn settings_path() -> PathBuf {
    python_runtime_dir().join("data").join("user").join("settings.json")
}

fn is_configured() -> bool {
    let path = settings_path();
    if !path.exists() { return false; }
    if let Ok(raw) = std::fs::read_to_string(&path) {
        if let Ok(val) = serde_json::from_str::<serde_json::Value>(&raw) {
            return val.is_object() && !val.as_object().unwrap().is_empty();
        }
    }
    false
}

fn http_request(method: &str, port: u16, path: &str, body: Option<&str>) -> Result<String, String> {
    let mut stream = TcpStream::connect(("127.0.0.1", port)).map_err(|e| format!("connect failed: {}", e))?;
    let payload = body.unwrap_or("");
    let req = format!("{} {} HTTP/1.1\r\nHost: 127.0.0.1:{}\r\nConnection: close\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n{}", method, path, port, payload.len(), payload);
    stream.write_all(req.as_bytes()).map_err(|e| format!("write failed: {}", e))?;
    let mut resp = String::new();
    stream.read_to_string(&mut resp).map_err(|e| format!("read failed: {}", e))?;
    let n = resp.replace("\r\r\n", "\r\n");
    let (_, body) = n.split_once("\r\n\r\n").ok_or("invalid http response")?;
    Ok(body.to_string())
}

fn parse_json(body: &str) -> Result<Value, String> {
    serde_json::from_str(body).map_err(|e| format!("invalid json: {}", e))
}

fn parse_cli_value(raw: &str) -> Value {
    serde_json::from_str(raw).unwrap_or_else(|_| Value::String(raw.to_string()))
}

fn print_json(v: &Value) {
    println!("{}", serde_json::to_string_pretty(v).unwrap_or_else(|_| v.to_string()));
}

fn api(port: u16, method: &str, path: &str, body: Option<&str>) -> Result<Value, String> {
    http_request(method, port, path, body).and_then(|b| parse_json(&b))
}

fn chat_request(port: u16, msg: &str, from: &str) -> Result<Value, String> {
    api(port, "POST", "/chat", Some(&json!({"message": msg, "from": from}).to_string()))
}

fn projects_request(port: u16) -> Result<Value, String> { api(port, "GET", "/projects", None) }
fn workspaces_request(port: u16) -> Result<Value, String> { api(port, "GET", "/workspaces", None) }
fn goals_request(port: u16) -> Result<Value, String> { api(port, "GET", "/api/v1/operate/goals", None) }
fn paired_request(port: u16) -> Result<Value, String> { api(port, "GET", "/mesh/pairing/paired", None) }
fn devices_request(port: u16) -> Result<Value, String> { api(port, "GET", "/mesh/peers", None) }
fn health_request(port: u16) -> Result<Value, String> { api(port, "GET", "/health", None) }
fn autonomy_status_request(port: u16) -> Result<Value, String> { api(port, "GET", "/autonomy/status", None) }

fn settings_request(port: u16, area: Option<&str>) -> Result<Value, String> {
    let p = match area { Some(a) => format!("/settings/{}", a), None => "/settings".to_string() };
    api(port, "GET", &p, None)
}

fn settings_update_request(port: u16, area: &str, key: &str, value: &str) -> Result<Value, String> {
    let current = settings_request(port, Some(area))?;
    let mut s = current.get("settings").and_then(|v| v.as_object()).cloned().unwrap_or_default();
    s.insert(key.to_string(), parse_cli_value(value));
    api(port, "POST", &format!("/settings/{}", area), Some(&Value::Object(s).to_string()))
}

fn openai_use_request(port: u16, model: &str) -> Result<Value, String> {
    let body = json!({"provider": "openai_oauth", "model": model}).to_string();
    api(port, "POST", "/settings/llm", Some(&body))
}

fn codex_command_path() -> PathBuf {
    if let Ok(appdata) = std::env::var("APPDATA") {
        let cmd = PathBuf::from(appdata).join("npm").join("codex.cmd");
        if cmd.exists() { return cmd; }
    }
    if cfg!(windows) { return PathBuf::from("codex.cmd"); }
    PathBuf::from("codex")
}

fn openai_status_command() -> Result<Value, String> {
    let output = Command::new(codex_command_path())
        .args(["login", "status"])
        .output()
        .map_err(|e| format!("codex login status fehlgeschlagen: {}", e))?;
    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
    let merged = if stderr.is_empty() { stdout.clone() } else if stdout.is_empty() { stderr.clone() } else { format!("{}\n{}", stdout, stderr) };
    let lower = merged.to_lowercase();
    Ok(json!({
        "ok": output.status.success(),
        "logged_in": lower.contains("logged in") || lower.contains("chatgpt"),
        "detail": merged,
    }))
}

fn openai_login_command(device_auth: bool) -> Result<(), String> {
    let mut cmd = Command::new(codex_command_path());
    cmd.arg("login");
    if device_auth {
        cmd.arg("--device-auth");
    }
    let status = cmd.status().map_err(|e| format!("codex login fehlgeschlagen: {}", e))?;
    if status.success() {
        Ok(())
    } else {
        Err(format!("codex login beendet mit {:?}", status.code()))
    }
}

fn create_project_request(port: u16, t: &str, d: &str, dom: &str) -> Result<Value, String> {
    api(port, "POST", "/projects", Some(&json!({"title": t, "description": d, "domain": dom}).to_string()))
}

fn delete_project_request(port: u16, id: &str) -> Result<Value, String> { api(port, "DELETE", &format!("/projects/{}", id), None) }

fn create_goal_request(port: u16, t: &str, d: &str, c: &str, p: i64, s: Vec<String>) -> Result<Value, String> {
    api(port, "POST", "/api/v1/operate/goals", Some(&json!({"title": t, "description": d, "category": c, "priority": p, "steps": s}).to_string()))
}

fn transition_goal_request(port: u16, id: &str, status: &str, err: Option<&str>) -> Result<Value, String> {
    let body = match err { Some(e) if !e.is_empty() => json!({"status": status, "error": e}), _ => json!({"status": status}) };
    api(port, "POST", &format!("/api/v1/operate/goals/{}/transition", id), Some(&body.to_string()))
}

fn delete_goal_request(port: u16, id: &str) -> Result<Value, String> { api(port, "DELETE", &format!("/api/v1/operate/goals/{}", id), None) }
fn pair_request(port: u16) -> Result<Value, String> { api(port, "POST", "/mesh/pairing/create", Some("{}")) }
fn unpair_request(port: u16, id: &str) -> Result<Value, String> { api(port, "DELETE", &format!("/mesh/pairing/paired/{}", id), None) }
fn settings_reset_request(port: u16, area: &str) -> Result<Value, String> { api(port, "POST", &format!("/settings/{}/reset", area), Some("{}")) }

fn resolve_active_workspace_id(port: u16) -> Result<String, String> {
    let status = autonomy_status_request(port)?;
    status
        .get("active_workspace")
        .and_then(|w| w.get("workspace_id"))
        .and_then(|v| v.as_str())
        .map(|s| s.to_string())
        .ok_or_else(|| "Kein aktiver Workspace vorhanden".to_string())
}

fn workspace_execute_request(port: u16, workspace_id: Option<&str>) -> Result<Value, String> {
    let id = match workspace_id {
        Some(id) if !id.trim().is_empty() => id.trim().to_string(),
        _ => resolve_active_workspace_id(port)?,
    };
    api(port, "POST", &format!("/workspaces/{}/orchestration/execute", id), Some("{}"))
}

fn workspace_summary(port: u16) -> Result<String, String> {
    let status = autonomy_status_request(port)?;
    let ws = status.get("active_workspace").cloned().unwrap_or(Value::Null);
    if ws.is_null() {
        return Ok("Kein aktiver Workspace".to_string());
    }
    let label = ws.get("topic_label").and_then(|v| v.as_str()).unwrap_or("Unbenannter Workspace");
    let kind = ws.get("workspace_type").and_then(|v| v.as_str()).unwrap_or("workspace");
    let next = ws
        .get("orchestration")
        .and_then(|o| o.get("next_best_action"))
        .and_then(|a| a.get("label").or_else(|| a.get("action")))
        .and_then(|v| v.as_str())
        .unwrap_or("keine direkte Folgeaktion");
    Ok(format!("Aktiver Workspace: {} ({}) · Nächste Aktion: {}", label, kind, next))
}

fn diagnose_request(port: u16) -> Value {
    let h = health_request(port).unwrap_or_else(|e| json!({"ok": false, "error": e}));
    let p = devices_request(port).unwrap_or_else(|e| json!({"ok": false, "error": e}));
    let q = api(port, "GET", "/mesh/quic-status", None).unwrap_or_else(|e| json!({"ok": false, "error": e}));
    json!({"runtime_port": port, "health": h, "mesh_peers": p, "quic": q})
}

fn repl_help() -> &'static str { "Befehle:\n  help\n  exit | quit\n  chat <nachricht>\n  devices\n  paired\n  pair\n  unpair <peer_id>\n  projects\n  workspaces\n  workspace-exec [workspace_id]\n  project-create <titel>\n  project-delete <project_id>\n  goals\n  goal-create <titel>\n  goal-transition <goal_id> <status>\n  goal-delete <goal_id>\n  settings [area]\n  settings-set <area> <key> <json|text>\n  settings-reset <area>\n  api <METHOD> <PATH> [JSON]\n  diagnose" }

fn run_chat_mode(port: u16) -> Result<(), String> {
    println!("Eidolon Chat — Port {} (leer = Beenden)", port);
    if let Ok(summary) = workspace_summary(port) {
        println!("{}", summary);
    }
    let stdin = io::stdin();
    loop {
        print!("du> ");
        io::stdout().flush().map_err(|e| e.to_string())?;
        let mut line = String::new();
        stdin.read_line(&mut line).map_err(|e| e.to_string())?;
        let line = line.trim();
        if line.is_empty() || matches!(line, "exit" | "quit" | "q") { break; }
        match chat_request(port, line, "eidolon-chat") {
            Ok(j) => {
                if let Some(r) = j.get("response").and_then(|v| v.as_str()) {
                    println!("{}", r);
                } else {
                    print_json(&j);
                }
            }
            Err(e) => eprintln!("{}", e),
        }
    }
    Ok(())
}

fn run_repl(port: u16) -> Result<(), String> {
    println!("Eidolon REPL — Port {}", port);
    println!("{}", repl_help());
    let stdin = io::stdin();
    loop {
        print!("eidolon> ");
        io::stdout().flush().map_err(|e| e.to_string())?;
        let mut line = String::new();
        stdin.read_line(&mut line).map_err(|e| e.to_string())?;
        let line = line.trim();
        if line.is_empty() { continue; }
        if matches!(line, "exit" | "quit") { break; }
        let result = if line == "help" { println!("{}", repl_help()); continue; }
        else if line == "chat" { let _ = run_chat_mode(port); continue; }
        else if let Some(msg) = line.strip_prefix("chat ") { chat_request(port, msg.trim(), "eidolon-repl") }
        else if line == "devices" { devices_request(port) }
        else if line == "paired" { paired_request(port) }
        else if line == "pair" { pair_request(port) }
        else if let Some(id) = line.strip_prefix("unpair ") { unpair_request(port, id.trim()) }
        else if line == "projects" { projects_request(port) }
        else if line == "workspaces" { workspaces_request(port) }
        else if let Some(id) = line.strip_prefix("workspace-exec ") { workspace_execute_request(port, Some(id.trim())) }
        else if line == "workspace-exec" { workspace_execute_request(port, None) }
        else if let Some(t) = line.strip_prefix("project-create ") { create_project_request(port, t.trim(), "", "") }
        else if let Some(id) = line.strip_prefix("project-delete ") { delete_project_request(port, id.trim()) }
        else if line == "goals" { goals_request(port) }
        else if let Some(t) = line.strip_prefix("goal-create ") { create_goal_request(port, t.trim(), "", "system", 1, vec![]) }
        else if let Some(r) = line.strip_prefix("goal-transition ") {
            let mut p = r.splitn(3, ' ');
            let id = p.next().unwrap_or("").trim();
            let s = p.next().unwrap_or("").trim();
            if id.is_empty() || s.is_empty() { Err("Nutze: goal-transition <goal_id> <status>".to_string()) } else { transition_goal_request(port, id, s, None) }
        }
        else if let Some(id) = line.strip_prefix("goal-delete ") { delete_goal_request(port, id.trim()) }
        else if line == "settings" { settings_request(port, None) }
        else if let Some(a) = line.strip_prefix("settings ") { settings_request(port, Some(a.trim())) }
        else if let Some(r) = line.strip_prefix("settings-set ") {
            let mut p = r.splitn(3, ' ');
            let a = p.next().unwrap_or("").trim();
            let k = p.next().unwrap_or("").trim();
            let v = p.next().unwrap_or("").trim();
            if a.is_empty() || k.is_empty() || v.is_empty() { Err("Nutze: settings-set <area> <key> <json|text>".to_string()) } else { settings_update_request(port, a, k, v) }
        }
        else if let Some(a) = line.strip_prefix("settings-reset ") { settings_reset_request(port, a.trim()) }
        else if let Some(r) = line.strip_prefix("api ") {
            let mut p = r.splitn(3, ' ');
            let m = p.next().unwrap_or("").trim();
            let path = p.next().unwrap_or("").trim();
            let body = p.next().map(str::trim).filter(|s| !s.is_empty());
            if m.is_empty() || path.is_empty() { Err("Nutze: api <METHOD> <PATH> [JSON]".to_string()) } else { api(port, m, path, body) }
        }
        else if line == "diagnose" { Ok(diagnose_request(port)) }
        else { Err(format!("Unbekannter Befehl: {}", line)) };
        match result { Ok(j) => print_json(&j), Err(e) => eprintln!("{}", e) };
    }
    Ok(())
}

fn prompt_line(prompt: &str) -> Result<String, String> {
    terminal::disable_raw_mode().map_err(|e| e.to_string())?;
    execute!(io::stdout(), cursor::Show).map_err(|e| e.to_string())?;
    print!("\r\n{}\r\n> ", prompt);
    io::stdout().flush().map_err(|e| e.to_string())?;
    let mut line = String::new();
    io::stdin().read_line(&mut line).map_err(|e| e.to_string())?;
    execute!(io::stdout(), cursor::Hide).map_err(|e| e.to_string())?;
    terminal::enable_raw_mode().map_err(|e| e.to_string())?;
    Ok(line.trim().to_string())
}

fn truncate_line(s: &str, w: usize) -> String {
    if w == 0 { return String::new(); }
    let c: Vec<char> = s.chars().collect();
    if c.len() <= w { return s.to_string(); }
    if w <= 1 { return "…".to_string(); }
    c[..w-1].iter().collect::<String>() + "…"
}

fn push_json_lines(lines: &mut Vec<String>, v: Value) {
    for l in serde_json::to_string_pretty(&v).unwrap_or_else(|_| v.to_string()).lines() { lines.push(l.to_string()); }
}

fn tab_lines(tab: TuiTab, port: u16, chat_log: &[(String, String)]) -> Vec<String> {
    let mut lines = Vec::new();
    match tab {
        TuiTab::Chat => {
            lines.push("Chat — c=schreiben, r=aktualisieren".to_string());
            if chat_log.is_empty() { lines.push("Noch keine lokale Chat-Historie.".to_string()); }
            else { for (r, c) in chat_log.iter().rev().take(12).rev() { lines.push(format!("{}: {}", r, c)); } }
        }
        TuiTab::Status => { lines.push("Status — echte Runtime-Health".to_string()); match health_request(port) { Ok(v) => push_json_lines(&mut lines, v), Err(e) => lines.push(format!("Fehler: {}", e)) } }
        TuiTab::Devices => {
            lines.push("Geräte — u=entkoppeln, g=Pairing-Code".to_string());
            lines.push("--- Peers ---".to_string()); match devices_request(port) { Ok(v) => push_json_lines(&mut lines, v), Err(e) => lines.push(format!("Fehler: {}", e)) }
            lines.push("--- Gekoppelt ---".to_string()); match paired_request(port) { Ok(v) => push_json_lines(&mut lines, v), Err(e) => lines.push(format!("Fehler: {}", e)) }
        }
        TuiTab::Projects => { lines.push("Projekte — n=anlegen, d=löschen".to_string()); match projects_request(port) { Ok(v) => push_json_lines(&mut lines, v), Err(e) => lines.push(format!("Fehler: {}", e)) } }
        TuiTab::Goals => { lines.push("Ziele — n=anlegen, a=aktivieren, p=pausieren, x=löschen".to_string()); match goals_request(port) { Ok(v) => push_json_lines(&mut lines, v), Err(e) => lines.push(format!("Fehler: {}", e)) } }
        TuiTab::Settings => { lines.push("Settings — e=ändern, z=zurücksetzen".to_string()); match settings_request(port, None) { Ok(v) => push_json_lines(&mut lines, v), Err(e) => lines.push(format!("Fehler: {}", e)) } }
        TuiTab::Help => { lines.extend(["1 Chat | 2 Status | 3 Geräte | 4 Projekte | 5 Ziele | 6 Settings | 7 Hilfe".to_string(), "q=Beenden".to_string(), "r=aktuelle Ansicht neu laden".to_string(), "c=Chat senden".to_string(), "g=Pairing-Code erzeugen".to_string(), "u=Gerät entkoppeln".to_string(), "n=Projekt/Ziel anlegen".to_string(), "d=Projekt löschen".to_string(), "a=Ziel aktivieren".to_string(), "p=Ziel pausieren".to_string(), "x=Ziel löschen".to_string(), "e=Setting ändern".to_string(), "z=Setting zurücksetzen".to_string()]); }
    }
    lines
}

fn render_tui(tab: TuiTab, port: u16, chat_log: &[(String, String)], status: &str) -> Result<(), String> {
    let (w, h) = terminal::size().map_err(|e| e.to_string())?;
    let (w, h) = (w as usize, h as usize);
    let mut o = io::stdout();
    execute!(o, cursor::MoveTo(0, 0), terminal::Clear(ClearType::All)).map_err(|e| e.to_string())?;
    let tabs = TuiTab::all().iter().enumerate().map(|(i, t)| { if *t == tab { format!("[{}:{}]", i+1, t.title()) } else { format!(" {}:{} ", i+1, t.title()) } }).collect::<Vec<_>>().join(" ");
    writeln!(o, "{}", truncate_line(&format!("Eidolon TUI · Port {} · {}", port, tabs), w)).map_err(|e| e.to_string())?;
    writeln!(o, "{}", "─".repeat(w.min(80))).map_err(|e| e.to_string())?;
    for l in tab_lines(tab, port, chat_log).into_iter().take(h.saturating_sub(4)) { writeln!(o, "{}", truncate_line(&l, w)).map_err(|e| e.to_string())?; }
    writeln!(o, "{}", "─".repeat(w.min(80))).map_err(|e| e.to_string())?;
    writeln!(o, "{}", truncate_line(status, w)).map_err(|e| e.to_string())?;
    o.flush().map_err(|e| e.to_string())
}

fn run_tui(port: u16) -> Result<(), String> {
    terminal::enable_raw_mode().map_err(|e| e.to_string())?;
    let mut o = io::stdout();
    execute!(o, EnterAlternateScreen, cursor::Hide).map_err(|e| e.to_string())?;
    let mut tab = TuiTab::Chat;
    let mut chat_log: Vec<(String, String)> = Vec::new();
    let mut status = "q beendet · r aktualisiert".to_string();
    render_tui(tab, port, &chat_log, &status)?;
    loop {
        if event::poll(Duration::from_millis(250)).map_err(|e| e.to_string())? {
            if let Event::Key(key) = event::read().map_err(|e| e.to_string())? {
                match key.code {
                    KeyCode::Char('q') => break,
                    KeyCode::Char('1') => tab = TuiTab::Chat,
                    KeyCode::Char('2') => tab = TuiTab::Status,
                    KeyCode::Char('3') => tab = TuiTab::Devices,
                    KeyCode::Char('4') => tab = TuiTab::Projects,
                    KeyCode::Char('5') => tab = TuiTab::Goals,
                    KeyCode::Char('6') => tab = TuiTab::Settings,
                    KeyCode::Char('7') => tab = TuiTab::Help,
                    KeyCode::Char('r') => status = format!("{} aktualisiert", tab.title()),
                    KeyCode::Char('c') if tab == TuiTab::Chat => {
                        let msg = prompt_line("Nachricht")?;
                        if !msg.is_empty() {
                            match chat_request(port, &msg, "eidolon-tui") {
                                Ok(j) => { let r = j.get("response").and_then(|v| v.as_str()).unwrap_or("Keine Antwort"); chat_log.push(("user".to_string(), msg)); chat_log.push(("assistant".to_string(), r.to_string())); status = "Chat gesendet".to_string(); }
                                Err(e) => status = format!("Chat-Fehler: {}", e),
                            }
                        }
                    }
                    KeyCode::Char('g') if tab == TuiTab::Devices => match pair_request(port) { Ok(j) => status = format!("Code: {}", j.get("code").and_then(|v| v.as_str()).unwrap_or("-")), Err(e) => status = format!("Pairing-Fehler: {}", e) },
                    KeyCode::Char('u') if tab == TuiTab::Devices => { let id = prompt_line("Peer-ID")?; if !id.is_empty() { match unpair_request(port, &id) { Ok(j) => status = format!("Entkoppelt: {}", j), Err(e) => status = format!("Fehler: {}", e) } } }
                    KeyCode::Char('n') if tab == TuiTab::Projects => { let t = prompt_line("Titel")?; if !t.is_empty() { match create_project_request(port, &t, "", "") { Ok(j) => status = format!("Angelegt: {}", j.get("project").and_then(|p| p.get("id")).and_then(|v| v.as_str()).unwrap_or("ok")), Err(e) => status = format!("Fehler: {}", e) } } }
                    KeyCode::Char('d') if tab == TuiTab::Projects => { let id = prompt_line("Projekt-ID")?; if !id.is_empty() { match delete_project_request(port, &id) { Ok(j) => status = format!("Gelöscht: {}", j.get("ok").and_then(|v| v.as_bool()).unwrap_or(false)), Err(e) => status = format!("Fehler: {}", e) } } }
                    KeyCode::Char('n') if tab == TuiTab::Goals => { let t = prompt_line("Titel")?; if !t.is_empty() { match create_goal_request(port, &t, "", "system", 1, vec![]) { Ok(j) => status = format!("Angelegt: {}", j.get("goal").and_then(|g| g.get("id")).and_then(|v| v.as_str()).unwrap_or("ok")), Err(e) => status = format!("Fehler: {}", e) } } }
                    KeyCode::Char('a') if tab == TuiTab::Goals => { let id = prompt_line("Goal-ID")?; if !id.is_empty() { match transition_goal_request(port, &id, "active", None) { Ok(j) => status = format!("Transition: {}", j), Err(e) => status = format!("Fehler: {}", e) } } }
                    KeyCode::Char('p') if tab == TuiTab::Goals => { let id = prompt_line("Goal-ID")?; if !id.is_empty() { match transition_goal_request(port, &id, "paused", None) { Ok(j) => status = format!("Transition: {}", j), Err(e) => status = format!("Fehler: {}", e) } } }
                    KeyCode::Char('x') if tab == TuiTab::Goals => { let id = prompt_line("Goal-ID")?; if !id.is_empty() { match delete_goal_request(port, &id) { Ok(j) => status = format!("Gelöscht: {}", j.get("ok").and_then(|v| v.as_bool()).unwrap_or(false)), Err(e) => status = format!("Fehler: {}", e) } } }
                    KeyCode::Char('e') if tab == TuiTab::Settings => { let a = prompt_line("Bereich")?; let k = prompt_line("Key")?; let v = prompt_line("Wert")?; if !a.is_empty() && !k.is_empty() && !v.is_empty() { match settings_update_request(port, &a, &k, &v) { Ok(_) => status = format!("{}.{} aktualisiert", a, k), Err(e) => status = format!("Fehler: {}", e) } } }
                    KeyCode::Char('z') if tab == TuiTab::Settings => { let a = prompt_line("Bereich")?; if !a.is_empty() { match settings_reset_request(port, &a) { Ok(_) => status = format!("{} zurückgesetzt", a), Err(e) => status = format!("Fehler: {}", e) } } }
                    _ => {}
                }
                render_tui(tab, port, &chat_log, &status)?;
            }
        }
    }
    terminal::disable_raw_mode().map_err(|e| e.to_string())?;
    execute!(o, cursor::Show, LeaveAlternateScreen).map_err(|e| e.to_string())?;
    Ok(())
}

fn run_setup(port: u16) -> Result<(), String> {
    println!("Eidolon Setup — Port {}", port);
    let dir = python_runtime_dir();
    let settings_path = dir.join("data").join("user").join("settings.json");

    println!("Runtime-Ordner: {}", dir.display());
    if !dir.exists() || !dir.join("agent_server.py").exists() {
        return Err("Python-Runtime nicht gefunden. Bitte Repository klonen und Setup wiederholen.".into());
    }

    let mut settings: std::collections::HashMap<String, serde_json::Value> = std::collections::HashMap::new();
    if settings_path.exists() {
        settings = serde_json::from_str(&std::fs::read_to_string(&settings_path).map_err(|e| e.to_string())?).unwrap_or_default();
    }

    println!("Setup: LLM-Anbieter wählen");
    println!("  1) Ollama (lokal)");
    println!("  2) OpenAI (Login via ChatGPT/Codex)");
    print!("Auswahl [1]: ");
    io::stdout().flush().map_err(|e| e.to_string())?;
    let mut provider_line = String::new();
    io::stdin().read_line(&mut provider_line).map_err(|e| e.to_string())?;
    let provider = match provider_line.trim() { "2" => "openai_oauth", _ => "ollama" };
    let mut llm = settings.entry("llm".into()).or_insert_with(|| json!({})).as_object().cloned().unwrap_or_default();
    llm.insert("provider".into(), Value::String(provider.into()));
    if provider == "ollama" {
        print!("Ollama-URL [http://localhost:11434]: ");
        io::stdout().flush().map_err(|e| e.to_string())?;
        let mut url = String::new();
        io::stdin().read_line(&mut url).map_err(|e| e.to_string())?;
        let url = url.trim();
        if !url.is_empty() { llm.insert("ollama_url".into(), Value::String(url.into())); }
        llm.insert("model".into(), Value::String("llama3.1:8b".into()));
    } else {
        llm.insert("model".into(), Value::String("gpt-5.5".into()));
        println!("OpenAI-Login nutzt deine ChatGPT/OpenAI-Anmeldung über Codex.");
        println!("Führe danach im Terminal aus: eidolon openai-login --device-auth");
    }
    settings.insert("llm".into(), Value::Object(llm));

    println!("Setup: Sprache");
    println!("  1) de");
    println!("  2) en");
    print!("Auswahl [1]: ");
    io::stdout().flush().map_err(|e| e.to_string())?;
    let mut lang_line = String::new();
    io::stdin().read_line(&mut lang_line).map_err(|e| e.to_string())?;
    let language = match lang_line.trim() { "2" => "en", _ => "de" };
    let mut ui = settings.entry("ui".into()).or_insert_with(|| json!({})).as_object().cloned().unwrap_or_default();
    ui.insert("language".into(), Value::String(language.into()));
    settings.insert("ui".into(), Value::Object(ui));

    fs::create_dir_all(settings_path.parent().unwrap()).map_err(|e| e.to_string())?;
    fs::write(&settings_path, serde_json::to_string_pretty(&settings).map_err(|e| e.to_string())?).map_err(|e| e.to_string())?;
    println!("Gespeichert: {}", settings_path.display());

    let health_ok = health_request(port).is_ok();
    if !health_ok {
        println!("Starte Runtime auf Port {}...", port);
        let dir = python_runtime_dir();
        let child = Command::new("python")
            .args(["-m", "uvicorn", "agent_server:app", "--host", "0.0.0.0", "--port", &port.to_string()])
            .current_dir(&dir)
            .spawn()
            .map_err(|e| format!("Runtime-Start fehlgeschlagen: {}", e))?;
        println!("Runtime gestartet (PID {})", child.id());
        println!("Warte auf Health-Endpoint...");
        for _ in 0..40 {
            if health_request(port).is_ok() { break; }
            std::thread::sleep(std::time::Duration::from_millis(250));
        }
        let _ = child;
    }

    println!("\nFertig. Du kannst jetzt direkt chatten.");
    run_chat_mode(port)
}

fn main() {
    let cli = Cli::parse();
    match &cli.command {
        Some(Commands::Serve { port }) => {
            let dir = python_runtime_dir();
            let s = Command::new("python").args(["-m", "uvicorn", "agent_server:app", "--host", "0.0.0.0", "--port", &port.to_string()]).env("EIDOLON_RUNTIME_PORT", port.to_string()).current_dir(&dir).status();
            match s {
                Ok(s) if s.success() => {}
                Ok(s) => { eprintln!("Runtime exited with {:?}", s.code()); std::process::exit(s.code().unwrap_or(1)); }
                Err(e) => { eprintln!("Failed to launch: {}", e); std::process::exit(1); }
            }
        }
        Some(Commands::Chat { message, port }) => match chat_request(*port, message, "eidolon-cli") { Ok(j) => print_json(&j), Err(e) => { eprintln!("Chat failed: {}", e); std::process::exit(1); } },
        Some(Commands::Repl { port }) => { if let Err(e) = run_repl(*port) { eprintln!("REPL failed: {}", e); std::process::exit(1); } }
        Some(Commands::Tui { port }) => { if let Err(e) = run_tui(*port) { let _ = terminal::disable_raw_mode(); let _ = execute!(io::stdout(), cursor::Show, LeaveAlternateScreen); eprintln!("TUI failed: {}", e); std::process::exit(1); } }
        Some(Commands::Devices { port }) => match devices_request(*port) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Devices failed: {}", e); std::process::exit(1); } },
        Some(Commands::Paired { port }) => match paired_request(*port) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Paired failed: {}", e); std::process::exit(1); } },
        Some(Commands::Pair { port }) => match pair_request(*port) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Pair failed: {}", e); std::process::exit(1); } },
        Some(Commands::Unpair { peer_id, port }) => match unpair_request(*port, peer_id) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Unpair failed: {}", e); std::process::exit(1); } },
        Some(Commands::Projects { port }) => match projects_request(*port) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Projects failed: {}", e); std::process::exit(1); } },
        Some(Commands::Workspaces { port }) => match workspaces_request(*port) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Workspaces failed: {}", e); std::process::exit(1); } },
        Some(Commands::WorkspaceExecute { workspace_id, port }) => match workspace_execute_request(*port, workspace_id.as_deref()) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Workspace execute failed: {}", e); std::process::exit(1); } },
        Some(Commands::ProjectCreate { title, description, domain, port }) => match create_project_request(*port, title, description, domain) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Project create failed: {}", e); std::process::exit(1); } },
        Some(Commands::ProjectDelete { project_id, port }) => match delete_project_request(*port, project_id) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Project delete failed: {}", e); std::process::exit(1); } },
        Some(Commands::Goals { port }) => match goals_request(*port) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Goals failed: {}", e); std::process::exit(1); } },
        Some(Commands::GoalCreate { title, description, category, priority, steps, port }) => match create_goal_request(*port, title, description, category, *priority, steps.clone()) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Goal create failed: {}", e); std::process::exit(1); } },
        Some(Commands::GoalTransition { goal_id, status, error, port }) => match transition_goal_request(*port, goal_id, status, Some(error)) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Goal transition failed: {}", e); std::process::exit(1); } },
        Some(Commands::GoalDelete { goal_id, port }) => match delete_goal_request(*port, goal_id) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Goal delete failed: {}", e); std::process::exit(1); } },
        Some(Commands::Settings { area, port }) => match settings_request(*port, area.as_deref()) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Settings failed: {}", e); std::process::exit(1); } },
        Some(Commands::SettingsSet { area, key, value, port }) => match settings_update_request(*port, area, key, value) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Settings update failed: {}", e); std::process::exit(1); } },
        Some(Commands::SettingsReset { area, port }) => match settings_reset_request(*port, area) { Ok(j) => print_json(&j), Err(e) => { eprintln!("Settings reset failed: {}", e); std::process::exit(1); } },
        Some(Commands::Setup { port }) => { if let Err(e) = run_setup(*port) { eprintln!("Setup failed: {}", e); std::process::exit(1); } },
        Some(Commands::OpenaiLogin { device_auth }) => { if let Err(e) = openai_login_command(*device_auth) { eprintln!("OpenAI login failed: {}", e); std::process::exit(1); } },
        Some(Commands::OpenaiStatus) => match openai_status_command() { Ok(j) => print_json(&j), Err(e) => { eprintln!("OpenAI status failed: {}", e); std::process::exit(1); } },
        Some(Commands::OpenaiUse { model, port }) => match openai_use_request(*port, model) { Ok(j) => print_json(&j), Err(e) => { eprintln!("OpenAI activation failed: {}", e); std::process::exit(1); } },
        Some(Commands::Api { method, path, body, port }) => match api(*port, method, path, body.as_deref()) { Ok(j) => print_json(&j), Err(e) => { eprintln!("API failed: {}", e); std::process::exit(1); } },
        Some(Commands::Diagnose { port }) => print_json(&diagnose_request(*port)),
        None => {
            let port = 8002;
            if !is_configured() {
                if let Err(e) = run_setup(port) { eprintln!("Setup failed: {}", e); std::process::exit(1); }
            }
            if health_request(port).is_err() {
                println!("Runtime auf Port {} wird gestartet...", port);
                let dir = python_runtime_dir();
                let _ = Command::new("python").args(["-m", "uvicorn", "agent_server:app", "--host", "0.0.0.0", "--port", &port.to_string()]).current_dir(&dir).spawn();
                for _ in 0..60 {
                    if health_request(port).is_ok() { break; }
                    std::thread::sleep(std::time::Duration::from_millis(250));
                }
            }
            if let Err(e) = run_chat_mode(port) { eprintln!("Chat failed: {}", e); std::process::exit(1); }
        }
    }
}
