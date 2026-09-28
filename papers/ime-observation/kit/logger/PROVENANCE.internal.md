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
ある必要はない）。詳しくは公開の README「manifest の書き直し」を参照。

## 名前の改名（判断 42）

2026-09-28 の判断 42 により、GSE を指す識別子を中立の語に改めた: `check_manifest.py` の
GSE 照合フラグ（ハイフン 2 つ + against + ハイフン + gse）→ `--against-upstream`、manifest の
`gse_path` / `gse_last_commit` / `gse_repo_commit` / `gse_range_sha256` →
`upstream_path` / `upstream_last_commit` / `upstream_repo_commit` / `upstream_range_sha256`。
公開の書き出し（issue 024）は `upstream_*` と `start_anchor` / `end_anchor` / `check_decls` を落とす。
