# タスクリスト — O1 の計器を「収集できる形」にする

## A. O1/R3 モードのマーカー

- [ ] A-1 `src-tauri/src/o1.rs` を新規作成 (`lib.rs` に `mod o1;`)
- [ ] A-2 マーカー `o1.mode` ＋ env `GSE_O1_MODE=1` の 2 経路
- [ ] A-3 `resolve()` で **G1 と相互排他** (G1 優先・O1 を落とす・`tracing::error!`)
- [ ] A-4 `run()` で起動時 1 回だけ解決し `OnceLock` へ
- [ ] A-5 テスト: env の厳しさ / マーカー優先 / **排他** / 両 OS の階層

## B. (B) 常時収集

- [ ] B-1 `analysis_gate_open` を `lib.rs:2713` の門に適用
- [ ] B-2 `recording_active` を `tray::current_state` に適用 (**ラベルは変えない**)
- [ ] B-3 `recording_active` を `liveness::step` の第 2 引数に適用 (**starved_ms が O1 で進む**)
- [ ] B-4 O1 では `INTERVENTION_ENABLED = false` (判断 O1-5)
- [ ] B-5 テスト: 真理値表 3 本 ＋ 「O1 で starved_ms が進む」

## C. 宣言 UI

- [ ] C-1 `declare_task_kind` IPC (Rotate → SessionMeta → reset → set_domain)
- [ ] C-2 `o1::decide_declaration_action` (純関数) ＋ テスト
- [ ] C-3 `DECLARED_TASK_KIND` と `get_recording_status` への追加
- [ ] C-4 `get_o1_mode` IPC
- [ ] C-5 `App.tsx`: O1 では start 画面を飛ばす / `record_session_meta` を呼ばない
- [ ] C-6 `App.tsx`: O1 では `calibrationMode` を強制 (盲検)
- [ ] C-7 `RecordingControls.tsx`: 「記録中 · 作業の種類: ○○」/「未設定」＋ 4 択
- [ ] C-8 ラベル 4 値 ＋ `creative` の補足 1 行 (判断 O1-3)

## D. 日次ローテート ＋ 48 時間

- [ ] D-1 `logger`: O1 では `gse_o1_<ts>.ndjson` で開く
- [ ] D-2 `o1::should_rotate_daily` ＋ 日次ローテートスレッド (O1 限定)
- [ ] D-3 `reconcile`: `CollectionMode` / `closed_o1_sessions` / `O1_SUBMIT_GRACE_MS`
- [ ] D-4 `reconcile`: O1 は承認不要 (`unsent_age_files`)
- [ ] D-5 `gse-submit --o1` ＋ `lib.rs` 側で付与
- [ ] D-6 テスト: 猶予中は候補にならない / 猶予後に候補になる / **猶予中に消せる**

## 検証

- [ ] V-1 `cargo test --manifest-path src-tauri/Cargo.toml --workspace`
- [ ] V-2 `cargo test --manifest-path src-tauri/Cargo.toml --features package`
- [ ] V-3 ゴールデン byte-equal (`gse-replay --snapshot`)
- [ ] V-4 `emit_schema` が `schema/current.json` と byte-equal (**schema drift ゼロ**)
- [ ] V-5 `cargo clippy --all-targets` / `cargo fmt`
- [ ] V-6 `npm run build` (tsc)
- [ ] V-7 実機確認: インジケータ / 宣言 → ローテート → reset
- [ ] V-8 `code-reviewer` + `security-checker` 並列 → `/cross-review`
- [ ] V-9 CI の状態を確認 (⚠️ **未実行なら「緑」と書かない**)
