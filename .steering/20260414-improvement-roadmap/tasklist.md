# タスクリスト

> 本タスクリストは `design.md`（ハイブリッド採用版）を実装単位に分解したもの。
> 各 Phase の完了時に `finish-task` フローで steering を最終化する。

## 準備
- [x] `docs/architecture.md` を再読（HMM スレッドモデル、独立 1Hz ゲート）
- [ ] `docs/functional-design.md` の Lv1/Lv2 発火条件を確認（次サイクル）
- [x] `src-tauri/src/lib.rs:482-690` の分析スレッド本体を通読
- [x] `src-tauri/src/analysis/engine.rs` と `features.rs` の全関数を把握

---

## Phase 0: Replay & Guard（2-3 週間）

### 実装
- [ ] P0-1: 分析ループ本体を `analysis/loop_step.rs` に `step()` 関数として抽出
  - [ ] `AnalysisState` 構造体定義（`extractor`, `last_event_time_ms`, `next_engine_update_ms`, `presses_since_silence`, `was_paused`, `pressed_keys`）
  - [ ] `LoopInput` enum 定義（`Key` / `ImeState`）
  - [ ] `StepOutput` 構造体定義（`log_entries`, `feat: Option<FeatSnapshot>`）
  - [ ] `step(state, engine, input, now_ms, ime_open) -> StepOutput` 実装
  - [ ] `Instant` を ms-based 時刻へ変換する基準時刻設計
- [ ] P0-2: `lib.rs` の分析スレッドを `step()` を呼ぶ薄いラッパーに書き換え
  - [ ] `Instant::now()` を ms に変換して渡す
  - [ ] `input::hook::IME_OPEN.load()` を引数化
  - [ ] 挙動が変わらないこと手動確認（実アプリ起動→数セッション）
- [ ] P0-3: `analysis/` に `Tauri` / `input::hook` グローバル直接依存がないことを確認
- [ ] P0-4: `src-tauri/src/bin/replay.rs` 新設
  - [ ] NDJSON パーサ（`serde_json` + `LogEntry` enum の `Deserialize` 実装）
  - [ ] タイムスタンプ順イベント列化
  - [ ] 1 秒刻み仮想時刻ループ
  - [ ] `FeatSnapshot` JSON 出力
  - [ ] `--snapshot <path>` で byte-equal（f64 誤差 1e-9）比較
  - [ ] `[bin]` エントリを `Cargo.toml` に追加
- [ ] P0-5: `engine.rs` に `pub const HMM_VERSION: &str = "0.2.0";` 追加
- [ ] P0-6: `logger.rs` の meta エントリに `hmm_version` フィールド追加
- [x] P0-7: 沈黙 3 状態のコメントリネーム
  - [x] `lib.rs:649-682` の 3 分岐にラベルコメント（TypingPath / TransitionPath / SilencePath）
  - [x] `features.rs:230` の `make_silence_observation` コメント更新
- [x] P0-8: `docs/architecture.md` §4.7「沈黙 3 状態機構」セクション追加完了
- [x] P0-9: `// TUNE:` マーカーを `engine.rs` / `features.rs` の全チューニング定数に付与
  - [x] 遷移行列、放出行列、β 値、EWMA α、ヒステリシス α、Synthetic Friction 閾値
  - [x] 併せて `INITIAL_PROBS` / `INITIAL_AXES_EWMA` / `BACKSPACE_PENALTY_THRESHOLD` をモジュール定数へ抽出（重複リテラル解消）
- [ ] P0-10: ゴールデンスナップショット 3 件作成
  - [ ] `tests/fixtures/flow.ndjson`（Flow 主体 10 分）
  - [ ] `tests/fixtures/incubation.ndjson`（Incubation 主体 10 分）
  - [ ] `tests/fixtures/stuck.ndjson`（Stuck + BS ペナルティ含む 10 分）
  - [ ] 初回 `gse-replay` 実行結果を `tests/snapshots/*.json` として保存

