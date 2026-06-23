use std::collections::hash_map::RandomState;
use std::hash::{BuildHasher, Hasher};
use std::net::UdpSocket;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use crossbeam_channel::Sender;
use qrcode::QrCode;
use tauri::{Emitter, Runtime, State};
use tiny_http::{Header, Response, Server};

use crate::analysis::intervention::InterventionAction;
use crate::logger::{DismissReason, LogEntry};
use crate::LogState;

/// Zen タイマーの長さ (ms)。HTML テンプレートの `DURATION=120` (秒) と
/// intervention-design Rule4 (120秒) に一致させる。`/shake`〜`/unlock` の経過が
/// この値未満なら早期解除 (非順守)、以上なら通常解除 (順守) と判定する。
const ZEN_TIMER_MS: u64 = 120_000;

/// 現在時刻 (UNIX エポックからの ms)。
fn now_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64
}

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
    /// 動的に追加したファイアウォールルール名。stop 時に削除する (Windows のみ)
    #[cfg(target_os = "windows")]
    firewall_rule: std::sync::Mutex<Option<String>>,
}

impl WallServerState {
    pub fn new() -> Self {
        Self {
            stop_flag: std::sync::Mutex::new(None),
            #[cfg(target_os = "windows")]
            firewall_rule: std::sync::Mutex::new(None),
        }
    }

    /// WallServerを停止し、ファイアウォールルールを削除する。
    /// quit_app から呼ばれてリソースを確実にクリーンアップする。
    pub fn stop(&self) {
        if let Some(flag) = self
            .stop_flag
            .lock()
            .unwrap_or_else(|p| p.into_inner())
            .take()
        {
            flag.store(true, Ordering::Release);
        }
        #[cfg(target_os = "windows")]
        if let Some(rule) = self
            .firewall_rule
            .lock()
            .unwrap_or_else(|p| p.into_inner())
            .take()
        {
            remove_firewall_rule(&rule);
        }
    }
}

// ---------------------------------------------------------------------------
// Tauri コマンド
// ---------------------------------------------------------------------------

#[tauri::command]
pub(crate) fn start_wall_server<R: Runtime>(
    app: tauri::AppHandle<R>,
    state: State<WallServerState>,
    log: State<Arc<Mutex<LogState>>>,
) -> Result<WallServerInfo, String> {
    // 前回サーバーを停止
    if let Some(flag) = state.stop_flag.lock().unwrap().take() {
        flag.store(true, Ordering::Release);
    }
    #[cfg(target_os = "windows")]
    if let Some(rule) = state.firewall_rule.lock().unwrap().take() {
        remove_firewall_rule(&rule);
    }

    let server = Server::http("0.0.0.0:0").map_err(|e| format!("HTTP bind failed: {}", e))?;
    let port = server
        .server_addr()
        .to_ip()
        .map(|addr| addr.port())
        .ok_or("Failed to get port")?;
    let local_ip = detect_local_ip();
    let token = generate_token();
    let url = format!("http://{}:{}/shake?token={}", local_ip, port, token);

    // Windowsファイアウォールにインバウンド許可ルールを追加
    #[cfg(target_os = "windows")]
    {
        let rule_name = format!("GSE-WallServer-{}", port);
        add_firewall_rule(port, &rule_name);
        *state.firewall_rule.lock().unwrap() = Some(rule_name);
    }

    tracing::info!(
        "WallServer: started on {}:{} (token={}...)",
        local_ip,
        port,
        &token[..8]
    );

    let qr_svg = generate_qr_data_url(&url)?;
    let info = WallServerInfo {
        qr_svg,
        url: url.clone(),
    };

    let shutdown = Arc::new(AtomicBool::new(false));
    let shutdown_clone = shutdown.clone();
    let server_arc = Arc::new(server);

    // logger 送信ハンドルを clone してサーバスレッドへ渡す (/unlock 応答記録用)。
    let log_tx = log.lock().unwrap_or_else(|p| p.into_inner()).clone_log_tx();
    // Wall 提示 (phone scan = /shake) 時刻を保持し、/unlock で経過時間を算出する。
    let shake_at = Arc::new(AtomicU64::new(0));

    thread::spawn(move || {
        server_loop(server_arc, token, shutdown_clone, app, log_tx, shake_at);
    });

    *state.stop_flag.lock().unwrap() = Some(shutdown);

    Ok(info)
}

