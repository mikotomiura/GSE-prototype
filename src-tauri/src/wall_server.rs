use std::collections::hash_map::RandomState;
use std::hash::{BuildHasher, Hasher};
use std::net::UdpSocket;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use qrcode::QrCode;
use tauri::{Emitter, Runtime, State};
use tiny_http::{Header, Response, Server};

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

#[derive(serde::Serialize, Clone, Debug)]
pub struct WallServerInfo {
    pub qr_svg: String,
    pub url: String,
}

pub struct WallServerState {
    stop_flag: std::sync::Mutex<Option<Arc<AtomicBool>>>,
    /// 動的に追加したファイアウォールルール名。stop 時に削除する (advice.md §B)
    firewall_rule: std::sync::Mutex<Option<String>>,
}

impl WallServerState {
    pub fn new() -> Self {
        Self {
            stop_flag: std::sync::Mutex::new(None),
            firewall_rule: std::sync::Mutex::new(None),
        }
    }
}

// ---------------------------------------------------------------------------
// Tauri コマンド
// ---------------------------------------------------------------------------

#[tauri::command]
pub fn start_wall_server<R: Runtime>(
    app: tauri::AppHandle<R>,
    state: State<WallServerState>,
) -> Result<WallServerInfo, String> {
    // 前回サーバーを停止し、既存のファイアウォールルールを削除
    if let Some(flag) = state.stop_flag.lock().unwrap().take() {
        flag.store(true, Ordering::Release);
    }
    if let Some(rule) = state.firewall_rule.lock().unwrap().take() {
        remove_firewall_rule(&rule);
    }

    let server = Server::http("0.0.0.0:0").map_err(|e| format!("HTTP bind failed: {}", e))?;
    let port = server.server_addr().to_ip().map(|addr| addr.port()).ok_or("Failed to get port")?;
    let local_ip = detect_local_ip();
    let token = generate_token();
    let url = format!("http://{}:{}/shake?token={}", local_ip, port, token);

    // Windowsファイアウォールにインバウンド許可ルールを追加 (advice.md §B)
    // netsh は管理者権限が必要。権限不足の場合は警告を出して続行する。
    let rule_name = format!("GSE-WallServer-{}", port);
    add_firewall_rule(port, &rule_name);
    *state.firewall_rule.lock().unwrap() = Some(rule_name);

    tracing::info!("WallServer: started on {}:{} (token={}...)", local_ip, port, &token[..8]);

    let qr_svg = generate_qr_data_url(&url)?;
    let info = WallServerInfo { qr_svg, url: url.clone() };

    let shutdown = Arc::new(AtomicBool::new(false));
    let shutdown_clone = shutdown.clone();
    let server_arc = Arc::new(server);

    thread::spawn(move || {
        server_loop(server_arc, token, shutdown_clone, app);
    });

    *state.stop_flag.lock().unwrap() = Some(shutdown);

    Ok(info)
}

#[tauri::command]
pub fn stop_wall_server(state: State<WallServerState>) {
    if let Some(flag) = state.stop_flag.lock().unwrap().take() {
        flag.store(true, Ordering::Release);
    }
    if let Some(rule) = state.firewall_rule.lock().unwrap().take() {
        remove_firewall_rule(&rule);
    }
}

// ---------------------------------------------------------------------------
// Server loop
// ---------------------------------------------------------------------------

fn server_loop<R: Runtime>(
    server: Arc<Server>,
    token: String,
    shutdown: Arc<AtomicBool>,
    app: tauri::AppHandle<R>,
) {
    let port = server.server_addr().to_ip().map(|addr| addr.port()).unwrap_or(0);
    let local_ip = detect_local_ip();
    let server_url = format!("http://{}:{}", local_ip, port);

    loop {
        if shutdown.load(Ordering::Acquire) { break; }

        match server.recv_timeout(Duration::from_secs(1)) {
            Ok(Some(request)) => {
                dispatch_request(request, &token, &server_url, &shutdown, &app);
            }
            Ok(None) => {}
            Err(_) => break,
        }
    }
}