### テスト
- [x] T0-1: `features.rs` に `#[cfg(test)]` モジュール追加 — **19 本追加**
  - [x] phi 境界値 7 本（baseline / below / midpoint / triple / way_above / zero_beta / negative_beta）
  - [x] silence 境界値 7 本（<2s / at_2s / just_before_10s / at_10s / at_30s / at_50s / at_100s）
  - [x] calculate_features 5 本（empty / flight_time_median / correction_rate / pause_count / ignores_repeats）
  - [ ] **次サイクル**: F4 バースト長 / F6 pause-after-delete / 30s cutoff / 2000ms FT cap のカバレッジ（code-reviewer MEDIUM 指摘）
- [x] T0-2: `engine.rs` に `#[cfg(test)]` モジュール追加 — **9 本追加**
  - [x] `transition_matrix_snapshot`（行和 1.0 不変条件も検証）
  - [x] `emission_matrix_snapshot`（78 要素全比較）
  - [x] `initial_probabilities_snapshot`
  - [x] `emission_penalty_bin_near_certain_stuck`（Stuck:Flow ≈ 99× 比検証）
  - [x] `register_keystroke_non_backspace_resets_streak`
  - [x] `register_keystroke_streak_at_13_does_not_trigger_penalty`（境界下）
  - [x] `register_keystroke_streak_at_14_triggers_pending_penalty`（境界）
  - [x] `register_keystroke_penalty_flag_persists_through_non_bs`
  - [x] `reset_clears_all_state`
  - [ ] **次サイクル**: `update()` / `update_silence()` の挙動テスト（penalty→Stuck 収束 / IME ガード / silence α 境界）— code-reviewer MEDIUM 指摘
- [ ] T0-3: ゴールデンスナップショット回帰テスト（P0-4 Replay CLI 依存で次サイクル）
- [x] T0-4: 全テスト PASS 確認（**28 PASS / 0 FAIL**）

### レビュー
- [x] R0-1: `code-reviewer` + `security-checker` 並列起動完了
- [x] R0-2: HIGH 2 件対応完了（行番号ドリフト修正 / EWMA α 定数化ポリシー明文化）+ 軽微 MEDIUM 1 件対応（§4.x → §4.7）
  - 残 MEDIUM 3 件（testing アクセサ / F4 F6 cutoff テスト / update 挙動テスト）は次サイクルへ繰り越し（ユーザー判断済み）
- [x] R0-3: `rust-standards` + `hmm-analysis` Skill 参照済み（本サイクル開始時）

### ドキュメント
- [x] D0-1: `docs/architecture.md` §4.7 沈黙 3 状態セクション完成
- [ ] D0-2: `docs/development-guidelines.md` に「リプレイ CLI を回帰保護の中心とする」方針追記（Replay CLI 実装サイクルで実施）
- [ ] D0-3: `README.md` に `gse-replay` の使用例と `hmm_version` bump 規約を追加（同上）

### Go/No-Go（Phase 1 へ進む条件）
- [ ] `cargo run --bin gse-replay tests/fixtures/flow.ndjson --snapshot tests/snapshots/flow.json` が一致
- [ ] 他 2 件のスナップショットも byte-equal
- [ ] `cargo test` で全テスト PASS
- [ ] `grep -n "TUNE:" src-tauri/src/analysis/*.rs` で全チューニング箇所が列挙される
- [ ] メタログに `hmm_version` が記録されることを実機確認

### 完了処理
- [ ] `design.md` の未解決事項「hmm_version 更新規約」を決定・記録（P0-5/P0-6 実施時）
- [x] `decisions.md` に沈黙パス統一しない理由を記録（判断 3）
- [ ] git commit（本サイクル分、ユーザー承認待ち）

