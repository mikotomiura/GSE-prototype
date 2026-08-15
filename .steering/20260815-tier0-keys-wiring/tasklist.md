# タスクリスト — Tier 0 配線（`keys` / `bs_keys`）

> ⚠️★★★ **本セッション（2026-08-15）はコードを 1 行も書いていない。** 準備までで止めた（研究者判断・コンテキスト都合）。

## 準備（★ 本セッションで完了）

- [x] 関連 docs を読む（`personalization-and-online-learning.md §5.2/§10` / ADR-008 / ADR-009 / `domain-adapter-boundary.md`）
- [x] ★ 設計の原本を読む（`.steering/20260801-recovery-axis-grounding/tier0-wiring-design.md`・181 行）
- [x] ★ 一次で `f3 = correction_keys / total_keys` を確認（`features.rs:146-152`）
- [x] ★ 一次で `feat` 行の書き出し位置を確認（`logger.rs:1214`。⚠️ memo の `:974` は古い）
- [x] ★ 一次で `FeatSnapshot` を確認（`analysis/loop_step.rs:134`・**golden の byte-equal 比較対象**）
- [x] ★ golden の本数を実測（**4 本**。⚠️ notes.md の「3 本」は古い）
- [x] ★ `C:\gse-dataset` の実在と HEAD を確認（`f3e8566`）
- [x] ⚠️★★★ **`check_schema_parity.py` を実行 → 既存 drift を検出（exit 1）**
- [x] ★ 研究者判断を 2 件取得（D1 順序 / D2 dataset 同時更新）
- [x] ★ 未決を 2 件閉じた（D3 案 B / D4 `FeatSnapshot` に含める）

## ⚠️★★★ 実装の前に（★ 2026-08-16 実施済み）

- [x] ⚠️★★★ **B-1: 既存 drift の解消** —— `hook_health` variant と `meta.g1_mode` を
      `C:\gse-dataset/schema/current.json` へ反映し、`check_schema_parity.py` を **exit 0** に戻した
      （★ 49 insertions / 0 deletions ＝ additive-only）
- [x] ★ B-1 の解消を **単独でコミット**した（★ `gse-dataset` の `c9e97ef`。⚠️ **push は未実施**）

## 実装（★ 2026-08-16 実施済み）

- [x] `features.rs` — `Features` に `keys` / `bs_keys` を追加し `calculate_features()` で埋める（★ 新規計算ゼロ）
- [x] `analysis/loop_step.rs` — `FeatSnapshot` に `keys: u64` / `bs_keys: u64` を追加
      （★ ⚠️ **推論経路に依らず実測値を書く**。判断 5 を参照）
- [x] `schema_dto.rs` — `Feat` DTO に `Option<u64>` ＋ `#[serde(default)]` で追加（★ 読むときは省略可）
- [x] `logger.rs` — `LogEntry::Feat` に 2 フィールド追加 ＋ **`format_feat_line()` を純粋関数として抽出**
      （★ `format_paste_line` と同型にしてテスト可能にした。★ 書き出しは常に値を書く）
- [x] ★ **`bin/replay.rs`（⚠️ 設計時に洗い出せていなかったファイル）** — `LoggedFeatDto` を同期。判断 7 を参照
- [x] `lib.rs` — `FeatSnapshot` → `LogEntry::Feat` の変換に 2 フィールド追加
- [x] `cargo run --bin emit_schema` → `schema/current.json` を再生成（★ 20 insertions / 0 deletions）
- [x] ★ gse-dataset 側へ本タスクの additive 変更を反映（⚠️ **コミットは未実施**＝本 repo と同時に行う）

## テスト（★ 2026-08-16 実施済み）

- [x] `logger.rs` のフォーマット文字列テストに期待文字列を追加
      （`feat_line_fixes_field_order_and_precision` / `feat_line_records_key_counts_as_integers_only`）
- [x] `features.rs` の単体テスト 4 件（★ 分母/分子の一致・release 除外/repeat 算入・30 秒窓・合成観測は 0）
- [x] ★ **旧 NDJSON（新フィールドなし）を読めること**
      （`logged_feat_dto_accepts_legacy_line_without_tier0_fields`）
- [x] ★★★ **golden 4 本を再生成し、差分が「新フィールドの追加のみ」であることを機械判定**
      —— ★ **`p_*` / `raw_*` / `ewma_*` / `obs` / `f1`〜`f6` は 1 ビットも動いていない**。
      詳細は `golden-regeneration.md`
