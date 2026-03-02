use std::collections::hash_map::RandomState;
use std::hash::{BuildHasher, Hasher};
use std::net::UdpSocket;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

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
}

impl WallServerState {
    pub fn new() -> Self {
        Self {
            stop_flag: std::sync::Mutex::new(None),
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
    if let Some(flag) = state.stop_flag.lock().unwrap().take() {
        flag.store(true, Ordering::Release);
    }

    let server = Server::http("0.0.0.0:0").map_err(|e| format!("HTTP bind failed: {}", e))?;
    let port = server.server_addr().to_ip().map(|addr| addr.port()).ok_or("Failed to get port")?;
    let local_ip = detect_local_ip();
    let token = generate_token();
    let url = format!("http://{}:{}/shake?token={}", local_ip, port, token);

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
    let start = Instant::now();
    let fallback_timeout = Duration::from_secs(60);

    let port = server.server_addr().to_ip().map(|addr| addr.port()).unwrap_or(0);
    let local_ip = detect_local_ip();
    let server_url = format!("http://{}:{}", local_ip, port);

    loop {
        if start.elapsed() > fallback_timeout {
            tracing::info!("WallServer: 60s timeout — auto-unlocking wall");
            let _ = app.emit("sensor-accelerometer", "move");
            break;
        }

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
        let html = build_shake_html(server_url, token);
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

fn build_shake_html(server_url: &str, token: &str) -> String {
    SHAKE_HTML_TEMPLATE.replace("__SERVER_URL__", server_url).replace("__TOKEN__", token)
}

// NOTE: DeviceMotionEvent requires HTTPS on iOS 13+ and Android Chrome 74+.
// Plain HTTP (local network) prevents sensor access. We use a tap-counter
// instead — works on all browsers over HTTP, no permissions required.
const SHAKE_HTML_TEMPLATE: &str = r##"<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>GSE - Unlock</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f172a;color:#f8fafc;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;padding:1.5rem;text-align:center;user-select:none;-webkit-user-select:none;}
h1{font-size:1.4rem;margin-bottom:0.5rem}
.sub{font-size:0.95rem;opacity:0.7;margin-bottom:1rem}
.progress-bg{width:80%;max-width:280px;height:20px;background:rgba(255,255,255,0.1);border-radius:10px;overflow:hidden;margin:0.8rem 0;}
.progress-fill{height:100%;background:#4ade80;border-radius:10px;transition:width 0.2s ease;width:0%;}
.status{font-size:1rem;margin:0.5rem 0;min-height:2.5em;opacity:0.85}
.icon{font-size:3rem;margin-bottom:0.8rem}
.done{color:#4ade80;font-size:1.5rem;font-weight:700}
.start-btn{padding:0.9rem 2.2rem;font-size:1.1rem;background:#4ade80;color:#0f172a;border:none;border-radius:10px;cursor:pointer;font-weight:700;margin-top:0.5rem;}
.tap-btn{display:none;width:180px;height:180px;border-radius:50%;background:#4ade80;color:#0f172a;border:none;font-size:1.6rem;font-weight:700;cursor:pointer;flex-direction:column;align-items:center;justify-content:center;margin-top:1rem;-webkit-tap-highlight-color:rgba(0,0,0,0);touch-action:manipulation;}
.tap-btn:active{opacity:0.75;transform:scale(0.93);}
.tap-count{font-size:1rem;margin-top:0.3rem;opacity:0.75;}
</style>
</head>
<body>
<div class="icon" id="icon">🚶</div>
<h1>Stand Up to Unlock</h1>
<p class="sub">Stand up and tap the button 10 times</p>
<div class="progress-bg"><div class="progress-fill" id="progress"></div></div>
<p class="status" id="status">Press Start when you are standing</p>
<button class="start-btn" id="startBtn">Start</button>
<button class="tap-btn" id="tapBtn">
  TAP
  <span class="tap-count" id="tapCount">0 / 10</span>
</button>
<script>
(function(){
  var REQUIRED=10;
  var SERVER='__SERVER_URL__',TOKEN='__TOKEN__';
  var count=0,unlocked=false;
  var statusEl=document.getElementById('status'),progressEl=document.getElementById('progress');
  var iconEl=document.getElementById('icon');
  var startBtn=document.getElementById('startBtn'),tapBtn=document.getElementById('tapBtn');
  var tapCountEl=document.getElementById('tapCount');

  function doUnlock(){
    unlocked=true;
    tapBtn.style.display='none';
    iconEl.textContent='\u2705';
    statusEl.textContent='Unlocked! Return to your computer.';
    statusEl.className='status done';
    progressEl.style.width='100%';
    fetch(SERVER+'/unlock?token='+TOKEN,{method:'POST'}).catch(function(){});
  }

  function onTap(e){
    if(unlocked)return;
    e.preventDefault();
    count++;
    tapCountEl.textContent=count+' / '+REQUIRED;
    progressEl.style.width=Math.min(100,(count/REQUIRED)*100)+'%';
    statusEl.textContent='Keep going! '+count+' of '+REQUIRED;
    if(count>=REQUIRED) doUnlock();
  }

  startBtn.addEventListener('click',function(){
    startBtn.style.display='none';
    tapBtn.style.display='flex';
    statusEl.textContent='Tap the button '+REQUIRED+' times!';
  });

  tapBtn.addEventListener('touchstart',onTap,{passive:false});
  tapBtn.addEventListener('click',onTap);
})();
</script>
</body>
</html>
"##;
