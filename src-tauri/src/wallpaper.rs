//! EH3 の肖像を壁紙に書く層（元の壁紙の保存・本人の差し替えの検出・復元の確認）。
//!
//! 何を出すかは `analysis::portrait` が決め、ここは「その画をモニタごとの壁紙にする」と「元に戻す」だけを行う。
//! OS の呼び出しは [`Backend`] に閉じ、Windows は `wallpaper_windows.rs`（`IDesktopWallpaper`）、
//! macOS は `wallpaper_macos.rs`（`NSWorkspace`）が持つ（技術的制約 11・`autostart.rs` と同じ扱い）。
//!
//! 要件（`.steering/20261011-portrait-eh3-prereg/implementation-requirements.md` R-P8・R-P9）:
//! - 元の壁紙を必ず戻す。戻せない背景（スライドショー・単色・スポットライト・動く壁紙・元のファイルが無い・
//!   Windows の Themes フォルダの写し）では動かさない。
//! - 戻した後は、OS から読み戻したパスと、元のファイルの SHA-256 の**両方**を確かめる。確かめられなければ
//!   保存した元の状態を消さず、次の機会（期間の終わり・次の起動）にもう一度戻す。
//! - 本人が自分で壁紙を替えたら、それ以降は上書きしない。期間の終わりにも戻さない（本人の壁紙を上書きしない）。
//! - 期間の終わりと、やめたとき（EH3 の印が外れた後の起動を含む）は、seed の印を残さずに元へ戻す。
//!
//! ⚠️★★★ **ここは何も記録しない**（R-P9）: NDJSON に行を送る口を持たず（`LogEntry` を知らない）、
//! `tracing` にも書き込み・復元・本人の差し替え・「戻せないので動かさない」を出さない。出すと、本人が肖像を
//! 止めた・戻した・替えたことが時刻から読める（台帳 肖13）。applog に出してよいのは、起動時の
//! 「肖像の層が使えるか」の 1 行（時刻と操作が対応しない粒度）だけで、それは呼び出し側の `lib.rs` が出す。

use std::path::{Path, PathBuf};

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

use crate::analysis::portrait::canvas::{upscale_rgb8, Canvas};
use crate::analysis::portrait::Show;

/// 1 台のモニタ。
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Monitor {
    /// OS のモニタの識別子（Windows はデバイスパス、macOS は画面の番号）。端末の中だけで使う。
    pub id: String,
    pub width: u32,
    pub height: u32,
}

/// 戻せない背景の種類（起動時の 1 行の applog にだけ使う・時刻と対応させない）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Unrestorable {
    /// スライドショー・単色・スポットライト・動く壁紙など、1 枚の画像でない背景。
    NotAPicture,
    /// 元の画像のファイルが無い・読めない・OS が上書きする写し。
    OriginalFileUnsafe,
    /// モニタが 1 台も取れない・API が使えない。
    Unavailable,
}

/// OS の壁紙の API（テストでは偽物に差し替える）。
pub trait Backend {
    /// いま接続しているモニタ。
    fn monitors(&mut self) -> Result<Vec<Monitor>, String>;
    /// モニタの壁紙のファイル（無ければ `None`）。
    fn get(&mut self, monitor_id: &str) -> Result<Option<PathBuf>, String>;
    /// モニタの壁紙を替える。
    fn set(&mut self, monitor_id: &str, path: &Path) -> Result<(), String>;
    /// 背景が 1 枚の画像か（スライドショー・単色・スポットライトなどでないか）。
    /// `None` は一時的に確かめられなかった（macOS でメインスレッドが応答しないなど）。
    fn background_is_picture(&mut self) -> Option<bool>;
    /// 画像の置き方（Windows の `DESKTOP_WALLPAPER_POSITION`。macOS は `None`）。
    fn position(&mut self) -> Option<i32>;
    fn set_position(&mut self, position: i32) -> Result<(), String>;
    /// OS が上書きする写しのパスか（Windows の Themes フォルダの `TranscodedWallpaper` など）。
    fn is_os_managed_copy(&self, path: &Path) -> bool;
}

/// 元の壁紙（モニタ 1 台ぶん）。
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct OriginalMonitor {
    pub id: String,
    pub path: PathBuf,
    pub sha256: String,
}

/// 端末の中に残す元の状態（`~/.gse/eh3_wallpaper_original.json`）。提出物に入らない。
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct Store {
    pub monitors: Vec<OriginalMonitor>,
    pub position: Option<i32>,
    /// 本人が自分で壁紙を替えたモニタ（そのモニタは以後上書きせず、終わりにも戻さない）。
    #[serde(default)]
    pub person_monitors: Vec<String>,
    /// 本人が「壁紙を元に戻す」を選んだ（以後どのモニタにも書かない。終わりには、まだ肖像のモニタを戻す）。
    #[serde(default)]
    pub stopped: bool,
    /// 最後にこの層が書いたファイル（モニタごと）。読み戻しと比べて本人の差し替えを見つける。
    pub last_set: Vec<(String, PathBuf)>,
    /// これから書くファイル（OS に書く前に保存する）。書いた直後に落ちても、読み戻しがこれと同じなら
    /// この層が書いたものと分かる（本人の差し替えと取り違えない）。
    #[serde(default)]
    pub pending_set: Vec<(String, PathBuf)>,
}

