# 設計 v1（既存プランから移植）

> このファイルは `C:\Users\johnd\.claude\plans\graceful-growing-moonbeam.md` を
> `.steering/` へ正規化したもの。次ステップで `/reimagine` による v2 案を生成し、比較する。

## 実装アプローチ

**原則**: 元ロードマップの提案を現状コードで検証 → 誤認を補正 → 欠落タスク（テスト・リプレイ・パラメータ外部化）を先行させる → Phase 分割。

**Phase 分割方針**: 基盤（Phase 0）→ GT 計測（Phase 1）→ Synthetic Friction 再設計（Phase 2）→ ML/IME シャドー収集（Phase 3）→ 介入層拡充（Phase 4）。

**設計原則**:
- パラメータ変更の前に **テストと リプレイ基盤** を先行構築（後戻りコスト最小化）
- HMM 既存挙動を壊さないため、新機能は **シャドーモード**（ログのみ）で検証 → 有効性確認後に本線統合
- 閾値は β 依存を排除するため **φ 正規化後の値** で判定する

## 元ロードマップ提案の判定結果

| # | 提案 | 判定 | 理由 |
|---|------|------|------|
| ① | Synthetic Friction 案 B 再設計 | ⚠️ 条件付き採用 | 現コードの二重パスを認識せず、閾値が β 依存。φ 正規化で再定義して採用 |
| ② | Ground Truth プロトコル Level 2 | ✅ 採用 | ただし 5 秒ホールド中は HMM 一時停止が必須（未言及の問題） |
| ③ | 訓練/評価データ時系列分割 | ✅ 採用 | `hmm_version` をメタデータに追加するのみ |
| ④ | Stage 2 Logistic Regression | ⚠️ 条件付き採用 | ONNX 不要。重みを Rust 定数として埋め込む方針に変更 |
| ⑤ | Stage 3 XGBoost | ❌ 却下 | 100 セッションでは過学習。Rust デプロイ手段なし。LR が不十分な場合のみ再検討 |
| ⑥ | Windows IME 追加特徴量 | ⚠️ 条件付き採用 | シャドーモード収集のみ。HMM 統合は分布分析後に判断 |
| ⑦ | Lv3 Thought Scaffold | ✅ 採用 | 固定 20 問、純フロントエンド、最小スコープ |
| ⑧ | Stuck 回復時間計測 | ✅ 採用 | 既存ログから Python で算出可能 |

**元ロードマップが見落としている欠落タスク:**
- 欠落 A: テスト基盤（`#[test]` がゼロ）
- 欠落 B: パラメータ外部化（すべてハードコード）
- 欠落 C: セッションリプレイツール
- 欠落 D: 沈黙パスの閾値不統一（`lib.rs:662-667` と `features.rs:242-251`）

## Phase 別タスク

### Phase 0: 基盤整備（1-2 週間）
- 0.1 `phi()`, `calculate_features()`, `make_silence_observation()` のユニットテスト — `features.rs` / S
- 0.2 HMM `update()` / `update_silence()` の統合テスト — `engine.rs` / M
- 0.3 遷移・放出行列のスナップショットテスト — `engine.rs` / S
- 0.4 `hmm_version` をログメタに追加 — `logger.rs`, `engine.rs` / S
- 0.5 沈黙パスの閾値不整合を統一 — `lib.rs:662-667`, `features.rs:242-251` / M

### Phase 1: Ground Truth + 計測基盤（2-3 週間）
- 1.1 `LogEntry::UserLabel` バリアント追加 — `logger.rs` / S
- 1.2 `submit_user_label` Tauri コマンド + ホールド中 HMM 一時停止 — `lib.rs` / S
- 1.3 GT 3 択ボタン UI（5 秒ホールド） — `Dashboard.tsx` / M
- 1.4 Stuck 回復時間の事後解析スクリプト — `analysis/recovery_time.py` / S
- 1.5 セッションリプレイスクリプト — `analysis/replay.py` / M
- 1.6 GT 付きセッション 10 件以上の収集 — 運用

### Phase 2: Synthetic Friction 再設計（2-3 週間）
- 2.1 `last_active_features: Option<Features>` を分析ループに追加 — `lib.rs` / S
- 2.2 文脈条件ゲートを沈黙パスに実装（φ 正規化後の閾値） — `lib.rs:659-678` / M
- 2.3 GT データからゲート閾値を校正 — 分析 → 定数更新 / M
- 2.4 回帰テスト（旧 vs 新パラメータ） — リプレイ使用 / S

### Phase 3: ML 統合準備 + IME シャドー収集（4-6 週間、Phase 2 と一部並行可）
**3A: IME 特徴量データ収集**
- 3A.1 IME composition 開始タイムスタンプ記録 — `hook.rs`, `hook_windows.rs` / S
- 3A.2 IME 候補選択中の矢印キーカウント — `hook_windows.rs` / S
- 3A.3 IME 中断カウント（ESC） — `hook_windows.rs` / S
- 3A.4 `feat` エントリに IME 特徴量追加ログ — `logger.rs`, `lib.rs` / S
- 3A.5 20+ セッションから分布分析 — Python / M

**3B: Logistic Regression（50+ セッション後）**
- 3B.1 LR 学習スクリプト — `analysis/train_lr.py` / M
- 3B.2 ラグ特徴量バッファ — `engine.rs` / S
- 3B.3 LR スコアリング（Rust 定数） — `engine.rs::lr_score()` / S
- 3B.4 `feat` エントリに LR スコア追加（シャドー） — `logger.rs`, `lib.rs` / S
- 3B.5 LR vs HMM 精度比較（LOOCV） — Python / M

### Phase 4: 介入層拡充（Phase 2 完了後）
- 4.1 Lv3 Thought Scaffold UI — `ThoughtScaffold.tsx`, `App.tsx` / S
- 4.2 Stuck 回復時間のリアルタイム Dashboard 表示 — `Dashboard.tsx`, `App.tsx` / S
- 4.3 介入フィードバック収集（2 択） — `Dashboard.tsx`, `logger.rs`, `lib.rs` / M

## Phase 移行条件（Go/No-Go）

| 移行 | 条件 |
|------|------|
| Phase 0 → 1 | `cargo test` PASS / 沈黙パス統一済み |
| Phase 1 → 2 | GT 10 件以上 / リプレイで混同行列算出可 / ベースライン精度確定 |
| Phase 2 → 3 | 思考中沈黙の Stuck 誤判定減少 / 挫折後沈黙の正判定維持 |
| LR Go/No-Go | Macro F1 ≥ HMM + 0.03（独立データ） |

## テスト戦略

- 単体テスト: `phi()`, `calculate_features()`, `make_silence_observation()`
- 統合テスト: HMM `update()` サイクル、既知入力列 → 期待状態遷移
- スナップショットテスト: 遷移行列・放出行列・β 値（意図しないドリフト検出）
- 回帰テスト: リプレイツールで旧 vs 新パラメータの全セッション再実行

## ロールバック計画

- Phase 0 は後方互換（テスト追加のみ、既存挙動変更なし）
- Phase 2 の文脈条件ゲートは feature flag で旧挙動に切り替え可能に実装
- LR 統合はシャドーモード（ログのみ）で運用、本線昇格は Go 判定後
