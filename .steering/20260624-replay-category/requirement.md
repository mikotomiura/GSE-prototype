# replay-category — gse-replay の匿名化 NDJSON (vk→category) 対応

## 背景

transfer-pipeline (#27) の `gse-package` が raw NDJSON を匿名化する際、`key` イベントの `vk` を
`category` (KeyCategory: alphabetic/backspace/delete/...) に置換し、絶対 epoch 時刻を session_start
相対へ変換する。D6 は「匿名化 NDJSON でも **Replay-as-Truth を維持** (特徴量再計算可)」を要求するが、
現状 `gse-replay` の `ReplayEvent::Key` は `vk` しか読まないため、匿名化済みデータを replay できない
(= 共有した暗号塊を研究者が復号しても特徴量再計算できない)。本タスクで loop を閉じる。

親: `roadmap-xy.md` Phase C / `decisions.md` D6 / transfer-pipeline (PR #27)。

## ゴール

`gse-replay` が匿名化 NDJSON (key の `category`) を replay でき、同じ raw を replay した場合と
同じ特徴量値 (f1-f6 / probs) を出すこと。既存の raw replay / `--snapshot` byte-equal は不変。

## スコープ

### 含むもの
- `src-tauri/src/bin/replay.rs` の `ReplayEvent::Key` を `vk` (raw) と `category` (匿名化) の両対応に。
  feature 計算に要るのは is_backspace (category==backspace) / is_delete (category==delete) / 時刻 / press のみ。
- `category` → InputEvent への変換 (is_backspace/is_delete を category から導出)。
- `collect_key_events` (--metrics outcome 経路) も category 解決に対応。ただし `is_text_producing`
  判定は `KeyCategory` 粒度で **OEM 句読点/Tab/テンキー演算子 (Other 畳み込み) を過小評価**する
  内在制約あり (decisions.md D-RC3)。**run_replay 特徴量再計算 (D6 本来の目的) は exact で無影響。**
- 検証: raw replay の FeatSnapshot と、その raw を gse-package で匿名化した NDJSON を replay した
  FeatSnapshot で特徴量値が一致すること (時刻 t は相対化で異なるため byte-equal でなく特徴量値一致で確認)。
  golden fixture に匿名化版を追加。
- schema_dto に anonymized key の category 形を反映するか検討 (emit_schema parity)。

### 含まないもの
- gse-package / anonymize.rs の変更 (#27 で完了)。HMM/engine/features ロジック変更。
- DuckDB ハーネス (#6・別タスク)。survey Form 等の運用。

## 受け入れ条件

- [ ] gse-replay が匿名化 NDJSON (category) を replay でき、raw と同じ特徴量値を出す
- [ ] 既存 raw replay / `--snapshot` byte-equal が不変
- [ ] `cargo test --workspace` 緑 (raw replay と匿名化 replay の特徴量値一致テスト追加)
- [ ] schema 触れば `emit_schema` parity 緑
- [ ] code-reviewer / security-checker / cross-review で CRITICAL/HIGH なし

## 関連ドキュメント

- `decisions.md` D6 (Replay-as-Truth on anonymized data)
- `docs/development-guidelines.md` §3 (Replay-as-Truth)
- transfer-pipeline の `anonymization.md` (KeyCategory 定義) / `analysis/anonymize.rs`
- Skill: `hmm-analysis` (features.rs が vk から何を使うか) / `rust-standards` / `data-privacy`

## 運用メモ
- /reimagine 適用: No
- 理由: 既存 ReplayEvent::Key を category 対応へ拡張する機械的な実装。アーキテクチャ判断や
  複数の非自明な設計案を伴わない (vk|category の両対応 enum 拡張が自明な最良案)。
