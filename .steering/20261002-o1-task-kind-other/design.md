# 設計: O1 の宣言に `other` を足す

## アプローチ

`task_kind` の enum に 5 つ目の値 `other` を足し、振り分けは既存の **Writing fallback**
（`TaskDomain::WritingFallback` / `head_id = writing_fallback`）に乗せる。
新しい head・新しい分岐・数値の変更は作らないので、**推論は 1 ビットも変わらない**。

画面に出すのは **O1 の宣言 UI だけ**（`RecordingControls.tsx` の `O1_TASK_KINDS`）。
G1 の開始画面（`App.tsx` の `TASK_KINDS`・argumentative lock）は触らない。

決定の記録は **ADR-037** として起こし、ADR-016 判断 4b-2「新 enum 値は足さない」を
番号の大きい側で覆す（★ ADR-016 本文は書き換えない）。同意フォーム（`Form_O1/*.gs`）の
4 択の逐語箇所を 5 択へ直し、gse-dataset に schema の対 PR を出す。

## 変更対象ファイル

### 決定
- `docs/adr/ADR-037-o1-task-kind-other.md` — 新規（Proposed → 研究者承認で Accepted）
- `docs/adr/README.md` — 索引に 1 行

### Rust（`src-tauri/`）
- `src/logger.rs`
  - `TaskKind` に `Other`、`as_str` / `parse` に `"other"`
  - `From<TaskKind> for TaskDomain`: `TaskKind::Creative | TaskKind::Other => WritingFallback`
  - テスト: 往復（4446 付近）・振り分け表（4486 付近）・`as_str`（4991 付近）・
    O1 ローテート検査の値リスト（3744）に `other` を追加／`session_meta` 逐語 JSON の `other` 版を 1 本
- `src/schema_dto.rs` — `TaskKindDto::Other`
- `src/analysis/heads/mod.rs` / `heads/writing.rs` / `schema_dto.rs` の `WritingFallback` 説明 —
  「Creative を」→「Creative と Other を」（★ 数値・型は不変、doc コメントのみ）
- `src/lib.rs:1347-1360` — `declare_task_kind` のコメント（「新 enum 値は足さない」）を ADR-037 に合わせる
- `schema/current.json` — `emit_schema` で再生成（手編集しない）

### TypeScript（`src/`）
- `probeTypes.ts` — `TaskKind` ユニオンに `"other"`
- `components/RecordingControls.tsx` — `O1_TASK_KINDS` に 5 つ目
  `{ value: "other", label: "その他・細切れの作業", note: "メールを読む・調べものなど、どれとも決めづらいとき（メールを書くのは「通信文」）" }`
  と、上のコメント（「新しい値を足さない」）の更新
- `App.tsx:14` — コメント「型 TaskKind は 4 種」を 5 種に（★ 選択肢は不変）

### 同意フォーム
- `Form_O1/GSE_O1_Form_Builder.gs:569-570` / `:930-931` — 「4 つの選択肢」→「5 つ」、逐語の列挙に「その他・細切れの作業」
- `Form_O1/o1_form_builder_test.cjs:1259-1260` — 逐語検査の配列に 5 つ目

### docs（数の記述の追随）
- `docs/glossary.md:33` / `docs/architecture/workspace-behavior-observation.md:160` /
  `docs/architecture/task-adaptation-and-scope-gating.md:273` / `docs/functional-design.md`（O1 の宣言の節）
  — ★ 過去の決定の記録（ADR 本文）は書き換えず、現行仕様を述べる箇所だけ直す。
  ★ 書き換えにくい箇所には「ADR-037 で 5 値になった」と注記する
- `.steering/20260823-o1-nonkeystroke-gap-and-prereg/preregistration-draft.md`（未凍結）— §8 / §11 に `other` の扱いを 1 段落

### 別 repo
- `~/gse-dataset/schema/current.json` — 同じ再生成結果を置く PR（`scripts/check_schema_parity.py --dataset ~/gse-dataset` で一致を確認）

## 既存パターンとの整合

- **Creative → WritingFallback の前例**（`.steering/20260818-adr006-head-extraction-wiring/decisions.md` D-6）に
  そのまま乗る。`writing_fallback` の定義「適合する head が無いまま Writing で採点したセッション」
  （`heads/mod.rs:96-104`）は `other` にも当てはまる。`head_id` だけでは Creative と区別できないが、
  `session_meta` の `task_kind` で事後に分けられる。
- **ADR-010 D1**（out-of-scope を head にしない）に反しない —— `other` は宣言の値であって head ではない。
  **D3**（観測から推定しない）にも触れない —— 本人の宣言である。
- **`HMM_VERSION` は上げない**: `engine.rs:36-58` の規約は「新しい入力クラスに対して挙動の**分岐条件が増える**」
  ときに MINOR とする。`other` は既存の fallback 経路に乗るだけで、出力は `writing` と同一（分岐は増えない）。
  ログ上の新しい値は schema（`current.json`）が版管理する。⚠️ ADR-037 の承認に含めて研究者に確認する。
- 旧バイナリで `other` を含むログを replay すると、`bin/replay.rs:3236-3240` / `:3695-3705` が警告して
  Writing に倒す（落ちない）。配布は新タグからなので実害は無い。

## テスト戦略

- `cargo test --workspace`（`src-tauri/`）: 往復・振り分け表（`Other → WritingFallback`）・`session_meta` 逐語 JSON・
  O1 ローテートの値リスト
- `gse-replay --snapshot` の既存ゴールデン（minimal ほか）が **byte-equal のまま**（推論不変の証拠）
- `emit_schema` の出力が `schema/current.json` と byte-equal
- `check_schema_parity.py --dataset ~/gse-dataset` が一致（gse-dataset 側 PR のブランチで）
- `npx tsc --noEmit` / `cargo clippy --all-targets`
- `node Form_O1/o1_form_builder_test.cjs`
- 手動（目視）: O1 モードで宣言 UI を開き、5 つ目が出て選べ、「現在の作業」に「その他・細切れの作業」と出る
  （`ui-changes-need-eyes`。Tauri の shim で実マウントする手順を使う）

## 実装中に判明したこと（2026-10-02）

- ⚠️ **schemars は enum の variant に doc コメントがあると `enum` を `oneOf` に組み替える**。
  → `TaskKindDto::Other` に doc を付けず、説明は型の doc に置いた（schema の差分は enum に 1 値足すだけ）。
- ⚠️ **同意文の上流は `consent-draft-o1.md`**（`.gs:543-546`「先にあちらを直してからここへ写す」）。
  当初 `.gs` だけを直し、code-reviewer に HIGH で指摘された → 雛形 §2 を 5 択にして整合させた。
- ★ UI は補足を「（…）」で囲んで描くので、補足の文言は括弧を含まない形にした（二重括弧の回避）。
- ★ 目視確認: Tauri の shim で実マウントし、5 択・`declare_task_kind {taskKind:"other"}`・表示「作業の種類: その他・細切れの作業」・文字と背景の輝度差 232 を確認（既存 4 択と同値＝対照）。
- ⚠️ G1 で `other` を出さないのは frontend の lock だけ（`record_session_meta` は 5 値を受け付ける・既存の状態）。ADR-037 の切り分け表に注記した。