/// 元の状態のファイル名。
pub const STORE_FILE_NAME: &str = "eh3_wallpaper_original.json";

/// 元の状態の置き場と、書き出す画像の置き場。
pub fn default_paths() -> Option<(PathBuf, PathBuf)> {
    let gse = crate::submission::home_dir()?.join(".gse");
    Some((gse.join(STORE_FILE_NAME), gse.join("eh3")))
}

/// ファイルの SHA-256（16 進）。大きな画像でも丸ごとメモリに読まない。
pub fn sha256_file(path: &Path) -> Option<String> {
    let mut f = std::fs::File::open(path).ok()?;
    let mut h = Sha256::new();
    std::io::copy(&mut f, &mut h).ok()?;
    Some(format!("{:x}", h.finalize()))
}

/// 2 つのパスが同じファイルを指すか（Windows は大文字小文字を区別しない）。
fn same_path(a: &Path, b: &Path) -> bool {
    if cfg!(windows) {
        a.to_string_lossy().to_lowercase() == b.to_string_lossy().to_lowercase()
    } else {
        a == b
    }
}

/// 本人だけが読み書きできるファイルを作る（unix は 0600。Windows はホームの既定の ACL）。
fn create_private(path: &Path) -> std::io::Result<std::fs::File> {
    let mut o = std::fs::OpenOptions::new();
    o.write(true).create(true).truncate(true);
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        o.mode(0o600);
    }
    o.open(path)
}

fn create_private_dir(dir: &Path) -> std::io::Result<()> {
    std::fs::create_dir_all(dir)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(dir, std::fs::Permissions::from_mode(0o700))?;
    }
    Ok(())
}

/// 画布をモニタの大きさの PNG にする。
pub fn write_png(path: &Path, canvas: &Canvas, width: u32, height: u32) -> std::io::Result<()> {
    let rgb = upscale_rgb8(canvas, width as usize, height as usize);
    if let Some(dir) = path.parent() {
        create_private_dir(dir)?;
    }
    let file = create_private(path)?;
    let mut enc = png::Encoder::new(std::io::BufWriter::new(file), width, height);
    enc.set_color(png::ColorType::Rgb);
    enc.set_depth(png::BitDepth::Eight);
    let mut w = enc.write_header().map_err(std::io::Error::other)?;
    w.write_image_data(&rgb).map_err(std::io::Error::other)?;
    w.finish().map_err(std::io::Error::other)?;
    Ok(())
}

/// 壁紙の管理。1 本のスレッドが持つ（Windows は COM の STA）。
pub struct Manager<B: Backend> {
    backend: B,
    store_path: PathBuf,
    work_dir: PathBuf,
    store: Option<Store>,
    /// 戻せない背景だったので、この走行では何もしない（一時的な失敗では立てない）。
    disabled: Option<Unrestorable>,
}

fn load_store(path: &Path) -> Option<Store> {
    serde_json::from_slice(&std::fs::read(path).ok()?).ok()
}

fn save_store(path: &Path, store: &Store) -> std::io::Result<()> {
    if let Some(dir) = path.parent() {
        create_private_dir(dir)?;
    }
    let tmp = path.with_extension("json.tmp");
    {
        use std::io::Write;
        let mut f = create_private(&tmp)?;
        f.write_all(&serde_json::to_vec(store).map_err(std::io::Error::other)?)?;
        f.sync_all()?;
    }
    std::fs::rename(&tmp, path)
}

/// 元の状態を取れなかった理由（`Retry` は一時的な失敗で、次の機会に取り直す）。
enum Capture {
    Fixed(Unrestorable),
    Retry,
}

impl<B: Backend> Manager<B> {
    /// 保存した元の状態があれば読む（異常終了の後でも元へ戻せるように）。
    pub fn new(backend: B, store_path: PathBuf, work_dir: PathBuf) -> Self {
        let store = load_store(&store_path);
        Self {
            backend,
            store_path,
            work_dir,
            store,
            disabled: None,
        }
    }

    /// この走行で肖像を出せるか（起動時の applog の 1 行に使う）。元の状態をまだ保存していなければ確かめる。
    /// `Ok(false)` は一時的に確かめられなかった（次の画で確かめ直す）。
    pub fn readiness(&mut self) -> Result<bool, Unrestorable> {
        if self.store.is_some() {
            return Ok(true);
        }
        match self.capture_original() {
            Ok(()) => Ok(true),
            Err(Capture::Fixed(why)) => Err(why),
            Err(Capture::Retry) => Ok(false),
        }
    }