fn dispatch_request<R: Runtime>(
    request: tiny_http::Request,
    token: &str,
    server_url: &str,
    shutdown: &Arc<AtomicBool>,
    app: &tauri::AppHandle<R>,
) {
    let url = request.url().to_string();

    if url.starts_with("/shake") && extract_token(&url) == token {
        let html = build_timer_html(server_url, token);
        let header = Header::from_bytes("Content-Type", "text/html; charset=utf-8").unwrap();
        let _ = request.respond(Response::from_string(html).with_header(header));
    } else if url.starts_with("/unlock") && extract_token(&url) == token {
        tracing::info!("WallServer: unlock signal received from smartphone");
        let _ = app.emit("sensor-accelerometer", "move");
        shutdown.store(true, Ordering::Release);

        let cors = Header::from_bytes("Access-Control-Allow-Origin", "*").unwrap();
        let ct = Header::from_bytes("Content-Type", "application/json").unwrap();
        let _ = request.respond(Response::from_string(r#"{"status":"unlocked"}"#).with_header(cors).with_header(ct));
    } else if request.method() == &tiny_http::Method::Options {
        let cors1 = Header::from_bytes("Access-Control-Allow-Origin", "*").unwrap();
        let cors2 = Header::from_bytes("Access-Control-Allow-Methods", "POST, OPTIONS").unwrap();
        let cors3 = Header::from_bytes("Access-Control-Allow-Headers", "Content-Type").unwrap();
        let _ = request.respond(Response::from_string("").with_header(cors1).with_header(cors2).with_header(cors3));
    } else {
        let _ = request.respond(Response::from_string("Not Found").with_status_code(tiny_http::StatusCode(404)));
    }
}

fn extract_token(url: &str) -> &str {
    url.split("token=").nth(1).unwrap_or("").split('&').next().unwrap_or("")
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

fn detect_local_ip() -> String {
    UdpSocket::bind("0.0.0.0:0")
        .and_then(|socket| { socket.connect("8.8.8.8:80")?; Ok(socket.local_addr()?.ip().to_string()) })
        .unwrap_or_else(|_| "127.0.0.1".to_string())
}

fn generate_token() -> String {
    let nanos = SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_nanos() as u64;
    let mut h1 = RandomState::new().build_hasher();
    h1.write_u64(nanos);
    let v1 = h1.finish();
    let mut h2 = RandomState::new().build_hasher();
    h2.write_u64(v1 ^ std::process::id() as u64);
    format!("{:016x}{:016x}", v1, h2.finish())
}

/// Windows Defender ファイアウォールにインバウンド TCP 許可ルールを追加する (advice.md §B)
/// netsh advfirewall は管理者権限が必要。権限不足でも Err を返さず警告ログのみ出す。
fn add_firewall_rule(port: u16, rule_name: &str) {
    let result = std::process::Command::new("netsh")
        .args([
            "advfirewall", "firewall", "add", "rule",
            &format!("name={}", rule_name),
            "protocol=TCP",
            "dir=in",
            "action=allow",
            &format!("localport={}", port),
        ])
        .output();

    match result {
        Ok(output) if output.status.success() => {
            tracing::info!("WallServer: firewall rule '{}' added for port {}", rule_name, port);
        }
        Ok(output) => {
            let stderr = String::from_utf8_lossy(&output.stderr);
            tracing::warn!(
                "WallServer: firewall rule add failed (admin required?): {}",
                stderr.trim()
            );
            tracing::warn!(
                "To allow smartphone access manually: \
                 netsh advfirewall firewall add rule name={} protocol=TCP dir=in action=allow localport={}",
                rule_name, port
            );
        }
        Err(e) => {
            tracing::warn!("WallServer: could not run netsh: {}", e);
        }
    }
}

/// Windows Defender ファイアウォールから GSE ルールを削除する
fn remove_firewall_rule(rule_name: &str) {
    let result = std::process::Command::new("netsh")
        .args([
            "advfirewall", "firewall", "delete", "rule",
            &format!("name={}", rule_name),
        ])
        .output();

    match result {
        Ok(output) if output.status.success() => {
            tracing::info!("WallServer: firewall rule '{}' removed", rule_name);
        }
        Ok(_) => {
            tracing::debug!("WallServer: firewall rule '{}' not found (already removed?)", rule_name);
        }
        Err(e) => {
            tracing::warn!("WallServer: could not remove firewall rule: {}", e);
        }
    }
}

fn generate_qr_data_url(url: &str) -> Result<String, String> {
    use base64::{engine::general_purpose::STANDARD, Engine};
    let code = QrCode::new(url.as_bytes()).map_err(|e| format!("QR encode failed: {}", e))?;
    let svg = code.render::<qrcode::render::svg::Color>().min_dimensions(200, 200)
        .dark_color(qrcode::render::svg::Color("#000000"))
        .light_color(qrcode::render::svg::Color("#ffffff")).build();
    Ok(format!("data:image/svg+xml;base64,{}", STANDARD.encode(svg.as_bytes())))
}

// ---------------------------------------------------------------------------
// HTML
// ---------------------------------------------------------------------------

fn build_timer_html(server_url: &str, token: &str) -> String {
    TIMER_HTML_TEMPLATE.replace("__SERVER_URL__", server_url).replace("__TOKEN__", token)
}

// Phone page: 2-minute countdown timer.
// Unlock condition: phone timer auto-calls /unlock at 0:00 (only unlock path).
// No early exit — Monk Mode on the PC is the escape hatch if Wall is unwanted.
const TIMER_HTML_TEMPLATE: &str = r##"<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>GSE - Break Time</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f172a;color:#f8fafc;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:1.5rem;text-align:center;user-select:none;-webkit-user-select:none;}
h1{font-size:1.4rem;margin-bottom:0.4rem}
.sub{font-size:0.9rem;opacity:0.65;margin-bottom:0.8rem;line-height:1.5}
.timer{font-size:5rem;font-weight:700;font-variant-numeric:tabular-nums;letter-spacing:0.04em;margin:0.3rem 0;color:#4ade80;}
.progress-bg{width:80%;max-width:280px;height:10px;background:rgba(255,255,255,0.12);border-radius:5px;overflow:hidden;margin:0.6rem 0;}
.progress-fill{height:100%;background:#4ade80;border-radius:5px;transition:width 0.5s linear;width:0%;}
.status{font-size:0.9rem;margin:0.5rem 0;min-height:3.5em;opacity:0.8;line-height:1.6}
.icon{font-size:3rem;margin-bottom:0.6rem}
.complete{color:#4ade80;font-weight:700}
</style>
</head>
<body>
<div class="icon" id="icon">🚶</div>
<h1>Take a Break!</h1>
<p class="sub">Take a 2-minute break from your keyboard.<br>Your PC unlocks automatically when the timer ends.</p>
<div class="timer" id="timer">2:00</div>
<div class="progress-bg"><div class="progress-fill" id="progress"></div></div>
<p class="status" id="status">Walk away and relax.<br>Your PC unlocks when the timer ends.</p>
<script>
(function(){
  var DURATION=120;
  var SERVER='__SERVER_URL__',TOKEN='__TOKEN__';
  var scanTime=Date.now(),done=false;
  var timerEl=document.getElementById('timer'),progressEl=document.getElementById('progress');
  var statusEl=document.getElementById('status'),iconEl=document.getElementById('icon');

  function doUnlock(){
    if(done)return;
    done=true;
    iconEl.textContent='\u2705';
    statusEl.innerHTML='<span class="complete">Unlocked!</span><br>You can return to your computer.';
    fetch(SERVER+'/unlock?token='+TOKEN,{method:'POST'}).catch(function(){});
  }

  function tick(){
    if(done)return;
    var elapsed=(Date.now()-scanTime)/1000;
    var remaining=Math.max(0,DURATION-elapsed);
    var mins=Math.floor(remaining/60);
    var secs=Math.floor(remaining%60);
    timerEl.textContent=mins+':'+(secs<10?'0':'')+secs;
    progressEl.style.width=Math.min(100,(elapsed/DURATION)*100)+'%';
    if(remaining<=0){
      doUnlock();
    } else {
      setTimeout(tick,500);
    }
  }

  tick();
})();
</script>
</body>
</html>
"##;
