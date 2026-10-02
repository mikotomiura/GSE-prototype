# O1 の作業種別の宣言に「その他・細切れの作業」（`other`）を足す

## 背景

O1（継続的自然作業収集・ADR-014）の作業種別の宣言は、いま 4 択である
（論述 / 通信文 / デザイン・映像・制作作業 / vibe coding。`src/components/RecordingControls.tsx` `O1_TASK_KINDS`）。
自然な作業には、メールを読む・調べものなど **4 つのどれとも決めづらい時間**が大量にあるが、その受け皿が無い。

- ⚠️ 被験者は **当てはまらない値を無理に選ぶ**か、**前の宣言を出しっぱなしにする**しかない。
  後者は ADR-016 判断 4b-3 が「原理的に検出できない」として事前登録 §11 の限界に回した
  **陳腐化した宣言**そのもので、制度の側でその発生源を増やしている。
- ⚠️ 「未設定」（`session_meta` が無い状態）は **忘れた** と **どれでもない** を区別できない。
  ★ 後者は「4 つのどれにも入らないと本人が言った」ラベルとして解析に使える（ADR-010 `scope_fit` の外部基準の候補）。

★ O1 は **まだ配っていない**（2026-10-02 研究者確認）。同意文書・事前登録（未凍結）を直す代償が最も安い時点である。

## ゴール

O1 の宣言に 5 つ目の値 **`other`（画面の語「その他・細切れの作業」）** を足し、
新 ADR・schema・backend・frontend・同意フォーム（.gs）・事前登録ドラフト・gse-dataset の対 PR を揃えて **main にマージする**。

## スコープ

### 含むもの
- 新 ADR（ADR-016 判断 4b-2「新 enum 値は足さない」を覆す。ADR-016 本文は書き換えない）
- `TaskKind` / `TaskKindDto` に `Other` を追加・`emit_schema` で `schema/current.json` を再生成
- head の振り分け: `other` → **Writing fallback**（`head_id = writing_fallback`）。推論は変えない
- O1 の宣言 UI（`O1_TASK_KINDS`）に 5 つ目を追加。補足:
  「メールを読む・調べものなど、どれとも決めづらいとき（メールを *書く* のは「通信文」）」
- 同意フォーム `Form_O1/GSE_O1_Form_Builder.gs` の 4 択の逐語箇所を 5 択へ（＋ `o1_form_builder_test.cjs`）
- O1 事前登録ドラフト（未凍結）に `other` の扱いを追記
- gse-dataset（別 repo）に対の PR
- 関連 docs（ADR README / glossary / architecture の該当表）の追随

### 含まないもの
- ⚠️ ADR-031（6 択 ESM）の承認・実装・同意改訂（別途。今回の同意改訂は `other` の 1 点だけ）
- ⚠️ G1 の UI（argumentative lock）には触れない。`other` は O1 の宣言だけに出す
- ⚠️ 観測から `task_kind` を推定すること（ADR-010 D3）
- ⚠️ `HMM_VERSION` の bump（推論を変えないため。要るなら設計段階で止めて相談）
- ⚠️ v0.1.39 のタグ切り・GAS フォームの再配備・`docs/o1-distribution-tag.md` の記録（配布直前の別タスク）

## 受け入れ条件

- [ ] 新 ADR が Accepted（研究者承認）で、`docs/adr/README.md` に載っている
- [ ] `TaskKind::parse("other")` / `as_str` の往復テストが緑、`other` の head が `writing_fallback` になるテストが緑
- [ ] `cargo run --bin emit_schema` の出力が `src-tauri/schema/current.json` と byte-equal（`other` を含む）
- [ ] `gse-replay` の既存ゴールデン（`minimal.json` ほか）が byte-equal のまま（推論不変の証拠）
- [ ] `cargo test --workspace` / `tsc` / clippy 緑
- [ ] O1 の宣言 UI に 5 つ目が出て選べることを目で確認（`ui-changes-need-eyes`）
- [ ] 同意フォーム .gs と UI のラベル・補足が逐語一致（`o1_form_builder_test.cjs` 緑）
- [ ] gse-dataset 側の対 PR が出ており、parity check が通る
- [ ] `/cross-review` 実施（または skip 理由を明記）・CI 緑・main にマージ

## 関連ドキュメント

- `docs/adr/ADR-016-nonkeystroke-interval-handling-in-o1.md` 判断 4b-2 / 4b-3
- `docs/adr/ADR-006-task-kind-beta-wiring.md`（routing）/ `ADR-010`（scope_fit・D3）/ `ADR-005`（additive）
- `.steering/20260823-o1-nonkeystroke-gap-and-prereg/preregistration-draft.md`（未凍結・task 分割を使わない）
- `Form_O1/GSE_O1_Form_Builder.gs:570`, `:931`

## 運用メモ
- /reimagine 適用: No
- 理由: 設計の分岐（head 振り分け・語・同意の版・完了地点・parity）は grill で研究者が全て確定済み。残りは機械的な追随で、複数案の比較が要る未決は無い
