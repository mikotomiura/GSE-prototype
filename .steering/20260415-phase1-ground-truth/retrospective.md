# Phase 1 Retrospective

- 期間: 2026-04-15 (1 日で 3 タスク完遂)
- Commits: `461e920` → `71674f2` → `e80ea33` → M1 fix (本 retrospective と同 commit)
- 関連: `20260415-phase1-ground-truth/`, `20260415-phase1-metrics/`, `20260415-phase1-counter-ui/`
- 並行追加: `.github/workflows/ci.yml` 拡充 (`20260415-ci-matrix-build/`)

## ゴール達成度

| 当初ゴール | 達成 |
|---|---|
| UserLabel 記録基盤 (logger + グローバルホットキー) | ✅ |
| `gse-replay --metrics` 算出エンジン (混同行列 / F1 / 中央値) | ✅ |
| Dashboard counter widget + 実機手動検証 | ✅ |
| Phase 0 条件 5 (hmm_version 実機目視) 消化 | ✅ |
| GT 付きセッションの初回 baseline 記録 (`baseline_metrics.md`) | ✅ (n=2) |

## 良かった点 (Keep)

1. **`/reimagine` v2 の徹底**: 「production path を一切触らない」方針で engine/features/hook/ime に 1 行も差分が入らず、Phase 2a で触るコードと Phase 1 で触ったコードが完全に分離した。Task 1/2/3 間の回帰リスクもゼロ
2. **3 分割ワークフロー**: 1 タスクで backend + CLI + frontend + 検証を全部抱え込まず、3 つの独立タスクディレクトリに分けたことで requirement/design/tasklist/decisions の粒度が適切になった。レビューも task 単位で並列化できた
3. **race-free デバウンス (compare_exchange)**: code-reviewer/security-checker 両方から MEDIUM で指摘されたが、修正コストが小さく即対応できた。実装時の初期方式 (load→store) でも動くが、雑な atomic が入り込む前に潰せた
4. **実機初回データで M1 (detection_lead_ms) 問題を発見**: `+50s` という窓端貼り付きが算出ロジックの欠陥を可視化。設計書の「/reimagine で決着済み」でも実データを通さないとわからない欠陥があるという学び
5. **CI 拡充を Phase 1 と並行実施**: Windows ビルドの未検証リスクが積み上がるのを防いだ。タスクの並列化で時間を節約

## 改善点 (Problem)

1. **初回 `detection_lead_ms` の定義ミス (M1)**: `find()` = 先頭ヒットを採る実装は、±60 秒窓という比較的広い窓では偶発的な同クラス出現を拾う。設計レビュー段階で気づけたはず → 今後は「窓内で何を選ぶか」を明示的に書く
2. **Stuck セッションの見落とし (V3-7)**: 初回実機検証で `⌘⇧⌥S` を押し忘れ、Stuck 0 件のまま metrics 算出 → 2 回目で追加検証。検証手順のチェックリスト化が有効だった (`verification_log.md` テンプレ)
3. **GT データ量不足 (n=2)**: Phase 2a Go/No-Go 判断には最低 5 セッション × F/I/S 各 ≥5 件必要。運用フェーズで貯めるしかない
4. **code-reviewer の MEDIUM が Phase 1 を跨いで残存 (M2-M4)**: 性能 (nearest_feat O(N))、JSON 手書き、Dashboard/metrics タイブレーク規則の明示コメント。Phase 2a 着手前または別タスクで消化する必要あり

## 学び (Try: 次タスク以降に持ち込む)

1. **実機データで算出系をすぐ回す**: 合成テストだけでは「窓端貼り付き」みたいな実務問題は見えない。Phase 2a 以降も「小さく実装 → 既存 GT に通す → 数値が妥当か確認」サイクルを高速化
2. **`.steering/<task>/decisions.md` の D# 番号再利用を避ける**: 本 retrospective 作成時に既存 decisions.md の D# 採番が衝突していた (重複 D6)。次タスクからは採番ルールを確認
3. **`baseline_metrics.md` の観察メモを「所見ログ」として育てる**: Phase 2a で触る箇所の根拠として残す。実装差分より「何を見て決めたか」の方が保守性に効く
4. **Phase 2a 着手前のチェックリスト**:
   - [ ] GT 付きセッション ≥5 件、F/I/S 各 ≥5 件
   - [ ] Stuck precision 平均 ≥ 0.6
   - [ ] code-reviewer MEDIUM (M2-M4) の消化

## メトリクス

| 項目 | 値 |
|---|---|
| 実装所要時間 | 1 日 (Task 1: 90min, Task 2: 90min, Task 3: 60min + 実機検証 20min + M1 修正 15min) |
| コード変更行数 | +1,200/-5 (Rust +630, TS +50, docs/steering +500) |
| テスト本数増加 | +15 (logger 8 + metrics 15) |
| レビュー HIGH 指摘 | 0 |
| レビュー MEDIUM 指摘 | 計 8 (Task 1: 3 / Task 2: 4 / Task 3: 3、うち M1 のみ Phase 1 内で修正、M2-M4 は持ち越し) |
| 実機セッション取得件数 | 2 (Flow/Inc 6+4件、Stuck 2件) |

## 次タスク候補

優先度順:
1. **Phase 2a 準備**: GT 収集継続 (運用タスク)、`baseline_metrics.md` を ≥5 セッションまで育てる
2. **Phase 2b IME Shadow Features**: Windows 実機確保時に着手 (GT 不要)。現状は macOS のみなので保留
3. **code-reviewer MEDIUM 消化**: M2 (nearest_feat 二分探索化) / M3 (手書き JSON → serde_json) / M4 (Dashboard タイブレーク規則コメント)
4. **CI 追加改善**: `cargo audit` 導入 (security-checker LOW で推奨), Rust toolchain pin 止め検討