    /// 元の壁紙を保存する（まだなら）。戻せない背景なら、以後この走行では何もしない。
    fn capture_original(&mut self) -> Result<(), Capture> {
        if let Some(why) = self.disabled {
            return Err(Capture::Fixed(why));
        }
        if self.store.is_some() {
            return Ok(());
        }
        match self.snapshot() {
            Ok(store) => {
                if save_store(&self.store_path, &store).is_err() {
                    // 元の状態を端末に残せないなら書き換えない（戻せる保証が無い）。次の機会に取り直す
                    return Err(Capture::Retry);
                }
                self.store = Some(store);
                Ok(())
            }
            Err(Capture::Fixed(why)) => {
                self.disabled = Some(why);
                Err(Capture::Fixed(why))
            }
            Err(Capture::Retry) => Err(Capture::Retry),
        }
    }

    fn snapshot(&mut self) -> Result<Store, Capture> {
        match self.backend.background_is_picture() {
            Some(true) => {}
            Some(false) => return Err(Capture::Fixed(Unrestorable::NotAPicture)),
            None => return Err(Capture::Retry),
        }
        let monitors = self.backend.monitors().map_err(|_| Capture::Retry)?;
        if monitors.is_empty() {
            return Err(Capture::Retry);
        }
        let mut out = Vec::new();
        for m in &monitors {
            let path = self
                .backend
                .get(&m.id)
                .map_err(|_| Capture::Retry)?
                .ok_or(Capture::Fixed(Unrestorable::OriginalFileUnsafe))?;
            // OS が上書きする写し・この層が書いた肖像そのもの（元の状態を失った後）は元として保存しない
            if self.backend.is_os_managed_copy(&path) || path.starts_with(&self.work_dir) {
                return Err(Capture::Fixed(Unrestorable::OriginalFileUnsafe));
            }
            let sha256 =
                sha256_file(&path).ok_or(Capture::Fixed(Unrestorable::OriginalFileUnsafe))?;
            out.push(OriginalMonitor {
                id: m.id.clone(),
                path,
                sha256,
            });
        }
        Ok(Store {
            monitors: out,
            position: self.backend.position(),
            person_monitors: Vec::new(),
            stopped: false,
            last_set: Vec::new(),
            pending_set: Vec::new(),
        })
    }

    /// いまの壁紙が、この層が最後に書いたもの（まだ書いていなければ元の壁紙）と違うモニタを、
    /// 本人が替えたモニタとして覚える（保存して次の起動でも覚えておく）。
    ///
    /// 単色など画像でない背景（読み戻しが `None`）に替えた場合も本人の差し替えとみなす。
    /// 読み出しの失敗（`Err`）だけは替えたとは言えないので数えない。
    fn detect_user_change(&mut self) {
        let Some(store) = self.store.as_ref() else {
            return;
        };
        let picture = self.backend.background_is_picture();
        // いまつながっているモニタだけを見る（外れたモニタの「壁紙なし」を本人の差し替えと取り違えない）
        let connected: Vec<String> = match self.backend.monitors() {
            Ok(ms) => ms.into_iter().map(|m| m.id).collect(),
            Err(_) => return,
        };
        let mut newly = Vec::new();
        for o in &store.monitors {
            if store.person_monitors.contains(&o.id) || !connected.contains(&o.id) {
                continue;
            }
            let ours = |p: &Path| {
                let in_list = |l: &Vec<(String, PathBuf)>| {
                    l.iter().any(|(id, q)| *id == o.id && same_path(q, p))
                };
                let has_last = store.last_set.iter().any(|(id, _)| *id == o.id);
                // 作業フォルダの下のファイルは常にこの層のもの（失敗と扱った後に OS が書いた場合も含む。
                // 元の壁紙として作業フォルダの下を保存することは `snapshot` が拒む）
                p.starts_with(&self.work_dir)
                    || in_list(&store.last_set)
                    || in_list(&store.pending_set)
                    || (!has_last && same_path(p, &o.path))
            };
            let changed = match self.backend.get(&o.id) {
                Ok(Some(now)) => !ours(&now),
                Ok(None) => true,
                Err(_) => false,
            };
            // 背景の種類そのものが画像でなくなった（スライドショー・単色・スポットライト）
            if changed || picture == Some(false) {
                newly.push(o.id.clone());
            }
        }
        if !newly.is_empty() {
            if let Some(store) = self.store.as_mut() {
                store.person_monitors.extend(newly);
                let _ = save_store(&self.store_path, store);
            }
        }
    }

    /// 画を出す。
    pub fn show(&mut self, show: &Show) {
        match show {
            Show::Original => {
                self.restore(false);
            }
            Show::Image(canvas) => self.show_image(canvas),
        }
    }

