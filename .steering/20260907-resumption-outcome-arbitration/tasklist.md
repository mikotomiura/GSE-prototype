# タスクリスト

## 準備
- [x] ハンドオフ (`.steering/_handoff/next-session-after-b1.md`) を読む（⚠️ 三次資料として扱う）
- [x] `experiments/20260906-p321-resumption-baseline/notes.md`（B1 の結果と限界）
- [x] `experiments/20260906-interruption-resumption-arm1/notes.md`（M1 の設計と限界）
- [x] `.steering/20260906-resumption-baseline/decisions.md`（判断 1〜5）
- [x] ADR-023 §Context / D6 / D7 / D8 / §Alternatives A3 / §Migration
- [x] 一次で実装を読む（`metrics.rs`）→ ★ **新発見 4 件**
- [x] `/start-task` の grill（`grilling` skill）→ ★ **判断 1〜6 を確定**
- [x] `rust-standards` / `architecture-rules` Skill
- [x] `impact-analyzer` で改名の影響範囲を調査（→ `impact-rename.md`）

## 実装
- [x] `intervention.rs`: `AWAY_IDLE_MS` を `pub const` にする（★ 値も挙動も変えない）
- [x] `metrics.rs`: `OutcomeConfig.away_gap_ms` を追加（既定 = `intervention::AWAY_IDLE_MS`）
- [x] `metrics.rs`: `recovery` 系識別子を `pflow_exit` 系へ改名（★ design.md の改名表）
- [x] `bin/replay.rs` / `intervention_eval.rs` の追随
- [x] `metrics.rs`: `segment_resumptions()`（離席候補明けの再開をエピソードに紐づける）
- [x] `metrics.rs`: `classify_resumption()`（受領 / 次の離席候補 / 打ち切り）
- [x] `metrics.rs`: `cif_receipt()`（Aalen–Johansen・依存 crate なし）
- [x] `metrics.rs`: `ReceiptFreeResumption` を `OutcomeMetrics` に組み込む
- [x] `metrics.rs`: 表示行 (`fmt_*`) を更新
- [x] `bin/replay.rs`: `--metrics` の出力に新指標を載せる

## テスト
- [x] design.md §テスト戦略の 10 本を追加
- [x] ⚠️★★★ **AC-2**: `p_flow` を全部 0.0 にしても新指標が変わらないことを固定
- [x] ⚠️★★★ **AC-3**: `away_gap_ms` の既定が `intervention::AWAY_IDLE_MS` と一致することを固定
- [x] `cargo test --workspace` が exit 0（**D-1 / D-2**）
- [x] `gse-replay --snapshot` が byte-equal（**D-3**）
- [x] `emit_schema` が byte-equal（**D-4**）

## ドキュメント
- [x] `docs/adr/ADR-024-*.md` を起票（★ 却下案 (i)/(ii)/(iii)/(b) と理由 = **AC-5**）
- [x] `docs/adr/README.md` に index 追加
- [x] `docs/glossary.md`: `:247` 例外条項 と `:248` を新版へ揃える（**AC-6**）
- [x] `docs/glossary.md`: 用語追加（`receipt` / `receipt_free_resumption` / `pflow_exit_without_receipt`）
- [x] `experiments/.../arm1/notes.md` §5 の表と定型文を新形へ（**AC-7** = 窓長依存を併記文に入れる）
- [x] `experiments/.../arm1/notes.md` §10 の未決を閉じる
- [x] `PYTHONUTF8=1 python scripts/check_citations.py` を「違反なし」まで（**D-5**）

## レビュー
- [x] `code-reviewer` + `security-checker` を **並列**起動
- [x] HIGH 指摘への対応（⚠️★★★ **backlog へ punt しない**）
- [x] `/cross-review`（⚠️ **コミット後 ＋ パス限定**で回す）

## 完了処理
- [x] design.md の最終化
- [x] decisions.md（★ grill で作成済み）
- [x] git commit（★ design.md §ロールバック計画の 3 本に割る）
- [x] 次セッター用ハンドオフの更新
