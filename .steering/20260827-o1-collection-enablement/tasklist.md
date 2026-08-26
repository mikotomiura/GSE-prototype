# タスクリスト — O1 の計器を「収集できる形」にする

## A. O1/R3 モードのマーカー

- [x] A-1 `src-tauri/src/o1.rs` を新規作成 (`lib.rs` に `mod o1;`)
- [x] A-2 マーカー `o1.mode` ＋ env `GSE_O1_MODE=1` の 2 経路
- [x] A-3 `resolve()` で **G1 と相互排他** (G1 優先・O1 を落とす・`tracing::error!`)
- [x] A-4 `run()` で起動時 1 回だけ解決し `OnceLock` へ
- [x] A-5 テスト: env の厳しさ / マーカー優先 / **排他** / 両 OS の階層

## B. (B) 常時収集

- [x] B-1 `analysis_gate_open` を `lib.rs:2713` の門に適用
- [x] B-2 `recording_active` を `tray::current_state` に適用 (**ラベルは変えない**)
- [x] B-3 `recording_active` を `liveness::step` の第 2 引数に適用 (**starved_ms が O1 で進む**)
- [x] B-4 O1 では `INTERVENTION_ENABLED = false` (判断 O1-5)
- [x] B-5 テスト: 真理値表 3 本 ＋ 「O1 で starved_ms が進む」

## C. 宣言 UI

- [x] C-1 `declare_task_kind` IPC (Rotate → SessionMeta → reset → set_domain)
- [x] C-2 `o1::decide_declaration_action` (純関数) ＋ テスト
- [x] C-3 `DECLARED_TASK_KIND` と `get_recording_status` への追加
- [x] C-4 `get_o1_mode` IPC
- [x] C-5 `App.tsx`: O1 では start 画面を飛ばす / `record_session_meta` を呼ばない
- [x] C-6 `App.tsx`: O1 では `calibrationMode` を強制 (盲検)
- [x] C-7 `RecordingControls.tsx`: 「記録中 · 作業の種類: ○○」/「未設定」＋ 4 択
- [x] C-8 ラベル 4 値 ＋ `creative` の補足 1 行 (判断 O1-3)

## D. 日次ローテート ＋ 48 時間

- [x] D-1 `logger`: O1 では `gse_o1_<ts>.ndjson` で開く
- [x] D-2 `o1::should_rotate_daily` ＋ 日次ローテートスレッド (O1 限定)
- [x] D-3 `reconcile`: `CollectionMode` / `closed_o1_sessions` / `O1_SUBMIT_GRACE_MS`
- [x] D-4 `reconcile`: O1 は承認不要 (`unsent_age_files`)
- [x] D-5 `gse-submit --o1` ＋ `lib.rs` 側で付与
- [x] D-6 テスト: 猶予中は候補にならない / 猶予後に候補になる / **猶予中に消せる**

## 検証

- [x] V-1 `cargo test --manifest-path src-tauri/Cargo.toml --workspace`
- [x] V-2 `cargo test --manifest-path src-tauri/Cargo.toml --features package`
- [x] V-3 ゴールデン byte-equal (`gse-replay --snapshot`)
- [x] V-4 `emit_schema` が `schema/current.json` と byte-equal (**schema drift ゼロ**)
- [x] V-5 `cargo clippy --all-targets` / `cargo fmt`
- [x] V-6 `npm run build` (tsc)
- [x] V-7 実機確認 (⚠️ **一部のみ**・詳細は `decisions.md` N-3):
  - [x] O1 で **「開始する」を押さずに記録が走る** (`feat` 行・`gse_o1_*.ndjson`)
  - [x] トレイが **「GSE — 計測中」** と出る (`session_active=false` のまま)
  - [x] **`starved_ms` が O1 で進む** (`hook_health {starved_ms:30000}`)
  - [x] 宣言 → ローテート → 新ファイルに宣言 (logger 統合テスト) ＋ `gse-replay` 受理
  - [ ] ⚠️ **`key` 行**: 本機ではフックが注入入力を受け取らないため**未確認**
  - [ ] ⚠️ **一時停止 → 「停止中（記録していません）」**: UI 操作が要るため未確認 (純関数テストで固定)
- [x] V-8 `code-reviewer` + `security-checker` 並列 → `/cross-review` (Codex)
  - [x] 並列レビュー: HIGH/MEDIUM 10 件を修正、9 件を研究者へ返す (`decisions.md`)
  - [x] `/cross-review`: Codex が 3 件を追加で指摘 → すべて修正 (`decisions.md` X-1〜X-3)
  - [x] ⚠️ secrets-filter は `--ack-filtered` で迂回せず、**フィクスチャ名を架空形式へ寄せて**通した
- [ ] V-9 CI の状態を確認 (⚠️ **未実行なら「緑」と書かない**)