    /// 次に書くファイルの印（直前に書いたものと違う名前にする。同じ名前の上書きは OS が読み直さないことがある）。
    fn next_tag(&self) -> &'static str {
        let last_a = self.store.as_ref().is_some_and(|s| {
            s.last_set
                .iter()
                .any(|(_, p)| p.to_string_lossy().contains("wall-a-"))
        });
        if last_a {
            "b"
        } else {
            "a"
        }
    }

    fn show_image(&mut self, canvas: &Canvas) {
        if self.capture_original().is_err() {
            return;
        }
        self.detect_user_change();
        let Some(store) = self.store.as_ref() else {
            return;
        };
        if store.stopped {
            return;
        }
        let monitors = match self.backend.monitors() {
            Ok(m) => m,
            Err(_) => return,
        };
        let tag = self.next_tag();
        // 書く画像を先に作り、書く予定を保存してから OS に書く（書いた直後に落ちても取り違えない）
        let mut planned = Vec::new();
        for (i, m) in monitors.iter().enumerate() {
            // 元の状態に無いモニタ（後から挿した）と、本人が替えたモニタは書かない
            let ours = self.store.as_ref().is_some_and(|s| {
                s.monitors.iter().any(|o| o.id == m.id) && !s.person_monitors.contains(&m.id)
            });
            if !ours {
                continue;
            }
            let path = self.work_dir.join(format!("wall-{tag}-{i}.png"));
            if write_png(&path, canvas, m.width.max(1), m.height.max(1)).is_ok() {
                planned.push((m.id.clone(), path));
            }
        }
        if planned.is_empty() {
            return;
        }
        if let Some(store) = self.store.as_mut() {
            store.pending_set = planned.clone();
            if save_store(&self.store_path, store).is_err() {
                return; // 予定を残せないなら書かない
            }
        }
        let mut written = Vec::new();
        for (id, path) in planned {
            if self.backend.set(&id, &path).is_ok() {
                written.push((id, path));
            }
        }
        if let Some(store) = self.store.as_mut() {
            for (id, p) in written {
                store.last_set.retain(|(i, _)| *i != id);
                store.pending_set.retain(|(i, _)| *i != id);
                store.last_set.push((id, p));
            }
            // 書けなかったモニタの予定は残す（失敗と扱った後に OS が書いても取り違えない）
            let _ = save_store(&self.store_path, store);
        }
    }

    /// 元の壁紙へ戻す。本人が替えたモニタは飛ばす（本人の壁紙を上書きしない）。
    /// 飛ばさなかったモニタがすべて戻ったことを確かめた（読み戻しのパスと元のファイルの SHA-256 の両方）
    /// ときだけ `true`。`finish` で `true` なら、保存した元の状態と書き出した画像を消す
    /// （期間の終わり・やめたとき。seed の印を残さない）。
    pub fn restore(&mut self, finish: bool) -> bool {
        if self.store.is_none() {
            return true;
        }
        self.detect_user_change();
        let Some(store) = self.store.clone() else {
            return true;
        };
        let targets: Vec<&OriginalMonitor> = store
            .monitors
            .iter()
            .filter(|o| !store.person_monitors.contains(&o.id))
            .collect();
        if !targets.is_empty() {
            if let Some(pos) = store.position {
                let _ = self.backend.set_position(pos);
            }
        }
        let connected: Vec<String> = self
            .backend
            .monitors()
            .map(|ms| ms.into_iter().map(|m| m.id).collect())
            .unwrap_or_default();
        let mut ok = true;
        let mut paths_ok = true;
        let mut restored = Vec::new();
        for o in targets {
            if !connected.contains(&o.id) {
                // 外れているモニタは後で戻す（元の状態を残して、戻せるまで試す）
                ok = false;
                paths_ok = false;
                continue;
            }
            if self.backend.set(&o.id, &o.path).is_err() {
                ok = false;
                paths_ok = false;
                continue;
            }
            let read_back =
                matches!(self.backend.get(&o.id), Ok(Some(p)) if same_path(&p, &o.path));
            let unchanged = sha256_file(&o.path).as_deref() == Some(o.sha256.as_str());
            if read_back {
                restored.push(o.id.clone());
            }
            paths_ok &= read_back;
            ok &= read_back && unchanged;
        }
        if let Some(s) = self.store.as_mut() {
            // 戻ったモニタは、次に本人の差し替えを比べる相手が元の壁紙になる。
            // ⚠️ 戻せなかったモニタは「この層が書いた」記録を残す（消すと、肖像のままなのに本人の差し替えと
            // 取り違え、二度と戻さなくなる）。
            s.last_set.retain(|(id, _)| !restored.contains(id));
            s.pending_set.retain(|(id, _)| !restored.contains(id));
            let _ = save_store(&self.store_path, s);
        }
        // 期間の終わりは、パスが戻れば片付ける（元のファイルの中身が変わっていても、それは本人のファイルで、
        // 肖像と seed の画像を残し続ける理由にならない）
        if finish && paths_ok {
            self.forget();
            return true;
        }
        ok
    }

    /// 本人が「壁紙を元に戻す」を選んだ: 元へ戻し、以後は書かない（次の起動でも覚えておく）。
    /// 戻しきれなかったモニタは、期間の終わりの `restore(true)` で戻し直す。
    pub fn stop_by_person(&mut self) {
        self.restore(false);
        if let Some(s) = self.store.as_mut() {
            s.stopped = true;
            let _ = save_store(&self.store_path, s);
        }
    }

    /// 保存した元の状態と書き出した画像を消す（seed の印を残さない）。
    fn forget(&mut self) {
        self.store = None;
        let _ = std::fs::remove_file(&self.store_path);
        let _ = std::fs::remove_dir_all(&self.work_dir);
    }

    /// 保存した元の状態が端末に残っているか（異常終了・やめた後の起動で戻すかを決める）。
    pub fn has_pending_original(&self) -> bool {
        self.store.is_some()
    }

    #[cfg(test)]
    fn backend_mut(&mut self) -> &mut B {
        &mut self.backend
    }
}

