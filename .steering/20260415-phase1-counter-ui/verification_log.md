# Phase 1 実機手動検証ログ

> **用語**: `docs/development-guidelines.md` §3 の **実機手動検証 (manual verification)**。
> Playwright 等の自動 E2E は含まない。回帰保護は Task 2 の `gse-replay --metrics` +
> ゴールデン byte-equal が担う。本ログは UI 結線の目視確認のみ。

## 実行環境

- 日時: **2026-04-15 17:00〜17:10 JST**
- ホスト: macOS 15.x (Apple Silicon, MacBook Air)
- ブランチ: main
- Task 1 commit: `461e920`
- Task 2 commit: `71674f2`
- Task 3 commit: `e80ea33`
- M1 修正 commit: _本ログ記録後に付与_

## 事前チェック

- [x] `git log --oneline -3` で Task 1/2/3 の commit を確認
- [x] `cd src-tauri && cargo test --workspace` 全 PASS (50 → 51 tests after M1 fix)
- [x] `cd src-tauri && cargo build --target aarch64-apple-darwin` warning 0
- [x] `npx tsc --noEmit` エラー 0

## 検証手順

### Step 1: 起動 + 権限確認
- [x] `npm run tauri dev` で起動成功
- [x] Input Monitoring 権限付与済み (既存環境で継承)
- [x] Dashboard 表示

### Step 2: Counter 初期表示
- [x] Counter widget が `GT: Flow 0 / Inc 0 / Stuck 0` を表示
- [x] ショートカット hint (`⌘⇧⌥ F/I/S`) 可視

### Step 3: Flow ラベル 1 回目
- [x] `⌘⇧⌥F` 押下 → Counter `Flow 1`
- [x] tracing に `user_label recorded: flow @ <ts>` (ユーザー確認済み)

### Step 4: デバウンス確認
- [x] 2 秒以内の再押下で Counter 不変 (ユーザー "Step 3-4 は大丈夫でした")

### Step 5: 2 秒以上待って再押下
- [x] 3 秒待機後 `⌘⇧⌥F` → Counter インクリメント (ユーザー "Step 3-4 大丈夫")

### Step 6: Incubation / Stuck
- [x] セッション 1 (gse_20260415_080214.ndjson): Flow ×6 / Inc ×4
- [x] セッション 2 (gse_20260415_080921.ndjson): Stuck ×2 (別セッションで追加検証)

### Step 7: セッション終了 + NDJSON 検査

セッション 1: `~/Documents/GSE-sessions/gse_20260415_080214.ndjson`
- [x] meta 行に `"hmm_version":"0.2.0"` 記録 (**Phase 0 条件 5 消化**)
- [x] user_label 10 件 (Flow ×6, Incubation ×4, Stuck ×0)
- [x] 全 `recovered_at: null` (想定通り、オフライン計算設計)
- [x] 最短ラベル間隔 2950ms (デバウンス違反ゼロ)

セッション 2: `~/Documents/GSE-sessions/gse_20260415_080921.ndjson`
- [x] hmm_version 記録、user_label 2 件 (Stuck ×2)
- [x] 間隔 5798ms (デバウンス OK)

### Step 8: `--metrics` pretty-print

セッション 1 (M1 修正後の再算出):
```
SessionMetrics
  Total labels: 10 (Flow:6, Inc:4, Stuck:0)
  Macro F1: 0.000 / Micro F1: 0.000
  Per-class: Flow P=0 R=0 F1=0 (support=6), Inc 同様, Stuck support=0
  Confusion:
    Flow       0  4  2
    Incubation 2  0  2
    Stuck      0  0  0
  Detection lead median: -3119 ms  (HMM が 3.1 秒遅延)
  Warnings: 0
```

セッション 2:
```
Total labels: 2 (Flow:0, Inc:0, Stuck:2)
Macro F1: 0.222 / Micro F1: 0.500
Stuck: P=1.000  R=0.500  F1=0.667  support=2
Detection lead median: +2383 ms  (HMM が 2.4 秒先行)
```

- [x] 両セッションで pretty-print 出力成功
- [x] warnings ゼロ (全ラベルが 1 秒窓内で FeatSnapshot マッチ)

### Step 9: `--metrics --json`
- [x] セッション 1 に対して JSON 出力成功、`jq '.total_labels'` 等で消費可能

### Step 10: 回帰確認
- [x] `gse-replay --snapshot tests/snapshots/minimal.json` → `OK: 15 snapshots match`
- [x] M1 修正後も snapshot byte-equal 維持

## 結果サマリ

- 全ステップ PASS: **Y**
- ブロッカー: なし
- 所要時間: 約 20 分 (Stuck 追加検証含む)
- セッションファイル:
  - `~/Documents/GSE-sessions/gse_20260415_080214.ndjson` (Flow/Inc)
  - `~/Documents/GSE-sessions/gse_20260415_080921.ndjson` (Stuck)

## 追加観察

### 実装バグ所見
- **なし**。全機能が期待通り動作。

### アルゴリズム所見 (Phase 2a に向けて)
1. **HMM の Flow クラス認識が弱い**: セッション 1 で Flow ラベル 6 件すべてが Inc/Stuck 判定。`analysis/engine.rs` の初期分布・遷移行列・放出行列の感度が Flow に不利に寄っている可能性
2. **Stuck は比較的当たる**: セッション 2 で P=1.0。Stuck ラベル後 15 分以内に p_flow > 0.5 復帰なし (sr_median = n/a) → 回復判定ロジックは現状厳しめ
3. **detection_lead_ms 定義の初期実装が間違っていた (M1)**: +50s → -3.1s/+2.4s に改善。Phase 2a の lead/lag 比較で歪みが出ないよう今回の修正が必須だった

### サンプル数不足
- F/I/S 各クラスが十分揃うにはさらに 3-5 セッション必要 (現状 F=6, I=4, S=2)
- Phase 2a Go/No-Go 判断前に `baseline_metrics.md` を埋める運用を継続
