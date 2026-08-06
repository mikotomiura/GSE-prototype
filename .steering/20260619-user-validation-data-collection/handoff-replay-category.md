# 次セッション開始プロンプト — replay の category 対応 (匿名化 NDJSON の特徴量再計算・D6)

> `feedback_handoff_prompt_in_steering` 方針に従い CLAUDE.md 制約込みで固定。
> 親: `roadmap-xy.md` Phase C / `decisions.md` D6 / transfer-pipeline (PR #27)。
> **新規 `/start-task` で着手。main 基点で別ブランチ・別 PR。main 直コミット禁止。**

## なぜこれが次か
transfer-pipeline (#27) で `gse-package` が raw NDJSON を匿名化する際、`key` イベントの `vk` を
`category` (KeyCategory: alphabetic/backspace/delete/...) に置換し、絶対 epoch 時刻を session_start
相対に変換する。D6 は「匿名化 NDJSON でも **Replay-as-Truth を維持** (特徴量再計算可)」を求めるが、
現状 `gse-replay` の `ReplayEvent::Key` は `vk` しか読まないため、**匿名化済みデータを replay できない**
(= 共有した暗号塊を研究者が復号しても特徴量再計算できない)。本タスクで loop を閉じる。

## スコープ
### 含むもの
- `src-tauri/src/bin/replay.rs` の `ReplayEvent::Key` を **`vk` (raw) と `category` (匿名化) の両対応**に。
  feature 計算に要るのは is_backspace (category==backspace) / is_delete (category==delete) / 時刻 / press
  のみ (features.rs 確認のこと)。exact key は不要なので category で同じ特徴量が出る。
- `category` → InputEvent への変換 (is_backspace/is_delete を category から導出)。
- 検証: **raw を replay した FeatSnapshot と、その raw を gse-package で匿名化した NDJSON を replay した
  FeatSnapshot で、特徴量値 (f1-f6/probs) が一致**すること (時刻 t は相対化で異なるため byte-equal でなく
  特徴量値一致で確認)。golden fixture に匿名化版を追加。
- schema_dto に anonymized key の category 形を反映するか検討 (emit_schema parity)。

### 含まないもの
- gse-package / anonymize.rs の変更 (#27 で完了)。HMM/engine/features ロジック変更。
- DuckDB ハーネス (#6・別タスク)。survey Form 等の運用。

## 必須プロトコル (CLAUDE.md 準拠)
1. `/start-task` → `/add-feature`。
2. docs 先読み: `decisions.md` D6 / `development-guidelines §3` (Replay-as-Truth) / `anonymization.md`
   (KeyCategory 定義) / transfer-pipeline の `analysis/anonymize.rs`。
3. Skill: `hmm-analysis` (features.rs が vk から何を使うか確認) / `rust-standards` / 必要なら `data-privacy`。
4. file-finder/impact-analyzer で replay.rs の Key パース・features.rs の is_backspace/is_delete 由来・
   schema_dto の Key DTO を調査。
5. 実装後 `code-reviewer` + (logger/replay 触るなら) `security-checker` 並列。
6. `/cross-review` (jq 導入済)。7. `/finish-task` (schema 触れば parity・drift で停止)。

## 検証ゲート
- `cargo test --workspace` 緑。**raw replay と 匿名化 replay の特徴量値一致**テスト追加。
- 既存 `--snapshot` byte-equal 不変 (raw 経路は不変・category は追加経路)。
- schema 触れば `emit_schema` parity 緑。

## 制約
- tracing/anyhow/any 禁止・winapi 禁止・analysis OS 非依存・本文非保存。`.steering/` 記録必須。別 PR・main 基点。

## 受け入れ条件
- gse-replay が匿名化 NDJSON (category) を replay でき、raw と同じ特徴量値を出す。
- 既存 raw replay/snapshot は不変。cargo test 緑・(schema 触れば parity 緑)。CRITICAL/HIGH なし。

## 補足: プロジェクト全体の現在地 (WBS 準拠)
- M0 コード基盤はほぼ完了 (capture #18 / metrics #19 / 介入応答 #20 / 転送 #27)。
- 残コード: 本タスク (replay category)、#6 DuckDB ハーネス (survey データ到着後)。
- 残りは **運用/文書** (PreReg 凍結・Google Form 事後アンケート・Dropbox 運用・blind 品質ルーブリック・
  Go/No-Go 拡張) で M1 Phase 1a (n=3-5 募集・実施) はコードのブロッカー無し。

---

## 貼り付け用プロンプト (新セッションで /clear 後に投入)

```
.steering/20260619-user-validation-data-collection/handoff-replay-category.md に従い、gse-replay を
匿名化 NDJSON (key の vk→category) に対応させてください。transfer-pipeline (#27) の gse-package が
出力する匿名化 NDJSON を研究者が特徴量再計算できるようにする (D6 Replay-as-Truth の本来目的)。

現状: ReplayEvent::Key は vk のみ読む → 匿名化済み (category) を replay 不能。feature に要るのは
is_backspace(category==backspace)/is_delete(category==delete)/時刻/press のみ。

/start-task → /add-feature。decisions.md D6 / development-guidelines §3 / anonymization.md /
analysis/anonymize.rs を先読み。hmm-analysis Skill で features.rs が vk から何を使うか確認。
file-finder/impact-analyzer で replay.rs(Key パース)・features.rs(is_backspace/is_delete 由来)・
schema_dto(Key DTO) を調査 → 実装 (ReplayEvent::Key を vk|category 両対応・category→InputEvent 変換) →
検証 (raw replay と 匿名化 replay の特徴量値一致テスト追加・既存 --snapshot byte-equal 不変・schema 触れば
emit_schema parity) → code-reviewer(+security-checker) 並列 → /cross-review → /finish-task。
制約: tracing/anyhow/any禁止・本文非保存・別PR・main基点。スコープ外: gse-package/anonymize 変更・
DuckDB・運用Form。
```