- [x] `HMM_VERSION` が `0.3.0` のまま（★ `engine.rs` は 1 行も変更していない）
- [x] `cargo test --workspace` が緑（**354 + 25 + 1 passed / 0 failed**）
- [x] `python scripts/check_schema_parity.py --dataset C:/gse-dataset` が **exit 0**
- [x] ★ `cargo fmt --all -- --check` 緑 ／ `cargo clippy` の**新規警告ゼロ**
      （⚠️ 既存の `schema_dto.rs:39-42` / `logger.rs:352` は本変更の前から出ているもの）
- [x] ★ **新フィールドを読む本番コードが存在しないこと**（★ grep 実測: 読み取りはテストと
      `loop_step.rs` の記録用退避のみ）

## レビュー（★ 2026-08-16 実施済み・詳細は `review-findings.md`）

- [x] ★★★ **`code-reviewer` + `security-checker` を並列起動**
- [x] `/cross-review`（★ Codex 独立レビュー）
      ⚠️ **コマンドはそのまま使えなかった**（★ 他タスク由来の未コミット 27 件で
      2000 行超 ＋ `secrets-filter*.sh` のファイル名が Step 2 の fail-closed に当たる）
      → ★ `scripts/run-codex-review.sh -- <paths>` を本タスクのパスに限定して直接呼んだ。
      ★ `secrets-filter.sh` は **exit 0**（`--ack-filtered` は使っていない）
- [x] HIGH 指摘への対応（★ **2 件とも対応済み**）
      - H-1: ⚠️★★★ **`keys` の意味を誤って記述していた**（「今から 30 秒」ではなく
        「最後の打鍵から遡る 30 秒」＝ **沈黙中は同じ値がくり返される**）→ doc 正本化 ＋
        テスト名訂正 ＋ 凍結挙動のテスト追加 ＋ `development-guidelines.md §10.3.2` 新設
      - H-2: ★ 中核判断（実測値の退避）が**どのテストでも観測できなかった** →
        `loop_step.rs` に `mod tests` を新設（4 件）。★ **変異テストで実効性を確認**
- [x] MEDIUM 5 件への対応（★ backlog に送らず本タスクで消化）
      - M-1 `anonymize.rs` の passthrough を **フィールド集合の固定テスト**でゲート
      - M-2 `format_feat_line` を **`struct FeatLine`** に（13 連続 f64 の取り違え防止）
      - M-3 旧ログ欠測を **`tracing::warn!`** で可視化 ＋ 解析者向け docs
      - M-4 **`engine_output_is_invariant_to_tier0_key_counts`**（★ 契約を実行可能にする）
      - M-5 **`bs_keys > keys` を入力側で reject**（★ 将来の u64 underflow を止める）

## ドキュメント（★ 2026-08-16 実施済み）

- [x] ⚠️★★★ `personalization-and-online-learning.md §10` の順序記述を改訂（★ D1・例外注記を追加）
- [x] ★ `§5.2` の Tier 0 表を更新（★ `keys` / `bs_rate` を「2026-08-16 配線済み」に。
      ⚠️ `bs_rate`「未配線」の誤りは 2026-08-01 に訂正済みだったので、そこへ `bs_keys` 追加の理由を追記）
- [x] ★ golden 再生成の差分を `.steering/` に記録（`golden-regeneration.md`）
- [x] ★ `notes.md §5③` の「golden 3 本」を訂正（★ **T0-Q3・研究者が 2026-08-16 に訂正を承認**）
      → ★ **4 本**に訂正し `deep_silence.json` を明記。★ 3 本だけ再生成すると
      `deep_silence` が取り残されて `cargo test` が落ちる旨と、`cd src-tauri` の注意も併記

## 完了処理

- [x] design.md の最終化
- [x] decisions.md の追記（★ 判断 5/6/7 ＋ 実測 3）
- [ ] `/finish-task`（★ Step 3 で schema parity check が走る）
- [ ] git commit（★ **1 コミットに閉じる** = revert 1 回で戻せるようにする）
- [ ] ⚠️★★★ **研究者の手が要る**: `gse-dataset` の push（★ `git push` は deny）。
      ⚠️ **本 repo 側と近接したタイミングでマージすること**（片側だけだと parity が落ちる）