#[cfg(test)]
pub(crate) mod tests {
    use super::*;
    use std::collections::HashMap;

    /// 偽の OS。モニタごとの壁紙のパスだけを持つ。
    #[derive(Debug, Clone)]
    pub struct FakeBackend {
        pub walls: HashMap<String, PathBuf>,
        pub sizes: Vec<(String, u32, u32)>,
        pub picture: bool,
        pub position: Option<i32>,
        pub sets: usize,
        /// 次の N 回の `set` を失敗させる。
        pub fail_sets: usize,
    }

    impl Backend for FakeBackend {
        fn monitors(&mut self) -> Result<Vec<Monitor>, String> {
            Ok(self
                .sizes
                .iter()
                .map(|(id, w, h)| Monitor {
                    id: id.clone(),
                    width: *w,
                    height: *h,
                })
                .collect())
        }
        fn get(&mut self, id: &str) -> Result<Option<PathBuf>, String> {
            Ok(self.walls.get(id).cloned())
        }
        fn set(&mut self, id: &str, path: &Path) -> Result<(), String> {
            if self.fail_sets > 0 {
                self.fail_sets -= 1;
                return Err("busy".into());
            }
            self.sets += 1;
            self.walls.insert(id.to_string(), path.to_path_buf());
            Ok(())
        }
        fn background_is_picture(&mut self) -> Option<bool> {
            Some(self.picture)
        }
        fn position(&mut self) -> Option<i32> {
            self.position
        }
        fn set_position(&mut self, p: i32) -> Result<(), String> {
            self.position = Some(p);
            Ok(())
        }
        fn is_os_managed_copy(&self, path: &Path) -> bool {
            path.to_string_lossy().contains("TranscodedWallpaper")
        }
    }