### 本サイクル（Phase 0 診断テスト層）で対応完了した項目サマリ
- **実装**: P0-7, P0-8, P0-9（+ INITIAL_PROBS / INITIAL_AXES_EWMA / BACKSPACE_PENALTY_THRESHOLD 抽出）
- **テスト**: T0-1（19 本）, T0-2（9 本）, T0-4（28 PASS）
- **レビュー**: R0-1, R0-2（HIGH + 軽微 MEDIUM）, R0-3
- **ドキュメント**: D0-1
- **次サイクル繰越**: P0-1〜P0-6, P0-10, T0-3, 残 MEDIUM 3 件, D0-2, D0-3

---

## Phase 1: Ground Truth（2 週間）

### 実装
- [ ] P1-1: `logger.rs` に `LogEntry::UserLabel { timestamp, label, recovered_at }` 追加
  - [ ] `UserLabel` enum（`Flow` / `Incubation` / `Stuck`）定義
  - [ ] NDJSON シリアライザ実装
- [ ] P1-2: `lib.rs` に `record_user_label(label: String, timestamp: u64)` Tauri コマンド追加
- [ ] P1-3: `lib.rs` に `set_engine_paused(paused: bool)` Tauri コマンド追加（既存の `engine.set_paused` を露出）
- [ ] P1-4: `Dashboard.tsx` に GT 3 択ボタン追加
  - [ ] Flow / Incubation / Stuck ボタン
  - [ ] 5 秒ホールド機構（`onMouseDown` で setTimeout、`onMouseUp` で cancel）
  - [ ] ホールド開始時に `set_engine_paused(true)`、完了・中断時に `set_engine_paused(false)` を呼ぶ
  - [ ] 記録完了時にトースト表示（押した時刻を確認可能に）
- [ ] P1-5: 分析スレッドに Stuck 回復時間の自動補完ロジック
  - [ ] `pending_stuck_label: Option<u64>` をスレッドローカルに追加
  - [ ] Stuck ラベル受信時に記録開始
  - [ ] `p_flow > 0.5` 到達時に `recovered_at` を埋めてログ追記
- [ ] P1-6: `gse-replay --metrics` サブコマンド実装
  - [ ] 混同行列出力
  - [ ] precision / recall / F1 算出
  - [ ] 検出リード/ラグ時間（中央値）算出
  - [ ] Stuck 回復時間（中央値）算出

### テスト
- [ ] T1-1: `LogEntry::UserLabel` の serialize/deserialize ユニットテスト
- [ ] T1-2: 5 秒ホールド中に HMM が一時停止することの手動確認（実機 + ログ目視）
- [ ] T1-3: Stuck ラベル → Flow 復帰で `recovered_at` が埋まることを確認（実機）
- [ ] T1-4: Phase 0 のゴールデンスナップショット再実行で差分ゼロ（`UserLabel` 追加が既存挙動に影響しないこと）

### レビュー
- [ ] R1-1: `code-reviewer` 実行
- [ ] R1-2: `typescript-standards` Skill に基づく Dashboard.tsx レビュー
- [ ] R1-3: HIGH 指摘への対応

### ドキュメント
- [ ] D1-1: `docs/functional-design.md` に GT ボタン仕様追加
- [ ] D1-2: `.steering/20260414-improvement-roadmap/baseline_metrics.md` 作成（ベースライン precision/recall 記録用）

### データ収集（運用タスク）
- [ ] C1-1: GT 付きセッションを自分で 10 件以上記録
- [ ] C1-2: 各セッションに Stuck ラベル 3 件以上を目標
- [ ] C1-3: `gse-replay --metrics` を各セッションに実行し `baseline_metrics.md` に集計

### Go/No-Go（Phase 2 へ進む条件）
- [ ] GT 付きセッションが 10 件以上
- [ ] ベースライン precision/recall が記録されている
- [ ] リード/ラグ時間の中央値が記録されている
- [ ] 5 秒ホールド中の HMM pause が実機で確認済み

### 完了処理
- [ ] `decisions.md` にベースライン数値と「なぜその数値を許容するか」を記録
- [ ] git commit

---

## Phase 2a: Synthetic Friction 再設計（1-1.5 週間）

