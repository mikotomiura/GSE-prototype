# tasklist

- [x] grill・requirement / decisions
- [x] Step B 調査（file-finder ∥ impact-analyzer）
- [x] design.md・ADR-037 起草 → 研究者承認（2026-10-02）・README 索引
- [x] Rust: `TaskKind::Other`（as_str / parse / 振り分け）・`TaskKindDto::Other`
- [x] Rust: `WritingFallback` の説明 3 か所・`lib.rs` の declare_task_kind コメント
- [x] Rust テスト: 往復・振り分け表・as_str・O1 ローテート値リスト・session_meta 逐語 JSON（other 版）
- [x] `emit_schema` で `schema/current.json` 再生成・byte-equal
- [x] TS: `probeTypes.ts`・`RecordingControls.tsx`（5 つ目＋コメント）・`App.tsx` コメント
- [x] Form_O1: `.gs` 2 か所・`o1_form_builder_test.cjs`
- [x] docs 追随: glossary / workspace-behavior-observation / task-adaptation-and-scope-gating §3.2 / functional-design / agent-shared（ADR 番号範囲）
- [x] 事前登録ドラフト（未凍結）に other の扱いと見直し閾値「過半」
- [x] cargo test --workspace / clippy --all-targets / tsc / gse-replay --snapshot（byte-equal）/ Form テスト
- [x] 宣言 UI の目視確認（5 つ目が出て選べる）
- [x] code-reviewer ∥ security-checker・指摘対応（HIGH 1: consent-draft §2 を上流として先に直す → 対応。MEDIUM 2 / LOW 6 は対応、G1 backend ガードは ADR に注記のみ）
- [x] gse-dataset の schema 対 PR・check_schema_parity.py 一致（ブランチ chore/schema-task-kind-other・89176ee。⚠️ prototype 側 merge 後に merge）
- [x] /finish-task: /cross-review 実施（Codex 完走・自己ブロックなし・両者一致 HIGH なし）。⚠️ Codex P2「other のローテーション結合テスト」は見送り（ローテーションは kind を値として運ぶだけで分岐しない。other 固有の行・振り分け・数値は単体テストで固定済み）
- [ ] push → PR → CI 緑 → merge

## ⚠️ 配布直前の別タスクへの申し送り（security-checker MEDIUM）
- [ ] 同意フォームの再配備は **本変更を含む新しい O1 タグと同時かその後**に行う（旧タグ v0.1.38 以前は 4 択しか出さない）
- [ ] `docs/o1-distribution-tag.md` の新しい節に「同意フォームは 5 択版」「v0.1.38 以前を O1 に使わない」と書く