    pub fn temp_dir(tag: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!("gse_wall_{tag}_{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    pub fn setup(tag: &str, monitors: usize) -> (Manager<FakeBackend>, PathBuf, Vec<PathBuf>) {
        let d = temp_dir(tag);
        let mut walls = HashMap::new();
        let mut sizes = Vec::new();
        let mut originals = Vec::new();
        for i in 0..monitors {
            let p = d.join(format!("orig{i}.jpg"));
            std::fs::write(&p, format!("original picture {i}")).unwrap();
            walls.insert(format!("m{i}"), p.clone());
            sizes.push((format!("m{i}"), 64, 36));
            originals.push(p);
        }
        let backend = FakeBackend {
            walls,
            sizes,
            picture: true,
            position: Some(4),
            sets: 0,
            fail_sets: 0,
        };
        let m = Manager::new(backend, d.join(STORE_FILE_NAME), d.join("eh3"));
        (m, d, originals)
    }

    fn some_image() -> Canvas {
        let mut c = Canvas::ground();
        c.blob(100.0, 60.0, 5.0, [0.2, 0.4, 0.6], 0.5);
        c
    }

    #[test]
    fn writes_every_monitor_and_restores_with_readback_and_hash() {
        let (mut m, d, originals) = setup("restore", 2);
        m.show(&Show::Image(some_image()));
        for i in 0..2 {
            let now = m.backend_mut().walls[&format!("m{i}")].clone();
            assert!(now.starts_with(d.join("eh3")), "肖像が書かれた");
        }
        assert!(m.restore(true), "読み戻しと SHA-256 の両方が合えば true");
        for (i, o) in originals.iter().enumerate() {
            assert_eq!(&m.backend_mut().walls[&format!("m{i}")], o);
        }
        assert!(
            !d.join(STORE_FILE_NAME).exists(),
            "終わりには元の状態を消す"
        );
        assert!(!d.join("eh3").exists(), "seed の印（画像）を残さない");
        assert_eq!(m.backend_mut().position, Some(4));
    }

    #[test]
    fn a_changed_original_file_is_not_reported_as_restored() {
        let (mut m, d, originals) = setup("hash", 1);
        m.show(&Show::Image(some_image()));
        std::fs::write(&originals[0], b"overwritten by someone").unwrap();
        // 期間の途中の戻し（空の日など）: パスが戻っても、中身が違えば「戻った」とは言わない
        assert!(
            !m.restore(false),
            "ファイルが変わっていたら、パスが戻っても戻ったとは言わない"
        );
        assert!(
            d.join(STORE_FILE_NAME).exists(),
            "確かめられなければ元の状態を残す"
        );
        // 期間の終わりの片付けは別（finishing_cleans_up_even_if_the_original_file_was_edited）
    }

    #[test]
    fn unrestorable_backgrounds_are_left_alone() {
        let (mut m, _d, _o) = setup("slideshow", 1);
        m.backend_mut().picture = false;
        m.show(&Show::Image(some_image()));
        assert_eq!(m.backend_mut().sets, 0, "1 枚の画像でない背景は替えない");
        assert_eq!(m.readiness(), Err(Unrestorable::NotAPicture));
        // この層が書いた肖像そのものは、元の壁紙として保存しない
        let (mut m, d, _o) = setup("ours", 1);
        let ours = d.join("eh3").join("wall-a-0.png");
        std::fs::create_dir_all(ours.parent().unwrap()).unwrap();
        std::fs::write(&ours, b"portrait").unwrap();
        m.backend_mut().walls.insert("m0".into(), ours);
        assert_eq!(m.readiness(), Err(Unrestorable::OriginalFileUnsafe));
        let (mut m, d, _o) = setup("themes", 1);
        let copy = d.join("TranscodedWallpaper");
        std::fs::write(&copy, b"x").unwrap();
        m.backend_mut().walls.insert("m0".into(), copy);
        m.show(&Show::Image(some_image()));
        assert_eq!(
            m.backend_mut().sets,
            0,
            "OS が上書きする写しは戻せないので替えない"
        );
    }

    #[test]
    fn after_the_person_changes_the_wallpaper_nothing_is_overwritten() {
        let (mut m, d, _o) = setup("override", 1);
        m.show(&Show::Image(some_image()));
        let mine = d.join("my_own.png");
        std::fs::write(&mine, b"mine").unwrap();
        m.backend_mut().walls.insert("m0".into(), mine.clone());
        let before = m.backend_mut().sets;
        m.show(&Show::Image(some_image()));
        m.show(&Show::Original);
        assert_eq!(m.backend_mut().sets, before, "本人が替えた後は書かない");
        assert!(
            m.restore(true),
            "本人が替えたモニタは飛ばし、残りは戻ったので true"
        );
        assert_eq!(
            m.backend_mut().walls["m0"],
            mine,
            "終わりにも本人の壁紙を上書きしない"
        );
        assert!(
            !d.join(STORE_FILE_NAME).exists(),
            "終わったら元の状態は消す"
        );
    }

    #[test]
    fn only_the_monitor_the_person_changed_is_left_alone() {
        // 本人がモニタ 0 だけを替えた: モニタ 1 には肖像を書き続け、終わりにはモニタ 1 だけを戻す
        let (mut m, d, originals) = setup("per_monitor", 2);
        m.show(&Show::Image(some_image()));
        let mine = d.join("mine.png");
        std::fs::write(&mine, b"mine").unwrap();
        m.backend_mut().walls.insert("m0".into(), mine.clone());
        m.show(&Show::Image(some_image()));
        assert_eq!(m.backend_mut().walls["m0"], mine);
        assert!(m.backend_mut().walls["m1"].starts_with(d.join("eh3")));
        assert!(m.restore(true));
        assert_eq!(m.backend_mut().walls["m0"], mine);
        assert_eq!(
            m.backend_mut().walls["m1"],
            originals[1],
            "肖像のまま残さない"
        );
    }

    #[test]
    fn a_failed_restore_is_retried_and_not_mistaken_for_the_persons_change() {
        let (mut m, _d, originals) = setup("retry", 1);
        m.show(&Show::Image(some_image()));
        m.backend_mut().fail_sets = 1; // 1 回目の復元で OS が受け付けない
        assert!(!m.restore(true), "戻せなかったら true にしない");
        assert!(m.has_pending_original(), "元の状態を残す");
        assert!(
            m.restore(true),
            "2 回目は戻る（本人の差し替えと取り違えていない）"
        );
        assert_eq!(m.backend_mut().walls["m0"], originals[0]);
    }

    #[test]
    fn a_crash_between_writing_and_saving_is_not_mistaken_for_the_persons_change() {
        let (mut m, d, originals) = setup("pending", 1);
        m.show(&Show::Image(some_image()));
        // 2 枚目を書く予定を保存した直後に落ちた、を作る: 予定にあるファイルを OS に書いたが last_set は古い
        let next = d.join("eh3").join("wall-b-0.png");
        std::fs::write(&next, b"next").unwrap();
        let store_path = d.join(STORE_FILE_NAME);
        let mut st: Store = serde_json::from_slice(&std::fs::read(&store_path).unwrap()).unwrap();
        st.pending_set = vec![("m0".into(), next.clone())];
        std::fs::write(&store_path, serde_json::to_vec(&st).unwrap()).unwrap();
        m.backend_mut().walls.insert("m0".into(), next);
        let backend = m.backend_mut().clone();
        drop(m);
        let mut again = Manager::new(backend, store_path, d.join("eh3"));
        assert!(
            again.restore(true),
            "予定にあったファイルはこの層のもの: 元へ戻す"
        );
        assert_eq!(again.backend_mut().walls["m0"], originals[0]);
    }

    #[test]
    fn a_late_write_after_a_reported_failure_is_still_ours() {
        // OS が失敗を返したのに、後から書かれた（macOS の時間切れの後など）
        let (mut m, d, originals) = setup("late", 1);
        m.backend_mut().fail_sets = 1;
        m.show(&Show::Image(some_image()));
        let late = d.join("eh3").join("wall-a-0.png");
        m.backend_mut().walls.insert("m0".into(), late);
        assert!(m.restore(true), "作業フォルダの下はこの層のもの: 元へ戻す");
        assert_eq!(m.backend_mut().walls["m0"], originals[0]);
    }

    #[test]
    fn finishing_with_a_monitor_unplugged_waits_until_it_returns() {
        let (mut m, _d, originals) = setup("unplug_finish", 2);
        m.show(&Show::Image(some_image()));
        m.backend_mut().sizes.retain(|(id, _, _)| id != "m1");
        assert!(!m.restore(true), "外れたモニタが戻るまで終われない");
        assert!(m.has_pending_original());
        m.backend_mut().sizes.push(("m1".into(), 64, 36));
        assert!(m.restore(true));
        assert_eq!(m.backend_mut().walls["m1"], originals[1]);
    }

    #[test]
    fn finishing_cleans_up_even_if_the_original_file_was_edited() {
        let (mut m, d, originals) = setup("edited", 1);
        m.show(&Show::Image(some_image()));
        std::fs::write(&originals[0], b"edited by the person").unwrap();
        assert!(m.restore(true), "パスが戻れば期間の終わりは片付ける");
        assert!(!d.join("eh3").exists(), "肖像と seed の画像を残さない");
        assert!(!d.join(STORE_FILE_NAME).exists());
    }

    #[test]
    fn a_disconnected_monitor_is_not_the_persons_change() {
        let (mut m, _d, originals) = setup("unplug", 2);
        m.show(&Show::Image(some_image()));
        // モニタ 1 を外す（壁紙の読み戻しもできない）→ 戻す → 挿し直してから終わりに戻す
        m.backend_mut().sizes.retain(|(id, _, _)| id != "m1");
        let portrait1 = m.backend_mut().walls.remove("m1").unwrap();
        m.show(&Show::Image(some_image()));
        m.backend_mut().sizes.push(("m1".into(), 64, 36));
        m.backend_mut().walls.insert("m1".into(), portrait1);
        assert!(m.restore(true));
        assert_eq!(
            m.backend_mut().walls["m1"],
            originals[1],
            "外れていたモニタも戻す"
        );
    }

    #[test]
    fn switching_to_a_solid_colour_counts_as_the_persons_change() {
        let (mut m, _d, _o) = setup("solid", 1);
        m.show(&Show::Image(some_image()));
        m.backend_mut().walls.remove("m0"); // 単色: 読み戻しが空
        let before = m.backend_mut().sets;
        m.show(&Show::Image(some_image()));
        assert_eq!(
            m.backend_mut().sets,
            before,
            "本人が選んだ単色を肖像で上書きしない"
        );
    }

    #[test]
    fn stopping_restores_and_stops_writing() {
        let (mut m, _d, originals) = setup("stop", 2);
        m.show(&Show::Image(some_image()));
        m.stop_by_person();
        assert_eq!(m.backend_mut().walls["m0"], originals[0]);
        let before = m.backend_mut().sets;
        m.show(&Show::Image(some_image()));
        assert_eq!(m.backend_mut().sets, before, "止めた後は書かない");
    }

    #[test]
    fn the_next_file_name_differs_from_the_last_one_across_restarts() {
        let (mut m, d, _o) = setup("tag", 1);
        m.show(&Show::Image(some_image()));
        let first = m.backend_mut().walls["m0"].clone();
        let backend = m.backend_mut().clone();
        drop(m);
        let mut next = Manager::new(backend, d.join(STORE_FILE_NAME), d.join("eh3"));
        next.show(&Show::Image(some_image()));
        assert_ne!(next.backend_mut().walls["m0"], first);
    }

    #[test]
    fn a_crash_leaves_the_original_on_disk_and_the_next_run_restores_it() {
        let (mut m, d, originals) = setup("crash", 1);
        m.show(&Show::Image(some_image()));
        let backend = m.backend_mut().clone();
        drop(m); // 異常終了
        let mut next = Manager::new(backend, d.join(STORE_FILE_NAME), d.join("eh3"));
        assert!(next.has_pending_original());
        assert!(next.restore(true));
        assert_eq!(next.backend_mut().walls["m0"], originals[0]);
    }

    #[test]
    fn a_monitor_plugged_in_later_is_not_touched() {
        let (mut m, d, _o) = setup("hotplug", 1);
        m.show(&Show::Image(some_image()));
        let extra = d.join("extra.jpg");
        std::fs::write(&extra, b"extra").unwrap();
        m.backend_mut().walls.insert("m9".into(), extra.clone());
        m.backend_mut().sizes.push(("m9".into(), 64, 36));
        m.show(&Show::Image(some_image()));
        assert_eq!(
            m.backend_mut().walls["m9"],
            extra,
            "戻す先の無いモニタは替えない"
        );
    }

    /// `tracing` の行を数える購読者（applog に何が出るかの代わり）。
    struct CountLayer(std::sync::Arc<std::sync::atomic::AtomicUsize>);

    impl<S: tracing::Subscriber> tracing_subscriber::Layer<S> for CountLayer {
        fn on_event(
            &self,
            _event: &tracing::Event<'_>,
            _ctx: tracing_subscriber::layer::Context<'_, S>,
        ) {
            self.0.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
        }
    }

    /// 同じ画の列を流し、`person` なら途中で本人が壁紙を替え・止める。applog に出た行の数を返す。
    fn run_counting(tag: &str, person: bool, leaky: bool) -> usize {
        use tracing_subscriber::layer::SubscriberExt;
        let count = std::sync::Arc::new(std::sync::atomic::AtomicUsize::new(0));
        let sub = tracing_subscriber::registry().with(CountLayer(count.clone()));
        tracing::subscriber::with_default(sub, || {
            let (mut m, d, _o) = setup(tag, 2);
            for k in 0..6 {
                if person && k == 2 {
                    let mine = d.join("mine.png");
                    std::fs::write(&mine, b"mine").unwrap();
                    m.backend_mut().walls.insert("m0".into(), mine);
                }
                if person && k == 4 {
                    m.stop_by_person();
                }
                m.show(&Show::Image(some_image()));
                if leaky {
                    // 陽性対照: 書き込みのたびに applog へ出す偽の実装
                    tracing::info!("wallpaper written");
                }
            }
            m.restore(true);
        });
        count.load(std::sync::atomic::Ordering::Relaxed)
    }

    /// R-P9: 肖像への本人の操作（自分で替える・止める）の有無だけを変えても、applog の行は同じ（0 行）。
    /// NDJSON と提出物へは、この層が `LogEntry` を知らないので構造的に届かない（下の静的な検査）。
    #[test]
    fn person_operations_leave_no_trace_in_the_applog() {
        let without = run_counting("trace_a", false, false);
        let with = run_counting("trace_b", true, false);
        assert_eq!(without, 0);
        assert_eq!(
            with, without,
            "本人の操作の有無で applog が変わってはならない"
        );
        // 陽性対照: 書き込みのたびに applog へ出す実装なら 0 でなくなる（検査が空回りしていない）。
        assert!(run_counting("trace_c", true, true) > 0);
    }

    /// R-P9（構造）: この層のソースは `LogEntry` を知らず、`tracing` を呼ばない（テストの部分を除く）。
    #[test]
    fn the_wallpaper_layer_cannot_write_records() {
        for (name, src) in [
            ("wallpaper.rs", include_str!("wallpaper.rs")),
            ("wallpaper_windows.rs", include_str!("wallpaper_windows.rs")),
            ("wallpaper_macos.rs", include_str!("wallpaper_macos.rs")),
            (
                "analysis/portrait/mod.rs",
                include_str!("analysis/portrait/mod.rs"),
            ),
        ] {
            let head = src.split("#[cfg(test)]").next().unwrap_or(src);
            // コメント（doc を含む）の中の言及は数えない
            let body: String = head
                .lines()
                .filter(|l| !l.trim_start().starts_with("//"))
                .collect::<Vec<_>>()
                .join(
                    "
",
                );
            for needle in ["LogEntry", "tracing::", "log_tx"] {
                assert!(
                    !body.contains(needle),
                    "{name} が {needle} を使っている（R-P9）"
                );
            }
        }
        // 対照: 探し方が空回りしていない（記録する側のファイルでは見つかる）
        assert!(include_str!("lib.rs").contains("LogEntry"));
    }

    #[test]
    fn png_has_the_monitor_size() {
        let d = temp_dir("png");
        let p = d.join("x.png");
        write_png(&p, &some_image(), 64, 36).unwrap();
        let dec = png::Decoder::new(std::io::BufReader::new(std::fs::File::open(&p).unwrap()));
        let r = dec.read_info().unwrap();
        assert_eq!((r.info().width, r.info().height), (64, 36));
    }
}
