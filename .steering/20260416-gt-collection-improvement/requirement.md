# GT 収集方式の改善

## 背景

Phase 1 で 6 セッション (Win 1 + Mac 5) の GT ラベル付きデータを収集したが、
リアルタイム hotkey 方式に本質的な問題がある:

1. **観察者効果**: Flow 中にラベリング操作 (Cmd+Shift+Option+F) を行うと Flow 自体が阻害される
2. **Stuck 自覚遅延**: ユーザーは Stuck 状態を事後にしか認識できず、リアルタイムでラベルを付けられない
3. **ラベル偏り**: 50 ラベル中 Stuck は 4 件 (8%) のみ、評価に不十分

結果として Stuck precision = 0.167 で Phase 2a Go 条件 (≥ 0.6) に大幅未達。
GT 品質を上げなければ HMM チューニング (Phase 2a) の効果検証も信頼できない。

## ゴール

1. 観察者効果を排除または大幅に低減する GT 収集方式を導入する
2. Stuck ラベルの事後認識を可能にし、ラベル偏りを改善する
3. 既存の gse-replay --metrics パイプラインとの互換性を維持する
4. 既存 hotkey 方式は廃止せず、新方式を追加する (併用可能)

## スコープ

### 含むもの
- gse-replay CLI への新モード追加 (事後レビュー / ラベルファイル統合)
- LABEL_MATCH_WINDOW_MS 定数の見直し
- レビューマーカー hotkey の追加 (認知状態判断不要のブックマーク)
- ラベルファイルの NDJSON フォーマット設計
- 既存セッションでの検証

### 含まないもの
- HMM emission / transition matrix の変更 (別タスク: Phase 2a / ml-workflow)
- ONNX 移行 (Phase 3)
- フロントエンド Dashboard の大規模改修
- 新規特徴量 (F7+) の追加
- β ベースライン値の変更 (Phase III で別途調査)

## 受け入れ条件

- [ ] gse-replay --review で事後セグメントレビューが実行できる
- [ ] .labels.ndjson サイドカーファイルにラベルが保存される
- [ ] gse-replay --metrics --labels <file> でサイドカーラベルを統合してメトリクス算出できる
- [ ] 既存 hotkey ラベルとの共存 (user_label と retrospective ラベルの union)
- [ ] 既存テスト (snapshot + fixture) が PASS
- [ ] 既存セッション 1 件以上で事後レビューを実施し、メトリクス改善を確認

## 関連ドキュメント

- `.steering/20260416-phase2a-synthetic-friction/requirement.md` (Phase 2a、本タスクの後続)
- `.steering/20260415-phase1-ground-truth/baseline_metrics.md` (現在の計測結果)
- `docs/functional-design.md` §7 (GT ラベル仕様)
- `docs/architecture.md` §4.7-4.9 (GT フロー)
- Plan: `~/.claude/plans/parallel-chasing-kite.md` (案 A/B/C 比較)

## 運用メモ

- /reimagine 適用: **Yes**
- 理由: 複数の GT 収集方式 (事後レビュー / ESM / ハイブリッド) が候補にあり、設計判断が必要。Plan で 3 案を起草済み、/reimagine で正式比較する
