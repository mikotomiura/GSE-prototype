# 要件定義: Phase 2a Synthetic Friction 再設計 (Incubation→Stuck 誤検出の抑制)

## 背景

Phase 1 の baseline 実測 (fix 後、2026-04-16 時点):

| Session | F/I/S | Macro F1 | 所見 |
|---|---|---|---|
| `gse_20260415_144120.ndjson` (Windows, n=1) | 4/1/1 | 0.722 | Flow 4 件中 2 件を Inc と予測 → Incubation precision 0.333 |

Mac baseline は `replay-feat-alignment-bug` fix 前の値しかなく dataset から削除済み (`.steering/20260415-phase1-ground-truth/baseline_metrics.md` 「再計算待ち」節)。次回 Mac セッションで再計算予定。

**観察された系統的誤り**: Flow タイピング中に 2s 以上の小休止が入ると HMM が Incubation/Stuck 側に寄り、実際にはユーザーが思考中 (生産的中断) の沈黙を Stuck と誤判定するリスク。Phase 1 retrospective の「Keep #1」にも「ユーザー自認より早く Inc/Stuck 側に振れる」と記録済み。

**根本原因仮説**: `src-tauri/src/analysis/features.rs::make_silence_observation()` の沈黙ゲートが φ 正規化**前の** raw F3 / F6 値で摩擦フロアを適用しており、「タイピング活動中に摩擦兆候があった」のか「単に沈黙しているだけ」なのかを区別していない。思考中の沈黙にも Stuck 寄りの観測を合成している。

詳細設計は `.steering/20260414-improvement-roadmap/design.md:300-350` に起草済み (v1 相当)。本 requirement は design 段階で改めて `/reimagine` で A/B 案を比較する前提。

## ゴール

1. 思考中の沈黙を Incubation/Stuck に誤分類しない文脈ゲートを導入する
2. Stuck precision の非劣化 (現状平均 ≥ 1.0、Phase 2a 完了後も >= 0.6 維持)
3. Incubation 対象セッションで Stuck 誤検出率を計測可能な形で低減
4. `baseline_metrics.md` を continue growing、Phase 2a 判定値を記録

## スコープ

### 含むもの
- `src-tauri/src/analysis/features.rs::make_silence_observation()` の F3/F6 再校正
  - 沈黙開始前の「直近 active 時の features」を参照して摩擦フロア適用を条件付け
- `src-tauri/src/lib.rs` 分析スレッド (loop_step::step 化後) に `last_active_features: Option<Features>` buffer 追加
- φ 閾値ゲート (`phi(F3, β_coding) >= THRESHOLD_PHI_F3` 等) の導入
- 初期閾値定数 (`THRESHOLD_PHI_F3`, `THRESHOLD_PHI_F6`) を engine 定数として追加、GT 校正結果のコメント
- `tests/snapshots/` のゴールデン再生成 (diff を `.steering/20260414-improvement-roadmap/phase2a_results.md` に記録)
- GT 付き全セッションに `gse-replay --metrics` を通して precision 維持を確認

### 含まないもの
- ONNX 化 (Phase 3 予定、`ml-workflow` Skill 参照)
- Lv2 Wall トリガー調整 (`intervention-design` Skill の管轄、Phase 2c 以降)
- Phase 2b IME Shadow Features (Windows 並列トラック、別タスク)
- 新規特徴量追加 (F7 以降)
- HMM emission_matrix / transition_matrix の変更 (`ml-workflow` 規約で要別タスク)

## 前提チェックリスト (Phase 1 retrospective L38-41 から転記、2026-04-16 現状反映)

- [ ] GT 付きセッション **≥ 5 件** (Phase 2a 着手閾値、現状 n=1 まで fix 後)
- [ ] F/I/S ラベル各 **≥ 5 件** (本件スコープで改善対象、現状 F=4/I=1/S=1)
- [ ] Stuck precision 平均 **≥ 0.6** (`STUCK_GO_THRESHOLD=0.6` in `gse-dataset/scripts/aggregate_metrics.py:30-40`)
- [ ] Phase 0.5 Close-out 完了 (BL-1 docs 同期、M3 TryFrom、Stage H sync-session、本 requirement 起草)
- [ ] Mac 側 baseline 再計算完了 (次回 Mac セッション)
- [ ] code-reviewer MEDIUM M3 (NaN/Inf 検証) マージ済み
- [ ] M4 (NDJSON 1-pass 統合) は defer 可、Phase 2a 着手を阻害しない

## Go/No-Go 条件 (Phase 2a 完了判定)

- [ ] Stuck precision が変更前から**非劣化** (≥ Phase 1 baseline 平均)
- [ ] Incubation→Stuck 誤検出率 (confusion matrix `cm[1][2]`) が現状比で減少
- [ ] ゴールデンスナップショット差分をレビュー承認
- [ ] 閾値 `THRESHOLD_PHI_F3` / `THRESHOLD_PHI_F6` を engine.rs 定数として記録、根拠 GT を `.steering/` に添付 (ml-workflow Skill の「HMM パラメータチューニングの根拠をコメントで書く」準拠)
- [ ] 新規テスト (snapshots 再生成 + NaN/Inf 耐性維持) PASS

## 参照必須 Skill / Agent

### Skill (起動時必須)
- **`hmm-analysis`**: F3/F6 の定義、φ 正規化 (β_coding / β_writing)、沈黙観測の合成式、観測ビン (obs=0..25) 量子化。本件で触る沈黙ゲートと observation 生成は hmm-analysis 管轄の中核
- **`ml-workflow`**: HMM パラメータチューニング根拠のコメント規約、将来 ONNX 化との境界
- **`rust-standards`**: features.rs / engine.rs / lib.rs 編集時の tracing / `anyhow::Result` / unsafe 周りのルール

### Sub-agent 活用計画
- **Plan 段階**: impact-analyzer で features.rs / engine.rs / lib.rs の波及分析 (make_silence_observation の caller、`last_active_features` の atomic / mutable 要件)
- **実装後**: code-reviewer + security-checker を並列起動 (プライバシー境界に触れないが入力バリデーション強化の波及を確認)
- **検証**: test-runner で全 tests PASS 確認、GT snapshot 再生成は build-executor で cargo run + diff、log-analyzer は必要なら

## 運用メモ

- **`/reimagine` 適用: Yes** — design.md 起草時点で必ず `/reimagine` を実行し、2 案比較後にユーザー承認を得る。`improvement-roadmap/design.md:300-350` は v1 案として比較対象に使う (退避せず参照のみ)
- **TDD 順序**: 合成テストで make_silence_observation 境界条件 → 実装 → 既存 golden snapshots 再生成 → GT sessions で `--metrics` 回帰確認 → マージ
- **commit 戦略**: feat(analysis): synthetic friction context gate / test(analysis): golden snapshot rebuild for phase2a / docs(steering): phase 2a results record の 3 commit 想定

## 関連

- 親 roadmap: `.steering/20260414-improvement-roadmap/design.md:300-350` (Phase 2a 詳細設計 v1)
- Phase 1 完了記録: `.steering/20260415-phase1-ground-truth/retrospective.md`、`baseline_metrics.md`
- 直前 cleanup: `.steering/20260416-replay-feat-alignment-bug/decisions.md` D1 (clock semantic)、Phase 0.5 close-out plan (`~/.claude/plans/virtual-foraging-clock.md`)
- GT 収集自動化: `scripts/sync-session.ps1` / `scripts/sync-session.sh`
