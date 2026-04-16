# 設計 v2: 活動境界セグメンテーション + エディタ注釈 + 範囲マッチング

## 実装アプローチ

### 核心のアイデア: 「点ラベル」から「範囲ラベル」への転換

現行の GT は **点ラベル** (hotkey を押した瞬間 ±1s の feat に紐づく) だが、
認知状態は本質的に **エピソード** (数十秒〜数分の区間) として経験される。

v2 では **範囲ラベル** を導入する:
- セッションを活動境界 (沈黙 ≥ 5s) で自動分割
- 各セグメントは [start_ms, end_ms] を持つ
- ラベルはセグメント全体に適用 → 区間内の**全 feat** と比較
- 1 ラベルから複数の feat-label ペアが生成される → 統計検出力が大幅に向上

### 施策 1: gse-replay --segment (セグメントファイル生成)

セッション NDJSON を解析し、活動境界で自動分割した `.segments.txt` を生成する。

```
# Session: gse_20260416_060712.ndjson
# Duration: 10m 23s  |  Total keys: 1847  |  Segments: 14
#
# Label: F=Flow  I=Incubation  S=Stuck  ?=Unknown  -=Skip
# Edit the Label column, then save.

 Seg  Start    End      Keys  Silence  CorrRate  AvgFT   Label
  1   00:00    00:32    142   2.1s     3.1%      121ms   ?
  2   00:32    01:05    0     33.0s    -         -       ?
  3   01:05    01:48    267   1.2s     8.4%      98ms    ?
 *4   01:48    02:15    45    12.3s    15.2%     203ms   ?
  5   02:15    03:01    312   0.8s     2.1%      89ms    ?
```

- `*` マーク: レビューマーカー (hotkey) がこのセグメント内にある
- ユーザーは任意のテキストエディタで `?` を F/I/S に書き換えるだけ
- 固定 30 秒ではなく、**自然な活動境界** (沈黙 ≥ 5s) で分割するので認知エピソードと整合

**メリット** (stdin プロンプト方式との比較):
- 全セグメントを俯瞰しながらラベリングできる
- 前後の文脈を見て判断を修正できる (stdin は逆戻り不可)
- エディタの検索・置換が使える
- ファイルとして保存 → git 管理可能

### 施策 2: gse-replay --metrics --segments <file> (範囲マッチング)

`.segments.txt` を読み込み、範囲ベースで confusion matrix を構築する:

```
for each segment [start, end, label]:
    for each feat in feats where start <= feat.t <= end:
        predicted = argmax(feat.p_flow, feat.p_inc, feat.p_stuck)
        confusion[label][predicted] += 1
```

**点ラベルとの統計検出力の比較**:
- 点ラベル: 1 ラベル → 1 feat-label ペア (±1s 窓)
- 範囲ラベル: 1 ラベル → N feat-label ペア (セグメント長 / 1Hz ≈ 30-60 ペア)
- 50 ラベル相当の GT を得るのに必要なセグメント数: 2-3 個

既存の点ラベル (--labels / 埋め込み user_label) も引き続きサポート。
混在時は点ラベル → nearest feat、範囲ラベル → 全 feat in range で統合。

### 施策 3: レビューマーカー hotkey

- `Cmd+Shift+Option+R` (macOS) / `Ctrl+Shift+Alt+R` (Windows)
- `{"type":"review_marker","t":...}` をログに記録
- --segment 生成時にマーカー所属セグメントに `*` を表示
- 認知状態の判断不要、作業の邪魔にならない

### LABEL_MATCH_WINDOW_MS について

範囲ラベルには LABEL_MATCH_WINDOW_MS は不要 (範囲全体がマッチ対象)。
既存の点ラベルとの互換性のために現行値 (1000ms) は維持するが、
範囲ラベルの導入により点ラベルの精度問題は実質的に解消される。
→ 定数変更は行わない (変更理由が消失したため)

## 変更対象

### 修正するファイル
- `src-tauri/src/bin/replay.rs` — --segment モード追加、--segments オプション追加、範囲マッチング統合、ReplayEvent に ReviewMarker バリアント追加、usage() 更新
- `src-tauri/src/analysis/metrics.rs` — RangeLabel 型追加、compute_range_metrics() 関数追加
- `src-tauri/src/lib.rs` — レビューマーカー hotkey 登録 (shortcuts 配列 + handler に KeyR 分岐)
- `src-tauri/src/logger.rs` — LogEntry::ReviewMarker バリアント追加 (独立 NDJSON type: "review_marker")、フォーマット関数追加
- `src-tauri/src/schema_dto.rs` — LogEntryDto に ReviewMarker バリアント追加 (CI schema drift check 対応)
- `src-tauri/schema/current.json` — emit_schema で再生成 (LogEntryDto 同期)

### 新規作成するファイル
- なし

### 削除するファイル
- なし

## 影響範囲

- gse-replay --metrics の既存動作は変更なし (点ラベルのみの場合)
- --segments 指定時のみ範囲マッチングが追加される
- 既存 snapshot テストは影響なし (LABEL_MATCH_WINDOW_MS 不変)
- **LogEntry::ReviewMarker 追加の連鎖影響** (impact-analyzer 検出):
  - `schema_dto.rs` の LogEntryDto にバリアント追加必須 (CI schema drift check が FAIL する)
  - `schema/current.json` を `cargo run --bin emit_schema` で再生成必須
  - `replay.rs` の ReplayEvent enum にバリアント追加必須 (run_replay の strict parse が FAIL する)
  - これら 3 ファイルは LogEntry と**アトミックに同期更新**する (部分コミットで CI FAIL を作らない)
- ReviewMarker は独立 NDJSON type (`"type":"review_marker"`) として設計。UserLabelKind には含めない (意味論が異なる: ラベルではなくブックマーク)

## 既存パターンとの整合性

- replay.rs の CLIフラグ追加は既存の --metrics / --json パターンに従う
- LogEntry 新バリアントは既存の UserLabel / ImeState パターンに従う
- metrics.rs の RangeLabel は既存の UserLabelEvent と並列の型として追加
- セグメントファイル形式は plain text (NDJSON ではない) — 人間が直接編集する前提

## テスト戦略

- 単体テスト: セグメント分割ロジック (沈黙 ≥ 5s 境界検出)
- 単体テスト: 範囲マッチング (segment [t1, t2, label] × feats → confusion matrix)
- 単体テスト: セグメントファイルのパーサー (ラベル行の解析、コメント行スキップ)
- 統合テスト: fixture NDJSON → --segment → 手動ラベル → --metrics --segments のパイプライン
- E2E: 実セッションで --segment → エディタ編集 → --metrics --segments

## ロールバック計画

- 全て新規追加のみ。既存の --metrics 動作は変更しない
- --segment / --segments は独立フラグなので、問題があれば使わなければよい
- LABEL_MATCH_WINDOW_MS は変更しないので snapshot テストへの影響なし

## 設計判断の履歴

- 実行回数: 1 回目
- 採用: v2 (活動境界セグメンテーション + エディタ注釈 + 範囲マッチング)
- 根拠: 範囲ラベルが認知状態の「エピソード」性を直接モデル化し、統計検出力が点ラベルの 30 倍。既存テストへの影響ゼロ。エディタベースの UX で全体俯瞰 + 自由な修正が可能