### 実装
- [ ] P2a-1: `gse-replay --scatter` サブコマンド実装
  - [ ] `UserLabel` 付きセッションで沈黙開始前 5 秒の平均 φ(F3) / φ(F6) を算出
  - [ ] 各沈黙とそのラベル（Incubation / Stuck）を CSV 出力
- [ ] P2a-2: `AnalysisState` に `last_active_features: Option<Features>` 追加
- [ ] P2a-3: `loop_step.rs` の step 関数で `silence_secs < 2.0 → ≥ 2.0` 遷移時に `last_active_features` を更新
- [ ] P2a-4: TransitionPath / SilencePath に文脈条件ゲート挿入
  - [ ] `// TUNE:` マーカー付きで `THRESHOLD_PHI_F3 = 0.30` / `THRESHOLD_PHI_F6 = 0.20` を定義
  - [ ] `phi(laf.f3, beta_f3) >= T_F3 || phi(laf.f6, beta_f6) >= T_F6` で `apply_friction` 判定
  - [ ] `apply_friction == false` なら既存の F6/F3 フロアを適用しない
- [ ] P2a-5: 既存ゴールデンスナップショット 3 件に対してリプレイ → 差分を `.steering/` に記録

### テスト
- [ ] T2a-1: 文脈条件ゲートのユニットテスト
  - [ ] `last_active_features` が None → friction 適用なし
  - [ ] 高摩擦 → friction 適用あり
  - [ ] 低摩擦 → friction 適用なし
- [ ] T2a-2: ゴールデンスナップショット更新（意図された差分のみ）
- [ ] T2a-3: Phase 1 GT 付きセッションで `gse-replay --metrics` → precision 低下がないこと

### 校正
- [ ] C2a-1: P2a-1 の散布図から経験的閾値を算出
- [ ] C2a-2: `THRESHOLD_PHI_F3` / `THRESHOLD_PHI_F6` を校正値に更新
- [ ] C2a-3: 再度 `gse-replay --metrics` で効果確認

### レビュー
- [ ] R2a-1: `code-reviewer` + `hmm-analysis` Skill レビュー
- [ ] R2a-2: HIGH 指摘への対応

### ドキュメント
- [ ] D2a-1: `docs/architecture.md` の沈黙 3 状態セクションを文脈ゲート込みで更新
- [ ] D2a-2: `.steering/20260414-improvement-roadmap/phase2a_results.md` に precision/recall 前後比較を記録

### Go/No-Go（Phase 3 / Phase 4 へ進む条件）
- [ ] Stuck precision が変更前から低下していない
- [ ] Incubation 沈黙の Stuck 誤検出率が減少（数値根拠付き）
- [ ] ゴールデンスナップショット差分が意図通り、承認記録あり
- [ ] 校正根拠の GT データが `.steering/` に記録されている

### 完了処理
- [ ] `decisions.md` に閾値選択根拠を記録
- [ ] git commit

---

## Phase 2b: IME Shadow Features（1 週間・Phase 2a と並列可）

### 実装
- [ ] P2b-1: `hook.rs` に IME 用 Atomic 追加
  - [ ] `IME_COMPOSITION_START_MS: AtomicU64`
  - [ ] `IME_CANDIDATE_NAV_COUNT: AtomicU32`
  - [ ] `IME_ABANDON_COUNT: AtomicU32`
- [ ] P2b-2: `hook_windows.rs` / `ime_windows.rs` に IME_SHOW / IME_HIDE イベントハンドラ追加
  - [ ] IME_SHOW 時に現在時刻を store
  - [ ] IME_HIDE 時に差分を計算、counter を snapshot してログ送信
- [ ] P2b-3: `hook_windows.rs` の `LowLevelKeyboardProc` 内で矢印キー/ESC カウント
  - [ ] `IME_ACTIVE.load() == true` かつ矢印キー → `IME_CANDIDATE_NAV_COUNT.fetch_add(1)`
  - [ ] `IME_ACTIVE.load() == true` かつ ESC → `IME_ABANDON_COUNT.fetch_add(1)`
  - [ ] CLAUDE.md 制約 (3) 遵守（Atomic 操作のみ）
