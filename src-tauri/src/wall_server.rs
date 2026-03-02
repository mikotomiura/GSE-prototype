/// Wall Server — スマートフォンQRコードによるWall解除サーバー
///
/// Wall発動時にローカルHTTPサーバーを起動し、QRコードを生成する。
/// スマートフォンでQRコードをスキャンして /unlock にアクセスすると
/// `sensor-accelerometer` イベントが発火し、Wallが解除される。
///
/// センサーAPIへの依存を排除し、デバイス非依存の解除方式を実現する。
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use qrcode::render::svg;
use qrcode::QrCode;
use serde::Serialize;
use tauri::{AppHandle, Emitter, Runtime, State};
use tiny_http::{Response, Server};

// ---------------------------------------------------------------------------
// 公開型
// ---------------------------------------------------------------------------

#[derive(Serialize)]
pub struct WallServerInfo {
    pub url: String,
    pub qr_svg: String,
}

/// Tauri管理状態: Wall Serverの起動/停止を制御する
pub struct WallServerState {
    stop_flag: Mutex<Option<Arc<AtomicBool>>>,
}

impl WallServerState {
    pub fn new() -> Self {
        Self {
            stop_flag: Mutex::new(None),
        }
    }
}

// ---------------------------------------------------------------------------
// ヘルパー
// ---------------------------------------------------------------------------

/// PCのローカルIPアドレスを取得する。
/// UDPソケットを経由してルーティングテーブルを参照するだけで、実際には送信しない。
fn get_local_ip() -> String {
    std::net::UdpSocket::bind("0.0.0.0:0")
        .ok()
        .and_then(|s| {
            s.connect("8.8.8.8:80").ok()?;
            s.local_addr().ok()
        })
        .map(|addr| addr.ip().to_string())
        .unwrap_or_else(|| "127.0.0.1".to_string())
}

/// OSに空きポートを割り当ててもらう
fn find_free_port() -> u16 {
    std::net::TcpListener::bind("0.0.0.0:0")
        .map(|l| l.local_addr().unwrap().port())
        .unwrap_or(8765)
}

/// URLからSVG QRコードを生成して文字列で返す
fn generate_qr_svg(url: &str) -> Result<String, String> {
    let code = QrCode::new(url.as_bytes()).map_err(|e| e.to_string())?;
    let svg = code
        .render::<svg::Color>()
        .min_dimensions(200, 200)
        .build();
    Ok(svg)
}

// ---------------------------------------------------------------------------
// Tauri コマンド
// ---------------------------------------------------------------------------

/// Wall発動時に呼び出す。ローカルHTTPサーバーを起動し、URLとQRコードSVGを返す。
/// 既存サーバーが起動中の場合は先に停止してから再起動する。
#[tauri::command]
pub fn start_wall_server<R: Runtime>(
    app: AppHandle<R>,
    state: State<WallServerState>,
) -> Result<WallServerInfo, String> {
    // 既存サーバーを停止
    {
        let mut guard = state.stop_flag.lock().unwrap();
        if let Some(prev_flag) = guard.take() {
            prev_flag.store(true, Ordering::Relaxed);
        }
    }

    let port = find_free_port();
    let ip = get_local_ip();
    let url = format!("http://{}:{}/unlock", ip, port);

    let qr_svg = generate_qr_svg(&url)?;

    let stop_flag = Arc::new(AtomicBool::new(false));
    let stop_flag_clone = stop_flag.clone();

    let server =
        Server::http(format!("0.0.0.0:{}", port)).map_err(|e| e.to_string())?;

    // サーバースレッドを起動（JoinHandleは破棄 = デタッチ）
    thread::spawn(move || {
        tracing::info!("Wall server listening on http://{}:{}", ip, port);
        loop {
            if stop_flag_clone.load(Ordering::Relaxed) {
                break;
            }
            match server.recv_timeout(Duration::from_millis(200)) {
                Ok(Some(req)) => {
                    if req.url() == "/unlock" {
                        tracing::info!("Wall unlock request received — emitting sensor event");
                        let _ = app.emit("sensor-accelerometer", "move");
                        let _ = req.respond(Response::from_string("Unlocked!"));
                    } else {
                        let _ = req.respond(Response::from_string("GSE Wall Server"));
                    }
                }
                Ok(None) => {} // タイムアウト: ループ継続
                Err(e) => {
                    tracing::warn!("Wall server recv error: {}", e);
                    break;
                }
            }
        }
        tracing::info!("Wall server stopped");
    });

    *state.stop_flag.lock().unwrap() = Some(stop_flag);

    Ok(WallServerInfo { url, qr_svg })
}

/// Wall解除時に呼び出す。バックグラウンドのサーバースレッドを停止する。
#[tauri::command]
pub fn stop_wall_server(state: State<WallServerState>) {
    if let Some(flag) = state.stop_flag.lock().unwrap().take() {
        flag.store(true, Ordering::Relaxed);
    }
}
