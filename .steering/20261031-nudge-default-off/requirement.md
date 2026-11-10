# Nudge の既定の無効化（ADR-040 D1・Migration 1）

## 背景

2026-10-31 に研究者は GSE の位置づけを改め、Nudge を GSE 本体の介入として出さないと決めた（ADR-040 D1）。今の実装では、通常のモードで開始画面の週セレクタの「第2週 (介入)」を選ぶと Nudge が出る（`src/App.tsx` の `PHASE_WEEKS`）。プロセスの初期値も有効である（`src-tauri/src/lib.rs:122` `INTERVENTION_ENABLED = true`。session_meta が届く前と、session_meta を通らない経路で効く。O1 は `lib.rs:4003` で明示的に false にしている）。

## ゴール

本体の通常の操作で Nudge が出ない状態にする。判断のロジック（`analysis/intervention.rs`）と overlay の表示の部品は残す（ADR-040 D2）。

## スコープ

### 含むもの
- `lib.rs:122` の初期値を false にする（研究者の決定・decisions D1）。
- `App.tsx` の第2週の `interventionEnabled` を false にする。`condition`（baseline）と `label_pool`（post_intervention）は変えない（decisions D1）。週の説明文を事実に合わせる。
- 事実を書く docs の「現行で稼働する介入は Nudge のみ」を直す（ADR-040 Consequences の最後の項）。

### 含まないもの
- `intervention.rs` の判断のロジック・`gse-replay --intervention`・`intervention_eval.rs` の変更。
- overlay のサイドカードの削除。
- 招待の配線（タスク B・Migration 2）。
- 論証や履歴の文書（文献カード・未踏の提出物・WBS の過去の計画・ADR の本文）の書き換え。

## 受け入れ条件

- [ ] `INTERVENTION_ENABLED` の初期値が false で、O1・EH3 の挙動が変わらない。
- [ ] 第2週を選んでも session_meta の `intervention_enabled` が false で記録される。
- [ ] ゴールデンのスナップショット回帰（cargo test 内）と `cargo test --workspace` が緑。
- [ ] `emit_schema` の出力が `schema/current.json` と一致（スキーマは変えない）。
- [ ] `tsc`（frontend の型検査）が緑。
- [ ] `/cross-review` を通す。

## 関連ドキュメント

- docs/adr/ADR-040-nudge-not-in-core.md
- .steering/20261031-gse-small-n-research-design/decisions.md 判断 11・12・14

## 運用メモ
- /reimagine 適用: No
- 理由: 研究者が変更の実体を決めた（初期値と第2週の 2 か所）。複数案の比較は済んでいる。