- [ ] P2b-4: `logger.rs` に `LogEntry::ImeShadow` 追加
- [ ] P2b-5: `lib.rs` 経由で IME_HIDE 時にログ送信
- [ ] P2b-6: macOS ビルドが壊れないことを確認（`#[cfg(target_os = "windows")]` 分離）

### テスト
- [ ] T2b-1: Windows 実機で IME を使ったセッションを 5 件記録
- [ ] T2b-2: `ImeShadow` ログが NDJSON に出力されていることを目視確認
- [ ] T2b-3: Phase 0 ゴールデンスナップショットで HMM 出力に差分ゼロ
- [ ] T2b-4: macOS ビルド（`cargo build --target=aarch64-apple-darwin` 相当）が通ることを CI または手動で確認

### レビュー
- [ ] R2b-1: `hook-constraints` Skill 遵守確認（フックコールバック内 Atomic のみ）
- [ ] R2b-2: `security-checker` 実行

### ドキュメント
- [ ] D2b-1: `docs/functional-design.md` に IME Shadow Features セクション追加
- [ ] D2b-2: macOS 保留の理由を記載

### Go/No-Go
- [ ] Windows で 5 セッション以上の `ImeShadow` ログが取れている
- [ ] HMM 既存出力に差分ゼロ
- [ ] macOS ビルドが壊れていない

### 完了処理
- [ ] git commit

---

## Phase 3: LR 判断ゲート（2 週間、Phase 2a 完了後）

### 前提確認
- [ ] GT 付きセッションが 50 件以上存在するか確認（不足なら Phase 1 へ戻る）

### 実装
- [ ] P3-1: `ml/train_lr.py` 作成
  - [ ] NDJSON + UserLabel 読み込み
  - [ ] 特徴量エンジニアリング（φ 正規化後の F1-F6 + ラグ特徴量）
  - [ ] 時系列 80/20 分割
  - [ ] sklearn LogisticRegression（C=0.1）
  - [ ] Leave-One-Session-Out CV で F1 算出
- [ ] P3-2: `ml/export_weights.py` 作成
  - [ ] LR の係数とバイアスを Rust const 配列としてエクスポート
- [ ] P3-3: `engine.rs` にラグ特徴量バッファ追加
  - [ ] `axes_history: Arc<Mutex<VecDeque<(f64, f64)>>>` 容量 5
  - [ ] `update()` 内で push_back / pop_front
- [ ] P3-4: `engine.rs` に `lr_score()` メソッド追加
  - [ ] LR_W / LR_B 定数を手貼り（P3-2 の出力）
  - [ ] φ 正規化後特徴量 + ラグ特徴量でスコア算出
- [ ] P3-5: `logger.rs` の `LogEntry::Feat` に optional `lr_stuck: Option<f64>` 追加（後方互換）
- [ ] P3-6: `lib.rs` 分析スレッドで `lr_score` を呼びログに記録（シャドーモード、介入判断には使わない）
- [ ] P3-7: `gse-replay --metrics --lr` サブコマンド実装
  - [ ] HMM 単独の precision/recall
  - [ ] HMM AND LR の precision/recall
  - [ ] 差分表を出力

### テスト
- [ ] T3-1: `lr_score` のユニットテスト（既知入力 → 期待スコア）
- [ ] T3-2: ラグ特徴量バッファの境界挙動テスト（5 未満の履歴、5 以上の履歴）
- [ ] T3-3: Phase 0 ゴールデンスナップショットで HMM 出力に差分ゼロ（LR はシャドー）

### 判定
- [ ] J3-1: `gse-replay --metrics --lr` の結果から Go/No-Go 判定
- [ ] J3-2: **Go の場合**: HMM AND LR を介入判断に統合する追加実装
  - [ ] `App.tsx` の stuck > 0.7 判定を `stuck > 0.7 AND lr_stuck > 0.6` に変更
  - [ ] ゴールデンスナップショットを更新