#[tauri::command]
pub(crate) fn stop_wall_server(state: State<WallServerState>) {
    if let Some(flag) = state.stop_flag.lock().unwrap().take() {
        flag.store(true, Ordering::Release);
    }
    #[cfg(target_os = "windows")]
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
    log_tx: Sender<LogEntry>,
    shake_at: Arc<AtomicU64>,
) {
    let port = server
        .server_addr()
        .to_ip()
        .map(|addr| addr.port())
        .unwrap_or(0);
    let local_ip = detect_local_ip();
    let server_url = format!("http://{}:{}", local_ip, port);

    loop {
        if shutdown.load(Ordering::Acquire) {
            break;
        }

        match server.recv_timeout(Duration::from_secs(1)) {
            Ok(Some(request)) => {
                dispatch_request(
                    request,
                    &token,
                    &server_url,
                    &shutdown,
                    &app,
                    &log_tx,
                    &shake_at,
                );
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
    log_tx: &Sender<LogEntry>,
    shake_at: &Arc<AtomicU64>,
) {
    let url = request.url().to_string();

    if url.starts_with("/shake") && extract_token(&url) == token {
        // /shake はページ取得 (GET) で、token は QR URL 自体が運ぶ設計 (/unlock の POST と非対称)。
        // スマートフォンがQRコードをスキャンして接続 → フロントエンドに通知。
        // phone scan = Zen タイマー起点。shake_at (受信時刻) は HTML 側 scanTime (描画時刻) と
        // 転送+描画ぶん (δ: 数十〜数百ms) だけずれる。server elapsed = phone_elapsed + δ + 往復遅延 で
        // 常に phone より大きいため通常解除判定は堅牢。境界の扱いは decisions.md D3 参照。
        //
        // 毎 /shake で上書きする (最新優先)。ページ再読込/再スキャンでは HTML 側 scanTime も
        // リセットされ phone タイマーが 2:00 から再開するため、最新 /shake を基準にするのが
        // 「今ユーザーが見ているタイマー」と一致して正しい (最初の /shake を保持すると逆に
        // 再読込後の早期解除を completed と誤判定する)。詳細は decisions.md D8。
        tracing::info!("WallServer: phone connected via /shake");
        shake_at.store(now_ms(), Ordering::Release);
        let _ = app.emit("wall-phone-connected", ());

        let html = build_timer_html(server_url, token);
        let header = Header::from_bytes("Content-Type", "text/html; charset=utf-8").unwrap();
        let _ = request.respond(Response::from_string(html).with_header(header));
    } else if url.starts_with("/unlock")
        && request.method() == &tiny_http::Method::Post
        && extract_token(&url) == token
    {
        // POST 限定 (intervention-design Rule6)。実フォン JS は常に method:'POST'。
        // 本タスクで /unlock に LogEntry 副作用を足したため、誤った GET 等で phantom な
        // intervention_response が出ないようメソッドを検証する (捕捉データの純度確保)。
        tracing::info!("WallServer: unlock signal received from smartphone");

        // 二度押し/fetch リトライ/複数端末で /unlock が複数回届いても重複記録しない。
        // shutdown を compare_exchange で false→true にできた「最初の解除」だけが記録・通知する。
        // 二回目以降も解除済みレスポンス (200) は返す (UX 不変)。
        let first_unlock = shutdown
            .compare_exchange(false, true, Ordering::AcqRel, Ordering::Acquire)
            .is_ok();
        if first_unlock {
            let _ = app.emit("sensor-accelerometer", "move");

            // 介入応答 (Wall 解除) を NDJSON に content-free で捕捉する (Phase A2)。
            // /shake からの経過時間で早期解除 (非順守) / 通常解除 (順守) を判定する。
            // JS は doUnlock() を 120s 後のみ・doEarlyUnlock() を 120s 前のみ許可するため、
            // server 側 elapsed が押下ボタンを一意に決定する (client 値は信頼しない)。
            let now = now_ms();
            let shake = shake_at.load(Ordering::Acquire);
            let (reason, elapsed_ms) = if shake != 0 {
                let elapsed = now.saturating_sub(shake);
                let reason = if elapsed < ZEN_TIMER_MS {
                    DismissReason::EarlyUnlock
                } else {
                    DismissReason::Completed
                };
                (reason, Some(elapsed))
            } else {
                // /shake を経ず (通常フロー外) に /unlock。順守を主張できないため早期解除扱い。
                // elapsed_ms=None が「フロー外」を示し、後段は Some を持つ実 early_unlock と区別できる。
                tracing::warn!("WallServer: /unlock without prior /shake (elapsed unknown)");
                (DismissReason::EarlyUnlock, None)
            };
            // try_send で非ブロッキング。channel full/disconnected でも解除レスポンスは返す
            // (研究捕捉 < ユーザー解除の確実性)。本文・キーストロークは一切含めない (data-privacy)。
            let _ = log_tx.try_send(LogEntry::InterventionResponse {
                timestamp: now,
                action: InterventionAction::Wall.as_str().to_string(),
                reason,
                elapsed_ms,
            });
        }

        let cors = Header::from_bytes("Access-Control-Allow-Origin", "*").unwrap();
        let ct = Header::from_bytes("Content-Type", "application/json").unwrap();
        let _ = request.respond(
            Response::from_string(r#"{"status":"unlocked"}"#)
                .with_header(cors)
                .with_header(ct),
        );
    } else if request.method() == &tiny_http::Method::Options {
        let cors1 = Header::from_bytes("Access-Control-Allow-Origin", "*").unwrap();
        let cors2 = Header::from_bytes("Access-Control-Allow-Methods", "POST, OPTIONS").unwrap();
        let cors3 = Header::from_bytes("Access-Control-Allow-Headers", "Content-Type").unwrap();
        let _ = request.respond(
            Response::from_string("")
                .with_header(cors1)
                .with_header(cors2)
                .with_header(cors3),
        );
    } else {
        let _ = request.respond(
            Response::from_string("Not Found").with_status_code(tiny_http::StatusCode(404)),
        );
    }
}

fn extract_token(url: &str) -> &str {
    url.split("token=")
        .nth(1)
        .unwrap_or("")
        .split('&')
        .next()
        .unwrap_or("")
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

fn detect_local_ip() -> String {
    UdpSocket::bind("0.0.0.0:0")
        .and_then(|socket| {
            socket.connect("8.8.8.8:80")?;
            Ok(socket.local_addr()?.ip().to_string())
        })
        .unwrap_or_else(|_| "127.0.0.1".to_string())
}

fn generate_token() -> String {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_nanos() as u64;
    let mut h1 = RandomState::new().build_hasher();
    h1.write_u64(nanos);
    let v1 = h1.finish();
    let mut h2 = RandomState::new().build_hasher();
    h2.write_u64(v1 ^ std::process::id() as u64);
    format!("{:016x}{:016x}", v1, h2.finish())
}

/// Windows Defender ファイアウォールにインバウンド TCP 許可ルールを追加する
/// netsh advfirewall は管理者権限が必要。権限不足でも Err を返さず警告ログのみ出す。
#[cfg(target_os = "windows")]
fn add_firewall_rule(port: u16, rule_name: &str) {
    let result = std::process::Command::new("netsh")
        .args([
            "advfirewall",
            "firewall",
            "add",
            "rule",
            &format!("name={}", rule_name),
            "protocol=TCP",
            "dir=in",
            "action=allow",
            &format!("localport={}", port),
        ])
        .output();

    match result {
        Ok(output) if output.status.success() => {
            tracing::info!(
                "WallServer: firewall rule '{}' added for port {}",
                rule_name,
                port
            );
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
#[cfg(target_os = "windows")]
fn remove_firewall_rule(rule_name: &str) {
    let result = std::process::Command::new("netsh")
        .args([
            "advfirewall",
            "firewall",
            "delete",
            "rule",
            &format!("name={}", rule_name),
        ])
        .output();

    match result {
        Ok(output) if output.status.success() => {
            tracing::info!("WallServer: firewall rule '{}' removed", rule_name);
        }
        Ok(_) => {
            tracing::debug!(
                "WallServer: firewall rule '{}' not found (already removed?)",
                rule_name
            );
        }
        Err(e) => {
            tracing::warn!("WallServer: could not remove firewall rule: {}", e);
        }
    }
}

fn generate_qr_data_url(url: &str) -> Result<String, String> {
    use base64::{engine::general_purpose::STANDARD, Engine};
    let code = QrCode::new(url.as_bytes()).map_err(|e| format!("QR encode failed: {}", e))?;
    let svg = code
        .render::<qrcode::render::svg::Color>()
        .min_dimensions(200, 200)
        .dark_color(qrcode::render::svg::Color("#000000"))
        .light_color(qrcode::render::svg::Color("#ffffff"))
        .build();
    Ok(format!(
        "data:image/svg+xml;base64,{}",
        STANDARD.encode(svg.as_bytes())
    ))
}

// ---------------------------------------------------------------------------
// HTML
// ---------------------------------------------------------------------------

fn build_timer_html(server_url: &str, token: &str) -> String {
    TIMER_HTML_TEMPLATE
        .replace("__SERVER_URL__", server_url)
        .replace("__TOKEN__", token)
}

// Phone page: 2-minute countdown timer with manual unlock.
// Primary unlock: "Unlock Wall" button appears after timer reaches 0:00.
// Early unlock: "早期解除する" button is always visible for immediate unlock.
// Monk Mode on the PC is the escape hatch if Wall is unwanted entirely.
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
.unlock-btn{display:none;margin-top:1rem;padding:1rem 2.5rem;font-size:1.2rem;font-weight:700;color:#0f172a;background:#4ade80;border:none;border-radius:12px;cursor:pointer;transition:transform 0.1s,opacity 0.2s;-webkit-tap-highlight-color:transparent;}
.unlock-btn:active{transform:scale(0.95);opacity:0.85}
.unlock-btn.visible{display:inline-block;animation:fadeIn 0.3s ease-out}
.early-unlock-btn{margin-top:1.5rem;padding:0.6rem 1.5rem;font-size:0.85rem;font-weight:500;color:rgba(248,250,252,0.5);background:transparent;border:1px solid rgba(248,250,252,0.2);border-radius:8px;cursor:pointer;transition:color 0.2s,border-color 0.2s,transform 0.1s;-webkit-tap-highlight-color:transparent;}
.early-unlock-btn:active{transform:scale(0.95);color:rgba(248,250,252,0.8);border-color:rgba(248,250,252,0.4)}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
</style>
</head>
<body>
<div class="icon" id="icon">&#x1F6B6;</div>
<h1>Take a Break!</h1>
<p class="sub">Take a 2-minute break from your keyboard.<br>Tap the button below when the timer ends.</p>
<div class="timer" id="timer">2:00</div>
<div class="progress-bg"><div class="progress-fill" id="progress"></div></div>
<p class="status" id="status">Walk away and relax.<br>Come back when the timer ends.</p>
<button class="unlock-btn" id="unlockBtn" onclick="doUnlock()">Unlock Wall</button>
<button class="early-unlock-btn" id="earlyUnlockBtn" onclick="doEarlyUnlock()">&#x1F513; &#x65E9;&#x671F;&#x89E3;&#x9664;&#x3059;&#x308B;</button>
<script>
(function(){
  var DURATION=120;
  var SERVER='__SERVER_URL__',TOKEN='__TOKEN__';
  var scanTime=Date.now(),done=false,timerDone=false;
  var timerEl=document.getElementById('timer'),progressEl=document.getElementById('progress');
  var statusEl=document.getElementById('status'),iconEl=document.getElementById('icon');
  var unlockBtn=document.getElementById('unlockBtn');
  var earlyUnlockBtn=document.getElementById('earlyUnlockBtn');

  // Screen Wake Lock: スマホ画面の自動消灯を防止
  (function requestWakeLock(){
    if('wakeLock' in navigator){
      navigator.wakeLock.request('screen').catch(function(){});
      // ページが再表示された際にも再取得
      document.addEventListener('visibilitychange',function(){
        if(document.visibilityState==='visible'){
          navigator.wakeLock.request('screen').catch(function(){});
        }
      });
    }
  })();

  function finishUnlock(){
    done=true;
    iconEl.textContent='\u2705';
    unlockBtn.style.display='none';
    earlyUnlockBtn.style.display='none';
    statusEl.innerHTML='<span class="complete">Unlocked!</span><br>You can return to your computer.';
    fetch(SERVER+'/unlock?token='+TOKEN,{method:'POST'}).catch(function(){});
  }

  window.doUnlock=function(){
    if(done||!timerDone)return;
    finishUnlock();
  };

  window.doEarlyUnlock=function(){
    if(done)return;
    finishUnlock();
  };

  function tick(){
    if(done)return;
    var elapsed=(Date.now()-scanTime)/1000;
    var remaining=Math.max(0,DURATION-elapsed);
    var mins=Math.floor(remaining/60);
    var secs=Math.floor(remaining%60);
    timerEl.textContent=mins+':'+(secs<10?'0':'')+secs;
    progressEl.style.width=Math.min(100,(elapsed/DURATION)*100)+'%';
    if(remaining<=0&&!timerDone){
      timerDone=true;
      timerEl.textContent='0:00';
      progressEl.style.width='100%';
      statusEl.innerHTML='Ready to unlock!<br>Tap the button below.';
      unlockBtn.classList.add('visible');
      earlyUnlockBtn.style.display='none';
    }
    if(!done){setTimeout(tick,500);}
  }

  tick();
})();
</script>
</body>
</html>
"##;
