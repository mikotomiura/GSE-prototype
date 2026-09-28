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
| **ファイル**（逐語コピー） | `src/analysis/key_gate.rs` | `src-tauri/src/analysis/key_gate.rs` | 同上。Windows の `is_observed_key`（ドライバの逐語の抜粋）が本体の先頭で `crate::analysis::key_gate::is_feature_key` を呼ぶため（011 の追補） |
| **抜粋**（逐語コピー） | `src/key_category.rs` | `src-tauri/src/analysis/anonymize.rs` の `KeyCategory` ほか | 範囲は `manifest.json` のアンカー。`// @excerpt-begin/end key_category` の間 |
| **新規**（シム） | `src/input/hook.rs` | `src-tauri/src/input/hook.rs` の定数と Atomic だけ | 値と型は `check_decls: true` を持つ manifest エントリに限り `--against-gse` が GSE と照合する |
| **新規** | `src/main.rs` | `lib.rs` の `emit_ime_shadow` と IME Monitor スレッドの、G1 を除いた写し | ＋ `meta` / `key` 行の書き出し・`--selftest`。GSE 側の判断そのものの照合は `main_emit_ime_shadow_judgment` / `main_ime_monitor_loop_judgment`（下記） |
| **新規** | `src/driver_api.rs` / `src/input/mod.rs` / `src/analysis/mod.rs` / `Cargo.toml` | — | ドライバと核の境界の型・候補窓の観測の差し込み口・停止の契約 |
| 差し込み口（**manifest に載せない**） | `src/driver_macos.rs` / `src/driver_windows.rs` | — | 空。中身は後続の issue（macOS = 012 / Windows = 013・014） |

一覧の正本は `manifest.json`（種別・`gse_path`・`gse_last_commit`・SHA-256・理由）。ドライバの manifest
（`manifest.macos.json` / `manifest.windows.json`）は後続の issue がそれぞれ持つ。

`meta` 行の `manifest_sha256` は `manifest.json`（核）のバイト列の SHA-256（ビルド時に埋め込む）。
ドライバの manifest は含まない。

⚠️ **`new` エントリの GSE 側ずれ検出（判断 33）**: `main.rs` は逐語コピーではないので、GSE 側の判断が
後で変わってもファイル全体のハッシュ照合では気付けない。そこで `main_emit_ime_shadow_judgment` /
`main_ime_monitor_loop_judgment` の 2 エントリが `lib.rs` の該当範囲（アンカーで切り出す・excerpt と同じ
決め方）の SHA-256 を `gse_range_sha256` として持ち、`--against-gse` が照合する。GSE 側がこの範囲を
変えると赤くなる（コピー自体は逐語である必要はない）。詳しくは下の「manifest の書き直し」を参照。

## ドライバの契約（`src/driver_api.rs`）

各ドライバは `pub fn start(ctx: DriverCtx) -> Result<DriverHandle, String>` を持つ。
打鍵を `KeyEvent { t, vk, press }`（`t` = 壁時計 ms・`vk` = Windows の VK に写した値）にして `ctx.keys` へ送り、
変換セッションの状態は `src/input/hook.rs` の Atomic（GSE と同じ）へ書く。

- **停止**: `ctx.stop` が立ったら、ドライバは自分のスレッドを `driver_api::STOP_DEADLINE_MS`（既定 500ms）
  以内に終えること。核のループは `JoinHandle::is_finished()` でドライバの生死を見張り、想定外にスレッドが
  終わっていればエラーで終わる。
- **候補窓の観測の差し込み口**: `DriverHandle.candidate_window_observer` に
  `Some(Box<dyn FnMut() -> bool + Send>)` を入れて返すと、核の監視ループ（`Monitor::poll`）が毎周期これを
  呼んで「候補窓が開いているか」を判定する（`None`＝既定は `IME_ACTIVE` の読み取り）。★ **呼び出しスレッド**
  は `Monitor::poll` を呼ぶスレッド（打鍵取得スレッドとは別でよい）。Windows で UIAutomation の COM
  （`CoInitializeEx`）を使うなら、その初期化は観測関数の初回呼び出し時に、呼び出し元スレッド上で行うこと
  （詳細は `driver_api.rs` のモジュール doc）。

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
出力先は `OpenOptions::new().write(true).create_new(true)` で開く（**既存の観測ログは上書きしない**。
ドライバの起動が成功した後に開く）。`--out` を 2 回渡す・`--duration-s` に負や非整数を渡すのは使い方の誤り
（exit 2）。`--selftest` は既定の出力先（`--out` を渡さなかった場合）を実行後に消す。

## manifest の書き直し

`check_manifest.py --update --manifest <manifest*.json> --entries <spec.json>` は、**指定した 1 つの manifest だけ**を
**id 単位でマージして**書く（同じ `id` のエントリは置き換え、それ以外の既存エントリは残す。他の `manifest*.json`
は一切開かない）。`spec.json` はエントリの `kind` / `id` / `path` / `gse_path` / アンカー / `symbol` / `check_decls` /
`reason` の配列で、`sha256` / `gse_range_sha256`・`gse_last_commit`・`gse_repo_commit` は照合器が埋める。
⚠️ コピーが GSE と逐語（または `new` の判断の範囲が一致）でないときは書かずに止まる。

`kind: "new"` は既定では `--against-gse` で何も照合しない（`gse_path` があるだけでは照合しない）。照合したいものを
明示する:

- `"check_decls": true` — コピー側ファイルの `pub const|static NAME: T = V;` の型・値が `gse_path` の宣言と同じことを
  確かめる（シムの値の照合。`hook_shim` エントリが使う）。
- `"start_anchor"` / `"end_anchor"` （＋ 照合器が埋める `"gse_range_sha256"`）— `gse_path` のその範囲（excerpt と
  同じ切り出し方: 開始アンカーの行を含み終了アンカーの行を含まない・行全体の一致・ファイル中にちょうど 1 回）の
  SHA-256 が一致することを確かめる（GSE 側の**判断**が変わっていないかの照合。コピー自体は逐語でなくてよい。
  `main_emit_ime_shadow_judgment` / `main_ime_monitor_loop_judgment` が使う・判断 33）。

`--against-gse` が赤になったら、GSE 側が変わっている。コピーを GSE に合わせて取り直し、テストを通してから `--update` する。
コピーを手で直して緑にしない。

## 限界

- SHA-256 は CRLF を LF に揃えて取る（LF と CRLF の違いだけは検出しない）。
- `Cargo.lock` は `src-tauri/Cargo.lock` を種にして解決し直してある（共通する crate はすべて同じ版）。
  版を上げる／crate を足すときは `src-tauri/Cargo.lock` を種にしたまま `cargo check` で解決し直すこと
  （`cargo update` / `cargo generate-lockfile` を引数なしで回すと最新へ上がってしまうので使わない）。
- 本ロガーを Windows で回しても `#[cfg(target_os = "macos")]` の側はコンパイルされない（macOS のコンパイルは 012 が初めて行う）。