- [ ] J3-3: **No-Go の場合**: シャドーログは残すが介入判断には使わない
  - [ ] `phase3_lr_decision.md` に判定根拠を記録

### レビュー
- [ ] R3-1: `code-reviewer` + `ml-workflow` Skill レビュー
- [ ] R3-2: HIGH 指摘への対応

### ドキュメント
- [ ] D3-1: `.steering/20260414-improvement-roadmap/phase3_lr_decision.md` 作成（Go / No-Go 判定根拠）
- [ ] D3-2: `docs/architecture.md` に LR 統合（または非統合）を反映

### Go/No-Go 判定（Phase 3 完了条件）
- [ ] Go または No-Go の明示的判定文書が存在
- [ ] LR シャドースコアがログに記録されている
- [ ] Go の場合: precision が 5% 以上改善 + recall が 3% 以上悪化していない
- [ ] No-Go の場合: その判断根拠が記録されている

### 完了処理
- [ ] git commit

---

## Phase 4: Lv3 Thought Scaffold + Feedback（1-1.5 週間、Phase 2a Go 後）

### 前提確認
- [ ] Phase 2a で Stuck precision 改善が確認されている（数値根拠あり）

### 実装
- [ ] P4-1: `src/components/ThoughtScaffold.tsx` 新規作成
  - [ ] 固定 20 問のソクラテス的問いかけリスト
  - [ ] ランダム選択・10 秒間表示・フェードアウト
  - [ ] React 19 + Tauri 2.0 IPC パターンに従う
- [ ] P4-2: `App.tsx` に Lv3 トリガーロジック追加
  - [ ] `sensor-accelerometer: "move"` 受信後に `isScaffoldActive = true`
  - [ ] 10 秒後に自動非表示
- [ ] P4-3: `logger.rs` に `LogEntry::InterventionFeedback` 追加
- [ ] P4-4: `lib.rs` に `record_intervention_feedback(intervention, helpful)` Tauri コマンド追加
- [ ] P4-5: Lv1 Nudge / Lv2 Wall / Lv3 Scaffold 発動後に 2 択フィードバックボタンを 30 秒表示
  - [ ] `App.tsx` / `Overlay.tsx` / `ThoughtScaffold.tsx` に追加

### テスト
- [ ] T4-1: Lv3 発動のユーザーテスト 3 セッション
- [ ] T4-2: フィードバックログが記録されることを目視確認
- [ ] T4-3: Phase 0 ゴールデンスナップショットで HMM 出力に差分ゼロ

### レビュー
- [ ] R4-1: `code-reviewer` + `typescript-standards` + `intervention-design` Skill レビュー
- [ ] R4-2: HIGH 指摘への対応

### ドキュメント
- [ ] D4-1: `docs/functional-design.md` に Lv3 仕様と 20 問リストを追加
- [ ] D4-2: `docs/glossary.md` に「Thought Scaffold」用語追加

### Go/No-Go
- [ ] Lv3 が 3 セッション以上で動作確認済み
- [ ] フィードバックログが収集できている
- [ ] 既存 Lv1/Lv2 の発火が壊れていない（ゴールデン確認）

### 完了処理
- [ ] git commit
- [ ] `/finish-task` 実行してロードマップ全体の steering を最終化

---

## 全 Phase 完了後

- [ ] `.steering/20260414-improvement-roadmap/retrospective.md` 作成
  - [ ] Phase ごとの予実対比（見積 vs 実績）
  - [ ] 採用判断 / 却下判断の振り返り
  - [ ] 未踏 2027 提案準備への活用可能データのサマリ
- [ ] `docs/architecture.md` / `docs/functional-design.md` / `docs/glossary.md` を全体レビュー
- [ ] `MEMORY.md` に「リプレイ CLI + ゴールデンスナップショットを回帰保護の中心に」を追加
