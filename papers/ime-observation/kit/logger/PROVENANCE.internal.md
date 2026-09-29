# kit/logger — 出どころの記録（内部用・公開しない）

このファイルは `*.internal.md` として公開の書き出しから除外される。GSE との対応関係は
ここにだけ書く（`papers/README.md` の「公開物の書き方」・判断 36）。

## 何を GSE と共有し、何を新規に書いたか

| 区分 | ファイル | GSE の一次 | 備考 |
|---|---|---|---|
| **ファイル**（逐語コピー） | `src/input/ime_compose.rs` | `src-tauri/src/input/ime_compose.rs` | 1 バイトも変えない。テストも一緒に走る |
| **ファイル**（逐語コピー） | `src/input/ime_cloak.rs` | `src-tauri/src/input/ime_cloak.rs` | 同上 |
| **ファイル**（逐語コピー） | `src/input/ime_mode.rs` | `src-tauri/src/input/ime_mode.rs` | 同上 |
| **ファイル**（逐語コピー） | `src/analysis/key_gate.rs` | `src-tauri/src/analysis/key_gate.rs` | 同上。Windows の `is_observed_key`（ドライバの逐語の抜粋）が本体の先頭で `crate::analysis::key_gate::is_feature_key` を呼ぶため（011 の追補） |
| **抜粋**（逐語コピー） | `src/key_category.rs` | `src-tauri/src/analysis/anonymize.rs` の `KeyCategory` ほか | 範囲は `manifest.json` のアンカー。`// @excerpt-begin/end key_category` の間 |
| **新規**（シム） | `src/input/hook.rs` | `src-tauri/src/input/hook.rs` の定数と Atomic だけ | 値と型は `check_decls: true` を持つ manifest エントリに限り `--against-upstream` が GSE と照合する |
| **新規** | `src/main.rs` | `lib.rs` の `emit_ime_shadow` と IME Monitor スレッドの、G1 を除いた写し | ＋ `meta` / `key` 行の書き出し・`--selftest`。GSE 側の判断そのものの照合は `main_emit_ime_shadow_judgment` / `main_ime_monitor_loop_judgment`（下記） |
| **新規** | `src/driver_api.rs` / `src/input/mod.rs` / `src/analysis/mod.rs` / `Cargo.toml` | — | ドライバと核の境界の型・候補窓の観測の差し込み口・停止の契約 |
| 差し込み口（**manifest に載せない**） | `src/driver_macos.rs` / `src/driver_windows.rs` | — | macOS は空（issue 012 が中身を入れる）。Windows は issue 013 / 014 で実装済み（`manifest.windows.json`） |

一覧の正本は `manifest.json`（種別・`upstream_path`・`upstream_last_commit`・SHA-256・理由）。ドライバの manifest
（`manifest.macos.json` / `manifest.windows.json`）は該当 issue がそれぞれ持つ。

`meta` 行の `manifest_sha256` は `manifest.json`（核）のバイト列の SHA-256（ビルド時に埋め込む）。
ドライバの manifest は含まない。

## `new` エントリの GSE 側ずれ検出（判断 33）

`main.rs` は逐語コピーではないので、GSE 側の判断が後で変わってもファイル全体のハッシュ照合では
気付けない。そこで `main_emit_ime_shadow_judgment` / `main_ime_monitor_loop_judgment` の 2 エントリが
`lib.rs` の該当範囲（アンカーで切り出す・excerpt と同じ決め方）の SHA-256 を `upstream_range_sha256`
として持ち、`--against-upstream` が照合する。GSE 側がこの範囲を変えると赤くなる（コピー自体は逐語で
ある必要はない）。詳しくは `check_manifest_upstream.internal.py` の docstring（`--update`）を参照。

## 名前の改名（判断 42）

