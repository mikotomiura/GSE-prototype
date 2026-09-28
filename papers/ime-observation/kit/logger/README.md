# ime-observation-logger — IME 観測の単体ロガー

GSE（Generative Struggle Engine）の**変換セッション状態機械**を、GSE 本体を変えずに切り出して使う単体ロガー。
評価（E1 / E3）で使うのはこのロガーであり、GSE のアプリではない。出力は `obs/1`（`../formats/FORMATS.md`）。

⚠️ **観測部は content-free**: `key` 行は 14 種の category だけ（どのキーかは残らない）、`ime_shadow` 行は数
（`dwell_ms` / `nav` / `abandon`）だけ。文字・変換候補・読み・ウィンドウ名は持たない。

## 何を GSE と共有し、何を新規に書いたか

| 区分 | ファイル | GSE の一次 | 備考 |
|---|---|---|---|
| **ファイル**（逐語コピー） | `src/input/ime_compose.rs` | `src-tauri/src/input/ime_compose.rs` | 1 バイトも変えない。テストも一緒に走る |
| **ファイル**（逐語コピー） | `src/input/ime_cloak.rs` | `src-tauri/src/input/ime_cloak.rs` | 同上 |
| **ファイル**（逐語コピー） | `src/input/ime_mode.rs` | `src-tauri/src/input/ime_mode.rs` | 同上 |
| **抜粋**（逐語コピー） | `src/key_category.rs` | `src-tauri/src/analysis/anonymize.rs` の `KeyCategory` ほか | 範囲は `manifest.json` のアンカー。`// @excerpt-begin/end key_category` の間 |
| **新規**（シム） | `src/input/hook.rs` | `src-tauri/src/input/hook.rs` の定数と Atomic だけ | 値と型は `--against-gse` が GSE と照合する |
| **新規** | `src/main.rs` | `lib.rs` の `emit_ime_shadow` と IME Monitor スレッドの、G1 を除いた写し | ＋ `meta` / `key` 行の書き出し・`--selftest` |
| **新規** | `src/driver_api.rs` / `src/input/mod.rs` / `Cargo.toml` | — | ドライバと核の境界の型 |
| 差し込み口（**manifest に載せない**） | `src/driver_macos.rs` / `src/driver_windows.rs` | — | 空。中身は後続の issue（macOS = 012 / Windows = 013・014） |

一覧の正本は `manifest.json`（種別・`gse_path`・`gse_last_commit`・SHA-256・理由）。ドライバの manifest
（`manifest.macos.json` / `manifest.windows.json`）は後続の issue がそれぞれ持つ。

`meta` 行の `manifest_sha256` は `manifest.json`（核）のバイト列の SHA-256（ビルド時に埋め込む）。
ドライバの manifest は含まない。

## ドライバの契約（`src/driver_api.rs`）

各ドライバは `pub fn start(ctx: DriverCtx) -> Result<std::thread::JoinHandle<()>, String>` を持つ。
打鍵を `KeyEvent { t, vk, press }`（`t` = 壁時計 ms・`vk` = Windows の VK に写した値）にして `ctx.keys` へ送り、
変換セッションの状態は `src/input/hook.rs` の Atomic（GSE と同じ）へ書く。`ctx.stop` が立ったら終わる。

## ビルド・selftest・照合

```bash
# リポジトリのルートから
cargo test  --manifest-path papers/ime-observation/kit/logger/Cargo.toml      # コピーした状態機械のテストを含む
cargo build --release --manifest-path papers/ime-observation/kit/logger/Cargo.toml
papers/ime-observation/kit/logger/target/release/ime-observation-logger --selftest --out /tmp/obs.jsonl
python3 papers/ime-observation/kit/formats/validate_logs.py --kind obs /tmp/obs.jsonl

python3 papers/ime-observation/kit/logger/check_manifest.py --self          # コピーが manifest と一致（GSE を読まない）
python3 papers/ime-observation/kit/logger/check_manifest.py --against-gse   # GSE の現在のファイルと一致（ずれの検出）
python3 papers/ime-observation/kit/logger/check_manifest.py --selftest      # 照合器の陰性対照
```

実行: `ime-observation-logger --out <path> [--duration-s <n>]`（ドライバが入るまでは「未実装」で終わる）。

## manifest の書き直し

`check_manifest.py --update --manifest <manifest*.json> --entries <spec.json>` は、**指定した 1 つの manifest だけ**を書く
（他の `manifest*.json` は触らない）。`spec.json` はエントリの `kind` / `id` / `path` / `gse_path` / アンカー / `symbol` / `reason`
の配列で、SHA-256・`gse_last_commit`・`gse_repo_commit` は照合器が埋める。⚠️ コピーが GSE と逐語でないときは書かずに止まる。

`--against-gse` が赤になったら、GSE 側が変わっている。コピーを GSE に合わせて取り直し、テストを通してから `--update` する。
コピーを手で直して緑にしない。

## 限界

- SHA-256 は CRLF を LF に揃えて取る（LF と CRLF の違いだけは検出しない）。
- `Cargo.lock` の解決は `src-tauri/Cargo.lock` と patch 版が違うことがある（`Cargo.toml` の版指定は同じ）。
- 本ロガーを Windows で回しても `#[cfg(target_os = "macos")]` の側はコンパイルされない（macOS のコンパイルは 012 が初めて行う）。