2026-09-28 の判断 42 により、GSE を指す識別子を中立の語に改めた: `check_manifest.py` の
GSE 照合フラグ（ハイフン 2 つ + against + ハイフン + gse）→ `--against-upstream`、manifest の
`gse_path` / `gse_last_commit` / `gse_repo_commit` / `gse_range_sha256` →
`upstream_path` / `upstream_last_commit` / `upstream_repo_commit` / `upstream_range_sha256`。
公開の書き出し（issue 024）は `upstream_*` と `start_anchor` / `end_anchor` / `check_decls` を落とす。

## 照合の道具を公開用と内部用に分ける（判断 43）

2026-09-28 の判断 43 により、写した元との関係の説明を公開物から一切除いた。これに伴い、照合の道具も
2 つに分けた:

- `check_manifest.py`（公開）: 自己照合（`--self`）と `--selftest` だけを持つ。manifest の
  `upstream_*` の欄・`start_anchor` / `end_anchor` / `check_decls` は読まない（公開の書き出しでこれらの
  欄が manifest から落ちても `--self` は動く）。
- `check_manifest_upstream.internal.py`（本ファイル）: 写した元との照合（`--against-upstream`）と
  manifest の書き直し（`--update`）を持つ。公開用の `check_manifest.py` を `import` して自己照合まわりの
  共通処理（`sha` / `to_lines` / `copy_range` / `safe_join` / `manifests` / `each_entry` / `check_self` 等）
  を再利用し、写した元の読み出し（`read_upstream_lines` / `upstream_range`）・`check_decls` の型と値の
  比較・`--update` の manifest 書き直しだけをここに持つ。

以前の `check_manifest.py --against-upstream --selftest` が一体で持っていた陰性対照は、この分割後も
どちらかの selftest に全て残る: 1 バイト違い・アンカーの 0 回 / 2 回・symbol・シムの値・別の manifest を
変えない・別ディレクトリの拒否・判断 33 の範囲のずれは `check_manifest_upstream.internal.py --selftest`
に、コピー側の 1 バイト違い・excerpt の目印欠落・path の安全性（NUL・絶対パス・entries が配列でない）は
`check_manifest.py --selftest` に、それぞれ残した。

## 写した元と意図的に違えた判断（判断 44）

`new` エントリの `candidate_window_observer`（`src/driver_windows/candidate.rs`）は、GSE の
`ImeMonitor::is_candidate_window_open`（`src-tauri/src/input/ime_windows.rs:72-129`）と同じ判断を同じ順で
書く（cloak 状態・EnumWindows・UIA の OR と、旧来の経路が駆動しているときの stale のリセット）。ただし
**UIA の判定だけ 1 点違える**（2026-09-29・判断 44・研究者の回答）:

| | GSE | 単体ロガー |
|---|---|---|
| フォーカス要素のクラス名に `Candidate` を含む | 候補窓とみなす | 候補窓とみなす（同じ） |
| フォーカス要素の名前（accessible name）に「候補」を含む | 候補窓とみなす（`ime_windows.rs:98-100`） | **読まない**（判定に使わない） |

- 理由: 名前はアプリによってはタブ名・リンク文言・本文になり、他アプリの任意の文字列をプロセスのメモリに
  読み込むことになる。一致すると `ime_shadow` 行の出力時刻が遅れる（1 ビット程度の副チャネル）。公開する
  README の「content-free by construction」を構造で保つため外した。
- 影響の見込み: GSE の実測（`ime_windows.rs:186-193`）では、cloak 経路の端末でこの UIA の裏取りは 0 件
  なので、主な環境では差が出ない。⚠️ IMM 経路の端末で、名前でしか裏が取れない候補窓があると
  `is_stale_winevent_active` の判断が GSE より早まりうる → M5（Windows の較正パイロット）で確かめる。
- 照合: `upstream_range_sha256` は GSE 側の範囲（名前の判定を含む）のハッシュのまま。GSE 側がこの範囲を
  変えると `--against-upstream` が赤になるので、そのときはこの違いを保ったまま追随する。
